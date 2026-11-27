from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.scheduler import get_sync_state, start_sync_async, update_schedule
from app.woo_commerce.client import WooCommerceClient

router = APIRouter()


class ScheduleUpdate(BaseModel):
    enabled: bool = True
    interval_hours: int = Field(default=6, ge=1, le=168)


@router.get("/test")
def test_woocommerce():
    try:
        client = WooCommerceClient()
        return client.test_connection()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sync/status")
def sync_status():
    return get_sync_state()


@router.post("/sync")
def sync_woocommerce(
    max_products: Optional[int] = Query(
        None, description="Limiter le nombre de produits (tests)"
    ),
):
    """Démarre la sync en arrière-plan (ne bloque pas l'UI)."""
    result = start_sync_async(max_products=max_products, trigger="manual")
    if not result.get("accepted"):
        raise HTTPException(status_code=409, detail=result.get("message"))
    return result


@router.put("/sync/schedule")
def set_sync_schedule(payload: ScheduleUpdate):
    return update_schedule(payload.enabled, payload.interval_hours)
