import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import PriceComparison, Product
from app.pricing.comparison import rebuild_comparisons

router = APIRouter()


class ComparisonOut(BaseModel):
    product_id: int
    sku: Optional[str] = None
    name: str
    category: Optional[str] = None
    purchase_price: Optional[float] = None
    sell_price: Optional[float] = None
    competitor_min_price: Optional[float] = None
    competitor_min_name: Optional[str] = None
    competitor_max_price: Optional[float] = None
    competitor_max_name: Optional[str] = None
    gap_vs_min_pct: Optional[float] = None
    estimated_margin_pct: Optional[float] = None
    alert_level: Optional[str] = None
    recommendation: Optional[str] = None
    permalink: Optional[str] = None

    model_config = {"from_attributes": True}


@router.post("/rebuild")
def rebuild(db: Session = Depends(get_db)):
    return rebuild_comparisons(db, only_with_sku=True)


@router.get("", response_model=list[ComparisonOut])
def list_comparisons(
    alert: Optional[str] = Query(None, description="cher|moins_cher|ok"),
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    rows = (
        db.query(PriceComparison, Product)
        .join(Product, Product.id == PriceComparison.product_id)
        .order_by(PriceComparison.id.desc())
        .all()
    )
    results: list[ComparisonOut] = []
    for comp, product in rows:
        if alert and comp.alert_level != alert:
            continue
        if q:
            like = q.lower()
            if like not in (product.name or "").lower() and like not in (
                product.sku or ""
            ).lower():
                continue
        results.append(
            ComparisonOut(
                product_id=product.id,
                sku=product.sku,
                name=product.name,
                category=product.category,
                purchase_price=comp.purchase_price,
                sell_price=comp.sell_price,
                competitor_min_price=comp.competitor_min_price,
                competitor_min_name=comp.competitor_min_name,
                competitor_max_price=comp.competitor_max_price,
                competitor_max_name=comp.competitor_max_name,
                gap_vs_min_pct=comp.gap_vs_min_pct,
                estimated_margin_pct=comp.estimated_margin_pct,
                alert_level=comp.alert_level,
                recommendation=comp.recommendation,
                permalink=product.permalink,
            )
        )
    return results


@router.get("/export.csv")
def export_csv(db: Session = Depends(get_db)):
    rows = list_comparisons(db=db)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(
        [
            "SKU",
            "Produit",
            "Categorie",
            "Prix achat",
            "Prix vente",
            "Concurrent min",
            "Prix min",
            "Concurrent max",
            "Prix max",
            "Ecart %",
            "Marge %",
            "Alerte",
            "Recommendation",
            "URL",
        ]
    )
    for r in rows:
        writer.writerow(
            [
                r.sku,
                r.name,
                r.category,
                r.purchase_price,
                r.sell_price,
                r.competitor_min_name,
                r.competitor_min_price,
                r.competitor_max_name,
                r.competitor_max_price,
                r.gap_vs_min_pct,
                r.estimated_margin_pct,
                r.alert_level,
                r.recommendation,
                r.permalink,
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=bricodari_comparateur.csv"
        },
    )
