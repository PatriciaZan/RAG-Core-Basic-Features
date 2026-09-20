"""
Schema de banco de dados MELHORADO para passar para IA.
- Adiciona purpose e context
- Disambigua tabelas confundíveis
- Documenta relacionamentos
- Clarifica qual tabela usar em cada caso
"""

# IA AJUDOU MUITO AQUI!

# ============================================================================
# SCHEMA COM CONTEXTO E DISAMBIGUAÇÃO
DATABASE_SCHEMA = {
    "products": {
        "label": "[MASTER] Catálogo de Produtos",
        "description": "Catálogo MASTER de todos os produtos oferecidos.",
        "type": "Master Data / Dimension Table",
        "purpose": (
            "Fonte de verdade para informações de produtos. "
            "Cada linha = um produto único com suas características, preços e responsáveis."
        ),
        "primary_key": "product_id",

        "this_table_has": [
            "Nome oficial de cada produto",
            "Features e características técnicas",
            "Preços padrão e por plano",
            "Informações de suporte (SLA, OS suportados)",
            "Responsáveis técnicos e de negócio"
        ],

        "do_NOT_confuse_with": {
            "sales": (
                "SALES = histórico de cada venda que aconteceu (quando, quem comprou, quanto pagou). "
                "PRODUCTS = definição do produto em si (nome, features, preço). "
                "Sales tem snapshots old do produto_name; products tem a versão atual."
            ),
            "pricing_plans": (
                "PRICING_PLANS = planos de assinatura (Starter, Pro, Enterprise). "
                "PRODUCTS = produtos individuais que podem estar em vários planos com preços diferentes."
            )
        },

        "use_this_table_when_question_asks_about": [
            "o que é o produto X?",
            "características do produto",
            "features suportadas",
            "preço padrão",
            "responsável técnico / product manager",
            "quais produtos temos?",
            "descrição do produto",
            "SLA / uptime",
        ],

        "do_NOT_use_when_question_asks_about": [
            "quantas unidades vendidas",
            "receita gerada",
            "quem comprou",
            "quanto foi cobrado",
            "quando foi a venda",
            "histórico de vendas",
            "tendências de venda"
        ],

        "columns": {
            "product_id": {
                "description": "ID único do produto (chave primária)",
                "type": "VARCHAR(50)",
                "examples": ["prod_001", "payment-gateway"]
            },
            "name": {
                "description": "Nome oficial do produto no catálogo ATUAL",
                "type": "VARCHAR(150)",
                "note": "Esta é a versão ATUAL. Em SALES, o product_name pode estar desatualizado."
            },
            "category": {
                "description": "Categoria/tipo do produto",
                "type": "VARCHAR(150)",
                "examples": ["Payment Processing", "Analytics", "Compliance"]
            },
            "description": {
                "description": "Descrição detalhada do produto",
                "type": "TEXT"
            },
            "tech_lead": {
                "description": "Responsável técnico (quem cuida da engineering)",
                "type": "VARCHAR(100)"
            },
            "product_manager": {
                "description": "Responsável de negócio (Product Manager)",
                "type": "VARCHAR(100)"
            },
            "standalone_monthly_price_brl": {
                "description": "Preço mensal quando vendido SOZINHO (não em plano)",
                "type": "NUMERIC(10,2)",
                "note": "Quando em um plano, o preço pode ser diferente (ver pricing_by_plan)"
            },
            "pricing_by_plan": {
                "description": "Preço deste produto EM CADA PLANO (Starter, Pro, Enterprise) - JSON",
                "type": "JSONB",
                "example": '{"starter": 500, "professional": 1200, "enterprise": null}'
            },
            "features": {
                "description": "Lista de features/funcionalidades suportadas - JSON",
                "type": "JSONB",
                "example": '["api", "webhook", "realtime", "export"]'
            },
            "supported_os": {
                "description": "Sistemas operacionais suportados - JSON",
                "type": "JSONB",
                "example": '["windows", "macos", "linux"]'
            },
            "sla_uptime": {
                "description": "Garantia de uptime (ex: 99.9%)",
                "type": "VARCHAR(20)",
                "example": "99.95%"
            }
        },
        "foreign_keys": []
    },

    # ========================================================================
    "sales": {
        "label": "[TRANSAÇÃO] Histórico de Vendas",
        "description": "Registro de cada VENDA que aconteceu: quem comprou, o quê, quando, por quanto.",
        "type": "Fact Table / Event Log / Transactional",
        "purpose": (
            "Log completo de transações. "
            "Cada linha = uma venda real que ocorreu. "
            "Use para análise de vendas, receita, tendências."
        ),
        "primary_key": "sale_id",

        "this_table_has": [
            "Cada transação de venda que aconteceu",
            "Quem comprou (customer_id)",
            "O que foi vendido (product_id)",
            "Quando foi vendido (date)",
            "Quanto foi cobrado (amount_brl)",
            "Onde foi vendido (store_id)"
        ],

        "important_notes": [
            "product_name aqui é um SNAPSHOT do momento da venda (pode estar desatualizado)",
            "Para informações ATUAIS do produto, JOIN com tabela PRODUCTS",
            "Cada linha = UMA VENDA, não é agregado"
        ],

        "do_NOT_confuse_with": {
            "products": (
                "PRODUCTS = catálogo (o que PODE ser vendido). "
                "SALES = histórico (o que FOI vendido). "
                "Products sem vendas ainda aparecem em PRODUCTS mas não em SALES."
            ),
            "customers": (
                "CUSTOMERS = cadastro de clientes (dados mestres). "
                "SALES = cada compra que um cliente fez. "
                "Um cliente pode ter 0, 1 ou muitas linhas em SALES."
            )
        },

        "use_this_table_when_question_asks_about": [
            "quantas unidades/vendas",
            "receita total / valor vendido",
            "histórico de vendas",
            "quem comprou",
            "quando foi vendido",
            "tendências de venda",
            "top selling products",
            "performance de vendas"
        ],

        "do_NOT_use_when_question_asks_about": [
            "características do produto",
            "features do produto",
            "preço padrão",
            "informações técnicas",
            "quem é o tech lead",
            "qual é o SLA"
        ],

        "columns": {
            "sale_id": {
                "description": "ID único da transação",
                "type": "TEXT",
                "note": "Chave primária - cada venda tem um ID único"
            },
            "customer_id": {
                "description": "ID do cliente que comprou",
                "type": "TEXT",
                "relation": "FOREIGN KEY → customers.customer_id"
            },
            "product_id": {
                "description": "ID do produto que foi vendido",
                "type": "TEXT",
                "relation": "FOREIGN KEY → products.product_id",
                "note": "Para dados ATUAIS do produto, JOIN com PRODUCTS"
            },
            "product_name": {
                "description": "Nome do produto NO MOMENTO DA VENDA (snapshot, pode estar desatualizado)",
                "type": "TEXT",
                "warning": "Esta é a versão antiga. Para nome atual, use products.name"
            },
            "store_id": {
                "description": "ID da loja onde a venda aconteceu",
                "type": "TEXT",
                "relation": "FOREIGN KEY → stores.store_id"
            },
            "store_name": {
                "description": "Nome da loja",
                "type": "TEXT"
            },
            "date": {
                "description": "Data e hora QUANDO a venda foi realizada",
                "type": "TIMESTAMP"
            },
            "amount_brl": {
                "description": "Valor cobrado na venda (em BRL)",
                "type": "NUMERIC(12,2)"
            },
            "payment_method": {
                "description": "Método de pagamento usado",
                "type": "TEXT",
                "examples": ["credit_card", "debit", "pix", "bank_transfer"]
            },
            "status": {
                "description": "Status da venda",
                "type": "TEXT",
                "examples": ["completed", "pending", "cancelled"]
            }
        },
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
            },
            {
                "column": "store_id",
                "references_table": "stores",
                "references_column": "store_id"
            }
        ]
    },

    # ========================================================================

    "customers": {
        "label": "[REGISTRO] Cadastro de Clientes",
        "description": "Dados mestres de cada cliente/empresa.",
        "type": "Master Data / Dimension Table",
        "purpose": (
            "Fonte de verdade para informações de clientes. "
            "Cada linha = uma empresa cliente com seus dados (nome, CNPJ, localização, plano)."
        ),
        "primary_key": "customer_id",

        "use_this_table_when_question_asks_about": [
            "informações do cliente",
            "empresas cadastradas",
            "CNPJ",
            "segmento de mercado",
            "MRR (receita mensal do cliente)",
            "contato do cliente",
            "localização do cliente"
        ],

        "columns": {
            "customer_id": {
                "description": "ID único do cliente (chave primária)",
                "type": "TEXT"
            },
            "company_name": {
                "description": "Nome da empresa cliente",
                "type": "TEXT"
            },
            "cnpj": {
                "description": "CNPJ da empresa",
                "type": "TEXT"
            },
            "state": {
                "description": "Estado onde cliente está localizado",
                "type": "CHAR(2)",
                "example": "SP"
            },
            "city": {
                "description": "Cidade",
                "type": "TEXT"
            },
            "segment": {
                "description": "Segmento de mercado do cliente",
                "type": "TEXT",
                "examples": ["Retail", "Finance", "Healthcare", "Tech"]
            },
            "plan": {
                "description": "Plano contratado (Starter, Pro, Enterprise)",
                "type": "TEXT"
            },
            "main_product": {
                "description": "Produto principal que cliente usa",
                "type": "TEXT"
            },
            "mrr": {
                "description": "Monthly Recurring Revenue (receita mensal do cliente)",
                "type": "NUMERIC(12,2)"
            },
            "status": {
                "description": "Status do cliente (ativo, inativo, suspenso)",
                "type": "TEXT"
            },
            "contact_email": {
                "description": "Email de contato principal",
                "type": "TEXT"
            }
        },
        "foreign_keys": []
    },

    # ========================================================================
    "stores": {
        "label": "[LOCALIZAÇÃO] Lojas/Unidades de Clientes",
        "description": "Unidades físicas/lojas que os clientes possuem.",
        "type": "Master Data / Dimension Table",
        "purpose": (
            "Rastreia onde cada cliente tem presença física. "
            "Uma empresa cliente pode ter múltiplas lojas/filiais."
        ),
        "primary_key": "store_id",

        "use_this_table_when_question_asks_about": [
            "lojas de um cliente",
            "quantas filiais",
            "localização das lojas",
            "terminais POS"
        ],

        "columns": {
            "store_id": {
                "description": "ID único da loja",
                "type": "VARCHAR(50)"
            },
            "customer_id": {
                "description": "Qual cliente é DONO dessa loja",
                "type": "VARCHAR(50)",
                "relation": "FOREIGN KEY → customers.customer_id"
            },
            "company_name": {
                "description": "Nome da empresa dona (desnormalizado)",
                "type": "VARCHAR(200)"
            },
            "store_name": {
                "description": "Nome/ID da loja específica",
                "type": "VARCHAR(200)"
            },
            "state": {
                "description": "Estado da loja",
                "type": "VARCHAR(2)"
            },
            "city": {
                "description": "Cidade da loja",
                "type": "VARCHAR(100)"
            },
            "pos_terminals_count": {
                "description": "Quantos terminais POS essa loja tem",
                "type": "INTEGER"
            },
            "active_modules": {
                "description": "Módulos/produtos ativos nessa loja - JSON",
                "type": "JSONB",
                "example": '["payment", "analytics", "loyalty"]'
            }
        },
        "foreign_keys": [
            {
                "column": "customer_id",
                "references_table": "customers",
                "references_column": "customer_id"
            }
        ]
    },

    # ========================================================================
    "pricing_plans": {
        "label": "[PLANOS] Planos de Assinatura",
        "description": "Planos/pacotes de cobrança (Starter, Professional, Enterprise).",
        "type": "Master Data / Configuration",
        "purpose": (
            "Define os planos disponíveis, seus valores e o que cada um inclui. "
            "É a 'configuração' de how much you charge. "
            "Não é sobre PRODUTOS específicos (ver products)."
        ),
        "primary_key": "name",

        "important_notes": [
            "PRICING_PLANS = modelos de cobrança (pacotes de preço)",
            "PRODUCTS = produtos individuais",
            "Um produto pode estar disponível em múltiplos planos com preços diferentes",
            "Ver products.pricing_by_plan para saber preço de cada produto em cada plano"
        ],

        "do_NOT_confuse_with": {
            "products": (
                "PRICING_PLANS = Starter, Professional, Enterprise (modelos de cobrança). "
                "PRODUCTS = Payment Gateway, Analytics, etc (produtos). "
                "Cada cliente escolhe UM plano. Cada plano inclui múltiplos produtos."
            )
        },

        "use_this_table_when_question_asks_about": [
            "quais planos temos",
            "preço do plano",
            "quantos terminais incluem",
            "o que cada plano inclui"
        ],

        "columns": {
            "name": {
                "description": "Nome do plano (Starter, Professional, Enterprise)",
                "type": "VARCHAR(50)"
            },
            "monthly_fee_brl": {
                "description": "Valor mensal do plano base",
                "type": "NUMERIC(10,2)"
            },
            "included_terminals": {
                "description": "Quantos terminais POS estão inclusos neste plano",
                "type": "INTEGER"
            },
            "extra_terminal_fee_brl": {
                "description": "Valor cobrado por terminal adicional além dos inclusos",
                "type": "NUMERIC(10,2)"
            },
            "description": {
                "description": "Descrição do plano",
                "type": "TEXT"
            },
            "last_updated": {
                "description": "Última vez que este plano foi modificado",
                "type": "DATE"
            }
        },
        "foreign_keys": []
    },

    # ========================================================================
    "employees": {
        "label": "[RH] Funcionários Internos",
        "description": "Folha de pessoal da sua empresa (não clientes).",
        "type": "Master Data / Configuration",
        "purpose": (
            "Dados de cada funcionário da sua empresa: RH, departamento, cargo, salário."
        ),
        "primary_key": "id",

        "use_this_table_when_question_asks_about": [
            "funcionários",
            "equipes",
            "departamentos",
            "salários",
            "quem é o tech lead de X (buscar em PRODUCTS primeiro)"
        ],

        "columns": {
            "id": {
                "description": "ID do funcionário",
                "type": "TEXT"
            },
            "name": {
                "description": "Nome completo",
                "type": "TEXT"
            },
            "email": {
                "description": "Email corporativo",
                "type": "TEXT"
            },
            "department": {
                "description": "Departamento (Engineering, Sales, etc)",
                "type": "TEXT"
            },
            "role": {
                "description": "Cargo (Engineer, Manager, etc)",
                "type": "TEXT"
            },
            "hire_date": {
                "description": "Data de contratação",
                "type": "DATE"
            },
            "salary": {
                "description": "Salário mensal",
                "type": "NUMERIC(12,2)"
            },
            "status": {
                "description": "Status (ativo, inativo, licença)",
                "type": "TEXT"
            }
        },
        "foreign_keys": []
    },

    # ========================================================================

    "system_logs": {
        "label": "[LOGS] Eventos/Logs do Sistema",
        "description": "Auditoria técnica: eventos, erros, debug do sistema.",
        "type": "Fact Table / Event Log",
        "purpose": (
            "Rastreamento técnico de tudo que acontece no sistema. "
            "Para debugging, auditoria, troubleshooting."
        ),
        "primary_key": "log_id",

        "use_this_table_when_question_asks_about": [
            "erros do sistema",
            "eventos técnicos",
            "auditoria",
            "logs"
        ],

        "columns": {
            "log_id": {
                "description": "ID único do log (auto-gerado)",
                "type": "SERIAL"
            },
            "timestamp": {
                "description": "Quando o evento aconteceu",
                "type": "TIMESTAMP"
            },
            "level": {
                "description": "Severidade: DEBUG, INFO, WARNING, ERROR, CRITICAL",
                "type": "VARCHAR(20)"
            },
            "service": {
                "description": "Qual serviço/módulo gerou o log",
                "type": "VARCHAR(100)"
            },
            "module": {
                "description": "Qual módulo específico",
                "type": "VARCHAR(100)"
            },
            "customer_id": {
                "description": "ID do cliente afetado (se aplicável)",
                "type": "VARCHAR(50)"
            },
            "event": {
                "description": "Tipo de evento",
                "type": "VARCHAR(100)"
            },
            "error_code": {
                "description": "Código de erro (se for erro)",
                "type": "VARCHAR(50)"
            },
            "message": {
                "description": "Mensagem descritiva",
                "type": "TEXT"
            }
        },
        "foreign_keys": []
    }
}

