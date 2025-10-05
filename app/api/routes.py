from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.session import get_db
from app.services.selection import VerseSelector
from app.models.daily_selection import DailySelection
from app.models.verse import Verse
from datetime import date

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/verse/today")
async def verse_today(db: Session = Depends(get_db)):
    selector = VerseSelector(db)
    selection = selector.get_for_date(date.today())
    verse = db.scalar(select(Verse).where(Verse.id == selection.verse_id))
    if not verse:
        return {"error": "verse not found"}
    return {
        "date": str(selection.date),
        "reference": verse.ref(),
        "kjv": verse.text_kjv,
    }

@router.get("/verse/random")
async def verse_random(db: Session = Depends(get_db)):
    verse = db.scalar(select(Verse).order_by(func.random()))  # SQLite / PG compatible
    if not verse:
        return {"error": "no verses loaded"}
    return {"reference": verse.ref(), "kjv": verse.text_kjv}
