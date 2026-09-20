
import json
from pathlib import Path

import faiss
import numpy as np

from vectorstore.similarity import normalize_embeddings


def build_faiss_index(input_dir, output_dir):
    #Percorre todos os arquivos JSON de uma pasta,
    #coleta seus embeddings e cria um único índice FAISS.

    #O índice utiliza produto interno (Inner Product)
    #sobre vetores normalizados, equivalente à
    #similaridade de cosseno.

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    # 1. Encontrar arquivos JSON
    json_files = sorted(input_dir.glob("*.json"))

    if not json_files:
        raise ValueError(
            f"Nenhum arquivo JSON encontrado em: {input_dir}"
        )

    print(f"Arquivos encontrados: {len(json_files)}")

    # 2. Preparar estruturas
    embeddings = []
    documents = []

    # 3. Processar cada JSON
    for json_file in json_files:
        print(f"\nProcessando: {json_file.name}")
        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)
        chunks = data.get("resultado", [])
        print(f"  Chunks encontrados: {len(chunks)}")

        for chunk in chunks:
            embedding = chunk.get("embedding")
            if embedding is None:
                raise ValueError(
                    f"Chunk sem embedding encontrado em "
                    f"{json_file.name}"
                )
            embeddings.append(embedding)

            # Documento associado ao vetor
            documents.append({
                "faiss_id": len(documents),
                "texto": chunk["texto"],
                "metadata": chunk["metadata"]
            })


    # 4. Verificar quantidade
    if not embeddings:
        raise ValueError(
            "Nenhum embedding encontrado nos arquivos."
        )

    # 5. Converter para NumPy
    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    print("\n-----------------------------------")
    print(f"Total de vetores: {len(embeddings)}")
    print(f"Dimensão dos embeddings: {embeddings.shape[1]}")

    # 6. Normalizar
    embeddings = normalize_embeddings(
        embeddings
    )
    print("Embeddings normalizados.")

    # 7. Criar índice FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print(
        f"Vetores adicionados ao FAISS: "
        f"{index.ntotal}"
    )

    # 8. Criar diretório de saída
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # 9. Salvar índice
    index_path = output_dir / "index.faiss"
    faiss.write_index(
        index,
        str(index_path)
    )

    # 10. Salvar documentos
    documents_path = output_dir / "documents.json"
    with open(
        documents_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            documents,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n-----------------------------------")
    print("Índice criado com sucesso!")
    print(f"FAISS:      {index_path}")
    print(f"Documents:  {documents_path}")
    return index