# ============================================================================
# RELACIONAMENTOS EXPLÍCITOS
DATABASE_RELATIONSHIPS = {
    "products": {
        "is_master_for": ["Definição de produto, features, preços"],
        "is_referenced_by": ["sales (histórico de vendas)", "pricing_plans (preços por plano)"],
        "foreign_keys_to": []
    },

    "sales": {
        "is_log_of": ["Cada transação de venda"],
        "references": {
            "product_id": "products",
            "customer_id": "customers",
            "store_id": "stores"
        }
    },

    "customers": {
        "is_master_for": ["Dados de cliente/empresa"],
        "is_referenced_by": ["sales", "stores"],
        "foreign_keys_to": []
    },

    "stores": {
        "is_child_of": "customers",
        "references": {
            "customer_id": "customers"
        }
    },

    "pricing_plans": {
        "is_configuration_for": ["Modelos de cobrança"],
        "is_referenced_by": ["products (pricing_by_plan)"]
    }
}
#============================================================================================
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

# ============================================================================
# QUICK REFERENCE: Qual tabela usar?
# ============================================================================

DISAMBIGUATION_GUIDE = {
    "Pergunta sobre O QUE é o produto": "products",
    "Pergunta sobre QUANTAS VENDAS": "sales",
    "Pergunta sobre QUEM COMPROU": "sales + customers",
    "Pergunta sobre CARACTERÍSTICAS DO PRODUTO": "products",
    "Pergunta sobre RECEITA / VALORES VENDIDOS": "sales",
    "Pergunta sobre CLIENTE": "customers",
    "Pergunta sobre LOJAS": "stores",
    "Pergunta sobre PLANOS": "pricing_plans",
    "Pergunta sobre FUNCIONÁRIOS": "employees",
    "Pergunta sobre ERROS/LOGS": "system_logs",
}
