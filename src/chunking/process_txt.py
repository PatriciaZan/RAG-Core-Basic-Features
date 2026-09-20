"""
Processador de arquivos TXT contendo e-mails.
Responsabilidades:
- Ler arquivos TXT.
- Identificar mensagens de e-mail.
- Extrair remetente, destinatários, data, assunto e ticket.
- Preservar o cabeçalho do e-mail como contexto textual.
- Dividir e-mails grandes sem perder o contexto do cabeçalho.
- Adicionar doc_type e sensitivity à metadata.

Compatível com:
    process_txt(file_path, doc_type, sensitivity)
"""

import re
import uuid
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 100

# ------------------------------------------------------------------------------------------------------------------------------------
# Leitura e identificação das mensagens
def split_emails(text: str) -> list[str]:
    """
    Divide um TXT que contém múltiplos e-mails.
    Formato principal:
        De: ...
        Para: ...
        Data: ...
        Assunto: ...
    Também aceita o formato antigo:
        [2026-02-10 09:15]
        ...
    """

    # Novo formato de e-mail.
    email_pattern = r"(?=^\s*De:\s*)"
    messages = re.split(
        email_pattern,
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    messages = [
        message.strip()
        for message in messages
        if message.strip()
    ]

    # Compatibilidade com o formato antigo do projeto.
    if len(messages) <= 1:
        old_pattern = r"(?=^\s*\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\])"
        messages = re.split(
            old_pattern,
            text,
            flags=re.MULTILINE,
        )
        messages = [
            message.strip()
            for message in messages
            if message.strip()
        ]
    return messages

# ------------------------------------------------------------------------------------------------------------------------------------
# Campos do e-mail
def extract_header_field(message: str, field_name: str) -> str | None:
    """
    Extrai um campo simples do cabeçalho.
    Exemplos:
        De: gerencia@boacompra.com.br
        Data: 10 de Fevereiro de 2026 09:15
        Assunto: Falha no estoque
    """
    pattern = rf"^\s*{re.escape(field_name)}\s*:\s*(.+?)\s*$"
    match = re.search(
        pattern,
        message,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1).strip()

def extract_sender(message: str) -> str | None:
    """Extrai o remetente do e-mail."""
    return extract_header_field(message, "De")


def extract_recipients(message: str) -> list[str]:
    """Extrai os destinatários do campo 'Para'."""
    value = extract_header_field(message, "Para")

    if not value:
        return []

    # Aceita destinatários separados por vírgula ou ponto e vírgula.
    recipients = re.split(r"[,;]", value)
    return [
        recipient.strip()
        for recipient in recipients
        if recipient.strip()
    ]


def extract_sent_date(message: str) -> str | None:
    """Extrai a data de envio."""
    return extract_header_field(message, "Data")

def extract_subject(message: str) -> str | None:
    """Extrai o assunto."""
    return extract_header_field(message, "Assunto")

# ------------------------------------------------------------------------------------------------------------------------------------
# Ticket
def extract_ticket_number(text: str) -> str | None:
    """
    Extrai o identificador do ticket.
    Exemplos reconhecidos:
        Ticket TCK-1001
        ticket: TCK-1001
        Ticket #TCK-1001
        chamado TCK-1001
        TCK-1001
    Retorna somente:
        TCK-1001
    """
    patterns = [
        r"\b(?:ticket|chamado|incidente)\s*[:#-]?\s*(TCK-\d+)\b",
        r"\b(TCK-\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1).upper()
    return None

# ------------------------------------------------------------------------------------------------------------------------------------
# Cabeçalho e corpo
def extract_email_header(message: str) -> str:
    """
    Extrai o cabeçalho completo do e-mail.
    O cabeçalho será preservado no texto de todos os chunks.
    """

    lines = message.splitlines()
    header_lines = []
    header_fields = (
        "de:",
        "para:",
        "cc:",
        "data:",
        "assunto:",
        "reply-to:",
    )

    found_header = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if found_header:
                break
            continue

        lower_line = stripped.lower()
        if lower_line.startswith(header_fields):
            header_lines.append(stripped)
            found_header = True

        elif found_header:
            break
    return "\n".join(header_lines).strip()


def extract_email_body(message: str) -> str:
    """
    Extrai somente o corpo do e-mail, removendo o cabeçalho.
    """
    lines = message.splitlines()
    header_started = False
    header_ended = False
    body_lines = []

    header_fields = (
        "de:",
        "para:",
        "cc:",
        "data:",
        "assunto:",
        "reply-to:",
    )

    for line in lines:
        stripped = line.strip()
        lower_line = stripped.lower()
        if not header_ended:
            if lower_line.startswith(header_fields):
                header_started = True
                continue
            if header_started and not stripped:
                header_ended = True
                continue
            if not header_started:
                continue
        if header_ended:
            body_lines.append(line)

    # Se não houver cabeçalho reconhecido, não descarta conteúdo.
    if not header_started:
        return message.strip()
    return "\n".join(body_lines).strip()

# ------------------------------------------------------------------------------------------------------------------------------------
# Limpeza
def clean_text(text: str) -> str:
    """Normaliza espaços sem destruir a separação dos parágrafos."""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(
        r"[ \t]+$",
        "",
        text,
        flags=re.MULTILINE,
    )

    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# ------------------------------------------------------------------------------------------------------------------------------------
# Chunking
def split_email_body(
    body: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """
    Divide o corpo do e-mail preservando, quando possível:

    1. parágrafos;
    2. linhas;
    3. frases;
    4. palavras.
    """

    if not body:
        return []

    if len(body) <= chunk_size:
        return [body]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "! ",
            "? ",
            " ",
            "",
        ],
    )

    return splitter.split_text(body)

# ------------------------------------------------------------------------------------------------------------------------------------
# Processador principal
def process_txt(
    file_path,
    doc_type=None,
    sensitivity=None,
    chunk_size=DEFAULT_CHUNK_SIZE,
    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
):
    """
    Processa um TXT contendo e-mails.

    Cada chunk contém:

        texto
        metadata
            sensitivity
            doc_type
            chunk_id
            file_name
            sender
            recipients
            sent_date
            subject
            ticket_number
            message_index
            part_index
            total_parts
    """

    file_path = Path(file_path)
    print(f"Processando TXT de e-mails: {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
    ) as file:
        text = file.read()

    if not text.strip():
        return []

    text = clean_text(text)
    messages = split_emails(text)
    chunks = []

    for message_index, message in enumerate(messages):

        message = clean_text(message)

        # ------------------------------------------------------------------------------------------------------------------
        # Metadados do e-mail
        sender = extract_sender(message)
        recipients = extract_recipients(message)
        sent_date = extract_sent_date(message)
        subject = extract_subject(message)
        ticket_number = extract_ticket_number(message)

        # ------------------------------------------------------------------------------------------------------------------
        # Cabeçalho e corpo
        header = extract_email_header(message)
        body = extract_email_body(message)

        if not body:
            body = message

        body = clean_text(body)
        header = clean_text(header)

        # ------------------------------------------------------------------------------------------------------------------
        # Divide o corpo
        parts = split_email_body(
            body,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        if not parts:
            parts = [body]

        total_parts = len(parts)

        # ------------------------------------------------------------------------------------------------------------------
        # Cria os chunks
        for part_index, part in enumerate(parts):

            part = clean_text(part)

            # Mantém o cabeçalho em todos os chunks.
            if header:
                texto = f"{header}\n\n{part}"
            else:
                texto = part

            metadata = {
                "sensitivity": sensitivity,
                "doc_type": doc_type,
                "chunk_id": uuid.uuid4().hex,
                "file_name": file_path.name,

                # Informações do e-mail
                "sender": sender,
                "recipients": recipients,
                "sent_date": sent_date,
                "subject": subject,

                # Identificador operacional
                "ticket_number": ticket_number,

                # Controle de chunking
                "message_index": message_index,
                "part_index": part_index,
                "total_parts": total_parts,
            }

            chunks.append(
                {
                    "texto": texto,
                    "metadata": metadata,
                }
            )

    return chunks
