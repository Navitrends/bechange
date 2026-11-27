from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductOut(BaseModel):
    id: int
    woo_id: Optional[int] = None
    sku: Optional[str] = None
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    display_price: Optional[float] = None
    currency: str = "TND"
    status: Optional[str] = None
    permalink: Optional[str] = None
    is_variation: bool = False
    last_synced_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CompetitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    website_url: str
    country: str = "TN"
    currency: str = "TND"
    language: str = "fr"
    catalog_url: Optional[str] = None
    crawl_frequency: str = "weekly"
    crawl_method: str = "html"
    is_active: bool = True


class CompetitorOut(CompetitorCreate):
    id: int
    last_crawled_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ImportJobOut(BaseModel):
    id: int
    job_type: str
    source_name: Optional[str] = None
    status: str
    rows_total: int
    rows_ok: int
    rows_error: int
    message: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StatsOut(BaseModel):
    products: int
    competitors: int
    suppliers: int
    erp_price_records: int
    supplier_offers: int
    import_jobs: int
