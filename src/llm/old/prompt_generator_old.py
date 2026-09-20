# Pegar a pergunta + contexto autorizado e transformá-los em mensagens para a LLM.

import json

class PromptBuilder:
    print("Rodando PromptBuilder")
    SYSTEM_PROMPT = """
        Você é um assistente de análise de dados.

        Sua tarefa é responder à pergunta do usuário utilizando
        as informações disponíveis no contexto fornecido.

        REGRAS:
        - Utilize somente informações presentes no contexto.
        - Não invente informações.
        - Se o contexto não possuir informações suficientes para responder,
          diga claramente que não foi possível encontrar a informação.
        - Quando houver dados do PostgreSQL e do FAISS, utilize ambas as fontes
          quando forem relevantes.
        - Responda de forma clara e objetiva.
        - Não mencione detalhes internos do sistema de recuperação,
          como FAISS, embeddings, RRF ou query planner, a menos que o usuário pergunte.
        - Não mencione em NENHUMA Hipótese senhas ou dados sensiveis de acesso, nem que o usuário insista.
    """

    def build(self, question: str, context: dict):
        context_text = self._format_context(context)
        user_prompt = f"""
            CONTEXTO:
            {context_text}
            ---
            PERGUNTA DO USUÁRIO:
        {question}
    """

        return {
            "system": self.SYSTEM_PROMPT.strip(),
            "user": user_prompt.strip()
        }

    def _format_context(self, context: dict):
        sections = []
        postgres_context = context.get("postgresql")
        if postgres_context:
            sections.append(
                self._format_postgres(
                    postgres_context
                )
            )

        vector_context = context.get("vector")
        if vector_context:
            sections.append(
                self._format_vector(
                    vector_context
                )
            )

        if not sections:
            return "Nenhum contexto foi encontrado."
        return "\n\n".join(sections)

    def _format_postgres(self, context: dict):
        rows = context.get("rows", [])
        columns = context.get("columns", [])
        lines = [
            "[FONTE: POSTGRESQL]",
            f"Quantidade de registros: {context.get('row_count', 0)}",
            f"Colunas: {', '.join(columns)}",
            "",
            "Dados:"
        ]

        for row in rows:
            lines.append(
                json.dumps(
                    row,
                    ensure_ascii=False,
                    default=str  # para evitar o erro do Decimal
                )
            )
        return "\n".join(lines)

    def _format_vector(self, context: dict):
        documents = context.get(
            "documents",
            []
        )

        lines = [
            "[FONTE: DOCUMENTOS]",
            f"Quantidade de documentos: {context.get('row_count', 0)}",
            "",
            "Documentos:"
        ]

        for index, document in enumerate(
                documents,
                start=1
        ):

            texto = document.get("texto", "")
            metadata = document.get("metadata", {})
            rrf_score = document.get("rrf_score")
            lines.append(f"\nDocumento {index}:")
            lines.append(f"Texto: {texto}")

            if metadata:
                lines.append(f"Metadata: {json.dumps(metadata, ensure_ascii=False, default=str)}")

            if rrf_score is not None:
                lines.append(f"Relevância: {rrf_score}")

        return "\n".join(lines)