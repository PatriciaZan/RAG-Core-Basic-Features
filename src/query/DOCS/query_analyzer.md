# Documento de analize do `query_analyzer.py`
**Este é o ponto de entrada que orquestra tudo**

Transforma a pergunta do usuário em um plano estruturado de execução usando uma LLM.

## Sua responsabilidade/funcionalidades:
1. System Prompt `build_system_prompt()`
- Este é o instrutor da LLM. Define tudo o que a LLM deve fazer   
- LLMs precisam de instruções muito específicas para produzir JSON estruturado consistente.   

---
2. Limpeza `clean_json_response()`
- Para limpar os "```json" antes do json

---
3. Normalização `normalize_plan()`
- Padroniza strings para lowercase.   
---
4. Validação `validate_plan()`
Esta função é um validador que garante:
- Route válida:
```python
    if route not in VALID_ROUTES:  # "postgresql", "faiss", "both"
        raise ValueError("Rota inválida")
```
- Intent é string:
```python
    if not isinstance(intent, str) or not intent.strip():
        raise ValueError("Intent inválida")
```

- Confidence é numérico (0-1):
```python
    if not 0 <= confidence <= 1:
        raise ValueError("Confidence fora do range")
```

- Tabelas existem no schema:
```python
    for table in tables:
        if table not in DATABASE_SCHEMA:
            raise ValueError(f"Tabela {table} não existe")
```

- Campos das tabelas existem
```python
    if field not in valid_fields:
        raise ValueError(f"Campo '{field}' não existe")
```

- Filtros correspondem a colunas:
```python
    for filter_name in filters.keys():
        if filter_name not in valid_columns:
            raise ValueError(f"Filtro '{filter_name}' inválido")
```

- Operações são válidas:
```python
    if operation not in VALID_OPERATIONS:  # "select", "count", "aggregate"
        raise ValueError(f"Operação inválida: {operation}")
```

- Agregações são válidas:
```python
    if aggregation not in VALID_AGGREGATIONS:  # "sum", "avg", "min", "max"
        raise ValueError(f"Agregação inválida: {aggregation}")
```
---
5. Construção: `build_query_plan()`
- Transforma o dicionário em objetos tipados

---
- `analyze_query()`
```
┌──────────────────────────────────────────────┐
│  1. VALIDAÇÃO INICIAL                        │
│     - Query não pode estar vazia             │
└──────────────┬───────────────────────────────┘
               │
┌──────────────↓───────────────────────────────┐
│  2. RESOLVER PERMISSÕES                      │
│     resolve_permissions(permission_level)    │
│     → Descobre o que o usuário pode acessar  │
└──────────────┬───────────────────────────────┘
               │
┌──────────────↓───────────────────────────────┐
│  3. CHAMAR LLM                               │
│     call_llm(system_prompt, user_query)      │
│     → LLM retorna JSON bruto                 │
└──────────────┬───────────────────────────────┘
               │
┌──────────────↓───────────────────────────────┐
│  4. LIMPAR JSON                              │
│     clean_json_response()                    │
│     → Remove markdown ```json``` fences      │
└──────────────┬───────────────────────────────┘
               │
┌──────────────↓───────────────────────────────┐
│  5. NORMALIZAR PLAN                          │
│     normalize_plan()                         │
│     → Converte "POSTGRESQL" → "postgresql"   │
└──────────────┬───────────────────────────────┘
               │
┌──────────────↓───────────────────────────────┐
│  6. VALIDAR PLAN                             │
│     validate_plan()                          │
│     → Verifica se tudo está válido           │
└──────────────┬───────────────────────────────┘
               │
┌──────────────↓───────────────────────────────┐
│  7. CONSTRUIR QUERYPLAN                      │
│     build_query_plan()                       │
│     → Transforma dict em objetos tipados     │
└──────────────┬───────────────────────────────┘
               │
┌──────────────↓───────────────────────────────┐
│  8. APLICAR PERMISSÕES (VECTOR)              │
│     apply_vector_permissions()               │
│     → Garante que só acessa o que pode       │
└──────────────┬───────────────────────────────┘
               │
        QueryPlan retornado
```