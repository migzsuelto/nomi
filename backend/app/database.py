import os

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, create_engine, func
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


class SourceFile(Base):
    __tablename__ = "source_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    storage_path: Mapped[str] = mapped_column(String(1024))
    imported_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CanonicalTransaction(Base):
    __tablename__ = "canonical_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_file_id: Mapped[int] = mapped_column(ForeignKey("source_files.id"), index=True)
    source_worksheet: Mapped[str] = mapped_column(String(255))
    date: Mapped[object] = mapped_column(DateTime())
    description: Mapped[str] = mapped_column(String(1024))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    balance: Mapped[float | None] = mapped_column(Float, nullable=True)
    account: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reference: Mapped[str | None] = mapped_column(String(1024), nullable=True)
