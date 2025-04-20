from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
import tempfile
import time
import traceback

from .schema import QuestionRequest, UploadResponse, ChatResponse
from .agent import DocumentQAAgent

# Create FastAPI app
app = FastAPI(
    title="Document QA API", 
    description="API for the Document QA application that processes various document types and answers questions"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the QA agent
agent = DocumentQAAgent()

# Create upload directory
UPLOAD_DIR = os.path.join(os.getcwd(), "data", "uploaded_docs")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a document file for processing"""
    try:
        print(f"Received file: {file.filename}")
        
        # Validate file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        supported_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.txt', '.ppt', '.pptx']
        
        if file_ext not in supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: {', '.join(supported_extensions)}"
            )
        
        # Check file size (10MB limit)
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > 10 * 1024 * 1024:  # 10MB
                    os.unlink(temp_file.name)
                    raise HTTPException(
                        status_code=400,
                        detail="File size exceeds 10MB limit"
                    )
                temp_file.write(chunk)
            
            temp_file_path = temp_file.name
        
        # Create a unique filename
        unique_filename = f"{os.path.splitext(file.filename)[0]}_{int(time.time())}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Move the temporary file to the upload directory
        shutil.move(temp_file_path, file_path)
        
        print(f"File saved to: {file_path}")
        print("Processing document...")
        
        try:
            # For document extraction, we use a simple question that doesn't analyze
            # This ensures we get the raw content rather than a summary or analysis
            result = agent.run(
                file_path=file_path, 
                question="Simply return the raw content of this document without any analysis or summary."
            )
            
            # Verify we got actual content
            if not result or len(result) < 20:
                # Try direct extraction instead
                print("Initial extraction yielded insufficient content, trying direct extraction...")
                from .processors import DocumentProcessor
                process_result = DocumentProcessor.process_document({"file_path": file_path})
                
                # Extract all document content
                content = ""
                if process_result and "documents" in process_result:
                    for doc in process_result["documents"]:
                        content += doc.page_content + "\n\n"
                    
                    if content.strip():
                        result = content
                    else:
                        raise ValueError("Could not extract text content from document")
                else:
                    # If we got an error in processing, report it
                    if process_result and "error" in process_result:
                        raise ValueError(process_result["error"])
                    else:
                        raise ValueError("Document processing failed to extract text content")
            
            # Validate the extracted content
            if not result or not result.strip() or len(result) < 10:
                raise ValueError("The document appears to be empty or contains no extractable text content")
            
            print(f"Document processed successfully, extracted {len(result)} characters")
            
            # Return success response with processed content
            preview = result[:500] + "..." if len(result) > 500 else result
            
            return UploadResponse(
                status="success",
                message="File uploaded and processed successfully",
                filename=unique_filename,
                content_preview=preview,
                content=result  # Full processed content
            )
            
        except Exception as e:
            # Clean up the file if processing fails
            if os.path.exists(file_path):
                os.remove(file_path)
            error_message = str(e)
            print(f"Error processing file: {error_message}")
            print("Full traceback:")
            print(traceback.format_exc())
            
            # Custom error messages for common issues
            if "openpyxl" in error_message.lower() or "xlrd" in error_message.lower():
                detail = "Excel processing failed: The server is missing required dependencies. Please ask the administrator to install: pip install openpyxl xlrd"
            elif ".xls" in file_path.lower() and "excel" in error_message.lower():
                detail = f"Excel processing failed: {error_message}. The file may be password-protected, corrupted, or in an unsupported format."
            elif "pandoc" in error_message.lower():
                detail = "PowerPoint processing failed: Pandoc is required but not installed. Please ask the administrator to install Pandoc from https://pandoc.org/installing.html"
            elif (".ppt" in file_path.lower() or "powerpoint" in error_message.lower()):
                detail = f"PowerPoint processing failed: {error_message}. The file may be password-protected, corrupted, or in an unsupported format."
            else:
                detail = f"Error processing file: {error_message}"
                
            raise HTTPException(
                status_code=500,
                detail=detail
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload endpoint: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: QuestionRequest):
    """Ask a question about the uploaded document"""
    try:
        print(f"Received chat request: {request.question}")
        print(f"File info available: {request.file_info is not None}")
        
        # Validate request
        if not request.question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # If we have file info from the frontend
        if request.file_info and request.file_info.get("content"):
            print("Using pre-processed content")
            content_length = len(request.file_info.get("content", ""))
            print(f"Content length: {content_length}")
            
            content = request.file_info.get("content", "").strip()
            if not content:
                raise HTTPException(
                    status_code=400,
                    detail="The document content is empty. Please try uploading the file again."
                )
            
            # Log the first 200 characters for debugging
            content_preview = content[:200].replace('\n', ' ') + '...'
            print(f"Content preview: {content_preview}")
            
            try:
                # Check if the content is too short to be a proper document
                if len(content) < 50:
                    raise ValueError("The document content is too short to process. Please upload a valid document.")
                
                answer = agent.run(
                    question=request.question,
                    pre_processed_content=content
                )
                print("Answer generated successfully using pre-processed content")
            except Exception as e:
                print(f"Error processing pre-processed content: {str(e)}")
                print("Full traceback:")
                print(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"Error processing content: {str(e)}")
        else:
            print("Looking for uploaded file")
            # Find the most recent file in the upload directory
            files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
            if not files:
                raise HTTPException(status_code=400, detail="No document has been uploaded")
            
            # Sort by modification time, newest first
            latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(UPLOAD_DIR, f)))
            file_path = os.path.join(UPLOAD_DIR, latest_file)
            print(f"Using file: {latest_file}")
            
            try:
                # Process the question
                answer = agent.run(
                    file_path=file_path,
                    question=request.question
                )
                print("Answer generated successfully using file")
            except Exception as e:
                print(f"Error processing file: {str(e)}")
                print("Full traceback:")
                print(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        
        return ChatResponse(
            status="success",
            answer=answer
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# Main entrypoint for the application
def run_api_server(host="0.0.0.0", port=8000, reload=True):
    """Run the FastAPI server"""
    # Mount the React frontend in production
    app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")
    
    # Start the server
    uvicorn.run("backend.api:app", host=host, port=port, reload=reload) 