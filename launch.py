#!/usr/bin/env python3
"""
Bible Verse Application Launcher

A unified launcher that starts both the API server and GUI application.
This provides a single entry point for users.
"""

import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import requests
import os

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import uvicorn
    except ImportError:
        missing_deps.append("uvicorn")
        
    try:
        import fastapi
    except ImportError:
        missing_deps.append("fastapi")
        
    try:
        import sqlalchemy
    except ImportError:
        missing_deps.append("sqlalchemy")
    
    return missing_deps

def install_dependencies():
    """Install missing dependencies"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[gui]"], 
                      check=True, cwd=Path.cwd())
        return True
    except subprocess.CalledProcessError:
        return False

def start_api_server():
    """Start the FastAPI server in background"""
    try:
        # Start the server
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--host", "127.0.0.1", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=Path.cwd())
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                return server_process
        except requests.exceptions.RequestException:
            pass
        
        # Server failed to start
        server_process.terminate()
        return None
        
    except Exception:
        return None

def launch_gui():
    """Launch the GUI application"""
    try:
        from gui.main import main
        from gui.manager import add_verse_manager_to_main_gui, VerseManagerWindow
        from gui.main import BibleVerseGUI
        
        # Enhance the main GUI with verse manager
        BibleVerseGUI = add_verse_manager_to_main_gui(BibleVerseGUI)
        
        # Start GUI
        root = tk.Tk()
        app = BibleVerseGUI(root)
        
        # Handle window closing
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start GUI: {e}")

def show_startup_dialog():
    """Show startup options dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    result = messagebox.askyesnocancel(
        "Bible Verse Application",
        "Choose how to start the application:\n\n"
        "Yes - Start with GUI (recommended)\n"
        "No - Start API server only\n"
        "Cancel - Exit"
    )
    
    root.destroy()
    return result

def main():
    """Main launcher function"""
    print("Bible Verse Application Launcher")
    print("=" * 40)
    
    # Check dependencies
    print("Checking dependencies...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print("Installing dependencies...")
        
        if install_dependencies():
            print("Dependencies installed successfully!")
        else:
            print("Failed to install dependencies.")
            print("Please run: pip install -e .[gui]")
            return 1
    else:
        print("All dependencies found!")
    
    # Check if running from command line with arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "gui":
            launch_gui()
        elif arg == "server":
            print("Starting API server only...")
            subprocess.run([
                sys.executable, "-m", "uvicorn", "app.main:app", 
                "--host", "127.0.0.1", "--port", "8000", "--reload"
            ], cwd=Path.cwd())
        else:
            print("Usage: python launch.py [gui|server]")
            return 1
    else:
        # Interactive mode
        startup_choice = show_startup_dialog()
        
        if startup_choice is None:  # Cancel
            return 0
        elif startup_choice:  # Yes - GUI
            print("Starting with GUI...")
            launch_gui()
        else:  # No - Server only
            print("Starting API server only...")
            print("Visit http://127.0.0.1:8000/docs for API documentation")
            subprocess.run([
                sys.executable, "-m", "uvicorn", "app.main:app", 
                "--host", "127.0.0.1", "--port", "8000", "--reload"
            ], cwd=Path.cwd())
    
    return 0

if __name__ == "__main__":
    sys.exit(main())