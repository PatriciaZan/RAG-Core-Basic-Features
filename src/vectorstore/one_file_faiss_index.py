# PREPARA DOS DADOS

# Aqui cria que cria os indices de busca vetorial do FAISS
# Ele vai ler os arquivos JSONs gerados com os embeddings e vai salvar

# Executar após a criação dos chunks + embeddings
# os arquivos gerados aqui serão: index.faiss e socuments.json

import json
from pathlib import Path
import faiss
import numpy as np
from src.vectorstore.similarity import normalize_embeddings


def create_faiss_index(input_json, output_dir):
    input_json = Path(input_json)
    output_dir = Path(output_dir)

    # 1. Abre e Le o arquivo JSON depois extrai os chunks contendo embeddings
    with open(input_json, "r", encoding="utf-8") as file:
        data = json.load(file)
    chunks = data["resultado"]
    if not chunks:
        raise ValueError("Nenhum chunk encontrado no arquivo.")

    # 2. Extrai embeddings
    # Vai fazer um loop por cada chunk para recuperar o embedding caso ele exista, e vai ir guardando em embeddings = []
    embeddings = []
    for chunk in chunks:
        embedding = chunk.get("embedding")
        if embedding is None:
            raise ValueError(
                f"Chunk {chunk['metadata']['chunk_index']} "
                "não possui embedding."
            )
        embeddings.append(embedding)

    # 3. Converter para numpy
    # Vai dar print em algumas infos
    embeddings = np.array(
        embeddings,
        dtype="float32"
    )
    print(f"Quantidade de vetores: {len(embeddings)}")
    print(f"Dimensão dos vetores: {embeddings.shape[1]}")

    # 4. Criar índice FAISS
    # Aqui que temos aquela normalização que tu comentou sobre o "IndexFlatIP" -> (Inner Product - produto interno rápido)
    #
    embeddings = normalize_embeddings(embeddings)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print(f"Vetores adicionados ao FAISS: {index.ntotal}")

    # 5. Criar diretório de saida/salvar o resultado desta operação
    # Ele já é responsável por criar o diretório caso ele não exista
    output_dir.mkdir(
        parents=True,
        exist_ok=True # se já existe
    )

    # 6. Salvar índice
    # definindo o caminho do arquivo que vai ser gerado
    index_path = output_dir / "index.faiss"
    #salva em disco
    faiss.write_index(
        index,
        str(index_path)
    )
    print(f"Índice salvo em: {index_path}")

    # 7. Salvar documentos/metadados
    # aqui que cria o arquivo documents.json para validarmos os resultados
    documents = []
    for chunk in chunks:
        documents.append({
            "texto": chunk["texto"],
            "metadata": chunk["metadata"]
        })
    documents_path = output_dir / "documents.json"

    with open(
        documents_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            documents,
            file,
            ensure_ascii=False, # para acentos/caracteres especiais
            indent=4 # deixar a formatação bonitinha
        )

    print(f"Documentos salvos em: {documents_path}")

    return index