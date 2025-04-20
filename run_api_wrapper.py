"""
Wrapper script to run the API in backward compatibility mode.
This allows existing code to continue working with the new backend structure.
"""
import sys
import os

# Make sure this file is in the root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the API launcher
from api_launcher.api import app, run_api_server

if __name__ == "__main__":
    print("Running API in backward compatibility mode...")
    run_api_server(host="0.0.0.0", port=8000, reload=True) 