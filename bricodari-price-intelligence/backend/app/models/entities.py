from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.utcnow()


class Product(Base):
    """Référentiel produit central (catalogue Bricodari / WooCommerce)."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    woo_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True)
    parent_woo_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    sku: Mapped[Optional[str]] = mapped_column(String(120), index=True)
    name: Mapped[str] = mapped_column(String(500))
    brand: Mapped[Optional[str]] = mapped_column(String(200))
    category: Mapped[Optional[str]] = mapped_column(String(300))
    short_description: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    regular_price: Mapped[Optional[float]] = mapped_column(Float)
    sale_price: Mapped[Optional[float]] = mapped_column(Float)
    display_price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="TND")
    status: Mapped[Optional[str]] = mapped_column(String(50))
    permalink: Mapped[Optional[str]] = mapped_column(String(500))
    stock_status: Mapped[Optional[str]] = mapped_column(String(50))
    is_variation: Mapped[bool] = mapped_column(Boolean, default=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    identifiers: Mapped[list["ProductIdentifier"]] = relationship(back_populates="product")
    erp_prices: Mapped[list["ErpPriceRecord"]] = relationship(back_populates="product")
    matches: Mapped[list["ProductMatch"]] = relationship(back_populates="product")
    comparisons: Mapped[list["PriceComparison"]] = relationship(back_populates="product")


class ProductIdentifier(Base):
    __tablename__ = "product_identifiers"
    __table_args__ = (UniqueConstraint("product_id", "id_type", "value", name="uq_product_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    id_type: Mapped[str] = mapped_column(String(50))  # sku, ean, manufacturer_ref
    value: Mapped[str] = mapped_column(String(200), index=True)
    source: Mapped[Optional[str]] = mapped_column(String(100))

    product: Mapped["Product"] = relationship(back_populates="identifiers")


class ErpPriceRecord(Base):
    """Prix d'achat internes (ERP / Excel / Drive)."""

    __tablename__ = "erp_price_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), index=True)
    sku: Mapped[Optional[str]] = mapped_column(String(120), index=True)
    designation: Mapped[Optional[str]] = mapped_column(String(500))
    brand: Mapped[Optional[str]] = mapped_column(String(200))
    manufacturer_ref: Mapped[Optional[str]] = mapped_column(String(200))
    ean: Mapped[Optional[str]] = mapped_column(String(50))
    purchase_price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="TND")
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    supplier_name: Mapped[Optional[str]] = mapped_column(String(200))
    price_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    source_file: Mapped[Optional[str]] = mapped_column(String(500))
    import_job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("import_jobs.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    product: Mapped[Optional["Product"]] = relationship(back_populates="erp_prices")


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    documents: Mapped[list["SupplierDocument"]] = relationship(back_populates="supplier")
    offers: Mapped[list["SupplierOffer"]] = relationship(back_populates="supplier")


class SupplierDocument(Base):
    __tablename__ = "supplier_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"), index=True)
    filename: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[Optional[str]] = mapped_column(String(50))
    source: Mapped[Optional[str]] = mapped_column(String(100))  # upload, drive, email
    status: Mapped[str] = mapped_column(String(50), default="pending")
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    supplier: Mapped[Optional["Supplier"]] = relationship(back_populates="documents")
    offers: Mapped[list["SupplierOffer"]] = relationship(back_populates="document")


