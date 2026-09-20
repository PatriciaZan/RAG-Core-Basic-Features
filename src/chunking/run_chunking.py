"""
run_chunking é a porta de entrada para processar os arquivos

"""

from pathlib import Path


from src.chunking.process_md import process_md
from src.chunking.process_txt import process_txt
from src.chunking.process_jsonl import process_jsonl
from src.generate_json.generate_json import generate_json


# Extensões aceitas pelo pipeline de chunking
SUPPORTED_EXTENSIONS = {
    ".md",
    ".txt",
    ".jsonl",
}


def get_data_folder(file_path: Path, data_folder: Path) -> str:
    relative_path = file_path.relative_to(data_folder)

    if not relative_path.parts:
        return ""
    return relative_path.parts[0]


def run_chunking(folder_path, output_folder_path):
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    folder = ROOT_DIR / 'data'
    output_folder = ROOT_DIR / "output" / "output_chunking"


    if not folder.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"O caminho informado não é uma pasta: {folder}")

    # Garante que /output/output_chunking exista
    output_folder.mkdir(parents=True, exist_ok=True)
    processors = {
        ".md": process_md,
        ".txt": process_txt,
        ".jsonl": process_jsonl,
    }

    resultados = []
    opcoes_validas = ["publico", "interno", "restrito"]

    print("\n" + "=" * 60)
    print("PROCESSAMENTO DE CHUNKING")
    print("=" * 60)
    print("\nComo deseja processar os arquivos?")
    print("  1 - Processar TODOS os arquivos da pasta")
    print("  2 - Processar UM arquivo específico")
    print("  3 - Processar por TIPO de arquivo")
    print("=" * 60)

    modo = None
    while modo not in ["1", "2", "3"]:
        choice = input("\nDigite a opção (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            modo = choice
        else:
            print("Opção inválida! Escolha 1, 2 ou 3.")

    arquivos_para_processar = []
    extensao_filtrada = None

    # ------------------------------------------------------------------------------------------------------------------
    # MODO 1 - TODOS
    if modo == "1":
        print("\nModo: Processar TODOS os arquivos")
        arquivos_para_processar = [
            file_path
            for file_path in folder.rglob("*")
            if file_path.is_file()
            and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

    # ------------------------------------------------------------------------------------------------------------------
    # MODO 2 - UM ARQUIVO
    elif modo == "2":
        print("\nModo: Processar UM arquivo específico")

        nome_arquivo = input(
            "Digite o nome exato do arquivo (ex: indicadores.md): "
        ).strip()

        arquivo_encontrado = None
        for file_path in folder.rglob("*"):
            if (
                file_path.is_file()
                and file_path.name == nome_arquivo
                and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
            ):
                arquivo_encontrado = file_path
                break

        if arquivo_encontrado:
            arquivos_para_processar = [arquivo_encontrado]
            print(f"Arquivo encontrado: {arquivo_encontrado}")
        else:
            print(
                f"Arquivo '{nome_arquivo}' não encontrado em {folder} "
                f"ou possui extensão não suportada."
            )
            return []

    # ------------------------------------------------------------------------------------------------------------------
    # MODO 3 - POR TIPO
    elif modo == "3":
        print("\nModo: Processar por TIPO de arquivo")
        print("  1 - Apenas arquivos .md")
        print("  2 - Apenas arquivos .txt")
        print("  3 - Apenas arquivos .json")

        tipo_choice = None

        while tipo_choice not in ["1", "2", "3"]:
            tipo = input("Digite a opção (1/2/3): ").strip()
            if tipo in ["1", "2", "3"]:
                tipo_choice = tipo
            else:
                print("Opção inválida! Escolha 1, 2 ou 3.")

        extensoes = {
            "1": ".md",
            "2": ".txt",
            "3": ".json",
        }

        extensao_filtrada = extensoes[tipo_choice]
        print(f"Filtrando apenas arquivos {extensao_filtrada}")
        arquivos_para_processar = [
            file_path
            for file_path in folder.rglob("*")
            if file_path.is_file()
            and file_path.suffix.lower() == extensao_filtrada
        ]

        if not arquivos_para_processar:
            print(
                f"Nenhum arquivo {extensao_filtrada} encontrado na pasta {folder}"
            )
            return []

    print(f"\nTotal de arquivos para processar: {len(arquivos_para_processar)}")
    print("=" * 60 + "\n")

    # ------------------------------------------------------------------------------------------------------------------
    # PROCESSAMENTO
    for file_path in arquivos_para_processar:
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()
        processor = processors.get(extension)

        if processor is None:
            print(f"Ignorando arquivo não suportado: {file_path.name}")
            continue

        if extensao_filtrada and extension != extensao_filtrada:
            continue

        # Tipo lógico do documento
        doc_type = file_path.parent.name

        # Pasta do primeiro nível dentro de /data
        data_folder = get_data_folder(file_path, folder)

        # --------------------------------------------------------------------------------------------------------------
        # SENSIBILIDADE
        print("\n" + "=" * 50)
        print(f"Arquivo encontrado: {file_path}")
        print(f"Tipo: {extension}")
        print(f"Pasta /data: {data_folder}")

        print("\nEscolha o nível de sensibilidade:")
        print("  1 - publico")
        print("  2 - interno")
        print("  3 - restrito")

        sensitivity = None

        while sensitivity not in opcoes_validas:
            choice = input(
                "Digite a opção (publico/interno/restrito): "
            ).strip().lower()

            if choice == "1":
                sensitivity = "publico"
            elif choice == "2":
                sensitivity = "interno"
            elif choice == "3":
                sensitivity = "restrito"
            elif choice in opcoes_validas:
                sensitivity = choice
            else:
                print(
                    "Opção inválida! Escolha entre: "
                    "publico, interno ou restrito."
                )

        print(
            f"\nProcessando '{file_path.name}' "
            f"com sensibilidade: [{sensitivity}]..."
        )

        # Cada arquivo gera seus próprios chunks isoladamente
        resultado = processor(
            file_path,
            doc_type,
            sensitivity
        )

        documento = {
            "source_file": file_path.name,
            "data_folder": data_folder,
            "doc_sensitivity": sensitivity,
            "doc_type": doc_type,
            "doc_extension": extension,
            "resultado": resultado,
        }

        resultados.append(documento)

        # Cada arquivo processado gera seu próprio JSON
        output_path = output_folder / f"{file_path.stem}.json"
        generate_json(
            documento,
            output_path
        )

    return resultados


# talvez padronizar isso aqui no futuro :/ agora não
BASE_DIR = Path(__file__).resolve().parent.parent
folder_path = BASE_DIR / "data"
output_folder_path = BASE_DIR / "output" / "output_chunking"

# executor para deixar bonitinho
if __name__ == "__main__":
    result = run_chunking(
        folder_path,
        output_folder_path
    )

    print("\n" + "=" * 60)
    print("PROCESSAMENTO CONCLUÍDO!")
    print("=" * 60)
    print(f"Total de arquivos processados: {len(result)}")

    if result:
        print(
            "Arquivos:",
            [doc["source_file"] for doc in result]
        )