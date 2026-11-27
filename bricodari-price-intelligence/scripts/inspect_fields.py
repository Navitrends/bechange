from sqlalchemy import create_engine, inspect, text

eng = create_engine("sqlite:///backend/bricodari.db")
insp = inspect(eng)
cols = [c["name"] for c in insp.get_columns("products")]
print("COLONNES EN BASE:")
for c in cols:
    print("-", c)

with eng.connect() as c:
    row = (
        c.execute(
            text(
                "select * from products where is_variation=0 "
                "and display_price is not null limit 1"
            )
        )
        .mappings()
        .first()
    )
    print("\nEXEMPLE PRODUIT:")
    for k, v in dict(row).items():
        val = str(v)
        if len(val) > 100:
            val = val[:100] + "..."
        print(f"  {k}: {val}")

    print("\nSTATS:")
    queries = {
        "total": "select count(*) from products",
        "avec_prix": "select count(*) from products where display_price is not null",
        "avec_sku": "select count(*) from products where sku is not null and sku != ''",
        "avec_marque": "select count(*) from products where brand is not null",
        "avec_categorie": "select count(*) from products where category is not null",
        "avec_url": "select count(*) from products where permalink is not null",
        "avec_description": "select count(*) from products where description is not null and description != ''",
    }
    for label, q in queries.items():
        print(f"  {label}: {c.execute(text(q)).scalar()}")
