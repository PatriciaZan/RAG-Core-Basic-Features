# Resumo Geral dos arquivos contidos em /src/query

## Estrutura (para me achar melhor)
```
query_analyzer.py
├── analyze_query() ← Ponto de entrada
├── build_system_prompt() ← Instrui a LLM
├── clean_json_response() ← Remove markdown
├── normalize_plan() ← Padroniza valores
├── validate_plan() ← Valida rigorosamente
├── build_query_plan() ← Converte em objetos tipados
└── apply_vector_permissions() ← Aplica segurança
```