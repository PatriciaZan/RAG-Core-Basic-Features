import json
import uuid
from pathlib import Path


def process_md(file_path, doc_type=None, sensitivity=None, chunk_size=1000):
    """Chunking simples e sem duplicação de headers"""

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    current_chunk = ""
    current_headers = {}

    for line in text.split("\n"):
        # Detecta headers
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            header_key = f"h{level}"
            current_headers[header_key] = line.lstrip("# ").strip()
            # Limpa headers de nível inferior
            for i in range(level + 1, 5):
                current_headers.pop(f"h{i}", None)

        # Acumula conteúdo
        current_chunk += line + "\n"

        # Quebra ao atingir tamanho + permite quebra em seções
        if len(current_chunk) >= chunk_size and line.startswith("##"):
            chunks.append({
                "texto": current_chunk.strip(),
                "metadata": {
                    "file_name": Path(file_path).name,
                    "sensitivity": sensitivity,
                    "doc_type": doc_type,
                    "chunk_index": len(chunks),
                    **current_headers
                }
            })
            current_chunk = ""

    # Último chunk
    if current_chunk.strip():
        chunks.append({
            "texto": current_chunk.strip(),
            "metadata": {
                "file_name": Path(file_path).name,
                "sensitivity": sensitivity,
                "doc_type": doc_type,
                "chunk_index": len(chunks),
                **current_headers
            }
        })

    return chunks