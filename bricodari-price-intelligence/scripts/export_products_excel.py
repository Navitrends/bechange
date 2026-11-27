from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend" / "bricodari.db"
OUT = ROOT / "exports" / "Bricodari_Produits_a_completer.xlsx"

OUT.parent.mkdir(parents=True, exist_ok=True)

eng = create_engine(f"sqlite:///{DB}")

df = pd.read_sql(
    """
    SELECT
        id AS id_interne,
        woo_id AS id_woocommerce,
        parent_woo_id AS id_parent_woocommerce,
        sku AS code_sku,
        name AS nom_produit,
        brand AS marque,
        category AS categorie,
        regular_price AS prix_normal,
        sale_price AS prix_promo,
        display_price AS prix_affiche,
        currency AS devise,
        status AS statut,
        stock_status AS stock,
        CASE WHEN is_variation = 1 THEN 'Oui' ELSE 'Non' END AS est_variante,
        permalink AS url_produit,
        short_description AS description_courte,
        description AS description,
        last_synced_at AS date_sync
    FROM products
    ORDER BY is_variation ASC, name ASC
    """,
    eng,
)

# Clean HTML a bit for readability in Excel
for col in ["description_courte", "description"]:
    df[col] = (
        df[col]
        .fillna("")
        .astype(str)
        .str.replace(r"<[^>]+>", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

# Add empty columns for the client to fill
df["code_sku_a_completer"] = df["code_sku"]
df["ean_code_barres"] = ""
df["reference_fabricant"] = ""
df["marque_a_completer"] = df["marque"].fillna("")
df["notes_client"] = ""

# Reorder columns for client-friendly sheet
cols = [
    "id_woocommerce",
    "id_parent_woocommerce",
    "est_variante",
    "code_sku",
    "code_sku_a_completer",
    "ean_code_barres",
    "reference_fabricant",
    "nom_produit",
    "marque",
    "marque_a_completer",
    "categorie",
    "prix_normal",
    "prix_promo",
    "prix_affiche",
    "devise",
    "statut",
    "stock",
    "url_produit",
    "description_courte",
    "notes_client",
    "date_sync",
]
df = df[cols]

with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Produits", index=False)

    # Summary sheet
    summary = pd.DataFrame(
        {
            "Indicateur": [
                "Nombre total de lignes",
                "Produits (non variantes)",
                "Variantes",
                "Avec code SKU rempli",
                "Sans code SKU (a completer)",
                "Avec prix",
            ],
            "Valeur": [
                len(df),
                int((df["est_variante"] == "Non").sum()),
                int((df["est_variante"] == "Oui").sum()),
                int(df["code_sku"].fillna("").astype(str).str.strip().ne("").sum()),
                int(df["code_sku"].fillna("").astype(str).str.strip().eq("").sum()),
                int(df["prix_affiche"].notna().sum()),
            ],
        }
    )
    summary.to_excel(writer, sheet_name="Resume", index=False)

    # Instructions sheet
    instructions = pd.DataFrame(
        {
            "Instructions pour le client": [
                "1. Compléter la colonne code_sku_a_completer (code article unique).",
                "2. Si possible, remplir ean_code_barres et reference_fabricant.",
                "3. Vérifier/compléter marque_a_completer.",
                "4. Ne pas modifier id_woocommerce (nécessaire pour la mise à jour).",
                "5. Une ligne = un produit ou une variante.",
                "6. Renvoyer ce fichier une fois complété.",
            ]
        }
    )
    instructions.to_excel(writer, sheet_name="Instructions", index=False)

print(f"OK: {OUT}")
print(f"Lignes: {len(df)}")
