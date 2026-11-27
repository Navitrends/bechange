from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.imports.competitors.excel_import import import_competitor_file
from app.schemas import ImportJobOut

router = APIRouter()


@router.post("/upload", response_model=ImportJobOut)
async def upload_competitor_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "competitors.xlsx").suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail="Formats acceptés: CSV, XLSX, XLS")

    dest = upload_dir / f"competitors_{file.filename}"
    dest.write_bytes(await file.read())
    return import_competitor_file(db, dest, source_name=file.filename)
