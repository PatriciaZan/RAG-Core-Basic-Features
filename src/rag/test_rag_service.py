import os
from pathlib import Path
from dotenv import load_dotenv
from src.rag.rag_service import RAGService

load_dotenv()

print("=" * 70)
print("INICIALIZANDO RAG SERVICE")

print("=" * 70)

DIR_PATH = Path(__file__).resolve().parent.parent.parent

FAISS_INDEX_PATH = (
    DIR_PATH /
    "output"/
    "output_faiss" /
    "index.faiss"
)

FAISS_DOCUMENTS_PATH = (
    DIR_PATH /
    "output" /
    "output_faiss" /
    "documents.json"
)

rag_service = RAGService(
    faiss_index_path=FAISS_INDEX_PATH,
    faiss_documents_path=FAISS_DOCUMENTS_PATH
)

def run_test(
    question: str,
    permission_level: str
):

    print("PERGUNTA")
    print(question)

    print("\nPERMISSÃO:")
    print(permission_level)

    print("\n")
    print("=" * 70)
    print("EXECUTANDO RAG")

    answer = rag_service.ask(
        question=question,
        permission_level=permission_level
    )

    print("\n")
    print("=" * 70)
    print("RESPOSTA FINAL da LLM")

    print(answer)

    return answer

if __name__ == "__main__":
    run_test(
        question="Qual é o prazo de arrependimento para reembolso integral de 100% no cancelamento de planos da VendeFácil?",
        permission_level="restrito"
    )