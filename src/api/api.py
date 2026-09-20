from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.rag.rag_service_api import RAGService

# http://localhost:8000/docs
# uvicorn src.api.api:app --reload

app = FastAPI(
    title="VendeFácil RAG API",
    description="API para perguntas ao sistema RAG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_rag_service() -> RAGService:
    return RAGService()

class AskRequest(BaseModel):
    question: str = Field(..., example="Qual é a política de reembolso?", description="A pergunta que o usuário deseja fazer ao sistema RAG.")
    permission: str = Field(..., example="publico", description="Nível de permissão ou perfil do usuário para filtragem de dados.")

class AskResponse(BaseModel):
    answer: str = Field(..., example="A política de reembolso permite devoluções em até 7 dias.", description="Resposta gerada pelo sistema RAG.")

class ErrorResponse(BaseModel):
    detail: str

@app.post(
    "/ask",
    response_model=AskResponse,
    summary="Realiza uma pergunta ao RAG",
    description="Processa a pergunta enviada considerando o nível de permissão do usuário e retorna a resposta gerada pelo sistema de IA.",
    responses={
        400: {"model": ErrorResponse, "description": "Erro nos parâmetros ou na requisição."},
        500: {"model": ErrorResponse, "description": "Erro interno ao processar o serviço RAG."}
    }
)
def ask(request: AskRequest, rag_service: RAGService = Depends(get_rag_service)):
    try:
        # Chamada ao serviço RAG injetado
        result = rag_service.ask(
            question=request.question,
            permission=request.permission
        )

        if not result or "answer" not in result:
            raise HTTPException(status_code=500, detail="O serviço RAG não retornou uma resposta válida.")

        return AskResponse(answer=result["answer"])

    except ValueError as ve:
        # Erros de validação de negócio ou parâmetros inválidos
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Tratamento genérico para falhas inesperadas de infraestrutura/IA
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")
