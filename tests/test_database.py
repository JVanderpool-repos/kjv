#!/usr/bin/env python3
"""
Test suite for database functionality and connectivity.
"""
import pytest
import sqlite3
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import Base, engine
from app.models.verse import Verse
from app.models.daily_selection import DailySelection


class TestDatabaseConnection:
    """Test basic database connectivity and structure."""
    
    def test_sqlite_file_exists(self):
        """Test that the SQLite database file exists."""
        assert os.path.exists('bible.db'), "Database file 'bible.db' should exist"
    
    def test_sqlite_direct_connection(self):
        """Test direct SQLite connection."""
        conn = sqlite3.connect('bible.db')
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        conn.close()
        
        table_names = [table[0] for table in tables]
        assert 'verses' in table_names
        assert 'daily_selections' in table_names
    
    def test_sqlalchemy_engine_connection(self):
        """Test SQLAlchemy engine connection."""
        # Test that we can connect through SQLAlchemy
        connection = engine.connect()
        result = connection.execute(text("SELECT 1"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1
        connection.close()
    
    def test_database_session_creation(self):
        """Test creating a database session."""
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test basic query through session
        result = session.execute(text("SELECT COUNT(*) FROM verses"))
        count = result.scalar()
        
        session.close()
        
        assert count is not None
        assert count >= 0


class TestDatabaseTables:
    """Test database table structure and content."""
    
    @pytest.fixture
    def db_session(self):
        """Create a database session for testing."""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_verses_table_structure(self, db_session):
        """Test the verses table structure."""
        # Test that we can query the verses table
        verses = db_session.query(Verse).limit(5).all()
        
        if verses:
            verse = verses[0]
            assert hasattr(verse, 'id')
            assert hasattr(verse, 'book')
            assert hasattr(verse, 'chapter')
            assert hasattr(verse, 'verse')
            assert hasattr(verse, 'text_kjv')
            
            # Test ref method
            assert verse.ref() == f"{verse.book} {verse.chapter}:{verse.verse}"
    
    def test_daily_selections_table_structure(self, db_session):
        """Test the daily_selections table structure."""
        # Test that we can query the daily_selections table
        selections = db_session.query(DailySelection).limit(5).all()
        
        # Even if empty, the table should exist and be queryable
        assert isinstance(selections, list)
        
        if selections:
            selection = selections[0]
            assert hasattr(selection, 'id')
            assert hasattr(selection, 'date')
            assert hasattr(selection, 'verse_id')
            assert hasattr(selection, 'created_at')
    
    def test_verse_count(self, db_session):
        """Test getting verse count from database."""
        count = db_session.query(Verse).count()
        assert count >= 0
        
        if count > 0:
            # If we have verses, test that they have valid data
            sample_verse = db_session.query(Verse).first()
            assert sample_verse.book is not None
            assert sample_verse.chapter > 0
            assert sample_verse.verse > 0
            assert len(sample_verse.text_kjv) > 0
    
    def test_daily_selections_count(self, db_session):
        """Test getting daily selections count from database."""
        count = db_session.query(DailySelection).count()
        assert count >= 0


class TestDatabaseOperations:
    """Test database CRUD operations."""
    
    @pytest.fixture
    def db_session(self):
        """Create a database session for testing."""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.rollback()  # Rollback any changes made during tests
        session.close()
    
    def test_verse_creation_and_query(self, db_session):
        """Test creating and querying a verse (within transaction)."""
        # Create a test verse
        test_verse = Verse(
            book="TestBook",
            chapter=999,
            verse=1,
            text_kjv="This is a test verse for the test suite."
        )
        
        db_session.add(test_verse)
        db_session.flush()  # Flush to get ID but don't commit
        
        # Query the verse back
        found_verse = db_session.query(Verse).filter(
            Verse.book == "TestBook",
            Verse.chapter == 999,
            Verse.verse == 1
        ).first()
        
        assert found_verse is not None
        assert found_verse.book == "TestBook"
        assert found_verse.chapter == 999
        assert found_verse.verse == 1
        assert found_verse.text_kjv == "This is a test verse for the test suite."
        assert found_verse.ref() == "TestBook 999:1"
    
    def test_verse_unique_constraint(self, db_session):
        """Test that the unique constraint on book/chapter/verse works."""
        # Create first verse
        verse1 = Verse(book="Test", chapter=1, verse=1, text_kjv="First verse")
        db_session.add(verse1)
        db_session.flush()
        
        # Try to create duplicate - should raise an error
        verse2 = Verse(book="Test", chapter=1, verse=1, text_kjv="Duplicate verse")
        db_session.add(verse2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError or similar
            db_session.flush()


class TestDatabaseIntegration:
    """Test database integration with application components."""
    
    def test_database_with_real_data(self):
        """Test database functionality with real data if available."""
        if not os.path.exists('bible.db'):
            pytest.skip("Database file not found")
        
        conn = sqlite3.connect('bible.db')
        cursor = conn.cursor()
        
        # Check for actual verses
        cursor.execute("SELECT COUNT(*) FROM verses")
        verse_count = cursor.fetchone()[0]
        
        # Check for daily selections
        cursor.execute("SELECT COUNT(*) FROM daily_selections")
        selection_count = cursor.fetchone()[0]
        
        # Test sample data quality if verses exist
        if verse_count > 0:
            cursor.execute("SELECT book, chapter, verse, text_kjv FROM verses LIMIT 1")
            sample = cursor.fetchone()
            book, chapter, verse, text = sample
            
            assert isinstance(book, str) and len(book) > 0
            assert isinstance(chapter, int) and chapter > 0
            assert isinstance(verse, int) and verse > 0
            assert isinstance(text, str) and len(text) > 10  # Reasonable verse length
        
        conn.close()
        
        assert verse_count >= 0
        assert selection_count >= 0


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__])