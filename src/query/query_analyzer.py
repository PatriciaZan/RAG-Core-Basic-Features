# MUITA Tentativa e erro (06/09/26)
# AJUDA DA IA para escrever o prompt e definir o fluxo
# Algumas melhorias pela IA nas funções pois eu estava com alguns erros de formatação devolvida pela LLM

# TENHO QUE FAZER
# - Separar essas funções em seus arquivos correspondentes pq odeio coisas grandes em arquivo unico :/
# mas não vou tocar nisso agora.


from dataclasses import asdict
import json
from src.llm.llm_client import call_llm
from src.database.database_schema import DATABASE_SCHEMA
from src.query.models import (QueryPlan,PostgresPlan,VectorPlan)
from src.query.query_permissions import (resolve_permissions,apply_vector_permissions)
from src.database.database_schema import (get_schema_for_prompt, VALID_AGGREGATIONS, VALID_OPERATIONS)


VALID_ROUTES = {
    "postgresql",
    "faiss",
    "both"
}


def build_system_prompt() -> str:

    database_schema = get_schema_for_prompt()

    return f"""
Você é o Query Analyzer de um sistema RAG.

Sua função é analisar a pergunta do usuário e criar
um plano de busca estruturado.

Você deve determinar:

1. A intenção da pergunta.
2. A rota:
   - postgresql
   - faiss
   - both

3. As tabelas PostgreSQL necessárias.
4. Os filtros estruturados necessários.
5. A operação PostgreSQL.
6. A agregação, quando necessária.
7. O campo da agregação.
8. A consulta semântica para FAISS.
9. Os filtros de metadata para FAISS.
10. Um nível de confiança entre 0.0 e 1.0.

REGRAS DE ROTEAMENTO:

postgresql:
Use para dados exatos, registros, filtros, datas, contagens,
somas, médias, valores monetários e informações estruturadas.

faiss:
Use para documentação, procedimentos, explicações,
manuais, troubleshooting e conhecimento textual.

both:
Use quando a pergunta exigir simultaneamente dados estruturados
e conteúdo documental ou explicativo.

REGRAS IMPORTANTES:

- Nunca gere SQL.
- Nunca invente tabelas, utilize apenas as existentes
- Nunca invente colunas.
- Utilize somente tabelas e colunas presentes no schema.
- Não gere permissões de acesso.
- Não gere doc_sensitivity.
- A permissão será aplicada pelo backend.
- Para soma, média, mínimo ou máximo:
    operation = "aggregate"
- Para contagem:
    operation = "count"
- Para consulta simples:
    operation = "select"
- aggregation deve ser:
    "sum", "avg", "min", "max" ou null.
- Se a rota for "postgresql", vector pode ser vazio.
- Se a rota for "faiss", postgres pode ser vazio.
- Se a rota for "both", ambos devem conter informações úteis.

REGRAS PARA FAISS:

- vector.filters deve conter somente filtros que existam
  explicitamente no metadata dos documentos.
- Nunca use campos do PostgreSQL em vector.filters.
- Nunca use company_name em vector.filters.
- Nunca use doc_sensitivity em vector.filters.
- Nunca gere sensitivity em vector.filters.
- A sensitivity será adicionada exclusivamente pelo backend
  através do VectorPermissionGuard.
- Se nenhum filtro de metadata for necessário, use {""}.

METADATA DISPONÍVEL NOS DOCUMENTOS:

- file_name
- sensitivity
- doc_type
- chunk_index
- h1
- h2
- section
- section_title
- keywords

Exemplo de filtro válido:

{{
    "doc_type": "reembolso"
}}

Exemplo inválido:

{{
    "company_name": "VendeFácil"
}}

Exemplo inválido:

{{
    "doc_sensitivity": ["publico"]
}}

Exemplo inválido:

{{
    "sensitivity": ["publico"]
}}

REGRAS PARA FILTROS POSTGRESQL:

- Os nomes dos filtros devem ser SOMENTE os nomes das colunas.
- Nunca use o formato "tabela.coluna".
- Nunca use prefixos de tabela nos filtros.

- REGRAS ESPECÍFICAS DE DOMÍNIO:
  * Quando a pergunta for sobre "produtos oferecidos", "catálogo" ou "o que a empresa vende/oferece", utilize prioritariamente a tabela "products".
  * Não confunda a empresa dona dos dados (ex: VendeFácil) com clientes cadastrados na tabela "customers". "VendeFácil" é a empresa principal, logo os produtos dela estão na tabela de catálogo ("products").
    
FILTROS DE METADATA FAISS:

Use filtros somente quando a pergunta indicar claramente
uma característica estrutural do documento.

Campos permitidos:
- doc_type
- file_name
- h1
- h2
- section
- section_title

Não utilize:
- sensitivity
- doc_sensitivity
- keywords

"sensitivity" é controlado exclusivamente pelo backend
através do permission_level.

Termos como "VendeFácil", "7 dias", "100%" etc.
devem permanecer na semantic_query, salvo quando
corresponderem claramente a um campo de metadata.

SCHEMA POSTGRESQL:

{database_schema}

RETORNE SOMENTE JSON VÁLIDO.

FORMATO:

{{
    "route": "postgresql | faiss | both",
    "intent": "string",
    "confidence": 0.0,

    "postgres": {{
        "tables": [],
        "filters": {{}},
        "operation": null,
        "aggregation": null,
        "field": null
    }},

    "vector": {{
        "semantic_query": null,
        "filters": {{}}
    }}
}}
"""


