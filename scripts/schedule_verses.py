"""Pre-generate a schedule of verses for a date range and export to CSV.

Usage:
  python -m scripts.schedule_verses --start 2025-01-01 --days 30 --out data/schedule.csv

If verses already exist for some days they are left intact (unless --overwrite is used).
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
import argparse
from sqlalchemy import select
from app.db.session import SessionLocal, engine, Base
from app.models.daily_selection import DailySelection
from app.models.verse import Verse
from app.services.selection import VerseSelector

Base.metadata.create_all(bind=engine)

def generate(start: date, days: int, overwrite: bool = False):
    db = SessionLocal()
    selector = VerseSelector(db)
    try:
        for offset in range(days):
            target = start + timedelta(days=offset)
            existing = db.scalar(select(DailySelection).where(DailySelection.date == target))
            if existing and not overwrite:
                continue
            if existing and overwrite:
                db.delete(existing)
                db.commit()
            selector.get_for_date(target)
    finally:
        db.close()


def export_csv(path: Path):
    db = SessionLocal()
    try:
        rows = db.execute(
            select(DailySelection.date, Verse.book, Verse.chapter, Verse.verse, Verse.text_kjv)
            .join(Verse, DailySelection.verse_id == Verse.id)
            .order_by(DailySelection.date)
        ).all()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "reference", "kjv"])
            for r in rows:
                ref = f"{r.book} {r.chapter}:{r.verse}"
                writer.writerow([r.date.isoformat(), ref, r.text_kjv])
    finally:
        db.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=str, required=True, help="Start date YYYY-MM-DD")
    p.add_argument("--days", type=int, required=True, help="Number of days to schedule")
    p.add_argument("--out", type=str, required=True, help="Output CSV path")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing selections in range")
    args = p.parse_args()
    start_date = date.fromisoformat(args.start)
    generate(start_date, args.days, overwrite=args.overwrite)
    export_csv(Path(args.out))
    print(f"Schedule written to {args.out}")

if __name__ == "__main__":
    main()
