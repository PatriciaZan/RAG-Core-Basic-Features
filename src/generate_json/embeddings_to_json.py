import json
from pathlib import Path
from src.llm.llm_embedding import get_embedding
# Will add the embeddings to the existing chunking json, but in new file and folder

def embeddings_to_json(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    # 1. Ler JSON
    with open(input_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    chunks = data["resultado"]
    print(f"Total de chunks: {len(chunks)}")

    # 2. Gerar embedding
    for index, chunk in enumerate(chunks):
        texto = chunk["texto"]
        print(
            f"[{index + 1}/{len(chunks)}] "
            f"Gerando embedding..."
        )

        embedding = get_embedding(texto)

        # Adiciona embedding ao chunk
        data["resultado"][index] = {
            "texto": texto,
            "embedding": embedding,
            "metadata": chunk["metadata"]
        }


    # 3. Salvar novo JSON
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"\nArquivo salvo em: {output_path}")