def build_query_plan(plan: dict) -> QueryPlan:
    route = plan["route"]
    postgres_plan = None
    vector_plan = None

    # PostgreSQL só é criado quando a rota utiliza PostgreSQL
    if route in ("postgresql", "both"):
        postgres_data = plan.get("postgres") or {}
        postgres_plan = PostgresPlan(
            tables=postgres_data.get(
                "tables",
                []
            ),
            filters=postgres_data.get(
                "filters",
                {}
            ),
            operation=postgres_data.get("operation"),
            aggregation=postgres_data.get("aggregation"),
            field=postgres_data.get("field")
        )

    # FAISS só é criado quando a rota utiliza FAISS
    if route in ("faiss", "both"):
        vector_data = plan.get("vector") or {}
        vector_plan = VectorPlan(
            semantic_query=vector_data.get("semantic_query"),
            filters=vector_data.get("filters",{})
        )

    return QueryPlan(
        route=route,
        intent=plan["intent"],
        confidence=float(plan.get("confidence",1.0)),
        postgres=postgres_plan,
        vector=vector_plan
    )



def analyze_query(
    query: str,
    permission_level: str
) -> QueryPlan:

    if not query or not query.strip():
        raise ValueError("A pergunta não pode ser vazia.")

# AQUI QUE O BACKEND RESOLVE AS PERMISSÕES!!
    permissions = resolve_permissions(permission_level)

    # Chamada à LLM entrará aqui.
    raw_response = call_llm(
        system_prompt=build_system_prompt(),
        user_prompt=query
    )

    #plan_dict = json.loads(raw_response)
    #print("\n--- RAW RESPONSE DA LLM ---")
    #print(repr(raw_response))
    #print("--- FIM RAW RESPONSE ---\n")

    if not raw_response:
        raise ValueError("A LLM retornou uma resposta vazia.")

    try:
        cleaned_response = clean_json_response(raw_response)
        plan_dict = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print("Resposta inválida da LLM:")
        print(raw_response)

        raise ValueError("A LLM não retornou um JSON válido.") from e

    # Normalização
    plan_dict = normalize_plan(plan_dict)

    #VAlidação
    plan_dict = validate_plan(plan_dict)

    #  Conversão para models
    plan = build_query_plan(plan_dict)

    # A permissão é aplicada pelo backend não pela LLM.
    if plan.vector:
        plan.vector = apply_vector_permissions(plan.vector,permissions)
    return plan

