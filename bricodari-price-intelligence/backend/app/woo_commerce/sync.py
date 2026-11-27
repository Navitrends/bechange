from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models import ImportJob, Product, ProductIdentifier
from app.woo_commerce.client import WooCommerceClient


def _safe_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _category_label(product: dict[str, Any]) -> Optional[str]:
    categories = product.get("categories") or []
    if not categories:
        return None
    return " > ".join(c.get("name", "") for c in categories if c.get("name"))


def _upsert_product(db: Session, data: dict[str, Any], *, is_variation: bool = False, parent_id: Optional[int] = None) -> Product:
    woo_id = data.get("id")
    product = db.query(Product).filter(Product.woo_id == woo_id).first()
    if product is None:
        product = Product(woo_id=woo_id)
        db.add(product)

    regular = _safe_float(data.get("regular_price"))
    sale = _safe_float(data.get("sale_price"))
    price = _safe_float(data.get("price"))

    product.parent_woo_id = parent_id
    # Ne pas écraser un SKU déjà renseigné (ex. démo / complété client)
    incoming_sku = (data.get("sku") or "").strip() or None
    if incoming_sku:
        product.sku = incoming_sku
    elif not product.sku:
        product.sku = None
    product.name = data.get("name") or f"Produit {woo_id}"
    product.short_description = data.get("short_description")
    product.description = data.get("description")
    product.regular_price = regular
    product.sale_price = sale
    product.display_price = price if price is not None else (sale or regular)
    product.status = data.get("status")
    product.permalink = data.get("permalink")
    product.stock_status = data.get("stock_status")
    product.is_variation = is_variation
    product.category = _category_label(data) if not is_variation else product.category
    product.last_synced_at = datetime.utcnow()

    # brand from attributes if present
    for attr in data.get("attributes") or []:
        if str(attr.get("name", "")).lower() in {"marque", "brand"}:
            options = attr.get("options") or []
            if options:
                product.brand = options[0]
            break

    db.flush()

    if product.sku:
        existing = (
            db.query(ProductIdentifier)
            .filter(
                ProductIdentifier.product_id == product.id,
                ProductIdentifier.id_type == "sku",
                ProductIdentifier.value == product.sku,
            )
            .first()
        )
        if not existing:
            db.add(
                ProductIdentifier(
                    product_id=product.id,
                    id_type="sku",
                    value=product.sku,
                    source="woocommerce",
                )
            )
    return product


def sync_catalog(db: Session, max_products: Optional[int] = None) -> ImportJob:
    job = ImportJob(
        job_type="woo",
        source_name="woocommerce",
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        client = WooCommerceClient()
        count = 0
        ok = 0
        errors = 0

        for item in client.iter_products():
            if max_products is not None and count >= max_products:
                break
            count += 1
            try:
                product = _upsert_product(db, item, is_variation=False)
                if item.get("type") == "variable":
                    for variation in client.get_variations(item["id"]):
                        _upsert_product(
                            db,
                            variation,
                            is_variation=True,
                            parent_id=item["id"],
                        )
                        # inherit category/brand from parent if empty
                        child = (
                            db.query(Product)
                            .filter(Product.woo_id == variation.get("id"))
                            .first()
                        )
                        if child and not child.category:
                            child.category = product.category
                        if child and not child.brand:
                            child.brand = product.brand
                ok += 1
                if ok % 25 == 0:
                    db.commit()
            except Exception as exc:  # noqa: BLE001
                errors += 1
                job.message = f"Dernière erreur: {exc}"

        job.rows_total = count
        job.rows_ok = ok
        job.rows_error = errors
        job.status = "completed" if errors == 0 else "completed_with_errors"
        job.finished_at = datetime.utcnow()
        db.commit()
    except Exception as exc:  # noqa: BLE001
        job.status = "failed"
        job.message = str(exc)
        job.finished_at = datetime.utcnow()
        db.commit()

    db.refresh(job)
    return job
