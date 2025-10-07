"""
Bible Verse Management GUI

Additional windows and utilities for managing verses, viewing statistics,
and performing administrative tasks.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import sys
from pathlib import Path
import sqlite3
from datetime import datetime, date, timedelta

class VerseManagerWindow:
    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("Verse Management")
        self.window.geometry("700x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_management_widgets()
        self.load_statistics()
        
    def create_management_widgets(self):
        """Create verse management interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Statistics Tab
        stats_frame = ttk.Frame(notebook, padding="10")
        notebook.add(stats_frame, text="Statistics")
        self.create_statistics_tab(stats_frame)
        
        # Data Management Tab
        data_frame = ttk.Frame(notebook, padding="10")
        notebook.add(data_frame, text="Data Management")
        self.create_data_management_tab(data_frame)
        
        # Scheduling Tab
        schedule_frame = ttk.Frame(notebook, padding="10")
        notebook.add(schedule_frame, text="Scheduling")
        self.create_scheduling_tab(schedule_frame)
        
    def create_statistics_tab(self, parent):
        """Create statistics display tab"""
        # Statistics display
        self.stats_text = scrolledtext.ScrolledText(parent, height=15, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(parent, text="Refresh Statistics", 
                                command=self.load_statistics)
        refresh_btn.pack(side=tk.RIGHT)
        
    def create_data_management_tab(self, parent):
        """Create data management tab"""
        # Load data section
        load_frame = ttk.LabelFrame(parent, text="Load Verse Data", padding="10")
        load_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(load_frame, text="Load verses from CSV file:").pack(anchor=tk.W)
        
        file_frame = ttk.Frame(load_frame)
        file_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_csv_file)
        browse_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        load_btn = ttk.Button(file_frame, text="Load", command=self.load_csv_data)
        load_btn.pack(side=tk.RIGHT)
        
        # Database operations section
        db_frame = ttk.LabelFrame(parent, text="Database Operations", padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 10))
        
        db_button_frame = ttk.Frame(db_frame)
        db_button_frame.pack(fill=tk.X)
        
        ttk.Button(db_button_frame, text="Reset Daily Selections", 
                  command=self.reset_daily_selections).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(db_button_frame, text="Clear All Verses", 
                  command=self.clear_all_verses).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(db_button_frame, text="Backup Database", 
                  command=self.backup_database).pack(side=tk.LEFT)
        
        # Export section
        export_frame = ttk.LabelFrame(parent, text="Export Data", padding="10")
        export_frame.pack(fill=tk.X)
        
        export_button_frame = ttk.Frame(export_frame)
        export_button_frame.pack(fill=tk.X)
        
        ttk.Button(export_button_frame, text="Export All Verses", 
                  command=self.export_verses).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_button_frame, text="Export Daily Selections", 
                  command=self.export_selections).pack(side=tk.LEFT)
        
    def create_scheduling_tab(self, parent):
        """Create verse scheduling tab"""
        # Schedule generation section
        schedule_frame = ttk.LabelFrame(parent, text="Generate Schedule", padding="10")
        schedule_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date range selection
        date_frame = ttk.Frame(schedule_frame)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(date_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.start_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        start_date_entry = ttk.Entry(date_frame, textvariable=self.start_date_var, width=15)
        start_date_entry.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(date_frame, text="Number of Days:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.days_var = tk.StringVar(value="30")
        days_entry = ttk.Entry(date_frame, textvariable=self.days_var, width=10)
        days_entry.grid(row=0, column=3)
        
        # Options
        options_frame = ttk.Frame(schedule_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.overwrite_var = tk.BooleanVar()
        overwrite_check = ttk.Checkbutton(options_frame, text="Overwrite existing selections", 
                                         variable=self.overwrite_var)
        overwrite_check.pack(side=tk.LEFT)
        
        # Generate button
        generate_btn = ttk.Button(schedule_frame, text="Generate Schedule", 
                                 command=self.generate_schedule)
        generate_btn.pack(side=tk.RIGHT)
        
        # Schedule display
        schedule_display_frame = ttk.LabelFrame(parent, text="Generated Schedule", padding="10")
        schedule_display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.schedule_text = scrolledtext.ScrolledText(schedule_display_frame, height=10, wrap=tk.WORD)
        self.schedule_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        export_schedule_btn = ttk.Button(schedule_display_frame, text="Export Schedule to CSV", 
                                       command=self.export_schedule_csv)
        export_schedule_btn.pack(side=tk.RIGHT)
        
    def load_statistics(self):
        """Load and display database statistics"""
        try:
            conn = sqlite3.connect('bible.db')
            cursor = conn.cursor()
            
            # Get verse count
            cursor.execute("SELECT COUNT(*) FROM verses")
            verse_count = cursor.fetchone()[0]
            
            # Get books count
            cursor.execute("SELECT COUNT(DISTINCT book) FROM verses")
            book_count = cursor.fetchone()[0]
            
            # Get daily selections count
            cursor.execute("SELECT COUNT(*) FROM daily_selections")
            selection_count = cursor.fetchone()[0]
            
            # Get date range of selections
            cursor.execute("SELECT MIN(date), MAX(date) FROM daily_selections")
            date_range = cursor.fetchone()
            
            # Get books breakdown
            cursor.execute("SELECT book, COUNT(*) FROM verses GROUP BY book ORDER BY book")
            books_breakdown = cursor.fetchall()
            
            # Get recent selections
            cursor.execute("""
                SELECT ds.date, v.book, v.chapter, v.verse 
                FROM daily_selections ds 
                JOIN verses v ON ds.verse_id = v.id 
                ORDER BY ds.date DESC 
                LIMIT 10
            """)
            recent_selections = cursor.fetchall()
            
            conn.close()
            
            # Format statistics display
            stats_text = "DATABASE STATISTICS\n"
            stats_text += "=" * 50 + "\n\n"
            
            stats_text += f"Total Verses: {verse_count:,}\n"
            stats_text += f"Total Books: {book_count}\n"
            stats_text += f"Daily Selections Made: {selection_count}\n"
            
            if date_range[0] and date_range[1]:
                stats_text += f"Selection Date Range: {date_range[0]} to {date_range[1]}\n"
            
            if verse_count > 0:
                percentage_used = (selection_count / verse_count) * 100
                stats_text += f"Percentage of Verses Used: {percentage_used:.1f}%\n"
            
            stats_text += "\nBOOKS BREAKDOWN\n"
            stats_text += "-" * 30 + "\n"
            for book, count in books_breakdown:
                stats_text += f"{book}: {count} verses\n"
            
            if recent_selections:
                stats_text += "\nRECENT SELECTIONS\n"
                stats_text += "-" * 30 + "\n"
                for sel_date, book, chapter, verse in recent_selections:
                    stats_text += f"{sel_date}: {book} {chapter}:{verse}\n"
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, f"Error loading statistics: {e}")
            
    def browse_csv_file(self):
        """Browse for CSV file to load"""
        file_path = filedialog.askopenfilename(
            title="Select Verses CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            
    def load_csv_data(self):
        """Load verse data from CSV file"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a CSV file first.")
            return
            
        try:
            result = subprocess.run([
                sys.executable, "-m", "scripts.load_verses", file_path
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                messagebox.showinfo("Success", f"Verses loaded successfully!\n\n{result.stdout}")
                self.load_statistics()  # Refresh statistics
            else:
                messagebox.showerror("Error", f"Failed to load verses:\n\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load verses: {e}")
            
    def reset_daily_selections(self):
        """Reset all daily selections"""
        if messagebox.askyesno("Confirm", "This will reset all daily selections. Are you sure?"):
            try:
                conn = sqlite3.connect('bible.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM daily_selections")
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Daily selections reset successfully!")
                self.load_statistics()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset selections: {e}")
                
    def clear_all_verses(self):
        """Clear all verses from database"""
        if messagebox.askyesno("Confirm", "This will delete ALL verses and selections. Are you sure?"):
            try:
                conn = sqlite3.connect('bible.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM daily_selections")
                cursor.execute("DELETE FROM verses")
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "All data cleared successfully!")
                self.load_statistics()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear data: {e}")
                
    def backup_database(self):
        """Create database backup"""
        backup_path = filedialog.asksaveasfilename(
            title="Save Database Backup",
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if backup_path:
            try:
                import shutil
                shutil.copy2('bible.db', backup_path)
                messagebox.showinfo("Success", f"Database backed up to:\n{backup_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to backup database: {e}")
                
    def export_verses(self):
        """Export all verses to CSV"""
        export_path = filedialog.asksaveasfilename(
            title="Export Verses",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if export_path:
            try:
                conn = sqlite3.connect('bible.db')
                cursor = conn.cursor()
                cursor.execute("SELECT book, chapter, verse, text_kjv FROM verses ORDER BY book, chapter, verse")
                verses = cursor.fetchall()
                conn.close()
                
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['book', 'chapter', 'verse', 'text_kjv'])
                    writer.writerows(verses)
                    
                messagebox.showinfo("Success", f"Verses exported to:\n{export_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export verses: {e}")
                
    def export_selections(self):
        """Export daily selections to CSV"""
        export_path = filedialog.asksaveasfilename(
            title="Export Daily Selections",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if export_path:
            try:
                result = subprocess.run([
                    sys.executable, "-m", "scripts.schedule_verses", 
                    "--start", "1900-01-01", "--days", "36500", "--out", export_path
                ], capture_output=True, text=True, cwd=Path.cwd())
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"Daily selections exported to:\n{export_path}")
                else:
                    messagebox.showerror("Error", f"Failed to export selections:\n\n{result.stderr}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export selections: {e}")
                
    def generate_schedule(self):
        """Generate verse schedule"""
        start_date = self.start_date_var.get()
        days = self.days_var.get()
        overwrite = "--overwrite" if self.overwrite_var.get() else ""
        
        try:
            # Validate inputs
            datetime.strptime(start_date, "%Y-%m-%d")
            int(days)
            
            # Generate schedule
            cmd = [sys.executable, "-m", "scripts.schedule_verses", 
                  "--start", start_date, "--days", days, "--out", "temp_schedule.csv"]
            if overwrite:
                cmd.append("--overwrite")
                
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                # Read and display the generated schedule
                with open("temp_schedule.csv", 'r', encoding='utf-8') as f:
                    schedule_content = f.read()
                    
                self.schedule_text.delete(1.0, tk.END)
                self.schedule_text.insert(1.0, schedule_content)
                
                messagebox.showinfo("Success", "Schedule generated successfully!")
                self.load_statistics()  # Refresh statistics
            else:
                messagebox.showerror("Error", f"Failed to generate schedule:\n\n{result.stderr}")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid date (YYYY-MM-DD) and number of days.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate schedule: {e}")
            
    def export_schedule_csv(self):
        """Export the displayed schedule to CSV"""
        if not self.schedule_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "No schedule to export. Generate a schedule first.")
            return
            
        export_path = filedialog.asksaveasfilename(
            title="Export Schedule",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if export_path:
            try:
                schedule_content = self.schedule_text.get(1.0, tk.END)
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(schedule_content)
                messagebox.showinfo("Success", f"Schedule exported to:\n{export_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export schedule: {e}")


# Add the verse manager to the main GUI
def add_verse_manager_to_main_gui(main_gui_class):
    """Add verse manager button to main GUI"""
    original_create_widgets = main_gui_class.create_widgets
    
    def enhanced_create_widgets(self):
        original_create_widgets(self)
        
        # Add verse manager button to bottom frame
        # Find the bottom frame in the main frame
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if hasattr(subchild, 'winfo_children'):
                        for frame in subchild.winfo_children():
                            if hasattr(frame, 'grid_info') and frame.grid_info().get('row') == 3:
                                self.manage_btn = ttk.Button(frame, text="Manage Verses", 
                                                           command=self.open_verse_manager)
                                self.manage_btn.grid(row=0, column=4, padx=(10, 0))
                                break
    
    def open_verse_manager(self):
        """Open verse management window"""
        VerseManagerWindow(self.root, self)
    
    main_gui_class.create_widgets = enhanced_create_widgets
    main_gui_class.open_verse_manager = open_verse_manager
    
    return main_gui_class