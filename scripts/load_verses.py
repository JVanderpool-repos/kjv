"""Script to load verses into the database from provided CSV or JSON files.
User must supply data files. Expected schema:
CSV columns: book,chapter,verse,text_kjv
"""

import csv
from pathlib import Path
from sqlalchemy import select
from app.db.session import SessionLocal, engine, Base
from app.models.verse import Verse

Base.metadata.create_all(bind=engine)

def load_csv(path: str | Path):
    path = Path(path)
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required = {"book", "chapter", "verse", "text_kjv"}
        if not required.issubset(reader.fieldnames or {}):
            raise ValueError(f"CSV must contain columns: {required}")
        db = SessionLocal()
        count_inserted = 0
        try:
            for row in reader:
                exists = db.scalar(select(Verse).where(
                    Verse.book == row["book"],
                    Verse.chapter == int(row["chapter"]),
                    Verse.verse == int(row["verse"]),
                ))
                if exists:
                    continue
                verse = Verse(
                    book=row["book"],
                    chapter=int(row["chapter"]),
                    verse=int(row["verse"]),
                    text_kjv=row["text_kjv"],
                )
                db.add(verse)
                count_inserted += 1
            db.commit()
        finally:
            db.close()
        print(f"Inserted {count_inserted} verses.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", help="Path to verses CSV file")
    args = parser.parse_args()
    load_csv(args.csv)
