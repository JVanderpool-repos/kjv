"""
GUI Package for Bible Verse Application

This package contains the graphical user interface components for the
Bible Verse of the Day application.
"""

from .main import BibleVerseGUI, main
from .manager import VerseManagerWindow

__all__ = ['BibleVerseGUI', 'VerseManagerWindow', 'main']