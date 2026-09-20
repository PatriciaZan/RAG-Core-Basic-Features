import re
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter


def process_txt(
    file_path,
    doc_type=None,
    sensitivity=None,
    chunk_size=1000,
    chunk_overlap=100
):
    print(f"Processando TXT: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Marcador de início de uma mensagem
    message_pattern = r"(?=^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\])"

    messages = re.split(
        message_pattern,
        text,
        flags=re.MULTILINE
    )

    # Remove mensagens vazias
    messages = [
        message.strip()
        for message in messages
        if message.strip()
    ]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    for message_index, message in enumerate(messages):

        # Mensagem pequena → 1 chunk
        if len(message) <= chunk_size:
            partes = [message]

        # Mensagem grande → divide mantendo overlap
        else:
            partes = splitter.split_text(message)

        for part_index, parte in enumerate(partes):

            chunks.append({
                "texto": parte,
                "metadata": {
                    "chunk_id": uuid.uuid4().hex,
                    "doc_sensitivity": sensitivity,
                    "chunk_index": len(chunks),
                    "total_chunks": len(chunks),
                    "file_name": file_path.name,
                    "message_index": message_index,
                    "part_index": part_index,
                    "total_parts": len(partes)
                }
            })

    return chunks

