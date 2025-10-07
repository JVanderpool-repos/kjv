"""
Bible Verse of the Day - GUI Application

A desktop interface for the Bible Verse API that provides:
- Daily verse display
- Random verse generation
- Verse history
- Settings management
- Data loading capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import json
import threading
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
import webbrowser

class BibleVerseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bible Verse of the Day")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configuration
        self.api_base = "http://127.0.0.1:8000"
        self.server_process = None
        
        # Style configuration
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Check if server is running
        self.check_server_status()
        
    def setup_styles(self):
        """Configure the visual styling"""
        style = ttk.Style()
        
        # Configure colors and fonts
        self.bg_color = "#f8f9fa"
        self.primary_color = "#2c3e50"
        self.text_color = "#34495e"
        self.accent_color = "#3498db"
        
        self.root.configure(bg=self.bg_color)
        
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = tk.Label(main_frame, text="Bible Verse of the Day", 
                              font=("Arial", 18, "bold"), 
                              fg=self.primary_color, bg=self.bg_color)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_label = tk.Label(status_frame, text="Checking server...", 
                                    fg=self.text_color, bg=self.bg_color)
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.start_server_btn = ttk.Button(status_frame, text="Start Server", 
                                          command=self.start_server)
        self.start_server_btn.grid(row=0, column=2, padx=(10, 0))
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.today_btn = ttk.Button(button_frame, text="Today's Verse", 
                                   command=self.get_today_verse, style="Accent.TButton")
        self.today_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.random_btn = ttk.Button(button_frame, text="Random Verse", 
                                    command=self.get_random_verse)
        self.random_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_btn = ttk.Button(button_frame, text="Refresh", 
                                     command=self.refresh_display)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Verse display area
        self.verse_display = scrolledtext.ScrolledText(content_frame, 
                                                      wrap=tk.WORD, 
                                                      height=15, 
                                                      font=("Georgia", 12),
                                                      bg="white",
                                                      relief=tk.RAISED,
                                                      borderwidth=2)
        self.verse_display.grid(row=1, column=0, sticky="nsew")
        
        # Bottom frame with utilities
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        bottom_frame.columnconfigure(2, weight=1)
        
        self.load_data_btn = ttk.Button(bottom_frame, text="Load Verses", 
                                       command=self.load_verses)
        self.load_data_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.settings_btn = ttk.Button(bottom_frame, text="Settings", 
                                      command=self.open_settings)
        self.settings_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.web_btn = ttk.Button(bottom_frame, text="Open Web Interface", 
                                 command=self.open_web_interface)
        self.web_btn.grid(row=0, column=3)
        
        # Initial display
        self.display_welcome_message()
        
    def display_welcome_message(self):
        """Show welcome message in verse display"""
        welcome_text = """Welcome to Bible Verse of the Day!

This application provides daily Bible verses from the King James Version.

Features:
• Get today's verse (same verse all day)
• Generate random verses for study
• Load your own verse data from CSV files
• No verse repetition until all verses are used
• Consecutive days avoid same chapters when possible

To get started:
1. Make sure the server is running (check status above)
2. Load some verse data using "Load Verses" button
3. Click "Today's Verse" to see your daily verse

The KJV text is public domain and free to use.

