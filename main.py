#!/usr/bin/env python3
"""
Document QA Agent - Main Entry Point
This script starts the FastAPI server for the Document QA application.
"""

import os
import sys
import platform
import shutil

def ensure_pandoc_available():
    """Ensure Pandoc is available for PowerPoint processing"""
    try:
        # Check if Pandoc is already in the PATH
        pandoc_path = shutil.which('pandoc')
        if pandoc_path:
            print(f"✅ Pandoc found in PATH: {pandoc_path}")
            os.environ["PYPANDOC_PANDOC"] = pandoc_path
            return True
        
        # Search for Pandoc in common locations
        system = platform.system()
        possible_locations = []
        
        if system == "Windows":
            possible_locations = [
                r"C:\Program Files\Pandoc\pandoc.exe",
                r"C:\Program Files (x86)\Pandoc\pandoc.exe",
                os.path.expanduser(r"~\AppData\Local\Pandoc\pandoc.exe")
            ]
        elif system == "Darwin":  # macOS
            possible_locations = [
                "/usr/local/bin/pandoc",
                "/opt/homebrew/bin/pandoc",
                "/opt/local/bin/pandoc"
            ]
        elif system == "Linux":
            possible_locations = [
                "/usr/bin/pandoc",
                "/usr/local/bin/pandoc"
            ]
        
        for location in possible_locations:
            if os.path.exists(location):
                print(f"✅ Pandoc found at: {location}")
                # Set environment variable for pypandoc
                os.environ["PYPANDOC_PANDOC"] = location
                
                # Add to PATH if not already there
                pandoc_dir = os.path.dirname(location)
                os.environ["PATH"] = pandoc_dir + os.pathsep + os.environ.get("PATH", "")
                
                return True
        
        print("⚠️ Pandoc not found. PowerPoint files will not be processed correctly.")
        print("   To install Pandoc, run: python install_pandoc.py")
        return False
    except Exception as e:
        print(f"⚠️ Error checking for Pandoc: {str(e)}")
        return False

# Ensure Pandoc is available before importing the backend
ensure_pandoc_available()

# Import backend after Pandoc is configured
from backend.api import run_api_server

if __name__ == "__main__":
    print("Starting Document QA Agent...")
    run_api_server() 