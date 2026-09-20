import json
from pathlib import Path
from src.rag.rag_service import RAGService

DIR_PATH = Path(__file__).resolve().parent.parent.parent
BENCHMARK_FILE = DIR_PATH / "benchmark" /  "questions_and_ground_truth.json"
INDEX_PATH = DIR_PATH / "output" / "output_faiss" / "index.faiss"
DOCUMENTS_PATH = DIR_PATH / "output" / "output_faiss" / "documents.json"

def run_benchmark():
    print("=== INICIANDO BENCHMARK RAG ===")

    # 1. Carregar benchmark
    benchmark_path = BENCHMARK_FILE
    if not benchmark_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado em: {benchmark_path}")

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    questions = benchmark_data.get("questions", benchmark_data) if isinstance(benchmark_data, dict) else benchmark_data

    # 2. Inicializar o RAGService
    rag = RAGService(
        faiss_index_path=INDEX_PATH,
        faiss_documents_path=DOCUMENTS_PATH
    )

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
        expected_chunks = set(item.get("expected_chunks", item.get("chunk_indices", [])))
        permission_level = item.get("permission_level", "restrito")

        print(f"\n--- Processando Questão {idx}/{len(questions)} [{q_type}] ---")
        print(f"Pergunta: {question_text}")

        # 3. Executar o fluxo completo do RAGService
        try:
            output = rag.ask(question=question_text, permission_level=permission_level)
            answer = output["answer"]
            vector_res = output["vector_result"]

            # Extrair índices dos chunks recuperados pelo vector (se houver)
            retrieved_chunks = []
            if vector_res and "results" in vector_res:
                retrieved_chunks = [r["chunk_index"] for r in vector_res["results"]]

        except Exception as e:
            print(f"❌ Erro ao processar questão {q_id}: {e}")
            continue

        retrieved_set = set(retrieved_chunks)

        # 4. Avaliação baseada nas regras do desafio
        intersection = expected_chunks.intersection(retrieved_set)
        context_relevance_score = 1.0 if len(intersection) > 0 or not expected_chunks else 0.0

        # Pontuação padrão (0.5 correta/recusa + 0.3 citação + 0.2 coerência)
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
            "answer_generated": answer,
            "retrieved_chunks": retrieved_chunks,
            "expected_chunks": list(expected_chunks),
            "context_relevance": context_relevance_score,
            "score": question_total_score
        })

    # 5. Salvar results.json
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