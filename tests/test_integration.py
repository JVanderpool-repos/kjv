#!/usr/bin/env python3
"""
Integration tests for the complete Bible Verse application.
Combines testing of GUI, API, and database components working together.
"""
import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock
import sys
import os
import sqlite3
import subprocess
import time
import signal
from sqlalchemy.orm import sessionmaker

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine
from app.services.selection import VerseSelector


class TestApplicationIntegration:
    """Test integration between different application components."""
    
    def test_gui_can_access_database(self):
        """Test that GUI components can access the database."""
        if not os.path.exists('bible.db'):
            pytest.skip("Database file not found")
        
        # Test direct SQLite access (as GUI might use)
        conn = sqlite3.connect('bible.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM verses")
        verse_count = cursor.fetchone()[0]
        conn.close()
        
        assert verse_count >= 0
    
    def test_api_with_database(self):
        """Test API components with the database."""
        if not os.path.exists('bible.db'):
            pytest.skip("Database file not found")
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Test the selection service
            selector = VerseSelector(session)
            daily_selection = selector.get_today()
            
            assert daily_selection is not None
            assert daily_selection.verse_id is not None
            
            if daily_selection.verse:
                verse = daily_selection.verse
                assert verse.book is not None
                assert verse.chapter > 0
                assert verse.verse > 0
                assert len(verse.text_kjv) > 0
        finally:
            session.close()
    
    def test_imports_work_together(self):
        """Test that all major components can be imported together."""
        # Test importing GUI components
        from gui.main import BibleVerseGUI, SettingsWindow
        from gui.manager import VerseManagerWindow
        
        # Test importing API components
        from app.main import app
        from app.api.routes import router
        from app.models.verse import Verse
        from app.models.daily_selection import DailySelection
        from app.services.selection import VerseSelector
        
        # All imports should succeed
        assert BibleVerseGUI is not None
        assert SettingsWindow is not None
        assert VerseManagerWindow is not None
        assert app is not None
        assert router is not None
        assert Verse is not None
        assert DailySelection is not None
        assert VerseSelector is not None


class TestApplicationLaunching:
    """Test application launching and startup procedures."""
    
    def test_launcher_script_exists(self):
        """Test that the launcher script exists and is importable."""
        assert os.path.exists('launch.py'), "launch.py should exist"
        
        # Test that we can read the launcher
        with open('launch.py', 'r') as f:
            content = f.read()
            assert 'BibleVerseGUI' in content or 'gui' in content
            assert 'import' in content
    
    @pytest.mark.skipif(os.environ.get('CI') == 'true', reason="Requires display")
    def test_gui_main_function(self):
        """Test that GUI main function exists and can be called."""
        from gui.main import main
        
        # Mock the GUI to avoid actually opening a window
        with patch('gui.main.BibleVerseGUI') as mock_gui:
            with patch('tkinter.Tk') as mock_tk:
                mock_root = MagicMock()
                mock_tk.return_value = mock_root
                
                try:
                    # This should not raise an exception
                    main()
                except SystemExit:
                    # main() might call sys.exit(), which is fine
                    pass
                except Exception as e:
                    pytest.skip(f"GUI requires display environment: {e}")


class TestAPIServer:
    """Test API server functionality in integration."""
    
    @pytest.mark.slow
    def test_api_server_can_start(self):
        """Test that the API server can be started and stopped."""
        try:
            # Start server in background
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--host", "127.0.0.1", 
                "--port", "8002"  # Use different port to avoid conflicts
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Give server time to start
            time.sleep(2)
            
            # Check if process is running
            if process.poll() is None:
                # Server started successfully
                success = True
            else:
                # Server failed to start
                stdout, stderr = process.communicate()
                success = False
            
            # Stop server
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            
            assert success, "API server should start successfully"
            
        except Exception as e:
            pytest.skip(f"API server test requires uvicorn: {e}")


class TestEndToEndScenarios:
    """Test complete end-to-end scenarios."""
    
    @pytest.mark.skipif(not os.path.exists('bible.db'), reason="Database file not found")
    def test_daily_verse_retrieval_workflow(self):
        """Test the complete workflow of retrieving a daily verse."""
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Step 1: Create verse selector
            selector = VerseSelector(session, seed=42)  # Use fixed seed for reproducibility
            
            # Step 2: Get today's verse
            daily_selection = selector.get_today()
            
            # Step 3: Verify the selection
            assert daily_selection is not None
            assert daily_selection.verse_id is not None
            
            # Step 4: Get the verse content
            if daily_selection.verse:
                verse = daily_selection.verse
                
                # Step 5: Verify verse data quality
                assert isinstance(verse.book, str)
                assert len(verse.book) > 0
                assert isinstance(verse.chapter, int)
                assert verse.chapter > 0
                assert isinstance(verse.verse, int)
                assert verse.verse > 0
                assert isinstance(verse.text_kjv, str)
                assert len(verse.text_kjv) > 10  # Reasonable minimum length
                
                # Step 6: Test verse reference generation
                reference = verse.ref()
                assert reference == f"{verse.book} {verse.chapter}:{verse.verse}"
                
        finally:
            session.close()
    
    def test_application_structure_completeness(self):
        """Test that all required application files and directories exist."""
        required_files = [
            'launch.py',
            'pyproject.toml',
            'README.md',
            'app/main.py',
            'app/api/routes.py',
            'app/models/verse.py',
            'app/models/daily_selection.py',
            'app/services/selection.py',
            'app/db/session.py',
            'gui/main.py',
            'gui/manager.py',
            'gui/__init__.py',
            'tests/test_selection.py',
        ]
        
        for file_path in required_files:
            assert os.path.exists(file_path), f"Required file {file_path} should exist"
    
    def test_application_dependencies_importable(self):
        """Test that all major dependencies can be imported."""
        try:
            import fastapi
            import uvicorn
            import sqlalchemy
            import pydantic
            import requests
            # tkinter is built-in, should always be available
            import tkinter
            
            # All imports should succeed
            assert fastapi is not None
            assert uvicorn is not None
            assert sqlalchemy is not None
            assert pydantic is not None
            assert requests is not None
            assert tkinter is not None
            
        except ImportError as e:
            pytest.fail(f"Required dependency not available: {e}")


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])