def validate_plan(plan: dict) -> dict:
    if not isinstance(plan, dict):
        raise ValueError("O Query Analyzer não retornou um objeto JSON.")

    # Route
    route = plan.get("route")
    if route not in VALID_ROUTES:
        raise ValueError(f"Rota inválida retornada pela LLM: {route}")

    # Intent
    intent = plan.get("intent")
    if not isinstance(intent, str) or not intent.strip():
        raise ValueError("O Query Analyzer não informou uma intenção válida.")


    # Confidence
    confidence = plan.get("confidence", 1.0)

    if not isinstance(confidence, (int, float)):
        raise ValueError("confidence deve ser numérico.")

    if not 0 <= confidence <= 1:
        raise ValueError("confidence deve estar entre 0 e 1.")

    # PostgreSQL
    if route in ("postgresql", "both"):
        postgres = plan.get("postgres")
        if not isinstance(postgres, dict):
            raise ValueError("A rota exige um plano PostgreSQL.")

        tables = postgres.get("tables", [])

        if not isinstance(tables, list):
            raise ValueError("postgres.tables deve ser uma lista.")
        for table in tables:
            if table not in DATABASE_SCHEMA:
                raise ValueError(f"Tabela inválida retornada pela LLM: {table}")

        operation = postgres.get("operation")

        if operation is not None:
            operation = operation.lower()
            if operation not in VALID_OPERATIONS:
                raise ValueError(f"Operação PostgreSQL inválida: {operation}")

        aggregation = postgres.get("aggregation")

        if aggregation is not None:
            aggregation = aggregation.lower()
            if aggregation not in VALID_AGGREGATIONS:
                raise ValueError(f"Agregação inválida: {aggregation}")

        field = postgres.get("field")

        if field:
            valid_fields = set()

            for table in tables:
                #valid_fields.update(DATABASE_SCHEMA[table]["columns"].keys())
                for col in DATABASE_SCHEMA[table]["columns"].keys():
                    valid_fields.add(col)
                    valid_fields.add(f"{table}.{col}")  # Aceita formato tabela.coluna

            if field not in valid_fields:
                raise ValueError(f"Campo '{field}' não existe nas tabelas selecionadas.")

        filters = postgres.get("filters", {})

        if not isinstance(filters, dict):
            raise ValueError("postgres.filters deve ser um objeto.")

        valid_columns = set()

        for table in tables:
            #valid_columns.update( DATABASE_SCHEMA[table]["columns"].keys())
            for col in DATABASE_SCHEMA[table]["columns"].keys():
                valid_columns.add(col)
                valid_columns.add(f"{table}.{col}")  # Aceita formato tabela.coluna nos filtros também

        for filter_name in filters.keys():
            # filtros especiais que não representam diretamente uma coluna
            if filter_name in {
                "month",
                "year",
                "date_start",
                "date_end"
            }:
                continue

            if filter_name not in valid_columns:
                raise ValueError(f"Filtro '{filter_name}' não corresponde a nenhuma coluna das tabelas {tables}.")

    # FAISS
    if route in ("faiss", "both"):
        vector = plan.get("vector")
        if not isinstance(vector, dict):
            raise ValueError("A rota exige um plano vetorial.")

        semantic_query = vector.get("semantic_query")

        if not isinstance(
            semantic_query,
            str
        ) or not semantic_query.strip():

            raise ValueError("semantic_query é obrigatória para busca FAISS.")

        filters = vector.get(
            "filters",
            {}
        )

        if not isinstance(filters, dict):
            raise ValueError("vector.filters deve ser um objeto.")
    return plan

def normalize_plan(plan: dict) -> dict:
    # Garante que 'route' existe antes de tentar manipular, definindo um padrão (ex: 'postgresql')
    route = plan.get("route", "postgresql")
    if isinstance(route, str):
        plan["route"] = route.strip().lower()
    else:
        plan["route"] = "postgresql" # Valor de fallback seguro

    postgres = plan.get("postgres")
    if isinstance(postgres, dict):
        operation = postgres.get("operation")

        if isinstance(operation, str):
            postgres["operation"] = operation.strip().lower()

        aggregation = postgres.get("aggregation")

        if isinstance(aggregation, str):
            postgres["aggregation"] = aggregation.strip().lower()

    return plan
'''
def normalize_plan(plan: dict) -> dict:
    plan["route"] = (
        plan["route"]
        .strip()
        .lower()
    )

    postgres = plan.get("postgres")
    if isinstance(postgres, dict):
        operation = postgres.get("operation")

        if isinstance(operation, str):
            postgres["operation"] = (operation.strip().lower())

        aggregation = postgres.get("aggregation")

        if isinstance(aggregation, str):
            postgres["aggregation"] = (aggregation.strip().lower())

    return plan
'''
def clean_json_response(raw_response: str) -> str:
    raw_response = raw_response.strip()

    if raw_response.startswith("```json"):
        raw_response = raw_response[
            len("```json"):
        ]

    elif raw_response.startswith("```"):
        raw_response = raw_response[
            len("```"):
        ]

    if raw_response.endswith("```"):
        raw_response = raw_response[
            :-len("```")
        ]

    return raw_response.strip()