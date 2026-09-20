from src.query.postgres_retriever import PostgresRetriever
from src.query.models import PostgresPlan

retriever = PostgresRetriever()
plan = PostgresPlan(
    tables=["customers"],

    fields=[
        "customers.company_name",
        "customers.state",
        "customers.status"
    ],

    filters={
        "customers.company_name": {
            "operator": "=",
            "value": "Supermercado Boa Compra"
        }
    },
    operation="select"
)

permissions = [
    "publico",
    "interno",
    "restrito"
]


for permission in permissions:
    print("=" * 60)
    print(f"PERMISSÃO: {permission}")
    print("=" * 60)

    try:
        result = retriever.retrieve(
            plan,
            permission
        )

        print("✓ ACESSO PERMITIDO")
        print(
            f"Registros: "
            f"{result['row_count']}"
        )

        for row in result["rows"]:
            print(row)

    except Exception as exc:
        print("✗ ACESSO NEGADO")
        print(exc)