#
from pathlib import Path
from vectorstore.faiss_index import build_faiss_index

ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_DIR = ( ROOT_DIR / "output" / "output_embeddings")
OUTPUT_DIR = (ROOT_DIR /  "output" / "output_faiss")

# Cria os índices
build_faiss_index(INPUT_DIR,OUTPUT_DIR)