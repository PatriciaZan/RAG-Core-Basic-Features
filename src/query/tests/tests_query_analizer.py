from dataclasses import asdict
from src.query.query_analyzer import analyze_query

TESTS = [
    (
        "Quanto a empresa Drogaria Vida & Saúde vendeu em agosto?",
        "interno"
    )
]


for i, (question, permission) in enumerate(
    TESTS,
    start=1
):

    print("\n" + "=" * 70)
    print(f"TESTE {i}")
    print(f"Pergunta: {question}")
    print(f"Permissão: {permission}")

    plan = analyze_query(
        query=question,
        permission_level=permission
    )

    print("\nQueryPlan:")
    print(asdict(plan) )