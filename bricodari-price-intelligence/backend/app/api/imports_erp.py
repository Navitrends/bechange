from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.imports.erp.excel_import import import_erp_file
from app.models import ImportJob
from app.schemas import ImportJobOut

router = APIRouter()


@router.post("/upload", response_model=ImportJobOut)
async def upload_erp_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "import.csv").suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail="Formats acceptés: CSV, XLSX, XLS")

    dest = upload_dir / f"erp_{file.filename}"
    content = await file.read()
    dest.write_bytes(content)

    job = import_erp_file(db, dest, source_name=file.filename)
    return job


@router.get("/jobs", response_model=list[ImportJobOut])
def list_import_jobs(db: Session = Depends(get_db)):
    return (
        db.query(ImportJob)
        .filter(ImportJob.job_type == "erp")
        .order_by(ImportJob.id.desc())
        .limit(50)
        .all()
    )
