
from psycopg import sql
from src.database.connection import get_connection

def create_table(schema):
    table_name = schema["table"]
    columns = schema["columns"]
    primary_key = schema.get("primary_key")
    foreign_keys = schema.get("foreign_keys", [])

    print(f"Verificando tabela: {table_name}")

    column_definitions = [
        sql.SQL("{} {}").format(
            sql.Identifier(column),
            sql.SQL(definition)
        )
        for column, definition in columns.items()
    ]

    # Primary key
    if primary_key:
        column_definitions.append(
            sql.SQL("PRIMARY KEY ({})").format(
                sql.Identifier(primary_key)
            )
        )

    # Foreign keys
    foreign_key_definitions = [
        sql.SQL(fk)
        for fk in foreign_keys
    ]

    create_table_query = sql.SQL(
        "CREATE TABLE IF NOT EXISTS {} ({})"
    ).format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(
            column_definitions
            + foreign_key_definitions
        )
    )

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
        conn.commit()

    print(
        f"✓ Tabela '{table_name}' verificada/criada."
    )


