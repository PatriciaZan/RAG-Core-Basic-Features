# Documento de analize do `context_builder.py`
Este arquivo é um "formatador de respostas" que pega os resultados brutos de duas fontes diferentes e os transforma em um formato padronizado para a LLM entender.

- Estrutura padronizada
- Fácil rastrear origem dos dados
- Processamento direto para a LLM

```
PostgreSQL result (tabular)  }
                             } → ContextBuilder → Contexto unificado para a LLM
FAISS result (documentos)    }                   
```

## Sua responsabilidade/funcionalidades:
1. Entrada Dupla
```
    build(postgres_result, vector_result)
```
- `postgres_result` → dados de banco de dados SQL estruturado
- `vector_result` → documentos recuperados do FAISS
---

2. Formatação Separada
PostgreSQL Context `_build_postgres_context()` Transforma dados tabulares em:
```json
{
  "source": "postgresql",
  "row_count": 3,
  "columns": ["id", "nome", "email"],
  "rows": [
    [1, "João", "joao@email.com"],
    [2, "Maria", "maria@email.com"]
  ]
}
```

E Vector Context `_build_vector_context()` Transforma documentos em:
```json
{
  "source": "faiss",
  "row_count": 2,
  "documents": [
    {
      "texto": "Python é uma linguagem...",
      "metadata": {"categoria": "programação"},
      "rrf_score": 0.85
    },
    {
      "texto": "Machine Learning com Python...",
      "metadata": {"categoria": "ML"},
      "rrf_score": 0.72
    }
  ]
}
```