from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    Competitor,
    ErpPriceRecord,
    ImportJob,
    PriceComparison,
    Product,
)

router = APIRouter()


class DashboardOut(BaseModel):
    products: int
    products_with_sku: int
    products_compared: int
    erp_price_records: int
    competitors: int
    alerts_cher: int
    alerts_moins_cher: int
    alerts_ok: int
    avg_gap_pct: Optional[float] = None
    avg_margin_pct: Optional[float] = None


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    products = db.query(func.count(Product.id)).scalar() or 0
    with_sku = (
        db.query(func.count(Product.id))
        .filter(Product.sku.isnot(None), Product.sku != "")
        .scalar()
        or 0
    )
    compared = db.query(func.count(PriceComparison.id)).scalar() or 0
    erp = db.query(func.count(ErpPriceRecord.id)).scalar() or 0
    comps = db.query(func.count(Competitor.id)).scalar() or 0

    def count_alert(level: str) -> int:
        return (
            db.query(func.count(PriceComparison.id))
            .filter(PriceComparison.alert_level == level)
            .scalar()
            or 0
        )

    avg_gap = db.query(func.avg(PriceComparison.gap_vs_min_pct)).scalar()
    avg_margin = db.query(func.avg(PriceComparison.estimated_margin_pct)).scalar()

    return DashboardOut(
        products=products,
        products_with_sku=with_sku,
        products_compared=compared,
        erp_price_records=erp,
        competitors=comps,
        alerts_cher=count_alert("cher"),
        alerts_moins_cher=count_alert("moins_cher"),
        alerts_ok=count_alert("ok"),
        avg_gap_pct=round(float(avg_gap), 2) if avg_gap is not None else None,
        avg_margin_pct=round(float(avg_margin), 2) if avg_margin is not None else None,
    )


@router.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    rows = db.query(ImportJob).order_by(ImportJob.id.desc()).limit(30).all()
    return [
        {
            "id": j.id,
            "job_type": j.job_type,
            "source_name": j.source_name,
            "status": j.status,
            "rows_total": j.rows_total,
            "rows_ok": j.rows_ok,
            "rows_error": j.rows_error,
            "message": j.message,
            "created_at": j.created_at,
            "finished_at": j.finished_at,
        }
        for j in rows
    ]


@router.get("/erp-prices")
def list_erp_prices(limit: int = 50, db: Session = Depends(get_db)):
    rows = (
        db.query(ErpPriceRecord)
        .order_by(ErpPriceRecord.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "sku": r.sku,
            "designation": r.designation,
            "brand": r.brand,
            "purchase_price": r.purchase_price,
            "currency": r.currency,
            "supplier_name": r.supplier_name,
            "source_file": r.source_file,
            "created_at": r.created_at,
        }
        for r in rows
    ]
