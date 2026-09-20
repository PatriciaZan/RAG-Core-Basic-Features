from pathlib import Path

from src.database.process_products_json import process_products
from src.database.process_stores_json import process_stores

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    PROJECT_ROOT
    / "src"
    / "data"
    / "structured"
)


def main():
    print("\n" + "=" * 60)
    print("PROCESSAMENTO DE JSON")
    print("=" * 60)
    products_path = DATA_DIR / "products.json"
    stores_path = DATA_DIR / "stores.json"
    process_products(products_path)
    process_stores(stores_path)
    print("\n" + "=" * 60)
    print("PROCESSAMENTO FINALIZADO")
    print("=" * 60)

if __name__ == "__main__":
    main()