from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models import (
    Competitor,
    CompetitorPriceObservation,
    CompetitorProduct,
    ErpPriceRecord,
    PriceComparison,
    Product,
    ProductMatch,
)


def _latest_erp_price(db: Session, product: Product) -> Optional[ErpPriceRecord]:
    q = db.query(ErpPriceRecord)
    if product.sku:
        q = q.filter(ErpPriceRecord.sku == product.sku)
    else:
        q = q.filter(ErpPriceRecord.product_id == product.id)
    return q.order_by(ErpPriceRecord.id.desc()).first()


def _competitor_prices(db: Session, product: Product) -> list[tuple[str, float]]:
    results: list[tuple[str, float]] = []

    # Matches validated
    matches = (
        db.query(ProductMatch)
        .filter(
            ProductMatch.product_id == product.id,
            ProductMatch.match_type == "competitor",
            ProductMatch.status.in_(["validated", "proposed"]),
        )
        .all()
    )
    for match in matches:
        cp = (
            db.query(CompetitorProduct)
            .filter(CompetitorProduct.id == match.matched_entity_id)
            .first()
        )
        if not cp:
            continue
        obs = (
            db.query(CompetitorPriceObservation)
            .filter(CompetitorPriceObservation.competitor_product_id == cp.id)
            .order_by(CompetitorPriceObservation.observed_at.desc())
            .first()
        )
        competitor = db.query(Competitor).filter(Competitor.id == cp.competitor_id).first()
        if obs and obs.price is not None and competitor:
            results.append((competitor.name, float(obs.price)))

    # Fallback: manufacturer_ref = sku
    if product.sku and not results:
        cps = (
            db.query(CompetitorProduct)
            .filter(CompetitorProduct.manufacturer_ref == product.sku)
            .all()
        )
        for cp in cps:
            obs = (
                db.query(CompetitorPriceObservation)
                .filter(CompetitorPriceObservation.competitor_product_id == cp.id)
                .order_by(CompetitorPriceObservation.observed_at.desc())
                .first()
            )
            competitor = (
                db.query(Competitor).filter(Competitor.id == cp.competitor_id).first()
            )
            if obs and obs.price is not None and competitor:
                results.append((competitor.name, float(obs.price)))

    return results


def rebuild_comparisons(db: Session, only_with_sku: bool = True) -> dict:
    query = db.query(Product).filter(Product.is_variation.is_(False))
    if only_with_sku:
        query = query.filter(Product.sku.isnot(None), Product.sku != "")

    products = query.all()
    created = 0

    for product in products:
        erp = _latest_erp_price(db, product)
        comps = _competitor_prices(db, product)

        purchase = erp.purchase_price if erp else None
        sell = product.display_price
        min_name = max_name = None
        min_price = max_price = None
        if comps:
            min_name, min_price = min(comps, key=lambda x: x[1])
            max_name, max_price = max(comps, key=lambda x: x[1])

        gap_abs = gap_pct = margin = None
        alert = None
        recommendation = None

        if sell is not None and min_price is not None:
            gap_abs = round(sell - min_price, 3)
            if min_price:
                gap_pct = round((sell - min_price) / min_price * 100, 2)
            if gap_pct is not None and gap_pct > 10:
                alert = "cher"
                recommendation = (
                    f"Plus cher que {min_name} ({min_price} TND). Écart {gap_pct}%."
                )
            elif gap_pct is not None and gap_pct < -5:
                alert = "moins_cher"
                recommendation = (
                    f"Moins cher que le marché (min {min_name}: {min_price} TND)."
                )
            else:
                alert = "ok"
                recommendation = "Prix aligné avec le marché."

        if sell is not None and purchase is not None and sell:
            margin = round((sell - purchase) / sell * 100, 2)

        row = (
            db.query(PriceComparison)
            .filter(PriceComparison.product_id == product.id)
            .first()
        )
        if not row:
            row = PriceComparison(product_id=product.id)
            db.add(row)

        row.purchase_price = purchase
        row.best_supplier_price = purchase
        row.best_supplier_name = erp.supplier_name if erp else None
        row.sell_price = sell
        row.competitor_min_price = min_price
        row.competitor_max_price = max_price
        row.competitor_min_name = min_name
        row.competitor_max_name = max_name
        row.gap_vs_min_abs = gap_abs
        row.gap_vs_min_pct = gap_pct
        row.estimated_margin_pct = margin
        row.alert_level = alert
        row.recommendation = recommendation
        row.computed_at = datetime.utcnow()
        created += 1

    db.commit()
    return {"products_compared": created}
