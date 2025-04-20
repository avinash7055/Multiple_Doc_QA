#!/usr/bin/env python3
"""
Command-line interface for the Document QA agent.
This allows using the agent directly without starting the API server.
"""
import argparse
import os
import sys
from .agent import DocumentQAAgent

def main():
    """Main entry point for direct agent usage"""
    parser = argparse.ArgumentParser(
        description="Document QA agent for answering questions about documents"
    )
    parser.add_argument(
        "-f", "--file", 
        help="Path to the document file to process"
    )
    parser.add_argument(
        "-q", "--question", 
        help="Question to ask about the document",
        required=True
    )
    parser.add_argument(
        "--content", 
        help="Pre-processed content to analyze instead of a file"
    )
    
    args = parser.parse_args()
    
    # Check that either file or content is provided
    if not args.file and not args.content:
        print("Error: Either --file or --content must be provided")
        sys.exit(1)
    
    # Make sure the file exists if provided
    if args.file and not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    # Initialize agent
    agent = DocumentQAAgent()
    
    try:
        # Run agent with provided arguments
        if args.file:
            print(f"Processing file: {args.file}")
            print(f"Question: {args.question}")
            answer = agent.run(
                question=args.question, 
                file_path=args.file
            )
        else:
            print(f"Processing provided content")
            print(f"Question: {args.question}")
            answer = agent.run(
                question=args.question, 
                pre_processed_content=args.content
            )
        
        # Print answer
        print("\nAnswer:")
        print("=" * 80)
        print(answer)
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 