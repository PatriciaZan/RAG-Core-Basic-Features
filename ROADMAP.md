# RAG Application Development Roadmap & Architecture
_Made by me, Patrícia so I don't lose myself :)_

## Phase 1: Data Preparation & Chunking
Objective: Clean, process, and split source documents into manageable pieces for vectorization.

- Key Steps:
1. Create data intake channels for various formats `.json`, `.md`, `.txt`
2. Built an automated orchestration script to execute the chunking pipelines `run_chunking`

## Phase 2: Database Layer & Relational Schema
Objective: Establish the primary database connections, schema design, and ingestion scripts for structured and semi-structured assets.

- Key Steps
1. Setup connection and schema management scripts (Create DB in postgres!)
2. Create simplified database variants for lightweight testing (I want to see if the connection is OK)
3. Implemente specific parsing scripts for diverse data types `.csv`, `.json` (Maybe good idea to create separated?)
4. Establish database query repositories

## Phase 3: Embedding Generation & Vector Store

Objective: Generate vector representations of processed text chunks and build a high-performance vector retrieval index.

- Key Steps
1. Implemente embedding generation scripts (send the chunking json to add the embedding to new file)
2. Create secondary pipeline utilities to bridge embeddings into structured JSON formats (to create new json)
3. Develop FAISS vector indexing prototypes and production builders
4. Add vector search evaluation and similarity scoring tools (I want to test before running final version)

## Phase 4: LLM Integration & Prompt Engineering
Objective: Establish reliable interfaces with LLM providers and construct template frameworks for dynamic context injections.

- Key Steps:
1. Configure base API clients and embedding wrappers
2. Built generation execution handlers 9to generate response, maybe O will do inside the caller file first?)
3. Designed prompt management and formatting architecture(maybe in refactor i do this, little time :/)

## Phase 5: Advanced Query Processing & Retrieval Security
Objective: Refine search capabilities, build robust context builders, and implement data governance/permissions.
- Key Steps:
1. Develop the context assembly  
2. **Implemente dual retrieval mechanisms supporting both traditional relational databases and vector search**
I will make this work, SQL + FAISS using the permissions outside the LLM! - It worked :)
3. Add query comprehension layers including user intent analysis and dynamic building
4. Embedded permission and security guardrails to govern data access - Don't show passwords, not data that is not allowed LLM + permission

## Phase 6: Core RAG Orchestration & Services
Objective: Unify retrieval and generation modules into cohesive, testable service layers.  
REMEMBER - make some tests 
I did remember, `test_rag_service.py`

- Key Steps
1. Implemente end-to-end RAG workflows (name rag_service ?) OK

## Phase 7: Benchmarking & API Exposure
Objective: Evaluate accuracy/performance metrics and wrap the core logic into production-ready API endpoints  

I need to read the benchmarking file and generate responses in a json

- Key Steps
1. Implemente pipeline benchmarking frameworks
2. Expose the RAG service through web endpoints
I want to make an API for the front end, using FastAPI  
I did it :D `rag_service_api.py`