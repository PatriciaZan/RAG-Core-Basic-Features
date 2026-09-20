import json

from langchain_text_splitters import RecursiveCharacterTextSplitter


def build_ticket_header(ticket):
    return (
        f"Ticket {ticket['ticket_id']}. "
        f"Cliente: {ticket['customer_name']} "
        f"({ticket['customer_id']}). "
        f"Estado: {ticket['state']}. "
        f"Módulo: {ticket['module']}. "
        f"Título: {ticket['title']}. "
        f"Prioridade: {ticket['priority']}. "
        f"Status: {ticket['status']}."
    )


def build_ticket_content(ticket):
    """Monta o conteúdo textual variável do ticket."""

    content = f"Descrição: {ticket.get('description', '')}"
    resolution = ticket.get("resolution")
    if resolution:
        content += f" Resolução: {resolution}"
    return content


def build_metadata(
    sensitivity,
    doc_type,
    file_path,
    ticket,
    part_index,


):
    """Cria os metadados utilizados na recuperação."""

    return {
        "file_name": file_path.name,
        "doc_type": doc_type,
        "chunk_id": (
            f"{file_path.stem}:"
            f"{ticket['ticket_id']}:"
            f"{part_index}"
        ),
        "sensitivity": sensitivity,
        "ticket_id": ticket["ticket_id"],
        "customer_id": ticket["customer_id"],
        "state": ticket["state"],
        "module": ticket["module"],
        "priority": ticket["priority"],
        "status": ticket["status"],
        "date": ticket["created_at"],
    }


def process_jsonl(
    file_path,
    doc_type="ticket",
    sensitivity="interno",
    chunk_size=1000,
    chunk_overlap=100,
):
    """Transforma tickets JSONL em chunks com metadados."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            ticket = json.loads(line)
            header = build_ticket_header(ticket)
            content = build_ticket_content(ticket)
            parts = splitter.split_text(content)


            for part_index, part in enumerate(parts):
                chunks.append(
                    {
                        "texto": f"{header} {part}",
                        "metadata": build_metadata(
                            sensitivity,
                            doc_type,
                            file_path,
                            ticket,
                            part_index,
                        ),
                    }
                )

    return chunks
