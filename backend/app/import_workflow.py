from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from .consolidator import CANONICAL_COLUMNS, UnsupportedWorkbook, consolidate
from .database import CanonicalTransaction, ConsolidationJob, SourceFile


@dataclass(frozen=True)
class ImportResult:
    transactions: pd.DataFrame
    imported_source_files: int
    skipped_source_files: int


class ImportWorkflow:
    def __init__(self, session: Session, source_files_dir: Path):
        self.session = session
        self.source_files_dir = source_files_dir

    def import_files(self, files: list[tuple[str, bytes]]) -> ImportResult:
        if not files:
            raise UnsupportedWorkbook("Upload at least one file.")

        imported_source_files = 0
        imported_transactions = 0
        skipped_source_files = 0
        for filename, content in files:
            content_hash = sha256(content).hexdigest()
            existing = self.session.scalar(
                select(SourceFile).where(SourceFile.content_hash == content_hash)
            )
            if existing:
                skipped_source_files += 1
                continue

            transactions = consolidate([(filename, content)])
            source_file = self._persist_source_file(filename, content, content_hash)
            self.session.add(source_file)
            self.session.flush()
            self._persist_transactions(transactions, source_file)
            imported_source_files += 1
            imported_transactions += len(transactions)

        self.session.add(
            ConsolidationJob(
                file_count=len(files),
                transaction_count=imported_transactions,
                download_name="nomi-consolidated-transactions.xlsx",
            )
        )
        self.session.commit()
        return ImportResult(
            transactions=self._all_canonical_transactions(),
            imported_source_files=imported_source_files,
            skipped_source_files=skipped_source_files,
        )

    def _persist_source_file(self, filename: str, content: bytes, content_hash: str) -> SourceFile:
        self.source_files_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(filename).suffix.lower()
        storage_path = self.source_files_dir / f"{content_hash}{suffix}"
        storage_path.write_bytes(content)
        return SourceFile(
            filename=filename,
            content_hash=content_hash,
            storage_path=str(storage_path),
        )

    def _persist_transactions(self, transactions: pd.DataFrame, source_file: SourceFile) -> None:
        for row in transactions[CANONICAL_COLUMNS].itertuples(index=False):
            self.session.add(CanonicalTransaction(
                source_file_id=source_file.id,
                source_worksheet=row.source_worksheet,
                date=pd.Timestamp(row.date).to_pydatetime(),
                description=str(row.description),
                amount=float(row.amount),
                currency=_nullable_text(row.currency),
                balance=_nullable_float(row.balance),
                account=_nullable_text(row.account),
                reference=_nullable_text(row.reference),
            ))

    def _all_canonical_transactions(self) -> pd.DataFrame:
        rows = self.session.execute(
            select(CanonicalTransaction, SourceFile.filename)
            .join(SourceFile, CanonicalTransaction.source_file_id == SourceFile.id)
            .order_by(
                CanonicalTransaction.date.desc(),
                SourceFile.filename,
                CanonicalTransaction.source_worksheet,
            )
        )
        return pd.DataFrame([
            {
                "date": transaction.date,
                "description": transaction.description,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "balance": transaction.balance,
                "account": transaction.account,
                "reference": transaction.reference,
                "source_file": filename,
                "source_worksheet": transaction.source_worksheet,
            }
            for transaction, filename in rows
        ], columns=CANONICAL_COLUMNS)


def _nullable_text(value: object) -> str | None:
    return None if pd.isna(value) else str(value)


def _nullable_float(value: object) -> float | None:
    return None if pd.isna(value) else float(value)
