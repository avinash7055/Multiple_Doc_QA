from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
import traceback
import os
from dotenv import load_dotenv

from .processors import DocumentProcessor
from .schema import AgentState

# Load environment variables
load_dotenv()

def build_qa_graph() -> StateGraph:
    """
    Build the LangGraph workflow for document QA.
    
    The graph has two nodes:
    1. process_document: Extracts text from various document formats
    2. answer_question: Generates an answer to the user's question
    
    Returns:
        A compiled StateGraph
    """
    # Create the graph with our state
    workflow = StateGraph(AgentState)
    
    # Add the document processing node
    workflow.add_node("process_document", DocumentProcessor.process_document)
    
    # Add the answer generation node
    workflow.add_node("answer_question", answer_question)
    
    # Define the edges
    workflow.add_edge("process_document", "answer_question")
    workflow.add_edge("answer_question", END)
    
    # Set the entry point
    workflow.set_entry_point("process_document")
    
    # Compile the graph
    return workflow.compile()


def answer_question(state: AgentState) -> AgentState:
    """
    Generate an answer to the user's question based on processed documents.
    
    Args:
        state: The current agent state containing documents and question
        
    Returns:
        Updated state with the answer
    """
    try:
        # Check if we have documents
        documents = state.get("documents", [])
        if not documents:
            return {
                **state, 
                "answer": "I don't have any document content to analyze. Please upload a document first."
            }

        # Extract content from documents
        content = ""
        file_type = "unknown"
        
        # Get content from all documents
        for doc in documents:
            content += doc.page_content + "\n\n"
            # Try to get file type from metadata
            if not file_type or file_type == "unknown":
                file_type = doc.metadata.get("file_type", file_type)
        
        if not content.strip():
            return {
                **state,
                "answer": "The document appears to be empty or contains no extractable text content. Please try uploading a different document format or check if the document contains actual text content that can be extracted."
            }
            
        # Print content preview for debugging
        content_preview = content[:200].replace('\n', ' ') + '...'
        print(f"Document content preview: {content_preview}")
        print(f"Total content length: {len(content)} characters")
        
        # Initialize Groq language model
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Check if API key is available
        if not os.getenv("GROQ_API_KEY"):
            print("WARNING: GROQ_API_KEY environment variable not set")
            return {
                **state,
                "answer": "API key not configured. Please set the GROQ_API_KEY environment variable."
            }
            
        # Check if we're just requesting the raw content
        if state.get("question", "").lower().strip() in [
            "simply return the raw content of this document without any analysis or summary.",
            "raw content", 
            "show content", 
            "extract content"
        ]:
            print("Returning raw document content as requested")
            return {
                **state,
                "answer": content[:8000] if len(content) > 8000 else content
            }
        
        # Build system prompt based on file type
        file_type_desc = "document"
        
        if "excel" in file_type:
            file_type_desc = "Excel spreadsheet"
        elif "word" in file_type:
            file_type_desc = "Word document"
        elif "pdf" in file_type:
            file_type_desc = "PDF document"
        elif "text" in file_type:
            file_type_desc = "text file"
        elif "powerpoint" in file_type:
            file_type_desc = "PowerPoint presentation"
        
        # Create prompt template with file type context
        system_prompt = f"""You are a document analysis assistant specialized in answering questions about {file_type_desc}s.
        Your task is to analyze the provided document content and answer questions about it EXACTLY as it appears in the document.
        Follow these rules strictly:
        1. ONLY use information that is EXPLICITLY contained in the document content
        2. If the answer cannot be found in the document, politely explain that you don't see that specific information in the current document, then try to be helpful by suggesting related information from the document that might be relevant or suggesting how the user might rephrase their question
        3. Be precise and specific in your answers, quoting directly from the text when possible
        4. For numerical data, provide exact values as they appear in the document
        5. If a question asks for information about a person or topic that's in the document, list all available details from the document
        6. Do NOT make assumptions, inferences, or provide information not present in the document
        7. For questions that are related to the document but where the exact answer isn't directly stated, explain what relevant information IS available in the document
        8. NEVER respond with "I cannot find any information about X in the document" and stop there - always try to provide the most relevant information that IS available
        9. If the document contains complex data (such as tables or numbers), make sure to convey this information clearly and accurately
        10. Assume the user has not seen the document content, so provide COMPLETE information"""
        
        print(f"Document content length: {len(content)} characters")
        # Ensure we're not truncating content too severely by increasing the character limit
        content_for_context = content[:25000] if len(content) > 25000 else content
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Document Content:\n\n{context}\n\nQuestion: {question}\n\nPlease provide a precise answer based only on the document content above."),
        ])
        
        # Create chain
        chain = prompt | llm
        
        # Generate answer
        response = chain.invoke({
            "context": content_for_context,
            "question": state["question"]
        })
        
        return {**state, "answer": response.content}
        
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        
        # Provide more specific error message for common issues
        error_message = str(e)
        if "openpyxl" in error_message.lower():
            return {
                **state, 
                "answer": "I encountered an error while processing your Excel file. The server is missing the 'openpyxl' package which is required for Excel support. Please contact the administrator to install this package by running: pip install openpyxl"
            }
        elif "xlrd" in error_message.lower():
            return {
                **state, 
                "answer": "I encountered an error while processing your Excel file. The server is missing packages required for Excel support. Please contact the administrator to install the necessary packages by running: pip install openpyxl xlrd"
            }
        elif "excel" in error_message.lower():
            return {
                **state, 
                "answer": "I encountered an error while processing your Excel file. Please make sure your Excel file is not password-protected or corrupted. The specific error was: " + error_message
            }
        elif "pandoc" in error_message.lower():
            return {
                **state, 
                "answer": "I encountered an error while processing your PowerPoint file. The server is missing Pandoc which is required for PowerPoint support. Pandoc is not a Python package but a separate program that needs to be installed on the system. Please ask the administrator to install Pandoc from https://pandoc.org/installing.html"
            }
        elif "powerpoint" in error_message.lower():
            return {
                **state, 
                "answer": "I encountered an error while processing your PowerPoint file. Please make sure your PowerPoint file is not password-protected or corrupted. The specific error was: " + error_message
            }
        
        return {
            **state, 
            "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}"
        }


