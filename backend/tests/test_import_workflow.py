from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import CanonicalTransaction, ConsolidationJob, SourceFile
from app.main import create_app


class ImportWorkflowTests(unittest.TestCase):
    def test_known_csv_is_persisted_and_an_identical_reupload_is_skipped(self) -> None:
        with TemporaryDirectory() as directory:
            database_url = f"sqlite:///{directory}/nomi.db"
            app = create_app(
                database_url=database_url,
                source_files_dir=f"{directory}/sources",
            )
            with TestClient(app) as client:
                first = client.post(
                    "/api/consolidate",
                    files={
                        "files": (
                            "checking.csv",
                            b"Date,Description,Amount,Currency\n2026-09-01,Coffee,-4.50,NZD\n",
                            "text/csv",
                        )
                    },
                )
                second = client.post(
                    "/api/consolidate",
                    files={
                        "files": (
                            "checking.csv",
                            b"Date,Description,Amount,Currency\n2026-09-01,Coffee,-4.50,NZD\n",
                            "text/csv",
                        )
                    },
                )

            with Session(create_engine(database_url)) as session:
                source_file = session.scalar(select(SourceFile))
                self.assertIsNotNone(source_file)
                self.assertEqual(Path(source_file.storage_path).read_bytes(), b"Date,Description,Amount,Currency\n2026-09-01,Coffee,-4.50,NZD\n")
                self.assertEqual(len(session.scalars(select(CanonicalTransaction)).all()), 1)
                self.assertEqual(len(session.scalars(select(ConsolidationJob)).all()), 2)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.headers["x-nomi-imported-source-files"], "1")
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.headers["x-nomi-imported-source-files"], "0")
        self.assertEqual(second.headers["x-nomi-skipped-source-files"], "1")

        workbook = pd.read_excel(BytesIO(second.content), sheet_name="Transactions")
        self.assertEqual(list(workbook.columns), [
            "date",
            "description",
            "amount",
            "currency",
            "balance",
            "account",
            "reference",
            "source_file",
            "source_worksheet",
        ])
        self.assertEqual(workbook.loc[0, "date"], pd.Timestamp("2026-09-01"))
        self.assertEqual(workbook.loc[0, "description"], "Coffee")
        self.assertEqual(workbook.loc[0, "amount"], -4.5)
        self.assertEqual(workbook.loc[0, "currency"], "NZD")
        self.assertTrue(pd.isna(workbook.loc[0, "balance"]))
        self.assertTrue(pd.isna(workbook.loc[0, "account"]))
        self.assertTrue(pd.isna(workbook.loc[0, "reference"]))
        self.assertEqual(workbook.loc[0, "source_file"], "checking.csv")
        self.assertEqual(workbook.loc[0, "source_worksheet"], "CSV")

    def test_csv_without_a_description_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            app = create_app(
                database_url=f"sqlite:///{directory}/nomi.db",
                source_files_dir=f"{directory}/sources",
            )
            with TestClient(app) as client:
                response = client.post(
                    "/api/consolidate",
                    files={
                        "files": (
                            "incomplete.csv",
                            b"Date,Amount\n2026-09-01,-4.50\n",
                            "text/csv",
                        )
                    },
                )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "incomplete.csv has no usable Description column.")

    def test_canonical_transactions_are_newest_first_with_source_tiebreakers(self) -> None:
        with TemporaryDirectory() as directory:
            app = create_app(
                database_url=f"sqlite:///{directory}/nomi.db",
                source_files_dir=f"{directory}/sources",
            )
            with TestClient(app) as client:
                response = client.post(
                    "/api/consolidate",
                    files=[
                        ("files", ("zeta.csv", b"Date,Description,Amount\n2026-09-01,Zeta,-1\n", "text/csv")),
                        ("files", ("alpha.csv", b"Date,Description,Amount\n2026-09-01,Alpha,-2\n", "text/csv")),
                        ("files", ("latest.csv", b"Date,Description,Amount\n2026-09-02,Latest,-3\n", "text/csv")),
                    ],
                )

        self.assertEqual(response.status_code, 200)
        workbook = pd.read_excel(BytesIO(response.content), sheet_name="Transactions")
        self.assertEqual(workbook["description"].tolist(), ["Latest", "Alpha", "Zeta"])


if __name__ == "__main__":
    unittest.main()
