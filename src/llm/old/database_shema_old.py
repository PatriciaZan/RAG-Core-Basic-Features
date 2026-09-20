# IA Ajudou em tudo neste arquivo

DATABASE_SCHEMA = {

    "customers": {
        "description": "Clientes e informações comerciais.",
        "table": "customers",

        "columns": {
            "customer_id": "TEXT",
            "company_name": "TEXT",
            "cnpj": "TEXT",
            "state": "CHAR(2)",
            "city": "TEXT",
            "segment": "TEXT",
            "plan": "TEXT",
            "main_product": "TEXT",
            "mrr": "NUMERIC(12,2)",
            "status": "TEXT",
            "contact_email": "TEXT"
        },
        "primary_key": "customer_id",
        "foreign_keys": []
    },

    "employees": {
        "description": "Funcionários e informações profissionais.",
        "table": "employees",

        "columns": {
            "id": "TEXT",
            "name": "TEXT",
            "email": "TEXT",
            "department": "TEXT",
            "role": "TEXT",
            "hire_date": "DATE",
            "salary": "NUMERIC(12,2)",
            "status": "TEXT"
        },
        "primary_key": "id",
        "foreign_keys": []
    },

    "sales": {
        "description": "Vendas e informações de pagamento.",
        "table": "sales",

        "columns": {
            "sale_id": "TEXT",
            "customer_id": "TEXT",
            "company_name": "TEXT",
            "store_id": "TEXT",
            "store_name": "TEXT",
            "state": "CHAR(2)",
            "city": "TEXT",
            "product_id": "TEXT",
            "product_name": "TEXT",
            "date": "TIMESTAMP",
            "payment_method": "TEXT",
            "amount_brl": "NUMERIC(12,2)",
            "pos_terminal": "TEXT",
            "status": "TEXT"
        },
        "primary_key": "sale_id",
        "foreign_keys": [
            {
                "column": "customer_id",
                "references_table": "customers",
                "references_column": "customer_id"
            },
            {
                "column": "product_id",
                "references_table": "products",
                "references_column": "product_id"
            }
        ]
    },

    "system_logs": {
        "description": "Logs, eventos e erros dos sistemas.",
        "table": "system_logs",

        "columns": {
            "log_id": "SERIAL",
            "timestamp": "TIMESTAMP",
            "level": "VARCHAR(20)",
            "service": "VARCHAR(100)",
            "module": "VARCHAR(100)",
            "customer_id": "VARCHAR(50)",
            "event": "VARCHAR(100)",
            "error_code": "VARCHAR(50)",
            "message": "TEXT"
        },

        "primary_key": "log_id",
        "foreign_keys": [
            {
                "column": "customer_id",
                "references_table": "customers",
                "references_column": "customer_id"
            }
        ]
    },

    "pricing_plans": {
        "description": "Planos comerciais e seus preços.",
        "table": "pricing_plans",

        "columns": {
            "name": "VARCHAR(50)",
            "monthly_fee_brl": "NUMERIC(10,2)",
            "included_terminals": "INTEGER",
            "extra_terminal_fee_brl": "NUMERIC(10,2)",
            "description": "TEXT",
            "last_updated": "DATE"
        },
        "primary_key": "name",
        "foreign_keys": []
    },

    "products": {
        "description": "Produtos, funcionalidades e preços.",
        "table": "products",

        "columns": {
            "product_id": "VARCHAR(50)",
            "name": "VARCHAR(150)",
            "category": "VARCHAR(150)",
            "description": "TEXT",
            "tech_lead": "VARCHAR(100)",
            "product_manager": "VARCHAR(100)",
            "standalone_monthly_price_brl": "NUMERIC(10,2)",
            "pricing_by_plan": "JSONB",
            "features": "JSONB",
            "supported_os": "JSONB",
            "sla_uptime": "VARCHAR(20)"
        },
        "primary_key": "product_id",
        "foreign_keys": []
    },

    "stores": {
        "description": "Lojas dos clientes, terminais e módulos.",
        "table": "stores",

        "columns": {
            "store_id": "VARCHAR(50)",
            "customer_id": "VARCHAR(50)",
            "company_name": "VARCHAR(200)",
            "store_name": "VARCHAR(200)",
            "state": "VARCHAR(2)",
            "city": "VARCHAR(100)",
            "pos_terminals_count": "INTEGER",
            "active_modules": "JSONB"
        },
        "primary_key": "store_id",
        "foreign_keys": [
            {
                "column": "customer_id",
                "references_table": "customers",
                "references_column": "customer_id"
            }
        ]
    }
}

VALID_ROUTES = {
    "postgresql",
    "faiss",
    "both"
}

VALID_OPERATIONS = {
    "select",
    "count",
    "aggregate"
}

VALID_AGGREGATIONS = {
    "sum",
    "avg",
    "min",
    "max"
}

TABLE_ALIASES = {
    "customers": "c",
    "employees": "e",
    "sales": "s",
    "system_logs": "sl",
    "pricing_plans": "pp",
    "products": "p",
    "stores": "st",
}

ALLOWED_OPERATORS = {
    "=",
    "!=",
    ">",
    "<",
    ">=",
    "<=",
    "IN",
    "NOT IN",
    "LIKE",
    "ILIKE",
    "BETWEEN",
    "IS NULL",
    "IS NOT NULL"
}

SPECIAL_FILTERS = {
    "month",
    "year",
    "date_start",
    "date_end"
}


def get_schema_for_prompt() -> str:
    """
    Converte o catálogo do banco em um texto compacto
    para ser enviado ao Query Analyzer.
    """

    lines = []
    for table_name, table_info in DATABASE_SCHEMA.items():
        lines.append(
            f"TABELA: {table_name}"
        )
        lines.append(
            f"DESCRIÇÃO: {table_info['description']}"
        )
        columns = ", ".join(
            table_info["columns"].keys()
        )
        lines.append(
            f"COLUNAS: {columns}"
        )
        lines.append("")
    return "\n".join(lines)