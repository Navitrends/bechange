import httpx
from sqlalchemy import create_engine, text

print("stats", httpx.get("http://127.0.0.1:8000/api/stats", timeout=30).json())

eng = create_engine("sqlite:///backend/bricodari.db")
with eng.connect() as c:
    print("products", c.execute(text("select count(*) from products")).scalar())
    print(
        "variations",
        c.execute(text("select count(*) from products where is_variation=1")).scalar(),
    )
    print(
        "parents",
        c.execute(text("select count(*) from products where is_variation=0")).scalar(),
    )
    print(
        "with_sku",
        c.execute(
            text(
                "select count(*) from products where sku is not null and sku != ''"
            )
        ).scalar(),
    )
    print(
        "last",
        c.execute(
            text(
                "select id, name, last_synced_at from products order by id desc limit 3"
            )
        ).fetchall(),
    )
