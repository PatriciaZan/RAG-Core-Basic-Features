from pathlib import Path
from generate_json.embeddings_to_json import embeddings_to_json

CURRENT_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = CURRENT_DIR.parent

INPUT_DIR = ROOT_DIR / "output" / "output_chunking"
OUTPUT_DIR = ROOT_DIR / "output" / "output_embeddings"


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

opcoes_validas = ["ok", "pular", "exit"]

for input_file in INPUT_DIR.glob("*.json"):
    output_file = OUTPUT_DIR / input_file.name

    print("\n" + "=" * 60)
    print(f"Arquivo encontrado: {input_file.name}")
    print("Escolha uma opção:")
    print("  [ok]    - Prosseguir com a geração de embedding para este arquivo")
    print("  [pular] - Pular este arquivo e ir para o próximo")
    print("  [exit]  - Parar completamente a execução")

    acao = None
    while acao not in opcoes_validas:
        acao = input("Digite sua escolha (ok / pular / exit): ").strip().lower()
        if acao not in opcoes_validas:
            print("Opção inválida! Digite apenas 'ok', 'pular' ou 'exit'.")

    if acao == "exit":
        print("\nProcesso interrompido pelo usuário.")
        break

    if acao == "pular":
        print(f"Pulando o arquivo: {input_file.name}")
        continue

    # Se a escolha for 'ok', prossegue com os embedding
    print(f"\nProcessando e gerando embedding para: {input_file.name}")
    embeddings_to_json(
        input_file,
        output_file
    )

print("\nExecução de embedding finalizada!")