from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Product
from app.schemas import ProductOut

router = APIRouter()


@router.get("", response_model=list[ProductOut])
def list_products(
    q: Optional[str] = Query(None, description="Recherche nom ou SKU"),
    skip: int = 0,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if q:
        like = f"%{q}%"
        query = query.filter((Product.name.ilike(like)) | (Product.sku.ilike(like)))
    return query.order_by(Product.id.desc()).offset(skip).limit(limit).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Produit introuvable")
    return product
