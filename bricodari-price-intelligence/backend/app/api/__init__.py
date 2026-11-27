from fastapi import APIRouter

from app.api import (
    comparisons,
    competitors,
    dashboard,
    health,
    imports_competitors,
    imports_erp,
    products,
    woo,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(woo.router, prefix="/woocommerce", tags=["woocommerce"])
api_router.include_router(imports_erp.router, prefix="/imports/erp", tags=["imports"])
api_router.include_router(
    imports_competitors.router, prefix="/imports/competitors", tags=["imports"]
)
api_router.include_router(competitors.router, prefix="/competitors", tags=["competitors"])
api_router.include_router(comparisons.router, prefix="/comparisons", tags=["comparisons"])
