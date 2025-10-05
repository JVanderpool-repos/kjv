from sqlalchemy import Integer, Date, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class DailySelection(Base):
    __tablename__ = "daily_selections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[Date] = mapped_column(Date, unique=True, index=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("verses.id"), index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    verse = relationship("Verse")

    __table_args__ = (
        UniqueConstraint("date", name="uq_date"),
    )
