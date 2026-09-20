from src.database.database_schema import (
    DATABASE_SCHEMA,
    DATABASE_RELATIONSHIPS
)

from src.llm.llm_embedding import get_embedding

from src.query.query_analyzer import analyze_query
from src.query.postgres_retriever import PostgresRetriever
from src.query.vector_retriever import VectorRetriever
from src.query.context_builder import ContextBuilder

from src.llm.prompt_generator import PromptBuilder
from src.llm.llm_generate_response import LLMService

from pathlib import Path
import json

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

class RAGService:
    def __init__(
        self,
        faiss_index_path=FAISS_INDEX_PATH,
        faiss_documents_path=FAISS_DOCUMENTS_PATH,
    ):

        self.postgres_retriever = PostgresRetriever()
        self.vector_retriever = VectorRetriever(
            index_path=str(faiss_index_path),
            documents_path=str(faiss_documents_path)
        )

        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder(
            DATABASE_SCHEMA,
            DATABASE_RELATIONSHIPS
        )
        self.llm_service = LLMService()
        self.log_path = Path("log_old_answers.json")
        self._initialize_log()

    # LOG
    def _initialize_log(self):
        if not self.log_path.exists():
            self.log_path.write_text(
                "[]",
                encoding="utf-8"
            )

    def _save_log(
        self,
        question: str,
        permission: str,
        answer: str
    ):
        try:
            with self.log_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                logs = json.load(file)

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):
            logs = []
        logs.append({
            "question": question,
            "permission": permission,
            "answer": answer
        })
        with self.log_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                logs,
                file,
                ensure_ascii=False,
                indent=4
            )

    # ASK
    # oque esperar de resposta
    '''
        {
          "route": "faiss",
          "intent": "Obter a política de reembolso",
          "postgres": {"tables": [], "filters": {}},
          "vector": {"semantic_query": "política de reembolso"}
        }
    '''
    def ask(
        self,
        question: str,
        permission: str
    ):

        # 1. QUERY ANALYZER
        plan = analyze_query(
            query=question,
            permission_level=permission
        )

        # 2. POSTGRESQL
        #exemplo doque ele deve retornar
        '''
        {
            "row_count": 3,
            "columns": ["product_id", "name", "price"],
            "rows": [
                {"product_id": 1, "name": "Produto A", "price": 99.90},
                ...
            ]
        }
        '''
        postgres_result = None
        if plan.route in (
            "postgresql",
            "both"
        ):
            postgres_result = self.postgres_retriever.retrieve(
                plan.postgres,
                permission
            )


        # 3. FAISS / VECTOR SEARCH
        vector_result = None

        if plan.route in (
            "faiss",
            "both"
        ):

            semantic_query = plan.vector.semantic_query
            query_embedding = get_embedding(semantic_query)

            vector_result = self.vector_retriever.retrieve(
                query_text=semantic_query,
                query_embedding=query_embedding,
                vector_plan=plan.vector,
                permission_level=permission,
                top_k=5
            )

        # 4. CONSTRUIR CONTEXTO
        # junta o FAISS + SQL e fornece o contexto
        context = self.context_builder.build(
            postgres_result=postgres_result,
            vector_result=vector_result
        )

        # 5. FORMATAR CONTEXTO PARA A LLM
        context_str = json.dumps(
            context,
            ensure_ascii=False,
            indent=2
        )

        # 6. GERAR RESPOSTA FINAL
        # System prompt: instruções para responder perguntas com contexto
        system_response_prompt = """Você é um assistente útil que responde perguntas 
baseado em contexto fornecido.

Suas responsabilidades:
1. Ler a pergunta do usuário
2. Analisar o contexto fornecido (dados PostgreSQL e/ou documentos FAISS)
3. Responder de forma clara, concisa e baseada APENAS nas informações do contexto
4. Se o contexto não contiver informações suficientes, informar isso ao usuário
5. Ser sempre preciso e evitar especulações

Contexto pode vir de duas fontes:
- postgresql: dados estruturados (tabelas, colunas, valores)
- faiss: documentos e conteúdo textual recuperado"""

        # User prompt: pergunta + contexto recuperado
        user_response_prompt = f"""PERGUNTA DO USUÁRIO:
{question}

CONTEXTO RECUPERADO:
{context_str}

Com base na pergunta e no contexto fornecido acima, responda de forma clara e concisa."""

        # Chamada à LLM para gerar resposta final
        answer = self.llm_service.generate(
            system_prompt=system_response_prompt,
            user_prompt=user_response_prompt
        )

        # 7. SALVAR LOG
        self._save_log(
            question=question,
            permission=permission,
            answer=answer
        )

        # 8. RETORNO
        return {"answer": answer }