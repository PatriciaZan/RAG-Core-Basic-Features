import json
from psycopg import sql

def insert_records(
    conn,
    schema,
    records,
):
    if not records:
        return 0

    table_name = schema["table"]
    columns = schema["columns"]
    conflict_key = schema.get("conflict_key")
    generated_columns = set(
        schema.get("generated_columns", [])
    )

    # COLUNAS DO INSERT
    insert_columns = [
        column
        for column in columns
        if column not in generated_columns
    ]

    column_identifiers = [
        sql.Identifier(column)
        for column in insert_columns
    ]

    placeholders = sql.SQL(", ").join(
        sql.Placeholder()
        for _ in insert_columns
    )

    # CONFLICT
    if conflict_key:
        update_columns = [
            column
            for column in insert_columns
            if column != conflict_key
        ]

        if update_columns:
            update_clause = sql.SQL(", ").join(
                sql.SQL("{} = EXCLUDED.{}").format(
                    sql.Identifier(column),
                    sql.Identifier(column)
                )
                for column in update_columns
            )
            conflict_clause = sql.SQL(
                "ON CONFLICT ({}) DO UPDATE SET {}"
            ).format(
                sql.Identifier(conflict_key),
                update_clause
            )

        else:
            conflict_clause = sql.SQL(
                "ON CONFLICT ({}) DO NOTHING"
            ).format(
                sql.Identifier(conflict_key)
            )

    else:
        conflict_clause = sql.SQL("")
        
    # INSERT QUERY
    insert_query = sql.SQL(
        """
        INSERT INTO {} ({})
        VALUES ({})
        {}
        """
    ).format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(
            column_identifiers
        ),
        placeholders,
        conflict_clause
    )

    # EXECUTAR
    count = 0

    with conn.cursor() as cursor:
        for record in records:
            values = []
            for column in insert_columns:
                value = record.get(column)
                column_type = (
                    columns[column]
                    .upper()
                    .strip()
                )
                if column_type == "JSONB":
                    value = json.dumps(
                        value,
                        ensure_ascii=False
                    )
                values.append(value)
            cursor.execute(
                insert_query,
                values
            )
            count += 1
    return count

