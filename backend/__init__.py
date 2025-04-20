# Backend package for Document QA application
# Using LangGraph and Groq 

"""
Document QA Agent Backend Module
Provides document processing and question answering capabilities.
"""

import os
import shutil
import platform
import sys

# Auto-detect and configure Pandoc
def configure_pandoc():
    """Auto-detect Pandoc and configure the environment"""
    try:
        # Try to find pandoc in common locations
        pandoc_path = shutil.which('pandoc')
        if not pandoc_path:
            # Check common install locations
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
                    pandoc_path = location
                    break
        
        if pandoc_path:
            print(f"✅ Pandoc found at: {pandoc_path}")
            # Set environment variable for pypandoc
            os.environ["PYPANDOC_PANDOC"] = pandoc_path
            
            # Add to PATH if not already there
            pandoc_dir = os.path.dirname(pandoc_path)
            if pandoc_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = pandoc_dir + os.pathsep + os.environ.get("PATH", "")
            
            return True
    except Exception as e:
        print(f"Warning: Error configuring Pandoc: {str(e)}")
    
    return False

# Run Pandoc configuration when module is imported
configure_pandoc() 