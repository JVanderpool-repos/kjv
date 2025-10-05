from sqlalchemy import String, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Verse(Base):
    __tablename__ = "verses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book: Mapped[str] = mapped_column(String(64), index=True)
    chapter: Mapped[int] = mapped_column(Integer, index=True)
    verse: Mapped[int] = mapped_column(Integer, index=True)
    text_kjv: Mapped[str] = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("book", "chapter", "verse", name="uq_book_chapter_verse"),
    )

    def ref(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}"
