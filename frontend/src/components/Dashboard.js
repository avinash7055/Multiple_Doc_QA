import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Grid,
  Typography,
  Paper,
  Stack,
} from '@mui/material';
import {
  Description as DescriptionIcon,
  QuestionAnswer as QuestionAnswerIcon,
  FileUpload as FileUploadIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Slideshow as SlideshowIcon,
  Article as ArticleIcon,
  TextSnippet as TextSnippetIcon,
  PictureAsPdf as PdfIcon,
  TableChart as TableIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Animation variants for staggered animations
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 100,
    },
  },
};

const fileTypes = [
  { name: 'PDF Documents', icon: <PdfIcon fontSize="large" sx={{ color: '#FF5733' }} /> },
  { name: 'Word Documents', icon: <ArticleIcon fontSize="large" sx={{ color: '#2B579A' }} /> },
  { name: 'Excel Spreadsheets', icon: <TableIcon fontSize="large" sx={{ color: '#217346' }} /> },
  { name: 'PowerPoint Slides', icon: <SlideshowIcon fontSize="large" sx={{ color: '#B7472A' }} /> },
  { name: 'Text Files', icon: <TextSnippetIcon fontSize="large" sx={{ color: '#444444' }} /> },
];

const features = [
  {
    title: 'Natural Language Q&A',
    description: 'Ask questions about your documents in plain English and get accurate answers.',
    icon: <QuestionAnswerIcon fontSize="large" sx={{ color: 'primary.main' }} />,
  },
  {
    title: 'Multiple File Formats',
    description: 'Support for PDF, Word, Excel, PowerPoint, TXT, and more document types.',
    icon: <DescriptionIcon fontSize="large" sx={{ color: 'primary.main' }} />,
  },
  {
    title: 'Fast Processing',
    description: 'Advanced AI processes your documents quickly, giving you insights in seconds.',
    icon: <SpeedIcon fontSize="large" sx={{ color: 'primary.main' }} />,
  },
  {
    title: 'Secure Handling',
    description: 'Your documents are processed securely and not stored permanently.',
    icon: <SecurityIcon fontSize="large" sx={{ color: 'primary.main' }} />,
  },
];

const Dashboard = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Box mb={6}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography 
            variant="h3" 
            component="h1" 
            gutterBottom 
            align="center"
            sx={{ 
              fontWeight: 700, 
              background: 'linear-gradient(90deg, #6366F1 0%, #EC4899 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 2
            }}
          >
            Intelligent Document Q&A
          </Typography>
          <Typography variant="h6" color="textSecondary" align="center" paragraph sx={{ mb: 4 }}>
            Upload your documents and chat with our AI to get instant answers to your questions
          </Typography>
          <Box display="flex" justifyContent="center" gap={2}>
            <Button
              component={RouterLink}
              to="/upload"
              variant="contained"
              size="large"
              color="primary"
              startIcon={<FileUploadIcon />}
              sx={{ px: 3, py: 1.5, borderRadius: 2 }}
            >
              Upload Document
            </Button>
            <Button
              component={RouterLink}
              to="/chat"
              variant="outlined"
              size="large"
              color="primary"
              startIcon={<QuestionAnswerIcon />}
              sx={{ px: 3, py: 1.5, borderRadius: 2 }}
            >
              Start Chatting
            </Button>
          </Box>
        </motion.div>
      </Box>

      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" component="h2" mb={4} fontWeight={600}>
          Supported Document Types
        </Typography>
        <Paper elevation={2} sx={{ borderRadius: 4, p: 3 }}>
          <Grid container spacing={2}>
            {fileTypes.map((fileType, index) => (
              <Grid item xs={6} sm={4} md={2.4} key={fileType.name}>
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      textAlign: 'center',
                      p: 2,
                    }}
                  >
                    {fileType.icon}
                    <Typography variant="body1" sx={{ mt: 1, fontWeight: 500 }}>
                      {fileType.name}
                    </Typography>
                  </Box>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Box>

      <Box>
        <Typography variant="h4" component="h2" mb={4} fontWeight={600}>
          Key Features
        </Typography>
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <Grid container spacing={3}>
            {features.map((feature) => (
              <Grid item xs={12} sm={6} md={3} key={feature.title}>
                <motion.div variants={itemVariants}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: 'transform 0.3s, box-shadow 0.3s',
                      '&:hover': {
                        transform: 'translateY(-8px)',
                        boxShadow: '0 12px 20px -10px rgba(0,0,0,0.1)',
                      },
                    }}
                    elevation={1}
                  >
                    <CardContent>
                      <Stack spacing={2} alignItems="center" sx={{ textAlign: 'center' }}>
                        <Box>{feature.icon}</Box>
                        <Typography variant="h6" component="h3" fontWeight={600}>
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {feature.description}
                        </Typography>
                      </Stack>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Box>
    </Container>
  );
};

export default Dashboard; 