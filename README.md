# Modular RAG (Retrieval-Augmented Generation) Application - STUDY
A modular RAG system designed with robust data ingestion pipelines, hybrid relational and vector retrieval, query authorization guards, and a dedicated API service layer.

## 🎯 Objectives
The primary goals of this project are for **study and testing** of the following functionalities:

1. **Modular Ingestion**: Cleanly parse and chunk multi-format documents (TXT, Markdown, JSON, CSV) to prepare unstructured data for embeddings.
2. **Hybrid Storage & Retrieval**: Combine relational databases (PostgreSQL) and vector indexes (FAISS) for precise similarity search and structured querying.
3. **Data Governance & Security**: Enforce row/vector-level security guardrails and query permissions before passing contexts to the LLM.
4. **Service-Oriented Architecture**: Wrap core RAG pipelines into clean micro-services and expose them via a FastAPI/Flask API layer.
5. **Benchmarking**: Maintain automated performance benchmarks to evaluate generation quality and retrieval accuracy.

## 📁 General Project Folder Structure
Simplified for show
```
src/
├── api/                  # API endpoints and application entry points
├── benchmark/            # Performance and accuracy evaluation scripts
├── chunking/             # Document parsers and chunking pipelines
├── database/             # Relational database schemas, connections, and repositories
├── embedding/            # Embedding generation utilities
├── generate_json/        # Bridge utilities converting vector formats to JSON
├── llm/                  # LLM clients, template builders, and prompt managers
├── query/                # Query analysis, context builders, and permission guards
├── rag/                  # Core orchestration services and end-to-end pipelines
│   ├── rag_faiss_only.py
│   ├── rag_service.py -> Can be tested by terminal
│   ├── rag_service_api.py -> This can be open in the FASTAPI browser /docs
│   └── test_rag_service.py
└── vectorstore/          # Vector index construction and similarity matching (FAISS)

```

## ⚙️ How to Execute
The project is not 100% finish, most of the executable are in the terminal, besides de `rag_service_api.py ` that opens for API /post service

1. Environment Setup
Clone the repository and install the required dependencies:
```
    pip install -r requirements.txt
```
- Make sure to configure your environment variables (e.g., API keys for your LLM provider, database connection strings) in a .env file at the root of your project.
- Make sure to create a local database in postgress

2. Data Ingestion & Chunking
Process raw documents and prepare chunks:
```
    python -m src.chunking.run_chunking
```

3. Generate Embeddings & Vector Index
Build vector representations and instantiate your vector database indices:
```
    python -m src.embedding.generate_embeddings
    python -m src.vectorstore.build_faiss
```

4. Run Tests & Validation
Validate the core RAG orchestration logic:
```
    python -m src.rag.test_rag_service
```

5. Launch the API Service
Start the backend server to serve RAG requests:
```
    python -m src.api.main
```

## 👓 Visual project structure

```

[ Raw Source Documents ]
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 1. CHUNKING & PREPARATION (`src/chunking/`)            │
│    • Ingests .txt, .md, .jsonl files                   │
│    • Splits documents into manageable text pieces      │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│ 2. STORAGE & INDEXING                                  │
│    ├── PostgreSQL Database (`src/database/`)           │
│    │     • Relational storage, schemas & connections   │
│    │     • Structured products & CSV/JSON processing   │
│    └── Vector Store (`src/vectorstore/`)               │
│          • Embedding generation (`src/embedding/`)     │
│          • FAISS index building & similarity search    │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│ 3. QUERY & SECURITY LAYER (`src/query/`)               │
│    • User inputs query                                 │
│    • Query Analyzer & Permissions (Guards access)      │
│    • Dual Retrievers (PostgreSQL + Vector Retriever)   │
│    • Context Builder (Assembles retrieved chunks)      │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│ 4. LLM & PROMPT ENGINEERING (`src/llm/`)               │
│    • LLM Client & Embedding configuration              │
│    • Prompt Templates & Generator                      │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│ 5. RAG CORE ORCHESTRATION (`src/rag/`)                 │
│    • Combines context + prompt + LLM execution         │
│    • Validated via RAG service tests                   │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│ 6. DEPLOYMENT & BENCHMARKING                           │
│    • API Exposure (`src/api/` & `rag_service_api.py`)  │
│    • Performance Evaluation (`src/benchmark/`)         │
└────────────────────────────────────────────────────────┘
```

---

_This is a OPEN project still, can have wrong parts in the code, as is my first "big" python project._  
:D


















