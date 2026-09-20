
import csv
from pathlib import Path

from src.database.connection import get_connection
from src.database.repository import insert_records
from src.database.schema_manager import create_table
from src.database.schemas import CSV_SCHEMAS


def process_csv(file_path):
    file_path = Path(file_path)
    schema_name = file_path.stem.lower()
    if schema_name not in CSV_SCHEMAS:
        raise ValueError(
            f"Schema não encontrado para: "
            f"{file_path.name}"
        )

    schema = CSV_SCHEMAS[schema_name]
    table_name = schema["table"]
    columns = schema["columns"]

    print("\n" + "=" * 60)
    print(f"Processando CSV: {file_path.name}")
    print(f"Tabela: {table_name}")

    # 1. LER CSV
    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)
        csv_columns = [
            column.strip()
            for column in reader.fieldnames or []
        ]

        if not csv_columns:
            raise ValueError(
                f"CSV sem cabeçalho: "
                f"{file_path.name}"
            )

        # 2. VALIDAR COLUNAS
        database_generated_columns = {
            "log_id"
        }
        required_csv_columns = [
            column
            for column in columns
            if column not in database_generated_columns
        ]
        missing_columns = (
            set(required_csv_columns)
            - set(csv_columns)
        )

        if missing_columns:
            raise ValueError(
                f"Colunas ausentes em "
                f"{file_path.name}: "
                f"{sorted(missing_columns)}"
            )

        # 3. LER REGISTROS
        rows = []

        for row in reader:
            cleaned_row = {}
            for column in csv_columns:
                if column not in columns:
                    continue
                value = row.get(column)
                if value == "":
                    value = None
                cleaned_row[column] = value
            rows.append(cleaned_row)
    print(
        f"Registros encontrados: {len(rows)}"
    )

    if not rows:
        print(
            "Nenhum registro para inserir."
        )
        return

    # 4. CRIAR TABELA
    create_table(schema)

    # 5. INSERIR REGISTROS
    with get_connection() as conn:

        count = insert_records(
            conn=conn,
            schema=schema,
            records=rows
        )
        conn.commit()
    print(
        f"✓ {count} registros processados "
        f"na tabela '{table_name}'."
    )



##### AQUI RODA, depois separar
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "src" / "data" / "structured"
DATA_DIR_SEMISTRUCTURE = PROJECT_ROOT / "src" / "data" / "semi_structured"

customers_path = DATA_DIR / "customers.csv"
employees_path = DATA_DIR / 'employees.csv'
sales_path = DATA_DIR / 'sales.csv'

systemlogs_path = DATA_DIR_SEMISTRUCTURE / 'system_logs.csv'

process_csv(
    systemlogs_path
)