from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"
SAMPLES = ROOT / "samples"

client = httpx.Client(timeout=120.0)

with open(SAMPLES / "demo_prix_achat.xlsx", "rb") as f:
    r = client.post(
        f"{BASE}/api/imports/erp/upload",
        files={
            "file": (
                "demo_prix_achat.xlsx",
                f,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    print("achat", r.status_code, r.text)

with open(SAMPLES / "demo_prix_concurrents.xlsx", "rb") as f:
    r = client.post(
        f"{BASE}/api/imports/competitors/upload",
        files={
            "file": (
                "demo_prix_concurrents.xlsx",
                f,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    print("concurrents", r.status_code, r.text)

r = client.post(f"{BASE}/api/comparisons/rebuild")
print("rebuild", r.status_code, r.text)

r = client.get(f"{BASE}/api/comparisons")
data = r.json()
print("comparisons", len(data))
for row in data[:5]:
    print(
        row["sku"],
        row["sell_price"],
        row["purchase_price"],
        row["competitor_min_price"],
        row["alert_level"],
    )

print("stats", client.get(f"{BASE}/api/stats").json())
