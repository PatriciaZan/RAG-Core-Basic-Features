# Documento de analize do `vector_retriever.py`
Ele implementa um sistema de recuperação de documentos que combina três técnicas diferentes.  

- Recupera documentos relevantes baseado em query do usuário.
- Combina busca semântica + keyword matching.
- Respeita permissões e filtros de metadata.
- Retorna ranking ordenado por relevância.

## Sua responsabilidade:
1. Busca Densa (Vetorial)
```
    _dense_search() → FAISS
```
- Usa embeddings (vetores numéricos) para buscar semanticamente
- Exemplo: "máquina de lavar" encontraria também "eletrodoméstico" mesmo sem essa palavra

---

2. Busca Lexical (Palavra por Palavra)
```
    _bm25_search() → BM25Okapi
```
- Busca por palavras-chave exatas
- Exemplo: se você procura "Python 3.11", encontra documentos com exatamente esses termos

---

3. Fusão Inteligente dos Dois
```
    _reciprocal_rank_fusion() → RRF
```
- Combina os resultados das duas buscas em um ranking único
- Evita favorecer demais uma ou outra abordagem

---

4. Controle de Acesso
```
    VectorPermissionGuard + _matches_filters()
```
- Filtra resultados baseado em permissões do usuário (sensitivity levels)
- Aplica filtros de metadata (campos como categoria, tipo, etc)

---
## FLUXO
```
        Query do usuário
            ↓
        [EMBEDDING] → "máquina de lavar" vira vetor 768-dim
            ↓
        ┌─────────────────────────────────────┐
        │   BUSCA DENSA (FAISS)               │ → top-4 mais similares
        │   + BUSCA LEXICAL (BM25)            │ → top-4 keywords matches
        └─────────────────────────────────────┘
            ↓
        FUSÃO RRF (combina com pesos)
            ↓
        FILTROS (permissão + metadata)
            ↓
        TOP-K resultados finais (ex: 5)
```