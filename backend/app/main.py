from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
import os
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .consolidator import UnsupportedWorkbook, as_excel
from .database import Base
from .import_workflow import ImportWorkflow


def create_app(
    database_url: str | None = None,
    source_files_dir: str | None = None,
) -> FastAPI:
    engine = create_engine(database_url or os.getenv("DATABASE_URL", "sqlite:///./nomi.db"))
    session_factory = sessionmaker(bind=engine, autoflush=False)
    sources = Path(source_files_dir or os.getenv("NOMI_SOURCE_FILES_DIR", "./nomi-data/sources"))

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        Base.metadata.create_all(bind=engine)
        yield

    app = FastAPI(title="Nomi API", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])

    def get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/consolidate")
    async def create_consolidated_workbook(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
        try:
            result = ImportWorkflow(db, sources).import_files([
                (file.filename or "upload", await file.read()) for file in files
            ])
        except UnsupportedWorkbook as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

        filename = "nomi-consolidated-transactions.xlsx"
        return StreamingResponse(
            BytesIO(as_excel(result.transactions)),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Nomi-Imported-Source-Files": str(result.imported_source_files),
                "X-Nomi-Skipped-Source-Files": str(result.skipped_source_files),
            },
        )

    return app

app = create_app()
