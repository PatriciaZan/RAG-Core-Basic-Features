# Documento de analize do `models.py`
Este arquivo define os "contratos de dados" (classes).  
Estruturam/moldam todos os componentes garantindo a mesma formatação.  

### **Em resumo: models.py é o "dicionário comum" que todos os componentes da RAG usam para se comunicarem de forma clara e tipada.**
- Definir estruturas de dados tipadas para padronizar a comunicação entre módulos.

---

- Python valida os dados automaticamente
- Todos os módulos entendem o mesmo "idioma"
- O código é auto-documentado
- Impossible enviar dados inválidos
- 	Erros de tipo são catch rápido

---

## Sua responsabilidade/funcionalidades:
1. PostgresPlan
- Usado quando um componente planeja uma query SQL
Exemplo:
```
    plan = PostgresPlan(
        tables=["usuarios"],
        fields=["id", "nome", "email"],
        filters={"status": "ativo"},
        operation="COUNT",
        field="id"
    )
    
    # Significa: SELECT COUNT(id) FROM usuarios WHERE status='ativo'
```

---

2. VectorPlan 
- Usado quando um componente planeja uma busca vetorial
Exemplo:
```
    plan = VectorPlan(
        semantic_query="Como aprender programação?",
        filters={"categoria": "educação", "idioma": "pt-BR"}
    )
    
    # Significa: Buscar documentos sobre "programação" 
    #            que têm categoria='educação' E idioma='pt-BR'
```

---

3. QueryPlan
- Usado após analisar a query do usuário, o sistema decide COMO responder
Exemplo:
```
    plan = QueryPlan(
        route="hybrid",
        intent="busca_info",
        confidence=0.92,
        postgres=PostgresPlan(
            tables=["cursos"],
            fields=["titulo", "descricao"],
            filters={}
        ),
        vector=VectorPlan(
            semantic_query="Cursos de programação",
            filters={"nivel": "iniciante"}
        )
    )
    
    # Significa: Buscar TANTO em PostgreSQL QUANTO em FAISS
    #            porque a query é complexa e precisa de dados
    #            estruturados + documentos semânticos
```

---

4. QueryRequest
- Usado quando o usuário envia uma pergunta
Exemplo:
````
    request = QueryRequest(
        query="Quais são os cursos de Python disponíveis?",
        permission_level="public"
    )
    
    # O sistema vai:
    # 1. Receber essa query
    # 2. Gerar um QueryPlan baseado no conteúdo
    # 3. Executar postgres + vector searches
    # 4. Retornar apenas documentos que o usuário pode ver
````