class SupplierOffer(Base):
    __tablename__ = "supplier_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"), index=True)
    document_id: Mapped[Optional[int]] = mapped_column(ForeignKey("supplier_documents.id"))
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), index=True)
    supplier_ref: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    manufacturer_ref: Mapped[Optional[str]] = mapped_column(String(200))
    ean: Mapped[Optional[str]] = mapped_column(String(50))
    designation: Mapped[Optional[str]] = mapped_column(String(500))
    brand: Mapped[Optional[str]] = mapped_column(String(200))
    unit_price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="TND")
    is_ttc: Mapped[Optional[bool]] = mapped_column(Boolean)
    discount: Mapped[Optional[float]] = mapped_column(Float)
    min_qty: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    supplier: Mapped[Optional["Supplier"]] = relationship(back_populates="offers")
    document: Mapped[Optional["SupplierDocument"]] = relationship(back_populates="offers")


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    website_url: Mapped[str] = mapped_column(String(500))
    country: Mapped[str] = mapped_column(String(50), default="TN")
    currency: Mapped[str] = mapped_column(String(10), default="TND")
    language: Mapped[str] = mapped_column(String(10), default="fr")
    catalog_url: Mapped[Optional[str]] = mapped_column(String(500))
    crawl_frequency: Mapped[str] = mapped_column(String(50), default="weekly")
    crawl_method: Mapped[str] = mapped_column(String(50), default="html")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_crawled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    products: Mapped[list["CompetitorProduct"]] = relationship(back_populates="competitor")


class CompetitorProduct(Base):
    __tablename__ = "competitor_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competitor_id: Mapped[int] = mapped_column(ForeignKey("competitors.id"), index=True)
    url: Mapped[str] = mapped_column(String(1000))
    name: Mapped[Optional[str]] = mapped_column(String(500))
    brand: Mapped[Optional[str]] = mapped_column(String(200))
    manufacturer_ref: Mapped[Optional[str]] = mapped_column(String(200))
    ean: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    competitor: Mapped["Competitor"] = relationship(back_populates="products")
    observations: Mapped[list["CompetitorPriceObservation"]] = relationship(
        back_populates="competitor_product"
    )


class CompetitorPriceObservation(Base):
    __tablename__ = "competitor_price_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competitor_product_id: Mapped[int] = mapped_column(
        ForeignKey("competitor_products.id"), index=True
    )
    price: Mapped[Optional[float]] = mapped_column(Float)
    sale_price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="TND")
    availability: Mapped[Optional[str]] = mapped_column(String(100))
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    competitor_product: Mapped["CompetitorProduct"] = relationship(back_populates="observations")


class ProductMatch(Base):
    __tablename__ = "product_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    match_type: Mapped[str] = mapped_column(String(50))  # erp, supplier, competitor
    matched_entity_type: Mapped[str] = mapped_column(String(50))
    matched_entity_id: Mapped[int] = mapped_column(Integer)
    match_method: Mapped[str] = mapped_column(String(50))  # sku, ean, fuzzy, manual
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="proposed")  # proposed, validated, rejected
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    product: Mapped["Product"] = relationship(back_populates="matches")


class PriceComparison(Base):
    """Fiche comparative consolidée par produit."""

    __tablename__ = "price_comparisons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), unique=True, index=True)
    purchase_price: Mapped[Optional[float]] = mapped_column(Float)
    best_supplier_price: Mapped[Optional[float]] = mapped_column(Float)
    best_supplier_name: Mapped[Optional[str]] = mapped_column(String(200))
    sell_price: Mapped[Optional[float]] = mapped_column(Float)
    competitor_min_price: Mapped[Optional[float]] = mapped_column(Float)
    competitor_max_price: Mapped[Optional[float]] = mapped_column(Float)
    competitor_min_name: Mapped[Optional[str]] = mapped_column(String(200))
    competitor_max_name: Mapped[Optional[str]] = mapped_column(String(200))
    gap_vs_min_abs: Mapped[Optional[float]] = mapped_column(Float)
    gap_vs_min_pct: Mapped[Optional[float]] = mapped_column(Float)
    estimated_margin_pct: Mapped[Optional[float]] = mapped_column(Float)
    alert_level: Mapped[Optional[str]] = mapped_column(String(50))
    recommendation: Mapped[Optional[str]] = mapped_column(Text)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    product: Mapped["Product"] = relationship(back_populates="comparisons")


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_type: Mapped[str] = mapped_column(String(50))  # erp, supplier, woo, competitor
    source_name: Mapped[Optional[str]] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    rows_total: Mapped[int] = mapped_column(Integer, default=0)
    rows_ok: Mapped[int] = mapped_column(Integer, default=0)
    rows_error: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
