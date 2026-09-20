# A saída é um dict pronto para ser enviado de volta à LLM para responder.
#Junta os resultados do PostgreSQL e FAISSem um contexto único para a LLM.

class ContextBuilder:
    def build(
        self,
        postgres_result=None,
        vector_result=None
    ):

        context = {
            "postgresql": None,
            "vector": None
        }

        if postgres_result:
            context["postgresql"] = (
                self._build_postgres_context(
                    postgres_result
                )
            )

        if vector_result:
            context["vector"] = (
                self._build_vector_context(
                    vector_result
                )
            )

        return context

    # POSTGRESQL
    def _build_postgres_context(
        self,
        result
    ):

        return {
            "source": "postgresql",
            "row_count": result.get(
                "row_count",
                0
            ),
            "columns": result.get(
                "columns",
                []
            ),
            "rows": result.get(
                "rows",
                []
            )
        }

    # VECTOR
    def _build_vector_context(
        self,
        result
    ):

        documents = []
        for item in result.get(
            "results",
            []
        ):

            documents.append({
                "texto": item.get("texto"),
                "metadata": item.get(
                    "metadata",
                    {}
                ),
                "rrf_score": item.get("rrf_score")
            })

        return {
            "source": "faiss",
            "row_count": len(documents),
            "documents": documents
        }