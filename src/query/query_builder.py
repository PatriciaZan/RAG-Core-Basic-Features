# PostgresPlan => SQL + parâmetros

from typing import Any

from src.query.models import PostgresPlan
from src.database.database_schema import DATABASE_SCHEMA, TABLE_ALIASES, ALLOWED_OPERATORS


class QueryBuilder:
    def build(self, plan: PostgresPlan):
        """
        Converte um PostgresPlan em SQL parametrizado. A LLM nunca fornece SQL diretamente.
        """

        if not plan.tables:
            raise ValueError("Nenhuma tabela foi informada no PostgresPlan.")

        self._validate_tables(plan.tables)

        if plan.operation == "count":
            return self._build_count(plan)

        if plan.operation == "aggregate":
            return self._build_aggregate(plan)

        if plan.operation == "select":
            return self._build_select(plan)

        raise ValueError(
            f"Operação PostgreSQL não suportada: "
            f"{plan.operation}"
        )

    def _build_select(self, plan: PostgresPlan):
        tables = plan.tables

        from_clause = self._build_from_clause(tables )
        fields = self._build_select_fields(plan)

        sql = f"""
            SELECT {fields}
            {from_clause}
        """

        sql, params = self._apply_filters(
            sql,
            plan.filters,
            plan.tables
        )

        sql += ";"
        return sql, params

    def _build_select_fields(
            self,
            plan: PostgresPlan
    ):
        if plan.fields:

            fields = []
            for field in plan.fields:
                alias, column = (
                    self._resolve_column(
                        field,
                        plan.tables
                    )
                )
                fields.append(f"{alias}.{column}")
            return ", ".join(fields)

        # Caso a LLM ainda não esteja enviando fields, usamos todas as colunas.
        fields = []

        for table in plan.tables:
            alias = TABLE_ALIASES[table]
            for column in DATABASE_SCHEMA[
                table
            ]["columns"]:
                fields.append(
                    f"{alias}.{column}"
                )
        return ", ".join(fields)

    def _build_count(
        self,
        plan: PostgresPlan
    ):
        from_clause = self._build_from_clause(plan.tables)
        sql = f"""
                SELECT COUNT(*) AS total
                {from_clause}
            """
        sql, params = self._apply_filters(
            sql,
            plan.filters,
            plan.tables
        )
        sql += ";"
        return sql, params

    def _build_aggregate(
            self,
            plan: PostgresPlan
    ):
        if not plan.aggregation:
            raise ValueError("Aggregation não informada.")
        if not plan.field:
            raise ValueError("Campo da agregação não informado.")

        allowed_aggregations = {
            "sum": "SUM",
            "avg": "AVG",
            "min": "MIN",
            "max": "MAX"
        }
        aggregation = (plan.aggregation.lower())

        if aggregation not in allowed_aggregations:
            raise ValueError(
                f"Agregação não permitida: "
                f"{aggregation}"
            )

        alias, column = self._resolve_column(
            plan.field,
            plan.tables
        )
        from_clause = self._build_from_clause(plan.tables)
        sql = f"""
            SELECT
                {allowed_aggregations[aggregation]}
                ({alias}.{column}) AS result
            {from_clause}
        """
        sql, params = self._apply_filters(
            sql,
            plan.filters,
            plan.tables
        )
        sql += ";"
        return sql, params

    def _apply_filters(
            self,
            sql: str,
            filters: dict[str, Any],
            tables: list[str]
    ):
        if not filters:
            return sql, []
        conditions = []
        params = []

        for field, definition in filters.items():

            # Filtros especiais
            if field in {
                "month",
                "year",
                "date_start",
                "date_end"
            }:
                condition, condition_params = (
                    self._build_special_filter(
                        field,
                        definition,
                        tables
                    )
                )
                conditions.append(condition)
                params.extend(condition_params)
                continue


            # Resolve e valida a coluna
            alias, column = self._resolve_column(
                field,
                tables
            )

            # Operador e valor
            operator = "="
            value = definition

            if isinstance(definition, dict):
                operator = definition.get(
                    "operator",
                    "="
                ).upper()

                value = definition.get("value")

            # Constrói condição
            condition, condition_params = (
                self._build_condition(
                    alias,
                    column,
                    operator,
                    value
                )
            )
            conditions.append(condition)
            params.extend(condition_params)

        if conditions:
            sql += "\nWHERE "
            sql += "\nAND ".join(conditions)
        return sql, params


    def _build_special_filter(
        self,
        field: str,
        value: Any,
        tables: list[str]
    ):
        date_tables = []
        for table in tables:
            if "date" in DATABASE_SCHEMA[
                table
            ]["columns"]:
                date_tables.append(table)
        if not date_tables:
            raise ValueError("Nenhuma das tabelas possui uma coluna 'date'.")
        if len(date_tables) > 1:
            raise ValueError("O filtro de data é ambíguo. Mais de uma tabela possui a coluna 'date'.")

        table = date_tables[0]
        alias = TABLE_ALIASES[table]
        date_column = f"{alias}.date"

        if field == "month":
            return (
                f"EXTRACT(MONTH FROM {date_column}) = %s",
                [value]
            )
        if field == "year":
            return (
                f"EXTRACT(YEAR FROM {date_column}) = %s",
                [value]
            )
        if field == "date_start":
            return (
                f"{date_column} >= %s",
                [value]
            )
        if field == "date_end":
            return (
                f"{date_column} <= %s",
                [value]
            )
        raise ValueError(f"Filtro especial não suportado: {field}")


    def _validate_tables(
            self,
            tables: list[str]
    ):
        for table in tables:
            if table not in DATABASE_SCHEMA:
                raise ValueError(f"Tabela não permitida: {table}")

    def _validate_field(
            self,
            table: str,
            field: str
    ):
        valid_fields = (DATABASE_SCHEMA[table]["columns"])

        if field not in valid_fields:
            raise ValueError(
                f"Campo '{field}' não existe "
                f"na tabela '{table}'."
            )

    def _build_from_clause(
            self,
            tables: list[str]
    ):
        if not tables:
            raise ValueError("Nenhuma tabela informada.")

        if len(tables) == 1:
            return tables[0]

        first_table = tables[0]
        first_alias = TABLE_ALIASES[first_table]

        sql = (
            f"FROM {first_table} "
            f"AS {first_alias}"
        )

        joined_tables = {first_table}
        remaining_tables = set(tables[1:])

        while remaining_tables:
            joined = False
            for table in list(remaining_tables):
                relationship = self._find_relationship(
                    table,
                    joined_tables
                )

                if not relationship:
                    continue

                source_table = relationship["source_table"]
                source_column = relationship["source_column"]
                target_table = relationship["target_table"]
                target_column = relationship["target_column"]


                # Descobre qual tabela está sendo adicionada ao JOIN
                if source_table in joined_tables:
                    join_table = target_table
                    join_alias = TABLE_ALIASES[target_table]
                    left_alias = TABLE_ALIASES[source_table]
                    left_column = source_column
                    right_alias = join_alias
                    right_column = target_column
                else:
                    join_table = source_table
                    join_alias = TABLE_ALIASES[source_table]
                    left_alias = TABLE_ALIASES[target_table]
                    left_column = target_column
                    right_alias = join_alias
                    right_column = source_column

                # Segurança
                if join_table not in remaining_tables:
                    continue

                sql += (
                    f"\nJOIN {join_table} "
                    f"AS {join_alias} "
                    f"ON {left_alias}.{left_column} "
                    f"= {right_alias}.{right_column}"
                )

                joined_tables.add(join_table)
                remaining_tables.remove(join_table)

                joined = True
                break

            if not joined:
                raise ValueError("Não foi possível encontrar relacionamentos entre as tabelas: "f"{remaining_tables}")
        return sql

    def _find_relationship(
            self,
            table: str,
            existing_tables: set[str]
    ):
        # Caso a tabela nova tenha FK
        #for fk in DATABASE_SCHEMA[table]["foreign_keys"]:
        for fk in DATABASE_SCHEMA[table].get("foreign_keys", []):

            if fk["references_table"] in existing_tables:
                return {
                    "source_table": table,
                    "source_column": fk["column"],
                    "target_table": fk["references_table"],
                    "target_column": fk["references_column"]
                }

        # Caso alguma tabela existente tenha FK
        for existing_table in existing_tables:

            #for fk in DATABASE_SCHEMA[existing_table]["foreign_keys"]:
            for fk in DATABASE_SCHEMA[existing_table].get("foreign_keys", []):
                if fk["references_table"] == table:
                    return {
                        "source_table": existing_table,
                        "source_column": fk["column"],
                        "target_table": table,
                        "target_column": fk["references_column"]
                    }
        return None

    def _resolve_column(
            self,
            field: str,
            tables: list[str]
    ):
        if "." in field:
            table, column = field.split(
                ".",
                1
            )
            if table not in tables:
                raise ValueError( f"Tabela '{table}' não está na consulta.")
            if column not in DATABASE_SCHEMA[
                table
            ]["columns"]:
                raise ValueError(f"Campo '{column}' não existe em '{table}'.")
            return (
                TABLE_ALIASES[table],
                column
            )

        matches = []

        for table in tables:
            if field in DATABASE_SCHEMA[
                table
            ]["columns"]:
                matches.append(table)
        if len(matches) == 0:
            raise ValueError(f"Campo '{field}' não encontrado.")

        if len(matches) > 1:
            raise ValueError(f"Campo '{field}' é ambíguo. Especifique a tabela.")

        table = matches[0]
        return (
            TABLE_ALIASES[table],
            field
        )

    def _build_filters(
            self,
            filters: dict,
            tables: list[str]
    ):
        if not filters:
            return "", []

        conditions = []
        params = []

        for field, definition in filters.items():
            alias, column = self._resolve_column(
                field,
                tables
            )

            operator = "="
            value = definition

            if isinstance(
                    definition,
                    dict
            ):
                operator = definition.get(
                    "operator",
                    "="
                ).upper()

                value = definition.get("value")

            if operator not in ALLOWED_OPERATORS:
                raise ValueError(f"Operador não permitido: {operator}")

            condition, condition_params = (
                self._build_condition(
                    alias,
                    column,
                    operator,
                    value
                )
            )
            conditions.append(condition)
            params.extend(condition_params)

        return ("WHERE " + "\nAND ".join(conditions),params)

    def _build_condition(
            self,
            alias: str,
            column: str,
            operator: str,
            value
    ):
        qualified_column = f"{alias}.{column}"

        if operator in {
            "IS NULL",
            "IS NOT NULL"
        }:
            return f"{qualified_column} {operator}",[]

        if operator in {
            "IN",
            "NOT IN"
        }:

            if not isinstance(
                    value,
                    (list, tuple)
            ):
                raise ValueError(f"{operator} exige uma lista.")

            if not value:
                raise ValueError(f"{operator} não pode receber uma lista vazia.")

            placeholders = ", ".join(["%s"] * len(value))

            return (
                f"{qualified_column} "
                f"{operator} ({placeholders})",
                list(value)
            )

        if operator == "BETWEEN":

            if not isinstance(
                    value,
                    (list, tuple)
            ) or len(value) != 2:
                raise ValueError("BETWEEN exige exatamente dois valores.")

            return (
                f"{qualified_column} "
                f"BETWEEN %s AND %s",
                [value[0], value[1]]
            )

        return (
            f"{qualified_column} "
            f"{operator} %s",
            [value]
        )