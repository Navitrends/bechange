from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models import Competitor, ErpPriceRecord, ImportJob, Product, Supplier, SupplierOffer
from app.schemas import StatsOut

router = APIRouter()


@router.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "woocommerce_url": settings.woocommerce_url,
        "woocommerce_configured": bool(
            settings.woocommerce_consumer_key and settings.woocommerce_consumer_secret
        ),
    }


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    return StatsOut(
        products=db.query(func.count(Product.id)).scalar() or 0,
        competitors=db.query(func.count(Competitor.id)).scalar() or 0,
        suppliers=db.query(func.count(Supplier.id)).scalar() or 0,
        erp_price_records=db.query(func.count(ErpPriceRecord.id)).scalar() or 0,
        supplier_offers=db.query(func.count(SupplierOffer.id)).scalar() or 0,
        import_jobs=db.query(func.count(ImportJob.id)).scalar() or 0,
    )
