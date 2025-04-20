import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Avatar,
  Chip,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  Alert,
  Tooltip,
  Fade,
  Zoom,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  FileUpload as UploadIcon,
  DeleteOutline as ClearIcon,
  History as HistoryIcon,
  ContentCopy as CopyIcon,
  Article as DocumentIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import { useFile } from '../contexts/FileContext';
import config from '../config';

// Message bubble animations
const messageVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
};

// Typing indicator animation
const typingVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.3 } },
  exit: { opacity: 0, transition: { duration: 0.3 } },
};

// Dot animation for typing indicator
const dotVariants = {
  initial: { y: 0 },
  animate: {
    y: [0, -5, 0],
    transition: { duration: 0.6, repeat: Infinity, repeatType: 'loop' },
  },
};

const Chat = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { uploadedFile, fileContent, fileType, chatHistory, addMessageToHistory, clearFile } = useFile();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDocumentInfo, setShowDocumentInfo] = useState(true);
  const endOfMessagesRef = useRef(null);
  const navigate = useNavigate();

  // Add an ID for the current loading session
  const [loadingSessionId, setLoadingSessionId] = useState(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory]);

  // Handle submission of a new question
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const userMessage = { role: 'user', content: input };
    addMessageToHistory(userMessage);
    setInput('');
    
    // Generate a unique loading session ID
    const currentSessionId = Date.now().toString();
    setLoadingSessionId(currentSessionId);
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Chat request URL:', `${config.API_BASE_URL}/api/chat`);
      console.log('File content available:', !!fileContent);
      
      // Check if we have valid file content
      if (!fileContent || !fileContent.trim()) {
        throw new Error('No valid document content is available. Please try re-uploading your document.');
      }
      
      if (fileContent.length < 20) {
        throw new Error('The document content appears to be too short or empty. Please try uploading a different document.');
      }
      
      const requestData = {
        question: input,
        file_info: fileContent ? {
          name: uploadedFile?.name || 'document',
          type: fileType || 'application/octet-stream',
          content: fileContent
        } : null
      };
      
      console.log('Sending request with file info:', {
        hasContent: !!requestData.file_info?.content,
        contentLength: requestData.file_info?.content ? requestData.file_info.content.length : 0
      });
      
      const response = await axios.post(`${config.API_BASE_URL}/api/chat`, requestData);
      
      if (response.data && response.data.status === 'success') {
        const botMessage = { role: 'assistant', content: response.data.answer };
        addMessageToHistory(botMessage);
      } else {
        throw new Error(response.data?.message || 'Failed to get answer');
      }
    } catch (err) {
      console.error('Chat error:', err);
      let errorMessage = 'Failed to get an answer';
      
      if (err.response) {
        // Handle HTTP error responses
        if (err.response.status === 400) {
          errorMessage += ': ' + (err.response.data?.detail || 'Bad request');
        } else if (err.response.status === 500) {
          errorMessage += ': Server error - ' + (err.response.data?.detail || 'Internal server error');
        } else {
          errorMessage += ': ' + (err.response.data?.detail || err.message);
        }
      } else if (err.request) {
        // Handle network errors
        errorMessage += ': Network error - Could not connect to server';
      } else {
        errorMessage += ': ' + err.message;
      }
      
      setError(errorMessage);
      // Add error message to chat history
      addMessageToHistory({ 
        role: 'assistant', 
        content: 'Sorry, I encountered an error: ' + errorMessage,
        isError: true 
      });
    } finally {
      // Safety cleanup in case of errors
      setIsLoading(false);
      setLoadingSessionId(null);
    }
  };

  const handleClear = () => {
    clearFile();
    navigate('/upload');
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
  };

  const toggleDocumentInfo = () => {
    setShowDocumentInfo(!showDocumentInfo);
  };

  // If no file is uploaded, redirect to upload page
  if (!uploadedFile) {
    return (
      <Container maxWidth="md" sx={{ py: 6, textAlign: 'center' }}>
        <Card elevation={3} sx={{ borderRadius: 3, p: 4 }}>
          <CardContent>
            <Typography variant="h5" component="h1" gutterBottom>
              No Document Loaded
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
              Please upload a document first to start chatting
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<UploadIcon />}
              onClick={() => navigate('/upload')}
              sx={{ mt: 2 }}
            >
              Upload Document
            </Button>
          </CardContent>
        </Card>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4, display: 'flex', flexDirection: 'column', height: 'calc(100vh - 80px)' }}>
      {/* Document Info Header */}
      <Fade in={true} timeout={500}>
        <Paper elevation={3} sx={{ 
          p: 2, 
          display: 'flex', 
          alignItems: 'center',
          justifyContent: 'space-between',
          borderRadius: 2,
          mb: 2,
          bgcolor: 'background.paper',
          position: 'sticky',
          top: 0,
          zIndex: 1
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <DocumentIcon />
            </Avatar>
            <Box>
              <Typography variant="subtitle1" fontWeight={600} noWrap>
                {uploadedFile?.name}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {uploadedFile?.size ? `${(uploadedFile.size / 1024).toFixed(1)} KB` : ''}
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Toggle Document Info">
              <IconButton onClick={toggleDocumentInfo} size="small">
                {showDocumentInfo ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Tooltip>
            <Tooltip title="Clear Chat">
              <IconButton 
                color="error" 
                onClick={handleClear} 
                size="small"
              >
                <ClearIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Paper>
      </Fade>

      {/* Chat Messages Area */}
      <Paper 
        elevation={3} 
        sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          flex: 1,
          borderRadius: 2,
          overflow: 'hidden',
          bgcolor: 'background.default',
        }}
      >
        <Box 
          sx={{ 
            flex: 1, 
            overflowY: 'auto', 
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            gap: 2
          }}
        >
          <AnimatePresence mode="sync">
            {chatHistory.map((message, index) => (
              <motion.div
                key={`message-${index}`}
                variants={messageVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                style={{ 
                  alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: isMobile ? '90%' : '70%'
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    gap: 1,
                    flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: message.role === 'user' ? 'secondary.main' : 'primary.main',
                    }}
                  >
                    {message.role === 'user' ? <PersonIcon /> : <BotIcon />}
                  </Avatar>
                  <Paper
                    elevation={1}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: message.role === 'user' ? 'secondary.light' : 'background.paper',
                      position: 'relative',
                    }}
                  >
                    {message.role === 'assistant' && (
                      <Tooltip title="Copy to Clipboard">
                        <IconButton
                          size="small"
                          sx={{
                            position: 'absolute',
                            top: 8,
                            right: 8,
                            opacity: 0.6,
                            '&:hover': { opacity: 1 },
                          }}
                          onClick={() => handleCopy(message.content)}
                        >
                          <CopyIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Box sx={{ pr: message.role === 'assistant' ? 4 : 0 }}>
                      {message.role === 'assistant' ? (
                        <Box className="markdown-body">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </Box>
                      ) : (
                        <Typography>{message.content}</Typography>
                      )}
                    </Box>
                  </Paper>
                </Box>
              </motion.div>
            ))}

            {/* Typing indicator - only show if loading and not just added a response */}
            {isLoading && (
              <motion.div
                key={`typing-indicator-${loadingSessionId}`}
                variants={typingVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                style={{ alignSelf: 'flex-start' }}
              >
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'flex-start', 
                  gap: 2,
                  mt: 2 
                }}>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    <BotIcon />
                  </Avatar>
                  <Paper
                    elevation={1}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1
                    }}
                  >
                    <Typography>Thinking</Typography>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {[0, 1, 2].map((i) => (
                        <motion.span
                          key={i}
                          variants={dotVariants}
                          animate="animate"
                          style={{ 
                            display: 'inline-block', 
                            width: '5px',
                            height: '5px',
                            borderRadius: '50%',
                            backgroundColor: 'currentColor', 
                          }}
                          transition={{ delay: i * 0.15 }}
                        >
                          .
                        </motion.span>
                      ))}
                    </Box>
                  </Paper>
                </Box>
              </motion.div>
            )}

            {error && (
              <Zoom in={true}>
                <Alert 
                  severity="error" 
                  sx={{ mt: 2, borderRadius: 2 }}
                  onClose={() => setError(null)}
                >
                  {error}
                </Alert>
              </Zoom>
            )}

            <div ref={endOfMessagesRef} />
          </AnimatePresence>
        </Box>

        <Divider />

        {/* Input area */}
        <Box 
          component="form" 
          onSubmit={handleSubmit} 
          sx={{ 
            p: 2, 
            bgcolor: 'background.paper',
            display: 'flex',
            gap: 1
          }}
        >
          <TextField
            fullWidth
            placeholder="Ask a question about your document..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            variant="outlined"
            disabled={isLoading}
            multiline
            maxRows={4}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={!input.trim() || isLoading}
            sx={{ 
              borderRadius: 2,
              minWidth: '50px',
              height: '56px'
            }}
          >
            {isLoading ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Chat; 