# Primeira etapa de todo o processo.
# Processar o chunking dos arquivos .md .txt e .json

from pathlib import Path

from chunking.antigos.process_email_txt import process_email_txt
from src.chunking.process_jsonl import process_jsonl
from chunking.antigos.process_md2 import process_md
from src.generate_json.generate_json import generate_json


def run_chunking(folder_path, output_folder_path):
    folder = Path(folder_path)
    output_folder = Path(output_folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"O caminho informado não é uma pasta: {folder}")

    # Garante que a pasta de output na raiz do projeto exista (cria se não existir)
    output_folder.mkdir(parents=True, exist_ok=True)

    processors = {
        ".md": process_md,
        ".txt": process_email_txt,
        ".jsonl": process_jsonl,
    }

    resultados = []
    opcoes_validas = ["publico", "interno", "restrito"]

    # MENU INICIAL
    print("\n" + "=" * 60)
    print("PROCESSAMENTO DE CHUNKING")
    print("=" * 60)
    print("\nComo deseja processar os arquivos?")
    print("  1 - Processar TODOS os arquivos da pasta (padrão)")
    print("  2 - Processar UM arquivo específico (informar o nome)")
    print("  3 - Processar por TIPO de arquivo (.md, .txt ou .jsonl)")

    modo = None
    while modo not in ["1", "2", "3"]:
        choice = input("\nDigite a opção (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            modo = choice
        else:
            print("Opção inválida! Escolha 1, 2 ou 3.")

    # Lista de arquivos a serem processados
    arquivos_para_processar = []
    extensao_filtrada = None

    if modo == "1":
        # Processar tudo
        print("\nModo: Processar TODOS os arquivos")
        arquivos_para_processar = list(folder.rglob("*"))

    elif modo == "2":
        # Processar um arquivo específico
        print("\nModo: Processar UM arquivo específico")
        nome_arquivo = input("Digite o nome exato do arquivo (ex: email_01.txt): ").strip()

        # Tenta encontrar o arquivo na pasta (busca recursiva)
        arquivo_encontrado = None
        for file_path in folder.rglob("*"):
            if file_path.is_file() and file_path.name == nome_arquivo:
                arquivo_encontrado = file_path
                break

        if arquivo_encontrado:
            arquivos_para_processar = [arquivo_encontrado]
            print(f"Arquivo encontrado: {arquivo_encontrado.name}")
        else:
            print(f"Arquivo '{nome_arquivo}' não encontrado na pasta {folder}")
            return []

    elif modo == "3":
        # Processar por extensão
        print("\nModo: Processar por TIPO de arquivo")
        print("  1 - Apenas arquivos .md")
        print("  2 - Apenas arquivos .txt")
        print("  3 - Apenas arquivos .jsonl")

        tipo_choice = None
        while tipo_choice not in ["1", "2", "3"]:
            tipo = input("Digite a opção (1/2/3): ").strip()
            if tipo in ["1", "2", "3"]:
                tipo_choice = tipo
            else:
                print("Opção inválida! Escolha 1, 2 ou 3.")

        if tipo_choice == "1":
            extensao_filtrada = ".md"
            print("Filtrando apenas arquivos .md")
        elif tipo_choice == "2":
            extensao_filtrada = ".txt"
            print("Filtrando apenas arquivos .txt")
        else:
            extensao_filtrada = ".jsonl"
            print("Filtrando apenas arquivos .jsonl")

        # Filtra arquivos pela extensão
        for file_path in folder.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() == extensao_filtrada:
                arquivos_para_processar.append(file_path)

        if not arquivos_para_processar:
            print(f"Nenhum arquivo {extensao_filtrada} encontrado na pasta {folder}")
            return []

    print(f"\n📋 Total de arquivos para processar: {len(arquivos_para_processar)}")
    print("=" * 60 + "\n")
    # ========== FIM DO MENU INICIAL ==========

    # Itera sobre os arquivos selecionados
    for file_path in arquivos_para_processar:
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()
        processor = processors.get(extension)

        # quando encontrar os arquivos dos outros tipos
        if processor is None:
            print(f"Ignorando arquivo não suportado: {file_path.name}")
            continue

        # Se estiver no modo 3 (filtro por extensão), pula arquivos que não batem
        if extensao_filtrada and extension != extensao_filtrada:
            continue

        if extension == ".jsonl":
            doc_type = "ticket"
        else:
            doc_type = Path(file_path).stem

        # Aqui adicionei a opção de preencher o sensitivity manualmente
        print("\n" + "=" * 50)
        print(f"Arquivo encontrado: {file_path.name}")
        print("Escolha o nível de sensibilidade (1/2/3):")
        print("  1 - publico")
        print("  2 - interno")
        print("  3 - restrito")

        sensitivity = None
        while sensitivity not in opcoes_validas:
            choice = input("Digite a opção (publico/interno/restrito): ").strip().lower()
            # Atalhos numéricos opcionais para facilitar a digitação
            if choice == "1":
                sensitivity = "publico"
            elif choice == "2":
                sensitivity = "interno"
            elif choice == "3":
                sensitivity = "restrito"
            elif choice in opcoes_validas:
                sensitivity = choice
            else:
                print("Opção inválida! Escolha entre: publico, interno ou restrito.")

        print(f"Processando '{file_path.name}' com sensibilidade: [{sensitivity}]...")

        # Cada arquivo gera seus próprios chunks de forma isolada
        resultado = processor(file_path, doc_type, sensitivity)
        documento = {
            "source_file": file_path.name,
            "doc_sensitivity": sensitivity,
            "doc_type": doc_type,
            "doc_extension": extension,
            "resultado": resultado
        }
        resultados.append(documento)

        # Salvando o arquivo JSON individual diretamente na pasta /output_chunking da raiz
        output_path = output_folder / f"{file_path.stem}.json"
        generate_json(documento, output_path)

    return resultados


# Passando o caminho da pasta /data
BASE_DIR = Path(__file__).resolve().parent
folder_path = BASE_DIR / "../../data"
output_folder_path = BASE_DIR / "../../output_chunking"

result = run_chunking(folder_path, output_folder_path)
print(f"\n✅ PROCESSAMENTO CONCLUÍDO! ✅ ")
print(f"Total de arquivos processados: {len(result)}")
if result:
    print(f"Arquivos: {[doc['source_file'] for doc in result]}")
