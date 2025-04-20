import os
import pandas as pd
import docx2txt
import PyPDF2
import traceback
import pypandoc
from typing import Dict, List, Any, Optional
from .schema import Document, AgentState
import logging
import tempfile
import subprocess
import platform
import shutil


class DocumentProcessor:
    """
    Handles the processing of various document types.
    This class extracts text content from different file formats.
    """
    
    @staticmethod
    def process_document(state: AgentState) -> AgentState:
        """
        Process the document and extract text content from various formats.
        Supports PDF, Word, Excel, PowerPoint, and plain text files.
        
        Args:
            state: The current agent state containing file_path or pre_processed_content
            
        Returns:
            Updated state with extracted documents and metadata
        """
        try:
            # Check for pre-processed content first
            if state.get("pre_processed_content"):
                print("Processing pre-processed content")
                return {
                    **state,
                    "documents": [Document(
                        page_content=state["pre_processed_content"],
                        metadata={"source": "pre_processed", "file_type": "text"}
                    )],
                    "metadata": {
                        "file_type": "text",
                        "document_count": 1,
                        "content_length": len(state["pre_processed_content"])
                    }
                }

            # Get file path
            file_path = state.get("file_path")
            if not file_path:
                raise ValueError("No file path or pre-processed content provided")

            print(f"Processing file: {file_path}")
            
            # Get file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Process based on file type
            if file_ext in ['.xlsx', '.xls']:
                return DocumentProcessor._process_excel(state, file_path, file_ext)
            elif file_ext in ['.docx']:
                return DocumentProcessor._process_docx(state, file_path)
            elif file_ext in ['.doc']:
                return DocumentProcessor._process_doc(state, file_path)
            elif file_ext == '.pdf':
                return DocumentProcessor._process_pdf(state, file_path)
            elif file_ext == '.txt':
                return DocumentProcessor._process_text(state, file_path)
            elif file_ext in ['.ppt', '.pptx']:
                return DocumentProcessor._process_powerpoint(state, file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

        except Exception as e:
            print(f"Error in process_document: {str(e)}")
            print("Full traceback:")
            print(traceback.format_exc())
            return {**state, "error": f"Error processing document: {str(e)}"}

    @staticmethod
    def _process_excel(state: AgentState, file_path: str, file_ext: str) -> AgentState:
        """Process Excel files (.xlsx, .xls)"""
        try:
            print("Processing Excel file")
            try:
                # Check if openpyxl is installed
                import importlib
                openpyxl_spec = importlib.util.find_spec("openpyxl")
                if openpyxl_spec is None:
                    raise ImportError("Missing required dependency 'openpyxl' for Excel processing. Please install with: pip install openpyxl")
                
                # Read all sheets
                xl = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
                documents = []
                
                for sheet_name, df in xl.items():
                    sheet_content = f"Sheet: {sheet_name}\n{df.to_string()}\n\n"
                    documents.append(Document(
                        page_content=sheet_content,
                        metadata={"source": file_path, "file_type": "excel", "sheet": sheet_name}
                    ))
                
                return {
                    **state,
                    "documents": documents,
                    "metadata": {
                        "file_type": "excel",
                        "document_count": len(documents),
                        "content_length": sum(len(doc.page_content) for doc in documents)
                    }
                }
            except ImportError as ie:
                raise ValueError(f"Excel processing error: {str(ie)}")
            except Exception as e:
                # Try with a different engine if openpyxl fails
                try:
                    print("Trying with xlrd engine as fallback")
                    xl = pd.read_excel(file_path, sheet_name=None, engine='xlrd')
                    documents = []
                    
                    for sheet_name, df in xl.items():
                        sheet_content = f"Sheet: {sheet_name}\n{df.to_string()}\n\n"
                        documents.append(Document(
                            page_content=sheet_content,
                            metadata={"source": file_path, "file_type": "excel", "sheet": sheet_name}
                        ))
                    
                    return {
                        **state,
                        "documents": documents,
                        "metadata": {
                            "file_type": "excel",
                            "document_count": len(documents),
                            "content_length": sum(len(doc.page_content) for doc in documents)
                        }
                    }
                except Exception as xlrd_e:
                    raise ValueError(f"Failed to process Excel file with both openpyxl and xlrd engines: {str(e)} and {str(xlrd_e)}")
        except Exception as e:
            raise ValueError(f"Error processing Excel file: {str(e)}")

    @staticmethod
    def _process_docx(state: AgentState, file_path: str) -> AgentState:
        """Process Word documents (.docx)"""
        try:
            print("Processing Word document (.docx)")
            text = docx2txt.process(file_path)
            return {
                **state,
                "documents": [Document(
                    page_content=text,
                    metadata={"source": file_path, "file_type": "word"}
                )],
                "metadata": {
                    "file_type": "word",
                    "document_count": 1,
                    "content_length": len(text)
                }
            }
        except Exception as e:
            raise ValueError(f"Error processing Word document: {str(e)}")

    @staticmethod
    def _process_doc(state: AgentState, file_path: str) -> AgentState:
        """Process older Word documents (.doc)"""
        try:
            print("Processing older Word document (.doc)")
            text = pypandoc.convert_file(file_path, 'plain')
            return {
                **state,
                "documents": [Document(
                    page_content=text,
                    metadata={"source": file_path, "file_type": "word"}
                )],
                "metadata": {
                    "file_type": "word",
                    "document_count": 1,
                    "content_length": len(text)
                }
            }
        except Exception as e:
            raise ValueError(f"Error processing older Word document: {str(e)}")

    @staticmethod
    def _process_pdf(state: AgentState, file_path: str) -> AgentState:
        """Process PDF files (.pdf)"""
        try:
            print("Processing PDF file")
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                print(f"PDF has {num_pages} pages")
                
                # First attempt: standard extraction
                documents = []
                for i, page in enumerate(pdf_reader.pages):
                    print(f"Extracting text from page {i+1}")
                    text = page.extract_text()
                    if text and text.strip():  # Only add non-empty pages
                        documents.append(Document(
                            page_content=text,
                            metadata={"source": file_path, "file_type": "pdf", "page": i + 1}
                        ))
                
                # If no text was extracted, try alternative extraction method
                if not documents:
                    print("No text extracted with primary method, trying alternative extraction...")
                    # Try another method (this is a fallback for scanned PDFs)
                    try:
                        import pypandoc
                        print("Attempting pypandoc extraction...")
                        text = pypandoc.convert_file(file_path, 'plain')
                        if text and text.strip():
                            documents.append(Document(
                                page_content=text,
                                metadata={"source": file_path, "file_type": "pdf", "extraction_method": "pypandoc"}
                            ))
                    except Exception as pandoc_err:
                        print(f"Pypandoc extraction failed: {str(pandoc_err)}")
                
                if not documents:
                    raise ValueError("No text content found in PDF. The PDF might be scanned or protected.")
                
                # Post-process extracted text to clean it up
                cleaned_documents = []
                for doc in documents:
                    # Clean up text by removing excessive whitespace and fixing common OCR issues
                    text = doc.page_content
                    text = ' '.join(text.split())  # Remove multiple spaces
                    text = text.replace(" .", ".")  # Fix common OCR issues
                    text = text.replace(" ,", ",")
                    
                    cleaned_documents.append(Document(
                        page_content=text,
                        metadata=doc.metadata
                    ))
                
                return {
                    **state,
                    "documents": cleaned_documents,
                    "metadata": {
                        "file_type": "pdf",
                        "document_count": len(cleaned_documents),
                        "page_count": num_pages,
                        "content_length": sum(len(doc.page_content) for doc in cleaned_documents)
                    }
                }
        except Exception as e:
            raise ValueError(f"Error processing PDF file: {str(e)}")

    @staticmethod
    def _process_text(state: AgentState, file_path: str) -> AgentState:
        """Process text files (.txt)"""
        try:
            print("Processing text file")
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return {
                **state,
                "documents": [Document(
                    page_content=text,
                    metadata={"source": file_path, "file_type": "text"}
                )],
                "metadata": {
                    "file_type": "text",
                    "document_count": 1,
                    "content_length": len(text)
                }
            }
        except Exception as e:
            raise ValueError(f"Error processing text file: {str(e)}")

    @staticmethod
    def _process_powerpoint(state: AgentState, file_path: str) -> AgentState:
        """Process PowerPoint files (.ppt, .pptx)"""
        try:
            print(f"Processing PowerPoint file: {file_path}")
            
            if not os.path.exists(file_path):
                raise ValueError(f"PowerPoint file not found: {file_path}")
            
            if os.path.getsize(file_path) == 0:
                raise ValueError(f"PowerPoint file is empty: {file_path}")
            
            # Auto-detect pandoc
            pandoc_path = None
            if os.environ.get("PYPANDOC_PANDOC"):
                pandoc_path = os.environ.get("PYPANDOC_PANDOC")
                logging.info(f"Using Pandoc from environment variable: {pandoc_path}")
            else:
                try:
                    pandoc_path = pypandoc.get_pandoc_path()
                    logging.info(f"Found Pandoc at: {pandoc_path}")
                except (OSError, ImportError):
                    # Try to find pandoc manually
                    platform_system = platform.system().lower()
                    possible_paths = []
                    
                    if platform_system == "windows":
                        possible_paths = [
                            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Pandoc", "pandoc.exe"),
                            os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Pandoc", "pandoc.exe"),
                            os.path.expanduser("~\\AppData\\Local\\Pandoc\\pandoc.exe")
                        ]
                    elif platform_system == "darwin":  # macOS
                        possible_paths = [
                            "/usr/local/bin/pandoc",
                            "/opt/homebrew/bin/pandoc",
                            "/opt/local/bin/pandoc"
                        ]
                    else:  # Linux and others
                        possible_paths = [
                            "/usr/bin/pandoc",
                            "/usr/local/bin/pandoc"
                        ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            pandoc_path = path
                            os.environ["PYPANDOC_PANDOC"] = pandoc_path
                            logging.info(f"Found Pandoc at: {pandoc_path}")
                            break
            
            if not pandoc_path:
                pandoc_path = shutil.which("pandoc")
                if pandoc_path:
                    os.environ["PYPANDOC_PANDOC"] = pandoc_path
                    logging.info(f"Found Pandoc in PATH: {pandoc_path}")
            
            if not pandoc_path:
                msg = "Pandoc not found. Please install Pandoc from https://pandoc.org/installing.html"
                msg += " or run the add_pandoc_to_path.bat script (on Windows) to add it to your PATH."
                logging.error(msg)
                raise RuntimeError(msg)
            
            file_extension = os.path.splitext(file_path)[1].lower()
            content = ""
            
            try:
                # Method 1: Try direct conversion with explicit format
                try:
                    logging.info(f"Attempting PowerPoint conversion using direct method with format '{file_extension[1:]}' for {file_path}")
                    if file_extension == '.pptx':
                        content = pypandoc.convert_file(file_path, 'plain', format='pptx')
                    else:
                        content = pypandoc.convert_file(file_path, 'plain', format='ppt')
                        
                    if content and len(content.strip()) > 0:
                        logging.info(f"Successfully converted PowerPoint file using direct method: {file_path}")
                        return {
                            **state,
                            "documents": [Document(
                                page_content=content,
                                metadata={"source": file_path, "file_type": "powerpoint", "extraction_method": "direct_conversion"}
                            )],
                            "metadata": {
                                "file_type": "powerpoint",
                                "document_count": 1,
                                "content_length": len(content)
                            }
                        }
                    else:
                        logging.warning(f"Direct conversion produced empty content for {file_path}")
                except Exception as e:
                    logging.warning(f"Direct conversion failed: {str(e)}")
                
                # Method 2: Try explicit conversion with temporary file
                try:
                    logging.info(f"Attempting PowerPoint conversion using temporary file method for {file_path}")
                    # Create a temporary file with .txt extension
                    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    # Use subprocess to call pandoc directly
                    cmd = [
                        pandoc_path,
                        file_path,
                        "-o", temp_path,
                        "--from", "pptx" if file_extension == '.pptx' else "ppt",
                        "--to", "plain"
                    ]
                    
                    logging.info(f"Running pandoc command: {' '.join(cmd)}")
                    subprocess.run(cmd, check=True, capture_output=True)
                    
                    # Read the content from the temporary file
                    with open(temp_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    
                    # Remove the temporary file
                    try:
                        os.unlink(temp_path)
                    except Exception as e:
                        logging.warning(f"Failed to remove temporary file {temp_path}: {str(e)}")
                    
                    if content and len(content.strip()) > 0:
                        logging.info(f"Successfully converted PowerPoint file using subprocess method: {file_path}")
                        return {
                            **state,
                            "documents": [Document(
                                page_content=content,
                                metadata={"source": file_path, "file_type": "powerpoint", "extraction_method": "subprocess_conversion"}
                            )],
                            "metadata": {
                                "file_type": "powerpoint",
                                "document_count": 1,
                                "content_length": len(content)
                            }
                        }
                    else:
                        logging.warning(f"Subprocess conversion produced empty content for {file_path}")
                except Exception as e:
                    logging.warning(f"Subprocess conversion failed: {str(e)}")
                
                # Method 3: Try auto-detection (last resort)
                try:
                    logging.info(f"Attempting PowerPoint conversion using auto-detection for {file_path}")
                    content = pypandoc.convert_file(file_path, 'plain')
                    
                    if content and len(content.strip()) > 0:
                        logging.info(f"Successfully converted PowerPoint file using auto-detection: {file_path}")
                        return {
                            **state,
                            "documents": [Document(
                                page_content=content,
                                metadata={"source": file_path, "file_type": "powerpoint", "extraction_method": "auto_detection"}
                            )],
                            "metadata": {
                                "file_type": "powerpoint",
                                "document_count": 1,
                                "content_length": len(content)
                            }
                        }
                    else:
                        logging.warning(f"Auto-detection conversion produced empty content for {file_path}")
                except Exception as e:
                    logging.warning(f"Auto-detection conversion failed: {str(e)}")
                
                # If we get here, all methods failed but didn't raise an exception
                if not content or len(content.strip()) == 0:
                    raise ValueError(f"Failed to extract content from PowerPoint file: {file_path}. " 
                                    f"The file may be empty, corrupted, or not a valid PowerPoint file.")
                
                return {
                    **state,
                    "documents": [Document(
                        page_content=content,
                        metadata={"source": file_path, "file_type": "powerpoint", "extraction_method": "fallback"}
                    )],
                    "metadata": {
                        "file_type": "powerpoint",
                        "document_count": 1,
                        "content_length": len(content)
                    }
                }
            
            except Exception as e:
                error_msg = (f"Error processing PowerPoint file '{os.path.basename(file_path)}': {str(e)}. "
                            f"Please ensure Pandoc is correctly installed and the file is not corrupted.")
                logging.error(error_msg)
                logging.error(f"Exception details: {traceback.format_exc()}")
                raise RuntimeError(error_msg)
            
        except Exception as e:
            error_msg = str(e)
            if "No pandoc was found" in error_msg or "Pandoc is required" in error_msg:
                raise ValueError("Pandoc is required for PowerPoint processing but was not found on the system. Please install Pandoc from https://pandoc.org/installing.html")
            
            # Add more context to the error
            if "pptx" in error_msg.lower() or "powerpoint" in error_msg.lower():
                # This is already a PowerPoint-specific error
                raise ValueError(f"Error processing PowerPoint file: {error_msg}")
            else:
                # Generic error, add PowerPoint context
                raise ValueError(f"Error processing PowerPoint file {file_path}: {error_msg}") 