from database.database_schema import DATABASE_SCHEMA, DATABASE_RELATIONSHIPS
from src.llm.llm_embedding import get_embedding

from src.query.query_analyzer import analyze_query
from src.query.postgres_retriever import PostgresRetriever
from src.query.vector_retriever import VectorRetriever
from src.query.context_builder import ContextBuilder
from src.llm.prompt_generator import PromptBuilder
from src.llm.llm_generate_response import LLMService

from pathlib import Path
import json

class RAGService:
    def __init__(
        self,
        faiss_index_path,
        faiss_documents_path,
    ):
        self.postgres_retriever = PostgresRetriever()
        self.vector_retriever = VectorRetriever(
            index_path=str(faiss_index_path),
            documents_path=str(faiss_documents_path)
        )

        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder(DATABASE_SCHEMA, DATABASE_RELATIONSHIPS)
        self.llm_service = LLMService()

    def ask(
        self,
        question: str,
        permission_level: str
    ):

        # 1. QUERY ANALYZER
        plan = analyze_query(
            query=question,
            permission_level=permission_level
        )

        # 2. POSTGRESQL RETRIEVAL
        postgres_result = None
        if plan.route in ("postgresql", "both"):
            postgres_plan = plan.postgres
            postgres_result = self.postgres_retriever.retrieve(
                postgres_plan,
                permission_level
            )

        # 3. FAISS VECTOR RETRIEVAL
        vector_result = None
        if plan.route in ("faiss", "both"):
            semantic_query = plan.vector.semantic_query
            query_embedding = get_embedding(semantic_query)
            vector_result = self.vector_retriever.retrieve(
                query_text=semantic_query,
                query_embedding=query_embedding,
                vector_plan=plan.vector,
                permission_level=permission_level,
                top_k=5
            )

        # 4. CONTEXT BUILDER
        context = self.context_builder.build(
            postgres_result=postgres_result,
            vector_result=vector_result
        )

        # 5. FORMATAR CONTEXTO PARA LLm
        context_str = json.dumps(
            context,
            ensure_ascii=False,
            indent=2
        )

        # 6. GERAR RESPOSTA FINAL
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

        # User prompt: pergunta + contexto
        user_response_prompt = f"""PERGUNTA DO USUÁRIO:
        {question}

            CONTEXTO RECUPERADO:
            {context_str}
            
            Com base na pergunta e no contexto fornecido acima, responda de forma clara e concisa."""

        # Chama LLM com system_prompt e user_prompt separados
        answer = self.llm_service.generate(
            system_prompt=system_response_prompt,
            user_prompt=user_response_prompt
        )

        # Retorna resposta final + metadados
        return {
            "answer": answer,
            "vector_result": vector_result,
            "postgres_result": postgres_result,
            "plan": plan
        }