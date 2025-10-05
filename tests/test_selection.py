from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.models.verse import Verse
from app.services.selection import VerseSelector

# In-memory SQLite for tests
engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)

def seed(db):
    # two books, multiple chapters
    verses = [
        Verse(book="Genesis", chapter=1, verse=1, text_kjv="KJV G1:1"),
        Verse(book="Genesis", chapter=1, verse=2, text_kjv="KJV G1:2"),
        Verse(book="Genesis", chapter=2, verse=1, text_kjv="KJV G2:1"),
        Verse(book="Exodus", chapter=1, verse=1, text_kjv="KJV E1:1"),
        Verse(book="Exodus", chapter=1, verse=2, text_kjv="KJV E1:2"),
    ]
    for v in verses:
        db.add(v)
    db.commit()


def test_no_repeat_and_chapter_variation():
    db = TestingSession()
    seed(db)
    selector = VerseSelector(db, seed=123)
    picked_refs = []
    picked_chapters = []
    base = date(2024, 1, 1)
    for i in range(5):
        sel = selector.get_for_date(base + timedelta(days=i))
        verse = db.get(Verse, sel.verse_id)
        assert verse is not None, f"Verse {sel.verse_id} not found"
        picked_refs.append(verse.ref())
        picked_chapters.append((verse.book, verse.chapter))
    assert len(set(picked_refs)) == len(picked_refs)
    # ensure not all consecutive chapters equal
    assert all(picked_chapters[i] != picked_chapters[i+1] for i in range(len(picked_chapters)-1) if len(picked_chapters) > 1)
