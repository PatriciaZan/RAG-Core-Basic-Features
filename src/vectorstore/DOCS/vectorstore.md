## `similarity.py` - Normalização de embeddings
Tem apenas a função `normalize_embeddings()`.
- Normaliza vetores usando L2 norm (euclidiana). Isso é essencial porque o FAISS usa IndexFlatIP (Inner Product), e vetores normalizados + produto interno = similaridade de cosseno.
- Normaliza para comprimento 1

---

## `create_faiss_index.py` - Cria índice de UM arquivo JSON
Processa **um único** arquivo JSON com embeddings.

1. Abre o JSON (estrutura: `{"resultado": [chunks com embeddings]}`)
2. Extrai todos os embeddings em um array NumPy
3. ormaliza com `similarity.py`
4. Cria `IndexFlatIP` (estrutura de dados FAISS para busca rápida)
5. Salva dois arquivos:
   - `index.faiss` — o índice binário (usado para buscar)
   - `documents.json` — metadados (texto, chunk_id, file_name, etc.)

---
   
## `faiss_index.py` - Combina vários JSONs em UM índice faiss
Versão escalável de `create_faiss_index.py`
- Lê TODOS os JSON de uma pasta (não um único arquivo)
- Acumula embeddings de vários arquivos
- Cria UM único índice FAISS combinado
- Salva `index.faiss` e `documents.json` (com metadados de todos os chunks)

---

## `build_faiss.py` - Arquivo de execução principal
é o script para rodar e gerar os índices  

1. Define caminhos (entrada = outputEmbeddings, saída = faiss/)
2. Chama `build_faiss_index()` do `faiss_index.py`

---

## `search_faiss.py` - Realiza a busca no índice pronto/já processado

Fluxo:  
1. `load_index()` — carrega index.faiss do disco
2. `load_documents()` — carrega documents.json (para retornar contexto)
3. `search_faiss(query, top_k=5)`:
   - Gera embedding da pergunta com `get_embedding(query)`
   - Normaliza o embedding da query
   - Busca os K documentos mais similares no FAISS
   - Retorna lista de resultados com score + metadados

---

## `ask_faiss.py` - Realiza a busca nos index.
Usuário pode fazer perguntas para o banco vetorial por esta função.

---
## Schema

```
[JSONs com embeddings gerados]
           ↓
   [create_faiss_index.py OU faiss_index.py]  ← Escolhe conforme entrada
           ↓
   [similarity.py normaliza]
           ↓
   [Índice FAISS criado em memória]
           ↓
   [Salva: index.faiss + documents.json]
           ↓
   [search_faiss.py carrega tudo]
           ↓
   [ask_faiss.py] → [Busca da pergunta, retorna top-k]
```