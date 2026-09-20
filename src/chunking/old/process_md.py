import uuid

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter
)
from src.generate_json.generate_json import generate_json

def process_md(
    file_path,
    doc_type=None,
    sensitivity=None,
    chunk_size=1000,
    chunk_overlap=100
):
    print(f"Processando Markdown: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
        ("####", "h4"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )

    sections = markdown_splitter.split_text(text)

    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = []

    for section_index, section in enumerate(sections):

        section_text = section.page_content
        metadata = section.metadata.copy()

        # Seção pequena
        if len(section_text) <= chunk_size:

            chunks.append({
                "texto": section_text,
                "metadata": {
                    "sensitivity": sensitivity,
                    "chunk_index": len(chunks),
                    "total_chunks": len(sections),
                    "chunk_id": uuid.uuid4().hex,
                    "file_name": file_path.name,
                    "section_index": section_index,
                    **metadata
                }
            })

            continue

        # Seção grande
        parts = size_splitter.split_text(section_text)

        for part_index, part in enumerate(parts):

            # Recupera a hierarquia da seção
            headers = []

            for key in ["h1", "h2", "h3", "h4"]:
                if key in metadata:
                    headers.append(f"{'#' * int(key[1])} {metadata[key]}")

            header_text = "\n".join(headers)

            # evita duplicar o cabeçalho caso ele já esteja no chunk
            if header_text and not part.startswith(header_text):
                part = f"{header_text}\n\n{part}"


            chunks.append({
                "texto": part,
                "chunk_index": len(chunks),
                "metadata": {
                    "source_file": file_path.name,
                    "section_index": section_index,
                    "part_index": part_index,
                    "total_parts": len(parts),
                    **metadata
                }
            })
    #generate_json(
    #    chunks,
     #   "resultado.json"
    #)

    return chunks