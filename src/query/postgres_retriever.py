import os
from typing import Any

import psycopg
from dotenv import load_dotenv

from src.query.query_builder import QueryBuilder
from src.query.query_permissions import PostgresPermissionGuard

load_dotenv()

class PostgresRetriever:

    def __init__(self, query_builder=None, permission_guard=None):
        self.query_builder = (
            query_builder
            or QueryBuilder()
        )

        self.permission_guard = (
            permission_guard
            or PostgresPermissionGuard()
        )

        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente.")

    def retrieve(self, plan, permission_level: str):
        # Verifica a permissão
        self.permission_guard.validate(permission_level)
        
        # 1. Gera SQL através do Builder
        sql, params = (self.query_builder.build(plan))

        # 2. Executa consulta
        try:
            with psycopg.connect(self.database_url) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql,
                        params
                    )
                    rows = cursor.fetchall()
                    columns = [
                        description.name
                        for description in cursor.description
                    ]

        except psycopg.Error as e:
            raise RuntimeError("Erro ao executar consulta no PostgreSQL.") from e

        # 3. Converte resultado
        formatted_rows = [
            dict(zip(columns, row))
            for row in rows
        ]
        return {
            "source": "postgresql",
            "row_count": len(
                formatted_rows
            ),
            "columns": columns,
            "rows": formatted_rows
        }