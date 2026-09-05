import os

from sqlalchemy import DateTime, Integer, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nomi.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    pass

class ConsolidationJob(Base):
    __tablename__ = "consolidation_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_count: Mapped[int] = mapped_column(Integer)
    transaction_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
    download_name: Mapped[str] = mapped_column(String(255))
