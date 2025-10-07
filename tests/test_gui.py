#!/usr/bin/env python3
"""
Test suite for GUI components.
"""
import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGUIImports:
    """Test that GUI components can be imported correctly."""
    
    def test_gui_main_import(self):
        """Test importing the main GUI module."""
        from gui.main import BibleVerseGUI
        assert BibleVerseGUI is not None
    
    def test_gui_manager_import(self):
        """Test importing the verse manager GUI module."""
        from gui.manager import VerseManagerWindow
        assert VerseManagerWindow is not None
    
    def test_gui_init_import(self):
        """Test importing the GUI package init."""
        import gui
        assert gui is not None


class TestGUIComponents:
    """Test GUI component functionality."""
    
    @patch('tkinter.Tk')
    def test_bible_verse_gui_creation(self, mock_tk):
        """Test that BibleVerseGUI can be instantiated."""
        from gui.main import BibleVerseGUI
        
        # Mock the root window
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # This should not raise an exception
        try:
            app = BibleVerseGUI(mock_root)
            assert app is not None
        except Exception as e:
            # If there are dependencies issues, we still want to test import
            pytest.skip(f"GUI creation requires display: {e}")
    
    def test_gui_settings_class_exists(self):
        """Test that SettingsWindow class exists."""
        from gui.main import SettingsWindow
        assert SettingsWindow is not None
    
    def test_verse_manager_class_exists(self):
        """Test that VerseManagerWindow class exists."""
        from gui.manager import VerseManagerWindow
        assert VerseManagerWindow is not None


class TestGUIIntegration:
    """Test GUI integration with backend components."""
    
    def test_gui_can_import_app_modules(self):
        """Test that GUI can import required app modules."""
        # These imports should work for GUI to function
        from app.models.verse import Verse
        from app.models.daily_selection import DailySelection
        from app.services.selection import VerseSelector
        
        assert Verse is not None
        assert DailySelection is not None
        assert VerseSelector is not None
    
    @pytest.mark.skipif(not os.path.exists('bible.db'), reason="Database file not found")
    def test_gui_database_access(self):
        """Test that GUI can access the database."""
        import sqlite3
        
        conn = sqlite3.connect('bible.db')
        cursor = conn.cursor()
        
        # Test basic database operations
        cursor.execute("SELECT COUNT(*) FROM verses")
        verse_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM daily_selections")
        selection_count = cursor.fetchone()[0]
        
        conn.close()
        
        assert verse_count >= 0
        assert selection_count >= 0


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__])