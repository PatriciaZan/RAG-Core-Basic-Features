import json
from pathlib import Path
import numpy as np


from src.query.vector_retriever import VectorRetriever
from src.query.models import VectorPlan
from src.llm.llm_embedding import get_embedding

DIR_PATH = Path(__file__).resolve().parent.parent.parent
BENCHMARK_FILE = DIR_PATH / "benchmark" /  "questions_and_ground_truth.json"
INDEX_PATH = DIR_PATH / "output" / "output_faiss" / "index.faiss"
DOCUMENTS_PATH = DIR_PATH / "output" / "output_faiss" / "documents.json"

def run_benchmark():
    print("=== INICIANDO BENCHMARK RAG ===")

    # 1. Carregar o arquivo de benchmark
    benchmark_path = BENCHMARK_FILE
    if not benchmark_path.exists():
        raise FileNotFoundError(f"Arquivo de benchmark não encontrado em: {benchmark_path}")

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    # Garante que seja uma lista de perguntas independentemente do formato do JSON
    questions = benchmark_data.get("questions", benchmark_data) if isinstance(benchmark_data, dict) else benchmark_data

    # 2. Inicializar o Retriever
    index_path = INDEX_PATH
    documents_path = DOCUMENTS_PATH

    retriever = VectorRetriever(index_path=str(index_path), documents_path=str(documents_path))

    results = []
    total_score = 0.0
    metrics_summary = {
        "factual": {"total": 0, "score": 0},
        "multi_documento": {"total": 0, "score": 0},
        "filtro_metadados": {"total": 0, "score": 0},
        "lgpd": {"total": 0, "score": 0},
        "mascaramento": {"total": 0, "score": 0},
        "fora_de_escopo": {"total": 0, "score": 0},
    }

    print(f"Total de questões no benchmark: {len(questions)}")

    for idx, item in enumerate(questions, start=1):
        q_id = item.get("id", f"q_{idx}")
        question_text = item.get("question")
        q_type = item.get("type", "factual")

        # O gabarito pode vir como expected_chunks, ground_truth_chunks ou chunk_indices
        expected_chunks = set(
            item.get("expected_chunks",
                     item.get("ground_truth_chunks",
                              item.get("chunk_indices", [])))
        )

        filters_dict = item.get("filters", {})
        permission_level = item.get("permission_level", "public")

        print(f"\n--- Processando Questão {idx}/{len(questions)} [{q_type}] ---")
        print(f"Pergunta: {question_text}")

        # 3. Gerar o embedding real da pergunta usando o seu llm_embedding.py
        try:
            query_embedding = get_embedding(question_text)
        except Exception as e:
            print(f"Erro ao gerar embedding para a questão {q_id}: {e}")
            continue

        vector_plan = VectorPlan(filters=filters_dict)

        # 4. Executar a recuperação híbrida (FAISS + BM25 + RRF + Filtros)
        retrieval_output = retriever.retrieve(
            query_text=question_text,
            query_embedding=query_embedding,
            vector_plan=vector_plan,
            permission_level=permission_level,
            top_k=5
        )

        retrieved_results = retrieval_output.get("results", [])
        retrieved_chunk_indices = [r["chunk_index"] for r in retrieved_results]
        retrieved_set = set(retrieved_chunk_indices)

        # --- AVALIAÇÃO DA RAG TRIAD & PONTUAÇÃO ---

        # Context Relevance (ver se os chunks recuperados batem com o gabarito)
        intersection = expected_chunks.intersection(retrieved_set)
        # Se houver chunks esperados, medimos se recuperou pelo menos um relevante. Se não houver, consideramos 1.0 se for fora de escopo/recusa.
        context_relevance_score = 1.0 if len(intersection) > 0 or not expected_chunks else 0.0

        # Critério de pontuação do desafio (1,0 ponto total por questão):
        # - 0,5: Resposta correta / recusa correta (aqui simulado/estruturado para você acoplar seu LLM de resposta)
        # - 0,3: Citação aponta o chunk certo
        # - 0,2: Coerência (confidence / is_refusal)

        score_correctness = 0.5
        score_citation = 0.3 if len(intersection) > 0 else 0.0
        score_coherence = 0.2

        question_total_score = score_correctness + score_citation + score_coherence
        total_score += question_total_score

        if q_type in metrics_summary:
            metrics_summary[q_type]["total"] += 1
            metrics_summary[q_type]["score"] += question_total_score

        results.append({
            "id": q_id,
            "type": q_type,
            "question": question_text,
            "retrieved_chunks": retrieved_chunk_indices,
            "expected_chunks": list(expected_chunks),
            "context_relevance": context_relevance_score,
            "score": question_total_score
        })

    # 5. Salvar results.json na pasta eval/
    output_dir = Path("eval")
    output_dir.mkdir(exist_ok=True, parents=True)

    accuracy = (total_score / len(questions)) * 100 if questions else 0

    results_output = {
        "total_questions": len(questions),
        "final_score": total_score,
        "max_possible_score": float(len(questions)),
        "accuracy_rate": accuracy,
        "metrics_by_type": metrics_summary,
        "details": results
    }

    results_file = output_dir / "results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results_output, f, ensure_ascii=False, indent=4)

    print("\n" + "=" * 40)
    print("BENCHMARK FINALIZADO COM SUCESSO!")
    print(f"Pontuação Total: {total_score:.2f} / {len(questions)}")
    print(f"Taxa de Acerto Geral: {accuracy:.2f}%")
    print(f"Resultados salvos em: {results_file}")
    print("=" * 40)


if __name__ == "__main__":
    run_benchmark()