import json
import re
from pathlib import Path

"""
    Chunking: separa por sub-seções numeradas (1.1, 1.2, 2.1, 2.2, etc)
"""

def process_md(file_path, doc_type=None, sensitivity=None):


    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Normalizar line endings
    text = text.replace('\r\n', '\n')

    chunks = []
    chunk_index = 0

    # Extrair h1
    h1_match = re.search(r'^# (.+?)(?:\n|$)', text)
    h1 = h1_match.group(1).strip() if h1_match else ""

    # Pattern: começa com número.número. (1.1, 2.2, etc)
    # Captura tudo até a próxima ocorrência
    pattern = r'^(\d+\.\d+)\.\s+(.+?)(?=\n\n*\d+\.\d+\.|$)'

    matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)

    for match in matches:
        section_num = match.group(1)
        content = match.group(2).strip()

        if not content:
            continue

        # Extrair h2 (seção principal como "1. Condições...")
        h2_match = re.search(r'^##\s+(\d+)\.\s+(.+?)$', text[:match.start()], re.MULTILINE)
        h2 = h2_match.group(2).strip() if h2_match else ""

        # Extrair título em negrito
        bold_match = re.search(r'\*\*([^*]+)\*\*', content)
        section_title = bold_match.group(1) if bold_match else ""

        # Extrair palavras-chave: números + "dias", percentuais, "dias corridos"
        keywords = []
        for kw in re.findall(r'\d+\s*(?:dias?|%)|100%|7\s+dias', content, re.IGNORECASE):
            if kw not in keywords:
                keywords.append(kw)

        chunks.append({
            "texto": content,
            "metadata": {
                "file_name": Path(file_path).name,
                "sensitivity": sensitivity,
                "doc_type": doc_type,
                "chunk_index": chunk_index,
                "h1": h1,
                "h2": h2,
                "section": section_num,
                "section_title": section_title,
                "keywords": keywords
            }
        })
        chunk_index += 1

    return chunks


def save_to_json(chunks, output_path):
    """Salva chunks em JSON"""
    output = {
        "source_file": "reembolso.md",
        "total_chunks": len(chunks),
        "resultado": chunks
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    file_path = Path("/mnt/user-data/uploads/reembolso.md")

    chunks = process_md(
        file_path,
        doc_type="reembolso",
        sensitivity="publico"
    )

    output_path = Path("/home/claude/reembolso_chunked.json")
    save_to_json(chunks, output_path)

    print(f"✅ {len(chunks)} chunks gerados\n")

    for chunk in chunks:
        meta = chunk['metadata']
        print(f"Chunk {meta['chunk_index']}: Seção {meta['section']} - {meta['section_title']}")
        print(f"  Palavras-chave: {meta['keywords']}")
        print(f"  Preview: {chunk['texto'][:80]}...\n")