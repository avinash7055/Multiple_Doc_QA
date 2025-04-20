# Document QA Agent with LangGraph and React UI

![Python Version](https://img.shields.io/badge/Python-3.8+-blue)
![React Version](https://img.shields.io/badge/React-18.0+-61DAFB)
![License](https://img.shields.io/badge/License-MIT-green)

A powerful document analysis tool that allows users to upload various document formats and ask questions about their content. The application uses LangGraph for workflow orchestration and Groq LLMs for natural language understanding.

## Features

- **Multi-format Document Support**: PDF, Word, Excel, PowerPoint, and text files
- **Modern React Frontend**: Clean, intuitive UI built with Material UI
- **Advanced Question Answering**: Extract precise information from your documents
- **LangGraph Architecture**: Modular, maintainable agent workflow

## Prerequisites

- Python 3.8+
- Node.js and npm
- Groq API key
- Pandoc (required for PowerPoint and legacy Word files)

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install Pandoc (required for PowerPoint and legacy Word files):
   - Windows: Download the installer from https://pandoc.org/installing.html
   - macOS: `brew install pandoc`
   - Linux: `apt install pandoc` or `yum install pandoc`
4. Create `.env` file with your Groq API key: `GROQ_API_KEY=your_key_here`
5. Run the backend: `python main.py`
6. In a separate terminal, navigate to the frontend directory and run: `npm install && npm start`
7. Open your browser to `http://localhost:3000`

## Dependencies

The application relies on:
- [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- [Groq](https://groq.com/) for LLM inference
- [React](https://reactjs.org/) and [Material UI](https://mui.com/) for the frontend
- [FastAPI](https://fastapi.tiangolo.com/) for the backend
- [Pandoc](https://pandoc.org/) for PowerPoint and legacy Word file processing

## Usage

### Web Application

1. Access the application at `http://localhost:3000`
2. Upload a document (PDF, Word, Excel, PowerPoint, or text file)
3. Ask questions about the document's content
4. Receive accurate answers based on the document

### Command Line

You can also use the agent directly from the command line:

```bash
# Process a file and ask a question
python -m backend --file path/to/document.pdf --question "What is this document about?"

# Process pre-processed content
python -m backend --content "Your text content here" --question "What does this content say about X?"
```

### API Usage

The application offers multiple ways to run:

1. Standard mode: `python main.py`
2. Backward compatibility mode: `python run_api_wrapper.py`
3. Direct CLI usage (as shown above)

## Architecture

### Backend

The backend uses a modular architecture built from scratch:

- **LangGraph Workflow**: Directed graph for document processing and QA
- **Document Processors**: Specialized handlers for each file format
- **FastAPI Server**: REST API with comprehensive error handling
- **CLI Interface**: Command-line access for direct agent usage

#### LangGraph Workflow Diagram

The Document QA Agent uses a directed graph built with LangGraph to process documents and answer questions:

```
                            ┌─────────────────┐
                            │                 │
                            │  User Question  │
                            │                 │
                            └────────┬────────┘
                                     │
                                     ▼
┌─────────────────┐          ┌─────────────────┐
│                 │          │                 │
│  Document File  ├─────────►│ Document        │
│  (PDF, DOCX...) │          │ Processing Node │
│                 │          │                 │
└─────────────────┘          └────────┬────────┘
                                     │
                                     │
                                     ▼
                            ┌─────────────────┐
                            │                 │
                            │  Question       │
                            │  Answering Node │
                            │                 │
                            └────────┬────────┘
                                     │
                                     │
                                     ▼
                            ┌─────────────────┐
                            │                 │
                            │   Response to   │
                            │     User        │
                            │                 │
                            └─────────────────┘
```

The workflow consists of two primary nodes:

1. **Document Processing Node**: Handles document ingestion and text extraction based on file type
   - PDF processing with PyPDF2
   - Word document processing with docx2txt
   - Excel processing with pandas
   - PowerPoint processing with Pandoc
   - Plain text processing

2. **Question Answering Node**: Uses the Groq LLM to:
   - Analyze the question intent
   - Generate a relevant, accurate response based on document content
   - Format the response appropriately

The graph maintains state throughout the workflow and has robust error handling at each node.

### Frontend

- **React**: Modern component-based UI
- **Material UI**: Polished user interface components
- **Context API**: Global state management
- **Axios**: API communication

## Development

### Backend Structure

The backend is organized into modular components:

- `backend/schema.py`: Data models and type definitions
- `backend/processors.py`: Document processing logic
- `backend/agent.py`: LangGraph agent implementation
- `backend/api.py`: FastAPI endpoints

### Frontend Structure

- `frontend/src/components`: React UI components
- `frontend/src/contexts`: Global state management
- `frontend/src/config.js`: API configuration
- `frontend/src/App.js`: Main application routing

## API Documentation

The API has two main endpoints:

- `POST /api/upload`: Upload a document
  - Request: `multipart/form-data` with a file
  - Response: Document content and metadata

- `POST /api/chat`: Ask a question
  - Request: JSON with question and optional file info
  - Response: Answer based on document content

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

MIT

## Acknowledgements

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Groq](https://groq.com/)
- [React](https://reactjs.org/)
- [Material UI](https://mui.com/)
- [FastAPI](https://fastapi.tiangolo.com/)

## Supported Document Types

- PDF (`.pdf`)
- Word (`.docx`, `.doc`)
- Excel (`.xlsx`, `.xls`)
- PowerPoint (`.ppt`, `.pptx`) - requires Pandoc
- Text (`.txt`)

## Troubleshooting

If you encounter issues with specific file types:

- **Excel files**: Make sure `openpyxl` is installed: `pip install openpyxl`
- **PowerPoint files**: Make sure Pandoc is installed on your system
- **Legacy Word (.doc)**: Requires Pandoc

For Windows users, run the included script to add Pandoc to your PATH:
```
add_pandoc_to_path.bat
```
