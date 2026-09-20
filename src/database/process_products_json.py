import json
from pathlib import Path

from src.database.connection import get_connection
from src.database.repository import insert_records
from src.database.schema_manager import create_table
from src.database.schemas import JSON_SCHEMAS


def process_products(file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: "
            f"{file_path.resolve()}"
        )

    print("\n" + "=" * 60)
    print(f"Processando JSON: {file_path.name}")

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # PRICING PLANS
    pricing_schema = JSON_SCHEMAS["pricing_plans"]
    create_table(pricing_schema)
    pricing_records = []
    last_updated = data.get("last_updated")
    for plan_name, plan in data.get(
        "pricing_plans",
        {}
    ).items():
        pricing_records.append({
            "name": plan_name,
            "monthly_fee_brl":
                plan.get("monthly_fee_brl"),
            "included_terminals":
                plan.get("included_terminals"),
            "extra_terminal_fee_brl":
                plan.get("extra_terminal_fee_brl"),
            "description":
                plan.get("description"),
            "last_updated":
                last_updated,
        })

    # PRODUCTS
    products_schema = JSON_SCHEMAS["products"]
    create_table(products_schema)
    product_records = data.get(
        "products",
        []
    )

    # INSERT
    with get_connection() as conn:
        pricing_count = insert_records(
            conn,
            pricing_schema,
            pricing_records
        )
        product_count = insert_records(
            conn,
            products_schema,
            product_records
        )
        conn.commit()
    print(
        f"Planos processados: {pricing_count}"
    )
    print(
        f"Produtos processados: {product_count}"
    )