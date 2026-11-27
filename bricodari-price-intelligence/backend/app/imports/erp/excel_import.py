from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models import ErpPriceRecord, ImportJob, Product


COLUMN_ALIASES = {
    "sku": ["sku", "ugs", "code", "code article", "référence", "reference", "ref"],
    "designation": ["designation", "désignation", "libelle", "libellé", "nom", "produit", "article"],
    "brand": ["brand", "marque"],
    "manufacturer_ref": ["ref fabricant", "référence fabricant", "manufacturer", "ref_fab"],
    "ean": ["ean", "code-barres", "barcode", "gtin"],
    "purchase_price": ["prix", "prix achat", "prix d'achat", "purchase_price", "pa", "cout", "coût"],
    "currency": ["devise", "currency"],
    "unit": ["unité", "unite", "unit"],
    "supplier_name": ["fournisseur", "supplier"],
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


def import_erp_file(db: Session, file_path: Path, source_name: Optional[str] = None) -> ImportJob:
    job = ImportJob(
        job_type="erp",
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
        if "purchase_price" not in mapping and "sku" not in mapping:
            raise ValueError(
                "Impossible de détecter les colonnes SKU / prix. "
                f"Colonnes trouvées: {list(df.columns)}"
            )

        ok = 0
        errors = 0
        for _, row in df.iterrows():
            try:
                sku = str(row[mapping["sku"]]).strip() if "sku" in mapping else None
                if sku in {"", "nan", "None"}:
                    sku = None
                designation = (
                    str(row[mapping["designation"]]).strip()
                    if "designation" in mapping
                    else None
                )
                purchase_price = (
                    _safe_float(row[mapping["purchase_price"]])
                    if "purchase_price" in mapping
                    else None
                )

                product_id = None
                if sku:
                    product = db.query(Product).filter(Product.sku == sku).first()
                    if product:
                        product_id = product.id

                record = ErpPriceRecord(
                    product_id=product_id,
                    sku=sku,
                    designation=designation if designation not in {"nan", "None"} else None,
                    brand=str(row[mapping["brand"]]).strip() if "brand" in mapping else None,
                    manufacturer_ref=(
                        str(row[mapping["manufacturer_ref"]]).strip()
                        if "manufacturer_ref" in mapping
                        else None
                    ),
                    ean=str(row[mapping["ean"]]).strip() if "ean" in mapping else None,
                    purchase_price=purchase_price,
                    currency=(
                        str(row[mapping["currency"]]).strip()
                        if "currency" in mapping
                        else "TND"
                    ),
                    unit=str(row[mapping["unit"]]).strip() if "unit" in mapping else None,
                    supplier_name=(
                        str(row[mapping["supplier_name"]]).strip()
                        if "supplier_name" in mapping
                        else None
                    ),
                    source_file=file_path.name,
                    import_job_id=job.id,
                )
                db.add(record)
                ok += 1
            except Exception:  # noqa: BLE001
                errors += 1

        job.rows_total = len(df)
        job.rows_ok = ok
        job.rows_error = errors
        job.status = "completed" if errors == 0 else "completed_with_errors"
        job.finished_at = datetime.utcnow()
        job.message = f"Mapping colonnes: {mapping}"
        db.commit()
    except Exception as exc:  # noqa: BLE001
        job.status = "failed"
        job.message = str(exc)
        job.finished_at = datetime.utcnow()
        db.commit()

    db.refresh(job)
    return job
