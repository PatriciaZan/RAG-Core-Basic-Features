from fastapi import FastAPI
from pydantic import BaseModel

from src.rag.rag_service import RAGService


app = FastAPI(
    title="VendeFácil RAG API",
    description="API para perguntas ao sistema RAG",
    version="1.0.0"
)


rag_service = RAGService()


class AskRequest(BaseModel):
    question: str
    permission: str


class AskResponse(BaseModel):
    answer: str


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    result = rag_service.ask(
        question=request.question,
        permission=request.permission
    )

    return AskResponse(
        answer=result["answer"]
    )