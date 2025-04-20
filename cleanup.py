#!/usr/bin/env python
import os
import shutil
import glob

def main():
    """Clean up the repository by removing temporary and unused files."""
    print("Cleaning up repository for GitHub...")
    
    # 1. Remove uploaded documents (test files)
    uploaded_docs_dir = os.path.join("data", "uploaded_docs")
    if os.path.exists(uploaded_docs_dir):
        print(f"Cleaning {uploaded_docs_dir}...")
        # Keep directory but remove contents
        for file in os.listdir(uploaded_docs_dir):
            file_path = os.path.join(uploaded_docs_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"  Removed: {file_path}")
    
    # 2. Remove all __pycache__ directories
    for root, dirs, files in os.walk("."):
        for dir in dirs:
            if dir == "__pycache__":
                cache_dir = os.path.join(root, dir)
                print(f"Removing: {cache_dir}")
                shutil.rmtree(cache_dir)
    
    # 3. Remove all .pyc files (compiled Python)
    for pyc_file in glob.glob("**/*.pyc", recursive=True):
        print(f"Removing: {pyc_file}")
        os.remove(pyc_file)
    
    # 4. Remove temporary/debugging files
    debug_files = [
        "use_pandoc.py",
        "run_with_pandoc.py", 
        "debug_pandoc.py",
        "check_dependencies.py",
        "install_pandoc.py"
    ]
    
    for file in debug_files:
        if os.path.exists(file):
            print(f"Removing debug file: {file}")
            os.remove(file)
    
    # 5. Create .gitignore if it doesn't exist
    if not os.path.exists(".gitignore"):
        create_gitignore()
    
    print("Clean-up complete! Your repository is ready for GitHub.")
    print("Remember to run 'git add .' to add your cleaned files.")

def create_gitignore():
    """Create a standard .gitignore file for Python projects."""
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
dist/
build/
*.egg-info/

# Virtual environments
venv/
env/
ENV/

# Environment variables
.env

# Uploaded documents (test files)
data/uploaded_docs/*
!data/uploaded_docs/.gitkeep

# IDE files
.vscode/
.idea/

# Logs
*.log

# OS specific files
.DS_Store
Thumbs.db
"""
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("Created .gitignore file")

if __name__ == "__main__":
    main() 