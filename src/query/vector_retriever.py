#oque eu tenho que fazer aqui com base nos testes
#index.faiss → busca Dense
#documents.json → texto + metadata
#BM25 → busca lexical
#RRF → fusão dos rankings
#VectorPlan.filters → filtros de metadata
#top_k / fetch_k → controle de candidatos

import json
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from src.query.vector_permission_guard import (VectorPermissionGuard)
from src.query.models import VectorPlan

class VectorRetriever:
    def __init__(
        self,
        index_path: str,
        documents_path: str,
    ):
        self.index_path = Path(index_path)
        self.documents_path = Path(documents_path)

        self.faiss_index = None
        self.corpus_chunks = []
        self.bm25 = None

        self.permission_guard = (
            VectorPermissionGuard()
        )

        self._load()

    # CARREGAMENTO
    def _load(self):
        print("Carregando índice FAISS...")
        self._load_faiss()

        print("Carregando documentos...")
        self._load_documents()

        print("Construindo índice BM25...")
        self._build_bm25()

        print(
            f"Total de chunks disponíveis: "
            f"{len(self.corpus_chunks)}"
        )

    def _load_faiss(self):
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Índice FAISS não encontrado: "
                f"{self.index_path}"
            )

        self.faiss_index = faiss.read_index(
            str(self.index_path)
        )

    def _load_documents(self):
        if not self.documents_path.exists():
            raise FileNotFoundError(
                f"Arquivo de documentos não encontrado: "
                f"{self.documents_path}"
            )

        with open(
            self.documents_path,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        # Caso documents.json seja uma lista
        if isinstance(data, list):
            documents = data

        # Caso seja {"documents": [...]}
        elif isinstance(data, dict):
            documents = data.get(
                "documents",
                data.get("resultado", [])
            )
        else:
            raise ValueError("Formato inválido do documents.json.")

        for document in documents:
            if "texto" not in document:
                continue
            self.corpus_chunks.append({
                "texto": document["texto"],
                "metadata": document.get(
                    "metadata",
                    {}
                )
            })

        if not self.corpus_chunks:
            raise ValueError("Nenhum documento válido encontrado.")

        # O número de documentos precisa corresponder aos vetores do FAISS.
        if (
            self.faiss_index.ntotal
            != len(self.corpus_chunks)
        ):
            raise ValueError("Quantidade de vetores no FAISS não corresponde à quantidade de documentos.")

    def _build_bm25(self):
        tokenized_corpus = [
            chunk["texto"]
            .lower()
            .split()
            for chunk in self.corpus_chunks
        ]

        self.bm25 = BM25Okapi(tokenized_corpus)

    # BUSCA HÍBRIDA
    def retrieve(
        self,
        query_text: str,
        query_embedding: list,
        vector_plan: VectorPlan,
        permission_level: str,
        top_k: int = 5,
        fetch_k_multiplier: int = 4,
    ):
        total_docs = len(self.corpus_chunks)

        if total_docs == 0:
            return self._empty_result()

        # a permissão aqui
        permission_filters = (self.permission_guard.build_filters(permission_level))

        # BUSCA DENSE - FAISS
        fetch_k = min(total_docs,top_k * fetch_k_multiplier)

        dense_ranking = self._dense_search(query_embedding,fetch_k)
        #print("\n===== DENSE RANKING =====")

        #for rank, idx in enumerate(dense_ranking[:10], start=1):
            #print(rank,self.corpus_chunks[idx]["metadata"].get("file_name"),
         #       self.corpus_chunks[idx]["texto"][:150]
         #   )

        #  BUSCA - BM25
        bm25_ranking = self._bm25_search(query_text,fetch_k)
        #print("\n===== BM25 RANKING =====")

       # for rank, idx in enumerate(bm25_ranking[:10], start=1):
        #    print(rank,self.corpus_chunks[idx]["metadata"].get("file_name"),
        #        self.corpus_chunks[idx]["texto"][:150]
        #    )
        #  RRF
        fused_ranking = (self._reciprocal_rank_fusion(dense_ranking,bm25_ranking))
       # print("\n===== RRF RANKING =====")

        #for rank, (idx, score) in enumerate(
        #        fused_ranking[:10],
        #        start=1
        #):
        #    print(
        #        rank,
         #       f"score={score:.5f}",
          #      self.corpus_chunks[idx]["metadata"].get("file_name"),
          #      self.corpus_chunks[idx]["texto"][:150]
           # )

        # FILTROS DE METADATA
        # semânticos
        plan_filters = (
            vector_plan.filters
            if vector_plan
            else {}
        )
        # permissão controlada aqui
        final_filters = dict(plan_filters)
        # Sobrescreve/define sensitivity com o que o usuário realmente pode acessar.
        final_filters["sensitivity"] = permission_filters["sensitivity"]

        final_results = []

        #print("\n===== FILTROS =====")
        #print("Permission filters:", permission_filters)
        #print("Plan filters:", plan_filters)
        #print("Final filters:", final_filters)

        for idx, rrf_score in fused_ranking:
            chunk = self.corpus_chunks[idx]
            #print("\n===== TESTANDO DOCUMENTO =====")
            #print("idx:", idx)
            #print("arquivo:", chunk["metadata"].get("file_name"))
            #print("metadata:", chunk["metadata"])
            #print("final_filters:", final_filters)

            matches = self._matches_filters( chunk["metadata"],final_filters)
            print("MATCH:", matches)

            if not matches:
                #print("❌ DOCUMENTO REJEITADO PELO FILTRO")
                continue

            #print("✅ DOCUMENTO ACEITO")

            final_results.append({
                "texto": chunk["texto"],
                "metadata": chunk["metadata"],
                "rrf_score": rrf_score,
                "chunk_index": idx,
            })

            #print("\n===== DOCUMENTO ACEITO =====")
            #print("Chunk:", idx)
            #print("Arquivo:", chunk["metadata"].get("file_name"))
            #print("Sensitivity:", chunk["metadata"].get("sensitivity"))
            #print("Texto:", chunk["texto"][:500])

            if len(final_results) >= top_k:
                break

        #print("\n===== RESULTADO FINAL VECTOR =====")
        #print("Quantidade:", len(final_results))

        #for result in final_results:
         #   print(
         #       result["metadata"].get("file_name"),
         #       result["chunk_index"]
          #  )

        return {
            "source": "faiss",
            "row_count": len(
                final_results
            ),
            "results": final_results
        }

    # FAISS
    def _dense_search(
        self,
        query_embedding: list,
        fetch_k: int
    ):
        query_vector = np.array(
            [query_embedding],
            dtype=np.float32
        )
        faiss.normalize_L2(query_vector)
        distances, indices = (
            self.faiss_index.search(
                query_vector,
                fetch_k
            )
        )

        return [
            int(idx)
            for idx in indices[0]
            if idx != -1
        ]

    # BM25
    def _bm25_search(
        self,
        query_text: str,
        fetch_k: int
    ):
        tokenized_query = (
            query_text
            .lower()
            .split()
        )
        scores = self.bm25.get_scores(
            tokenized_query
        )
        ranking = np.argsort(
            scores
        )[::-1][:fetch_k]

        return [
            int(idx)
            for idx in ranking
        ]

    # RRF
    # ajuda da IA para elaborar calcular e entender
    def _reciprocal_rank_fusion(
        self,
        dense_results,
        bm25_results,
        k: int = 60
    ):

        rrf_scores = {}
        for rank, idx in enumerate(dense_results):
            rrf_scores[idx] = (
                rrf_scores.get(idx, 0.0)
                + 1.0 / (k + rank + 1)
            )

        for rank, idx in enumerate(bm25_results):
            rrf_scores[idx] = (
                rrf_scores.get(idx, 0.0)
                + 1.0 / (k + rank + 1)
            )

        return sorted(
            rrf_scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

    # METADATA FILTER
    # AQUI QUE TAVA O ERRO: onde estava eliminando todos os arquivos por estar comparando com um formato "sensitivity" errado
    def _matches_filters(
            self,
            metadata: dict,
            filters: dict
    ):
        if not filters:
            return True

        for field, expected_value in filters.items():
            # Se o documento não possui o campo exigido pelo filtro, tentamos mapear variações comuns
            # (ex: o filtro pede 'doc_sensitivity', mas no metadata está 'sensitivity')
            actual_field = field
            if field not in metadata and field == "doc_sensitivity" and "sensitivity" in metadata:
                actual_field = "sensitivity"
            elif field not in metadata and field == "sensitivity" and "doc_sensitivity" in metadata:
                actual_field = "doc_sensitivity"

            if actual_field not in metadata:
                return False

            actual_value = metadata.get(actual_field)

            # Lógica de comparação flexível (Lista vs String ou String vs Lista)
            if isinstance(expected_value, list):
                # Se o documento tem uma string (ex: "publico") e o filtro é uma lista (ex: ["publico", "interno"])
                if isinstance(actual_value, str):
                    if actual_value not in expected_value:
                        return False
                # Se ambos forem listas
                elif isinstance(actual_value, list):
                    if not any(val in expected_value for val in actual_value):
                        return False
                else:
                    return False
            else:
                # Se o esperado for string e o atual for lista
                if isinstance(actual_value, list):
                    if expected_value not in actual_value:
                        return False
                else:
                    if actual_value != expected_value:
                        return False
        return True
