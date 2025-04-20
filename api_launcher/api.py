"""
API launcher for backward compatibility.
This file allows existing code to continue working with the new backend.
"""
import sys
import os

# Add parent directory to path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the new backend module
from backend.api import app, run_api_server

# Set the app variable for backward compatibility
app = app

if __name__ == "__main__":
    print("Starting Document QA API server (backward compatibility mode)...")
    print("This launcher maintains compatibility with the old API structure")
    print("For new projects, use 'python main.py' instead")
    
    # Run the API server
    run_api_server(host="0.0.0.0", port=8000, reload=True) 