"""
        self.verse_display.delete(1.0, tk.END)
        self.verse_display.insert(1.0, welcome_text)
        
    def check_server_status(self):
        """Check if the API server is running"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=2)
            if response.status_code == 200:
                self.status_label.config(text="✅ Server running", fg="green")
                self.start_server_btn.config(text="Stop Server", command=self.stop_server)
                self.enable_buttons()
            else:
                self.server_not_running()
        except requests.exceptions.RequestException:
            self.server_not_running()
            
    def server_not_running(self):
        """Handle server not running state"""
        self.status_label.config(text="❌ Server not running", fg="red")
        self.start_server_btn.config(text="Start Server", command=self.start_server)
        self.disable_buttons()
        
    def enable_buttons(self):
        """Enable verse-related buttons"""
        self.today_btn.config(state=tk.NORMAL)
        self.random_btn.config(state=tk.NORMAL)
        self.refresh_btn.config(state=tk.NORMAL)
        
    def disable_buttons(self):
        """Disable verse-related buttons"""
        self.today_btn.config(state=tk.DISABLED)
        self.random_btn.config(state=tk.DISABLED)
        self.refresh_btn.config(state=tk.DISABLED)
        
    def start_server(self):
        """Start the FastAPI server in background"""
        try:
            # Start server process
            self.server_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "app.main:app", 
                "--host", "127.0.0.1", "--port", "8000"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=Path.cwd())
            
            self.status_label.config(text="🔄 Starting server...", fg="orange")
            
            # Wait a moment then check status
            self.root.after(3000, self.check_server_status)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
            
    def stop_server(self):
        """Stop the FastAPI server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            
        self.status_label.config(text="❌ Server stopped", fg="red")
        self.start_server_btn.config(text="Start Server", command=self.start_server)
        self.disable_buttons()
        
    def get_today_verse(self):
        """Fetch and display today's verse"""
        try:
            response = requests.get(f"{self.api_base}/verse/today", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.display_verse(data, "Today's Verse")
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                self.display_error(f"Error getting today's verse: {error_msg}")
        except requests.exceptions.RequestException as e:
            self.display_error(f"Network error: {e}")
            
    def get_random_verse(self):
        """Fetch and display a random verse"""
        try:
            response = requests.get(f"{self.api_base}/verse/random", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.display_verse(data, "Random Verse")
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                self.display_error(f"Error getting random verse: {error_msg}")
        except requests.exceptions.RequestException as e:
            self.display_error(f"Network error: {e}")
            
    def display_verse(self, verse_data, title="Verse"):
        """Display verse data in the text area"""
        self.verse_display.delete(1.0, tk.END)
        
        # Format the verse display
        content = f"{title}\n"
        content += "=" * len(title) + "\n\n"
        
        if 'date' in verse_data:
            content += f"Date: {verse_data['date']}\n"
        
        content += f"Reference: {verse_data['reference']}\n\n"
        content += f"KJV Text:\n{verse_data['kjv']}\n\n"
        
        content += f"Retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        self.verse_display.insert(1.0, content)
        
    def display_error(self, error_message):
        """Display error message in the text area"""
        self.verse_display.delete(1.0, tk.END)
        error_content = f"Error\n=====\n\n{error_message}\n\n"
        error_content += "Possible solutions:\n"
        error_content += "• Make sure the server is running\n"
        error_content += "• Load some verse data using 'Load Verses'\n"
        error_content += "• Check your internet connection\n"
        self.verse_display.insert(1.0, error_content)
        
    def refresh_display(self):
        """Refresh the current display"""
        self.check_server_status()
        
    def load_verses(self):
        """Open file dialog to load verses from CSV"""
        file_path = filedialog.askopenfilename(
            title="Select Verses CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Run the load script
                result = subprocess.run([
                    sys.executable, "-m", "scripts.load_verses", file_path
                ], capture_output=True, text=True, cwd=Path.cwd())
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"Verses loaded successfully!\n\n{result.stdout}")
                else:
                    messagebox.showerror("Error", f"Failed to load verses:\n\n{result.stderr}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load verses: {e}")
                
    def open_settings(self):
        """Open settings dialog"""
        settings_window = SettingsWindow(self.root, self)
        
    def open_web_interface(self):
        """Open the web interface in default browser"""
        try:
            webbrowser.open(f"{self.api_base}/docs")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open web interface: {e}")
            
    def on_closing(self):
        """Handle application closing"""
        if self.server_process:
            self.stop_server()
        self.root.destroy()


class SettingsWindow:
    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("400x300")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_settings_widgets()
        
    def create_settings_widgets(self):
        """Create settings interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Settings
        api_frame = ttk.LabelFrame(main_frame, text="API Settings", padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(api_frame, text="API Base URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.api_url_var = tk.StringVar(value=self.main_app.api_base)
        api_url_entry = ttk.Entry(api_frame, textvariable=self.api_url_var, width=40)
        api_url_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Database Settings
        db_frame = ttk.LabelFrame(main_frame, text="Database Settings", padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(db_frame, text="Database Path:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.db_path_var = tk.StringVar(value="bible.db")
        db_path_entry = ttk.Entry(db_frame, textvariable=self.db_path_var, width=30)
        db_path_entry.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        browse_btn = ttk.Button(db_frame, text="Browse", command=self.browse_database)
        browse_btn.grid(row=1, column=1, padx=(5, 0))
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)
        
    def browse_database(self):
        """Browse for database file"""
        file_path = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("Database files", "*.db"), ("SQLite files", "*.sqlite"), ("All files", "*.*")]
        )
        if file_path:
            self.db_path_var.set(file_path)
            
    def save_settings(self):
        """Save settings and close window"""
        self.main_app.api_base = self.api_url_var.get().rstrip('/')
        # Here you could save settings to a config file
        messagebox.showinfo("Settings", "Settings saved successfully!")
        self.window.destroy()


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = BibleVerseGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()