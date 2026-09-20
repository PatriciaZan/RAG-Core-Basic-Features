# Documento de analize do `post_retriever.py`
Executar consultas SQL no banco de dados PostgreSQL de forma segura e tipada.  

QueryPlan → PostgresRetriever → SQL executado → Resultados formatados

---
- Verifica se usuário tem permissão
- Monta SQL parameterizado
- Conecta e executa no PostgreSQL
- Converte tuplas em dicionários
- Previne SQL injection
- Trata falhas 
---

## Sua responsabilidade/funcionalidades:
1. Inicialização: `__init__`
```python
    def __init__(self, query_builder=None, permission_guard=None):
        self.query_builder = QueryBuilder()
        self.permission_guard = PostgresPermissionGuard()
        self.database_url = os.getenv("DATABASE_URL")
```
- Carrega a URL do banco (de .env)
- Inicializa o construtor de SQL
- Inicializa o validador de permissões

---
2. `retrieve()` método principal
- Validação de permissão => `permission_guard.validate()`  
Valida se permission_level="public" pode acessar esses dados (EX) pelo `permission_guard.validate("public")`

- Construção e execução SQL => `query_builder.build(plan) ` e `cursor.execute(sql, params)`  
Utilzia do `query_builder` para construir o SQL e depois o `psycong.connect...` para executar a consulta.  
- Formatação do resultado => `dict(zip(columns, row))`


---
3. Possui segurança no SQL
```python
cursor.execute("SELECT * FROM usuarios WHERE status = %s", (status,))
# Sempre trata como string literal, nunca como SQL
```