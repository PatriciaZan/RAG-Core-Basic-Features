## Processamento de arquivos .txt contendo arquivos de email

import re
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter

import re
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter


def process_email_txt(
        file_path,
        doc_type=None,
        sensitivity="internal",
        chunk_size=1000,
        chunk_overlap=100
):
    print(f"Processando E-mails TXT: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Regex para identificar o início de um novo e-mail pelo campo "De:" no começo de linha
    email_pattern = r"(?=^De:\s)"
    emails = re.split(email_pattern, text, flags=re.MULTILINE)
    emails = [e.strip() for e in emails if e.strip()]

    # Aqui ele começa a dividir o texto
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    for email_index, email_content in enumerate(emails):
        # Extração opcional de metadados do cabeçalho e referências para enriquecer a busca (RAG)
        from_match = re.search(r"^De:\s*(.+)$", email_content, re.MULTILINE)
        to_match = re.search(r"^Para:\s*(.+)$", email_content, re.MULTILINE)
        date_match = re.search(r"^Data:\s*(.+)$", email_content, re.MULTILINE)
        subject_match = re.search(r"^Assunto:\s*(.+)$", email_content, re.MULTILINE)

        # Regex para buscar padrões de ID de ticket (ex: TCK-1001, TICKET-999, ou apenas TCK1001)
        # Procura primeiro no assunto ou no texto geral do e-mail
        ticket_match = re.search(r"\b(TCK-\d+|TICKET-\d+)\b", email_content, re.IGNORECASE)

        email_metadata = {
            "remetente": from_match.group(1).strip() if from_match else "Desconhecido",
            "destinatario": to_match.group(1).strip() if to_match else "Desconhecido",
            "assunto": subject_match.group(1).strip() if subject_match else "Sem assunto",
            "data": date_match.group(1).strip() if date_match else "Desconhecida",
            "ticket_id": ticket_match.group(1).strip() if ticket_match else "Nenhum"  # <-- ADICIONADO AQUI
        }

        # Divide o e-mail caso ultrapasse o limite de caracteres
        partes = splitter.split_text(email_content)

        for part_index, parte in enumerate(partes):
            chunk_data = {
                "texto": parte,
                "metadata": {
                    "sensitivity": sensitivity,
                    "chunk_index": part_index,
                    "total_chunks": len(partes),
                    "chunk_id": uuid.uuid4().hex,
                    "file_name": getattr(file_path, "name", str(file_path)),
                    **email_metadata,
                }
            }
            chunks.append(chunk_data)

    return chunks