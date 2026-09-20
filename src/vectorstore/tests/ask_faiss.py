# ask_faiss.py - Script interativo para fazer buscas no índice FAISS
# Permite o usuário digitar perguntas e ver resultados em tempo real

from pathlib import Path
from src.vectorstore.search_faiss import search_faiss

def display_results(results):

    # Exibe os resultados de forma formatada e bonita
    if not results:
        print("\n Nenhum resultado encontrado.")
        return

    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)

    for i, result in enumerate(results, start=1):
        document = result["document"]
        score = result["score"]

        # Exibe o número e a similaridade
        print(f"\n[{i}] Similaridade: {score:.4f}")
        # Exibe metadados
        print(f"   Chunk ID: {document.get('metadata', {}).get('chunk_id', 'N/A')}")
        print(f"   Arquivo: {document.get('metadata', {}).get('file_name', 'N/A')}")

        # Exibe preview do texto (primeiros 500 caracteres)
        texto = document.get("texto", "")
        preview = texto[:500] if len(texto) > 500 else texto

        print(f"\n   {preview}")

        if len(texto) > 500:
            print("   ...")

    print("\n" + "=" * 70)



def main():
    #Loop principal do programa
    print("\n" + "=" * 70)
    print("Vende Fácil - Busca de Documentos")
    print("=" * 70)
    print("\nDigite suas perguntas para fazer buscas no índice.")
    print("Comandos especiais:")
    print("  - 'top_k [número]' para mudar quantidade de resultados (padrão: 5)")
    print("  - 'sair' ou 'exit' para encerrar")
    print("=" * 70)

    # Configuração padrão
    top_k = 5

    while True:
        try:
            # Entrada do usuário
            query = input(" Digite sua pergunta: ").strip()

            # Verifica comandos especiais
            if query.lower() in ["sair", "exit"]:
                print(f"Programa encerrado!")
                break

            if query.lower().startswith("top_k"):
                try:
                    novo_top_k = int(query.split()[1])
                    top_k = novo_top_k
                    print(f"top_k alterado para {top_k}")
                except (IndexError, ValueError):
                    print("Use: top_k [número]")
                continue

            # Valida entrada vazia
            if not query:
                print("Por favor, digite uma pergunta.")
                continue

            # Faz a busca
            print(f" Buscando nos documentos (top_k={top_k})...")
            results = search_faiss(query, top_k=top_k)

            # Exibe resultados
            display_results(results)

        except KeyboardInterrupt:
            print("Programa interrompido pelo usuário.")
            break
        except FileNotFoundError as e:
            print(f" Erro: {e}")
            print("Certifique-se de que os arquivos index.faiss e documents.json existem.")
            break
        except Exception as e:
            print(f" Erro ao buscar: {e}")


if __name__ == "__main__":
    main()