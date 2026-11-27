from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models import (
    Competitor,
    CompetitorPriceObservation,
    CompetitorProduct,
    ImportJob,
    Product,
)


COLUMN_ALIASES = {
    "sku": ["sku", "ugs", "code", "code_sku", "référence", "reference"],
    "name": ["nom", "nom produit", "designation", "désignation", "produit"],
    "competitor": ["concurrent", "competitor", "site"],
    "price": ["prix", "price", "prix concurrent"],
    "currency": ["devise", "currency"],
    "url": ["url", "lien", "link"],
}


def _normalize_columns(df: pd.DataFrame) -> dict[str, str]:
    mapping: dict[str, str] = {}
    cols = {str(c).strip().lower(): c for c in df.columns}
    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in cols:
                mapping[field] = cols[alias]
                break
    return mapping


def _safe_float(value: Any) -> Optional[float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().replace(" ", "").replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def import_competitor_file(
    db: Session, file_path: Path, source_name: Optional[str] = None
) -> ImportJob:
    job = ImportJob(
        job_type="competitor",
        source_name=source_name or file_path.name,
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        if file_path.suffix.lower() in {".xlsx", ".xls"}:
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        mapping = _normalize_columns(df)
        required = {"sku", "competitor", "price"}
        if not required.issubset(mapping.keys()):
            raise ValueError(
                f"Colonnes requises manquantes (SKU, Concurrent, Prix). Trouvé: {list(df.columns)}"
            )

        ok = 0
        errors = 0
        for _, row in df.iterrows():
            try:
                sku = str(row[mapping["sku"]]).strip()
                competitor_name = str(row[mapping["competitor"]]).strip()
                price = _safe_float(row[mapping["price"]])
                name = (
                    str(row[mapping["name"]]).strip()
                    if "name" in mapping
                    else None
                )
                url = str(row[mapping["url"]]).strip() if "url" in mapping else ""
                currency = (
                    str(row[mapping["currency"]]).strip()
                    if "currency" in mapping
                    else "TND"
                )

                competitor = (
                    db.query(Competitor)
                    .filter(Competitor.name == competitor_name)
                    .first()
                )
                if not competitor:
                    competitor = Competitor(
                        name=competitor_name,
                        website_url=url or f"https://{competitor_name.lower().replace(' ', '-')}.tn",
                    )
                    db.add(competitor)
                    db.flush()

                product = db.query(Product).filter(Product.sku == sku).first()

                cp = (
                    db.query(CompetitorProduct)
                    .filter(
                        CompetitorProduct.competitor_id == competitor.id,
                        CompetitorProduct.url == (url or f"manual://{sku}"),
                    )
                    .first()
                )
                if not cp:
                    cp = CompetitorProduct(
                        competitor_id=competitor.id,
                        url=url or f"manual://{sku}",
                        name=name,
                        manufacturer_ref=sku,
                    )
                    db.add(cp)
                    db.flush()

                db.add(
                    CompetitorPriceObservation(
                        competitor_product_id=cp.id,
                        price=price,
                        currency=currency,
                        observed_at=datetime.utcnow(),
                    )
                )

                # Auto-match by SKU if product found
                if product:
                    from app.models import ProductMatch

                    existing = (
                        db.query(ProductMatch)
                        .filter(
                            ProductMatch.product_id == product.id,
                            ProductMatch.matched_entity_type == "competitor_product",
                            ProductMatch.matched_entity_id == cp.id,
                        )
                        .first()
                    )
                    if not existing:
                        db.add(
                            ProductMatch(
                                product_id=product.id,
                                match_type="competitor",
                                matched_entity_type="competitor_product",
                                matched_entity_id=cp.id,
                                match_method="sku",
                                confidence=1.0,
                                status="validated",
                            )
                        )
                ok += 1
            except Exception:  # noqa: BLE001
                errors += 1

        job.rows_total = len(df)
        job.rows_ok = ok
        job.rows_error = errors
        job.status = "completed" if errors == 0 else "completed_with_errors"
        job.finished_at = datetime.utcnow()
        job.message = f"Mapping: {mapping}"
        db.commit()
    except Exception as exc:  # noqa: BLE001
        job.status = "failed"
        job.message = str(exc)
        job.finished_at = datetime.utcnow()
        db.commit()

    db.refresh(job)
    return job
