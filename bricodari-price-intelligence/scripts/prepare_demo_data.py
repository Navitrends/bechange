"""Prépare un jeu de test : 15 produits avec SKU + fichiers achat/concurrents."""

from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend" / "bricodari.db"
SAMPLES = ROOT / "samples"
SAMPLES.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB}")

products = pd.read_sql(
    """
    SELECT id, woo_id, name, display_price, category, permalink
    FROM products
    WHERE is_variation = 0
      AND display_price IS NOT NULL
    ORDER BY id
    LIMIT 15
    """,
    engine,
)

# Assign demo SKUs
skus = [f"BRICO-DEMO-{i:03d}" for i in range(1, len(products) + 1)]
products["sku"] = skus

# Update DB
with engine.begin() as conn:
    for _, row in products.iterrows():
        conn.execute(
            text(
                "UPDATE products SET sku = :sku, brand = COALESCE(brand, :brand), "
                "updated_at = :now WHERE id = :id"
            ),
            {
                "sku": row["sku"],
                "brand": "DemoBrand",
                "now": datetime.utcnow().isoformat(sep=" "),
                "id": int(row["id"]),
            },
        )
        # identifiers
        exists = conn.execute(
            text(
                "SELECT id FROM product_identifiers "
                "WHERE product_id=:pid AND id_type='sku' AND value=:sku"
            ),
            {"pid": int(row["id"]), "sku": row["sku"]},
        ).first()
        if not exists:
            conn.execute(
                text(
                    "INSERT INTO product_identifiers (product_id, id_type, value, source) "
                    "VALUES (:pid, 'sku', :sku, 'demo')"
                ),
                {"pid": int(row["id"]), "sku": row["sku"]},
            )

# Export site sample with references
site_export = products.rename(
    columns={
        "sku": "code_sku",
        "name": "nom_produit",
        "display_price": "prix_vente",
        "category": "categorie",
        "permalink": "url",
        "woo_id": "id_woocommerce",
    }
)[
    [
        "code_sku",
        "id_woocommerce",
        "nom_produit",
        "prix_vente",
        "categorie",
        "url",
    ]
]
site_path = SAMPLES / "demo_catalogue_site.xlsx"
site_export.to_excel(site_path, index=False)

# Purchase prices (ERP) — slight variations
achat_rows = []
for i, row in products.iterrows():
    sell = float(row["display_price"])
    cost = round(sell * 0.55, 3)  # ~45% margin
    achat_rows.append(
        {
            "SKU": row["sku"],
            "Désignation": row["name"],
            "Marque": "DemoBrand",
            "Prix achat": cost,
            "Devise": "TND",
            "Fournisseur": "Fournisseur Demo A" if i % 2 == 0 else "Fournisseur Demo B",
        }
    )
achat_df = pd.DataFrame(achat_rows)
achat_path = SAMPLES / "demo_prix_achat.xlsx"
achat_df.to_excel(achat_path, index=False)

# Competitors — two competitors with min/max around sell price
comp_rows = []
for i, row in products.iterrows():
    sell = float(row["display_price"])
    comp_rows.append(
        {
            "SKU": row["sku"],
            "Nom produit": row["name"],
            "Concurrent": "Concurrent Alpha",
            "Prix": round(sell * 0.92, 3),
            "Devise": "TND",
            "URL": f"https://concurrent-alpha.tn/produit/{row['sku'].lower()}",
        }
    )
    comp_rows.append(
        {
            "SKU": row["sku"],
            "Nom produit": row["name"],
            "Concurrent": "Concurrent Beta",
            "Prix": round(sell * 1.08, 3),
            "Devise": "TND",
            "URL": f"https://concurrent-beta.tn/produit/{row['sku'].lower()}",
        }
    )
# Make 2 products more expensive than both competitors for alerts
if len(products) >= 3:
    for j in [0, 2]:
        sku = products.iloc[j]["sku"]
        sell = float(products.iloc[j]["display_price"])
        for r in comp_rows:
            if r["SKU"] == sku and r["Concurrent"] == "Concurrent Alpha":
                r["Prix"] = round(sell * 0.75, 3)

comp_df = pd.DataFrame(comp_rows)
comp_path = SAMPLES / "demo_prix_concurrents.xlsx"
comp_df.to_excel(comp_path, index=False)

# Also register competitors in DB if empty
with engine.begin() as conn:
    for name, url in [
        ("Concurrent Alpha", "https://concurrent-alpha.tn"),
        ("Concurrent Beta", "https://concurrent-beta.tn"),
    ]:
        exists = conn.execute(
            text("SELECT id FROM competitors WHERE name=:n"), {"n": name}
        ).first()
        if not exists:
            conn.execute(
                text(
                    "INSERT INTO competitors (name, website_url, country, currency, language, "
                    "crawl_frequency, crawl_method, is_active, created_at) "
                    "VALUES (:n, :u, 'TN', 'TND', 'fr', 'weekly', 'manual', 1, :now)"
                ),
                {"n": name, "u": url, "now": datetime.utcnow().isoformat(sep=" ")},
            )

print("Produits demo avec SKU:")
print(site_export[["code_sku", "nom_produit", "prix_vente"]].to_string(index=False))
print()
print("Fichiers créés:")
print("-", site_path)
print("-", achat_path)
print("-", comp_path)
