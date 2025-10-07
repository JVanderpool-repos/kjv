#!/usr/bin/env python3
"""
Test suite for API components and functionality.
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import Base
from app.models.verse import Verse
from app.models.daily_selection import DailySelection
from app.services.selection import VerseSelector


class TestAPIImports:
    """Test that API components can be imported correctly."""
    
    def test_fastapi_app_import(self):
        """Test importing the FastAPI app."""
        from app.main import app
        assert app is not None
    
    def test_api_routes_import(self):
        """Test importing API routes."""
        from app.api.routes import router
        assert router is not None
    
    def test_models_import(self):
        """Test importing database models."""
        from app.models.verse import Verse
        from app.models.daily_selection import DailySelection
        assert Verse is not None
        assert DailySelection is not None
    
    def test_services_import(self):
        """Test importing service classes."""
        from app.services.selection import VerseSelector
        assert VerseSelector is not None


class TestVerseSelector:
    """Test the VerseSelector service functionality."""
    
    @pytest.fixture
    def db_session(self):
        """Create an in-memory database session for testing."""
        engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        Base.metadata.create_all(bind=engine)
        
        session = TestingSession()
        
        # Seed with test data
        verses = [
            Verse(book="Genesis", chapter=1, verse=1, text_kjv="In the beginning God created the heaven and the earth."),
            Verse(book="Genesis", chapter=1, verse=2, text_kjv="And the earth was without form, and void."),
            Verse(book="Genesis", chapter=2, verse=1, text_kjv="Thus the heavens and the earth were finished."),
            Verse(book="Exodus", chapter=1, verse=1, text_kjv="Now these are the names of the children of Israel."),
            Verse(book="Exodus", chapter=1, verse=2, text_kjv="Reuben, Simeon, Levi, and Judah."),
        ]
        for verse in verses:
            session.add(verse)
        session.commit()
        
        yield session
        session.close()
    
    def test_verse_selector_creation(self, db_session):
        """Test that VerseSelector can be created with a database session."""
        selector = VerseSelector(db_session)
        assert selector is not None
        assert selector.db == db_session
    
    def test_get_today_creates_selection(self, db_session):
        """Test that get_today() creates a daily selection."""
        selector = VerseSelector(db_session, seed=42)
        
        # Should create a new selection for today
        selection = selector.get_today()
        assert selection is not None
        assert selection.date == date.today()
        assert selection.verse is not None
    
    def test_get_today_returns_existing_selection(self, db_session):
        """Test that get_today() returns existing selection for the same date."""
        selector = VerseSelector(db_session, seed=42)
        
        # Get first selection
        selection1 = selector.get_today()
        verse1_id = selection1.verse_id
        
        # Get selection again - should be the same
        selection2 = selector.get_today()
        verse2_id = selection2.verse_id
        
        assert verse1_id == verse2_id
        assert selection1.id == selection2.id
    
    def test_get_for_date(self, db_session):
        """Test getting selection for a specific date."""
        selector = VerseSelector(db_session, seed=42)
        
        # Get selection for a specific date
        test_date = date(2025, 1, 1)
        selection = selector.get_for_date(test_date)
        
        assert selection is not None
        assert selection.date == test_date
        assert selection.verse is not None


class TestDatabaseModels:
    """Test database model functionality."""
    
    def test_verse_model_creation(self):
        """Test creating a Verse model instance."""
        verse = Verse(
            book="John",
            chapter=3,
            verse=16,
            text_kjv="For God so loved the world, that he gave his only begotten Son..."
        )
        
        assert verse.book == "John"
        assert verse.chapter == 3
        assert verse.verse == 16
        assert "God so loved" in verse.text_kjv
        assert verse.ref() == "John 3:16"
    
    def test_daily_selection_model_creation(self):
        """Test creating a DailySelection model instance."""
        selection = DailySelection(
            date=date.today(),
            verse_id=1
        )
        
        assert selection.date == date.today()
        assert selection.verse_id == 1


@pytest.mark.skipif(not os.path.exists('bible.db'), reason="Database file not found")
class TestAPIWithRealDatabase:
    """Test API functionality with the real database."""
    
    def test_verse_selector_with_real_db(self):
        """Test VerseSelector with the actual database."""
        from app.db.session import engine
        from sqlalchemy.orm import sessionmaker
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            selector = VerseSelector(session)
            selection = selector.get_today()
            
            assert selection is not None
            if selection.verse:
                assert selection.verse.book is not None
                assert selection.verse.chapter > 0
                assert selection.verse.verse > 0
                assert len(selection.verse.text_kjv) > 0
        finally:
            session.close()


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__])