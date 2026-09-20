# Uma schema simplificada para passar para a LLM

DATABASE_SCHEMA = {
    "customers": {
        "description": "Clientes e informações comerciais.",
        "columns": [
            "customer_id",
            "company_name",
            "cnpj",
            "state",
            "city",
            "segment",
            "plan",
            "main_product",
            "mrr",
            "status",
            "contact_email"
        ],
        "foreign_keys": []
    },

    "employees": {
        "description": "Funcionários e informações profissionais.",
        "columns": [
            "id",
            "name",
            "email",
            "department",
            "role",
            "hire_date",
            "salary",
            "status"
        ],
        "foreign_keys": []
    },

    "sales": {
        "description": "Registro de vendas.",
        "columns": [
            "sale_id",
            "customer_id",
            "company_name",
            "store_id",
            "store_name",
            "state",
            "city",
            "product_id",
            "product_name",
            "date",
            "payment_method",
            "amount_brl",
            "pos_terminal",
            "status"
        ],
        "foreign_keys": []
    },

    "system_logs": {
        "description": "Logs, eventos e erros do sistema.",
        "columns": [
            "log_id",
            "timestamp",
            "level",
            "service",
            "module",
            "customer_id",
            "event",
            "error_code",
            "message"
        ],
        "foreign_keys": []
    },

    "pricing_plans": {
        "description": "Planos e preços.",
        "columns": [
            "name",
            "monthly_fee_brl",
            "included_terminals",
            "extra_terminal_fee_brl",
            "description",
            "last_updated"
        ],
        "foreign_keys": []
    },

    "products": {
        "description": "Produtos e suas características.",
        "columns": [
            "product_id",
            "name",
            "category",
            "description",
            "tech_lead",
            "product_manager",
            "standalone_monthly_price_brl",
            "pricing_by_plan",
            "features",
            "supported_os",
            "sla_uptime"
        ],
        "foreign_keys": []
    },

    "stores": {
        "description": "Lojas dos clientes.",
        "columns": [
            "store_id",
            "customer_id",
            "company_name",
            "store_name",
            "state",
            "city",
            "pos_terminals_count",
            "active_modules"
        ],
        "foreign_keys": []
    }
}