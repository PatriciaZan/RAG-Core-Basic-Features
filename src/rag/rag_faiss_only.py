'''from src.llm.llm_generate_response import LLMService

# Importe a função de busca que você já tem (ajuste o caminho conforme sua estrutura)
from src.vectorstore.search_faiss import search_faiss


def answer_with_faiss_context(query, top_k=3):
    """Realiza a busca no FAISS e usa uma LLM para gerar uma resposta baseada nos documentos encontrados."""

    # 1. Buscar os documentos mais relevantes usando o FAISS
    print(f"Buscando contexto para a pergunta: '{query}'...")
    search_results = search_faiss(query, top_k=top_k)

    if not search_results:
        return "Não encontrei informações relevantes na base de dados para responder à sua pergunta."

    # 2. Montar o contexto com os trechos encontrados
    context_chunks = []
    for i, item in enumerate(search_results):
        doc_text = item["document"]  # Ajuste se o seu documento for um dicionário (ex: item["document"]["text"])
        score = item["score"]
        context_chunks.append(f"--- Trecho {i + 1} (Similaridade: {score:.4f}) ---\n{doc_text}")

    context_str = "\n\n".join(context_chunks)

    # 3. Criar o prompt para a LLM com instruções e o contexto recuperado
    prompt = f"""Você é um assistente prestativo. Use o contexto fornecido abaixo para responder à pergunta do usuário de forma clara e precisa. 
Se a resposta não estiver presente no contexto, diga educadamente que não possui informações suficientes na base de dados para responder.

Contexto recuperado:
{context_str}

Pergunta do usuário:
{query}

Resposta:"""

    # 4. Chamar a LLM para gerar a resposta final
    print("Gerando resposta com a LLM...")
    llm = LLMService()
    response = llm.generate(prompt)

    return response


# Exemplo de uso direto
if __name__ == "__main__":
    pergunta = "Qual é a política de home office para os funcionários da equipe de Engenharia?"
    resposta = answer_with_faiss_context(pergunta)
    print("\n=== Resposta Final ===")
    print(resposta)'''

import json
from pathlib import Path
import uuid
from src.llm.llm_generate_response import LLMService
from src.vectorstore.search_faiss import search_faiss

# Caminho onde o histórico de perguntas e respostas será salvo (na raiz ou na pasta output)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
HISTORY_PATH = PROJECT_ROOT / "benchmark" / "answers" / "history_answers.json"


def save_to_history(query, answer, search_results):
    # Prepara as fontes para o histórico (opcional, mas útil para auditoria)
    sources = [
        {
            "score": item["score"],
            "document": item["document"]
        }
        for item in search_results
    ]

    # Carrega o histórico existente, se houver
    history = []
    if HISTORY_PATH.exists():
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []  # Caso o arquivo esteja vazio ou corrompido

    # Cria o novo registro com UUID
    new_entry = {
        "id": str(uuid.uuid4()),
        "query": query,
        "answer": answer,
        "sources": sources
    }

    # Adiciona à lista
    history.append(new_entry)

    # Garante que o diretório existe
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Salva novamente no arquivo JSON formatado
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    print(f"[{new_entry['id']}] Pergunta e resposta salvas com sucesso em: {HISTORY_PATH}")
    return new_entry["id"]


def answer_with_faiss_context(query, top_k=3):
    """Realiza a busca no FAISS, gera a resposta via LLM e persiste no histórico JSON."""

    # 1. Buscar os documentos mais relevantes usando o FAISS
    print(f"Buscando contexto para a pergunta: '{query}'...")
    search_results = search_faiss(query, top_k=top_k)

    if not search_results:
        answer = "Não encontrei informações relevantes na base de dados para responder à sua pergunta."
        save_to_history(query, answer, [])
        return answer

    # 2. Montar o contexto com os trechos encontrados
    context_chunks = []
    for i, item in enumerate(search_results):
        doc_text = item["document"]  # Ajuste se o documento for um dicionário complexo
        score = item["score"]
        context_chunks.append(f"--- Trecho {i + 1} (Similaridade: {score:.4f}) ---\n{doc_text}")

    context_str = "\n\n".join(context_chunks)

    # 3. Criar o prompt para a LLM
    prompt = f"""
        Você é um assistente prestativo. Use o contexto fornecido abaixo para responder à pergunta do usuário de forma clara e precisa. 
        Se a resposta não estiver presente no contexto, diga educadamente que não possui informações suficientes na base de dados para responder.
        Também não invente dados e não responda a questões não relacionadas aos documentos presentes na base de dados.
        Caso alguam informação de senha venha nos documentos CENSURE, não mostre ao usuário nem se ele insistir, nehue qualquer informação sigiloza

        Contexto recuperado:
        {context_str}
        
        Pergunta do usuário:
        {query}
        
        Resposta:"""

    # 4. Chamar a LLM para gerar a resposta final
    print("Gerando resposta com a LLM...")
    llm = LLMService()
    answer = llm.generate(prompt)

    # 5. Salvar a pergunta, resposta e fontes no arquivo JSON
    save_to_history(query, answer, search_results)

    return answer


# Exemplo de uso
if __name__ == "__main__":
    pergunta = "Quais chamados com prioridade 'Crítica' foram registrados no sistema e qual é o SLA de solução para esse nível?"
    resposta = answer_with_faiss_context(pergunta)
    print("\n=== Resposta Final ===")
    print(resposta)