import random
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.verse import Verse
from app.models.daily_selection import DailySelection
from app.core.config import get_settings

settings = get_settings()

class VerseSelector:
    """Service encapsulating verse selection rules.

    Rules:
    - Do not repeat any verse until all have been used.
    - Avoid selecting from the same (book, chapter) on consecutive days unless no alternative.
    """

    def __init__(self, db: Session, seed: int | None = None):
        self.db = db
        self.random = random.Random(seed or settings.seed)

    def get_today(self) -> DailySelection:
        return self.get_for_date(date.today())

    def get_for_date(self, target_date: date) -> DailySelection:
        existing = self.db.scalar(
            select(DailySelection).where(DailySelection.date == target_date)
        )
        if existing:
            return existing
        verse = self._pick_new_verse()
        selection = DailySelection(date=target_date, verse_id=verse.id)
        self.db.add(selection)
        self.db.commit()
        self.db.refresh(selection)
        return selection

    def _pick_new_verse(self) -> Verse:
        # Verses already used
        used_ids = {id_ for (id_,) in self.db.execute(select(DailySelection.verse_id)).all()}
        # Last day's chapter to avoid consecutive chapter repeats
        last_selection = self.db.scalar(
            select(DailySelection).order_by(DailySelection.date.desc())
        )
        last_chapter = None
        if last_selection:
            last_verse = self.db.scalar(select(Verse).where(Verse.id == last_selection.verse_id))
            if last_verse:
                last_chapter = (last_verse.book, last_verse.chapter)

        # Candidate verses not used
        candidates = self.db.execute(
            select(Verse.id, Verse.book, Verse.chapter).where(~Verse.id.in_(used_ids))
        ).all()
        if not candidates:
            raise ValueError("All verses exhausted. Consider resetting or extending logic.")

        # Filter out same chapter as last day if possible
        filtered = [c for c in candidates if (c.book, c.chapter) != last_chapter]
        pool = filtered if filtered else candidates
        choice_meta = self.random.choice(pool)
        verse = self.db.scalar(select(Verse).where(Verse.id == choice_meta.id))
        assert verse is not None
        return verse