class DocumentQAAgent:
    """
    Main agent class that processes documents and answers questions.
    Uses LangGraph for workflow orchestration.
    """
    
    def __init__(self):
        # Compile the graph once during initialization
        self.graph = build_qa_graph()
    
    def run(self, question: str, file_path: str = None, pre_processed_content: str = None) -> str:
        """
        Run the document QA agent with either a file path or pre-processed content.
        
        Args:
            question: The question to answer
            file_path: Path to document file (optional if pre_processed_content is provided)
            pre_processed_content: Pre-processed text content (optional if file_path is provided)
            
        Returns:
            The answer generated by the agent
        """
        if not file_path and not pre_processed_content:
            return "No document provided. Please provide either a file path or pre-processed content."
        
        # Create initial state
        initial_state: AgentState = {
            "question": question
        }
        
        # Add either file path or pre-processed content, but not both
        if pre_processed_content:
            print(f"Running agent with pre-processed content ({len(pre_processed_content)} chars)")
            # Validate content length
            if len(pre_processed_content) < 10:
                return "The provided document content is too short or empty. Please upload a valid document."
                
            initial_state["pre_processed_content"] = pre_processed_content
        elif file_path:
            print(f"Running agent with file: {file_path}")
            # Check if file exists
            if not os.path.exists(file_path):
                return f"File not found: {file_path}. Please upload a valid document."
                
            initial_state["file_path"] = file_path
        
        try:
            # Invoke the graph with the configured state
            config = {"recursion_limit": 50}
            result = self.graph.invoke(initial_state, config)
            
            # Check for errors in the result
            if "error" in result:
                print(f"Error reported in graph result: {result['error']}")
                return f"Error processing document: {result['error']}"
            
            # Extract and return the answer
            answer = result.get("answer")
            if not answer:
                return "No answer could be generated. Please try rephrasing your question or upload a different document."
            
            return answer
            
        except Exception as e:
            print(f"Error in DocumentQAAgent.run(): {str(e)}")
            print("Full traceback:")
            print(traceback.format_exc())
            return f"An error occurred while processing your request: {str(e)}" 