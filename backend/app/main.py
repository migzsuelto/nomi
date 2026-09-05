from contextlib import asynccontextmanager
from io import BytesIO
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .consolidator import UnsupportedWorkbook, as_excel, consolidate
from .database import Base, ConsolidationJob, SessionLocal, engine

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Nomi API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/api/consolidate")
async def create_consolidated_workbook(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    try:
        transactions = consolidate([(file.filename or "upload", await file.read()) for file in files])
    except UnsupportedWorkbook as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    filename = "nomi-consolidated-transactions.xlsx"
    content = as_excel(transactions)
    db.add(ConsolidationJob(file_count=len(files), transaction_count=len(transactions), download_name=filename))
    db.commit()
    return StreamingResponse(BytesIO(content), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}"'})
