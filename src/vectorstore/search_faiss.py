# LEITURA DOS DADOS index.faiss

# Aqui ele vai carregar o index.faiss gerado em create_faiss_index.py
# vai fazer a leitura / busca! (buscar por similaridade de significado, não apenas palavras-chave)

import json
from pathlib import Path

import faiss
import numpy as np

from src.llm.llm_embedding import get_embedding

# Config dos caminhos, raiz do projeto, acha onde está o index.fass e define onde os docs serão salvos
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FAISS_DIR = PROJECT_ROOT / "output" / "output_faiss"
INDEX_PATH = FAISS_DIR /  "index.faiss"
DOCUMENTS_PATH = FAISS_DIR / "documents.json"

# Carrega o arquivo faiss, validando se o index existe
def load_index():
    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"Índice FAISS não encontrado: {INDEX_PATH}"
        )
    return faiss.read_index(
        str(INDEX_PATH)
    )


# Carrega o arquivo documents.json e valida se existe
def load_documents():
    if not DOCUMENTS_PATH.exists():
        raise FileNotFoundError(
            f"documents.json não encontrado: "
            f"{DOCUMENTS_PATH}"
        )
    #retorna a lista de documentos existentes
    with open(
        DOCUMENTS_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# Aqui é a função principal
def search_faiss(
    query,
    top_k=5
):
    # 1. Carregar índice
    index = load_index()

    # 2. Carregar documentos
    documents = load_documents()

    # 3. Gera o embedding da pergunta
    query_embedding = get_embedding(query)
    query_vector = np.array(
        [query_embedding],
        dtype="float32"
    )
    # 4. Normaliza o vetor da pergunta
    # manter o padrão dos embeddings
    faiss.normalize_L2(
        query_vector
    )

    # 5. Limitar top_k
    # aqui vai evitar erros caso o 'user' peça um número de resultados e eles não existam
    top_k = min(
        top_k,
        index.ntotal
    )

    # 6. Buscar no FAISS
    # scores = números de similaridade (quanto maior, mais similar)
    # indices = posições dos chunks no vetor original
    scores, indices = index.search(
        query_vector,
        top_k
    )

    # 7. Montar resultados
    # vai percorrer os scores e indices em paralelo
    results = []
    for score, index_position in zip(
        scores[0],
        indices[0]
    ):
        # aqui vai pular resultados inválidos = -1
        if index_position == -1:
            continue
        #recupera o doc original
        document = documents[index_position]
        # cria o resultado do score + documento
        results.append({
            "score": float(score),
            "document": document
        })
    return results

