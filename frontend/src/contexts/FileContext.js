import React, { createContext, useState, useContext } from 'react';

const FileContext = createContext();

export const useFile = () => useContext(FileContext);

export const FileProvider = ({ children }) => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [fileType, setFileType] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  const clearFile = () => {
    setUploadedFile(null);
    setFileContent(null);
    setFileType(null);
    setChatHistory([]);
  };

  const addMessageToHistory = (message) => {
    setChatHistory(prev => [...prev, message]);
  };

  const value = {
    uploadedFile,
    setUploadedFile,
    fileContent,
    setFileContent,
    fileType,
    setFileType,
    isProcessing,
    setIsProcessing,
    chatHistory,
    setChatHistory,
    clearFile,
    addMessageToHistory
  };

  return <FileContext.Provider value={value}>{children}</FileContext.Provider>;
}; 