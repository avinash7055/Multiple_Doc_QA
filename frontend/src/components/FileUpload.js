import React, { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Typography,
  Paper,
  Container,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Alert,
  AlertTitle,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  Check as CheckIcon,
  Clear as ErrorIcon,
  PictureAsPdf as PdfIcon,
  Article as WordIcon,
  TableChart as ExcelIcon,
  Slideshow as PowerPointIcon,
  TextSnippet as TextIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import axios from 'axios';
import { useFile } from '../contexts/FileContext';
import config from '../config';

// File type icons mapping
const getFileIcon = (fileType) => {
  switch (fileType) {
    case 'application/pdf':
      return <PdfIcon sx={{ color: '#FF5733' }} />;
    case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
    case 'application/msword':
      return <WordIcon sx={{ color: '#2B579A' }} />;
    case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
    case 'application/vnd.ms-excel':
      return <ExcelIcon sx={{ color: '#217346' }} />;
    case 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
    case 'application/vnd.ms-powerpoint':
      return <PowerPointIcon sx={{ color: '#B7472A' }} />;
    case 'text/plain':
      return <TextIcon sx={{ color: '#444444' }} />;
    default:
      return <FileIcon />;
  }
};

// File size formatter
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Supported file types
const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/vnd.ms-excel': ['.xls'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-powerpoint': ['.ppt'],
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  'text/plain': ['.txt'],
};

const FileUpload = () => {
  const { setUploadedFile, setFileContent, setFileType, setIsProcessing } = useFile();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles) => {
    setError(null);
    
    // Only take the first file if multiple are dropped
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setUploadStatus(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 10485760, // 10MB
    accept: ACCEPTED_FILE_TYPES,
    onDropRejected: (rejections) => {
      const rejection = rejections[0];
      if (rejection.errors[0].code === 'file-too-large') {
        setError('File is too large. Maximum size is 10MB.');
      } else if (rejection.errors[0].code === 'file-invalid-type') {
        setError('Unsupported file type. Please upload a PDF, Word, Excel, PowerPoint, or text file.');
      } else {
        setError('File upload error: ' + rejection.errors[0].message);
      }
    },
  });

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setIsProcessing(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      console.log('Uploading file to:', `${config.API_BASE_URL}/api/upload`);
      const response = await axios.post(`${config.API_BASE_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Upload response status:', response.status);
      
      if (response.data && response.data.status === 'success') {
        if (!response.data.content) {
          throw new Error('No content received from server. The document may be empty or could not be processed.');
        }
        
        console.log('Received content length:', response.data.content.length);
        setUploadStatus('success');
        setUploadedFile(file);
        setFileContent(response.data.content);  // Store the full content
        setFileType(file.type);
        
        // Navigate to chat after successful upload
        setTimeout(() => {
          setIsProcessing(false);
          navigate('/chat');
        }, 1500);
      } else {
        throw new Error(response.data?.message || 'Upload failed');
      }
    } catch (err) {
      console.error('Upload error:', err);
      const errorMsg = err.response?.data?.detail || err.message;
      setError('Failed to upload file: ' + errorMsg);
      setUploadStatus('error');
      setIsProcessing(false);
    } finally {
      setUploading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setUploadStatus(null);
    setError(null);
    setUploadedFile(null);
  };

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography 
          variant="h4" 
          component="h1" 
          align="center" 
          gutterBottom
          sx={{ 
            fontWeight: 700,
            mb: 2
          }}
        >
          Upload Your Document
        </Typography>
        <Typography variant="body1" color="textSecondary" align="center" paragraph sx={{ mb: 4 }}>
          Upload a document to start analyzing and asking questions about its content
        </Typography>
      </motion.div>

      <Card elevation={3} sx={{ borderRadius: 3, mb: 4 }}>
        <CardContent sx={{ p: 4 }}>
          <Box {...getRootProps()} sx={{ mb: 3 }}>
            <input {...getInputProps()} />
            <Paper
              variant="outlined"
              sx={{
                border: isDragReject 
                  ? '2px dashed #f44336' 
                  : isDragActive 
                    ? '2px dashed #6366f1' 
                    : '2px dashed #e0e0e0',
                borderRadius: 2,
                p: 6,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                cursor: 'pointer',
                bgcolor: isDragActive ? 'rgba(99, 102, 241, 0.04)' : 'transparent',
                transition: 'all 0.2s ease-in-out',
              }}
            >
              <motion.div
                animate={{ scale: isDragActive ? 1.1 : 1 }}
                transition={{ duration: 0.2 }}
              >
                <UploadIcon 
                  sx={{ 
                    fontSize: 64, 
                    mb: 2, 
                    color: isDragReject 
                      ? 'error.main' 
                      : isDragActive 
                        ? 'primary.main' 
                        : 'text.secondary' 
                  }} 
                />
              </motion.div>
              
              <Typography variant="h6" align="center" sx={{ mb: 1 }}>
                {isDragActive 
                  ? "Drop your file here" 
                  : "Drag & drop your file here or click to browse"}
              </Typography>
              
              <Typography variant="body2" color="textSecondary" align="center">
                Supports PDF, Word, Excel, PowerPoint, and text files (max 10MB)
              </Typography>
            </Paper>
          </Box>

          {error && (
            <Alert 
              severity="error" 
              sx={{ mb: 3, borderRadius: 2 }}
              onClose={() => setError(null)}
            >
              <AlertTitle>Error</AlertTitle>
              {error}
            </Alert>
          )}

          {file && !error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ duration: 0.3 }}
            >
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, mb: 3 }}>
                <List disablePadding>
                  <ListItem>
                    <ListItemIcon>
                      {getFileIcon(file.type)}
                    </ListItemIcon>
                    <ListItemText 
                      primary={file.name} 
                      secondary={formatFileSize(file.size)} 
                    />
                    <Chip 
                      label={uploadStatus === 'success' ? 'Uploaded' : 'Ready to upload'} 
                      color={uploadStatus === 'success' ? 'success' : 'default'}
                      size="small"
                      icon={uploadStatus === 'success' ? <CheckIcon /> : null}
                      sx={{ mr: 1 }}
                    />
                    <Button 
                      size="small" 
                      color="error" 
                      onClick={removeFile}
                      disabled={uploading}
                      startIcon={<ErrorIcon />}
                    >
                      Remove
                    </Button>
                  </ListItem>
                </List>
              </Paper>
            </motion.div>
          )}

          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              disabled={!file || uploading || uploadStatus === 'success'}
              onClick={handleUpload}
              startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <UploadIcon />}
              sx={{ px: 4, py: 1.2, borderRadius: 2 }}
            >
              {uploading ? 'Uploading...' : 'Upload Document'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Supported Document Types
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
              <List dense>
                <ListItem>
                  <ListItemIcon><PdfIcon sx={{ color: '#FF5733' }} /></ListItemIcon>
                  <ListItemText primary="PDF Documents (.pdf)" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><WordIcon sx={{ color: '#2B579A' }} /></ListItemIcon>
                  <ListItemText primary="Word Documents (.doc, .docx)" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><TextIcon sx={{ color: '#444444' }} /></ListItemIcon>
                  <ListItemText primary="Text Files (.txt)" />
                </ListItem>
              </List>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
              <List dense>
                <ListItem>
                  <ListItemIcon><ExcelIcon sx={{ color: '#217346' }} /></ListItemIcon>
                  <ListItemText primary="Excel Spreadsheets (.xls, .xlsx)" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><PowerPointIcon sx={{ color: '#B7472A' }} /></ListItemIcon>
                  <ListItemText primary="PowerPoint Presentations (.ppt, .pptx)" />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default FileUpload; 