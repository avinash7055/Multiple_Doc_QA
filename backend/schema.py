from typing import Dict, List, Optional, TypedDict, Any, Union
from pydantic import BaseModel, Field


class Document(BaseModel):
    """Represents a document or chunk of a document with content and metadata."""
    page_content: str = Field(..., description="The textual content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the document")


class AgentState(TypedDict, total=False):
    """The state object passed between nodes in the LangGraph workflow."""
    # Inputs
    file_path: Optional[str]  # Path to the document file
    pre_processed_content: Optional[str]  # Pre-processed text if available
    question: str  # User's question
    
    # Processing results
    documents: List[Document]  # Processed documents
    metadata: Dict[str, Any]  # Document metadata
    answer: str  # Final answer to return to user
    error: Optional[str]  # Error message if processing failed


class QuestionRequest(BaseModel):
    """Request model for the chat endpoint."""
    question: str
    file_info: Optional[Dict[str, Any]] = None


class UploadResponse(BaseModel):
    """Response model for the file upload endpoint."""
    status: str
    message: str
    filename: str
    content_preview: str
    content: str


class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    status: str
    answer: str 