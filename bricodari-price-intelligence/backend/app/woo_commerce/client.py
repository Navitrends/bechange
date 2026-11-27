from typing import Any, Optional

import httpx

from app.core.config import get_settings


class WooCommerceClient:
    """Client REST API WooCommerce (lecture seule pour le catalogue)."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.woocommerce_url).rstrip("/")
        self.consumer_key = consumer_key or settings.woocommerce_consumer_key
        self.consumer_secret = consumer_secret or settings.woocommerce_consumer_secret
        if not self.consumer_key or not self.consumer_secret:
            raise ValueError(
                "Clés WooCommerce manquantes. Renseignez WOOCOMMERCE_CONSUMER_KEY "
                "et WOOCOMMERCE_CONSUMER_SECRET dans le fichier .env"
            )

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=f"{self.base_url}/wp-json/wc/v3",
            auth=(self.consumer_key, self.consumer_secret),
            timeout=60.0,
        )

    def test_connection(self) -> dict[str, Any]:
        with self._client() as client:
            response = client.get("/products", params={"per_page": 1})
            response.raise_for_status()
            total = response.headers.get("X-WP-Total", "?")
            return {
                "ok": True,
                "url": self.base_url,
                "products_reported": total,
                "sample": response.json()[0]["name"] if response.json() else None,
            }

    def iter_products(self, per_page: int = 50, status: str = "any"):
        page = 1
        with self._client() as client:
            while True:
                response = client.get(
                    "/products",
                    params={"per_page": per_page, "page": page, "status": status},
                )
                response.raise_for_status()
                items = response.json()
                if not items:
                    break
                for item in items:
                    yield item
                total_pages = int(response.headers.get("X-WP-TotalPages", "1"))
                if page >= total_pages:
                    break
                page += 1

    def get_variations(self, product_id: int, per_page: int = 50) -> list[dict[str, Any]]:
        variations: list[dict[str, Any]] = []
        page = 1
        with self._client() as client:
            while True:
                response = client.get(
                    f"/products/{product_id}/variations",
                    params={"per_page": per_page, "page": page},
                )
                response.raise_for_status()
                items = response.json()
                if not items:
                    break
                variations.extend(items)
                total_pages = int(response.headers.get("X-WP-TotalPages", "1"))
                if page >= total_pages:
                    break
                page += 1
        return variations
