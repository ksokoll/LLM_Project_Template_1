# RAG-Pipeline Project Skeleton

## Projektstruktur

```
📁 project_root/
├── 📁 api/                      # FastAPI REST API
│   ├── __init__.py
│   └── main.py                  # API Endpoints
├── 📁 src/                      # Core Logic
│   ├── __init__.py
│   ├── config.py                # Configuration & Settings
│   ├── models.py                # Pydantic Data Models
│   ├── classifier.py            # Intent Classification
│   ├── retriever.py             # Knowledge Retrieval (Vector DB)
│   ├── generator.py             # LLM Response Generation
│   ├── quality_check.py         # Response Quality Validation
│   ├── answer_judge.py          # Answer Quality Scoring
│   ├── pipeline.py              # Main Pipeline Orchestration
│   ├── rate_limiter.py          # API Rate Limiting
│   └── utils.py                 # Helper Functions
├── 📁 data/
│   ├── 📁 knowledge_base/       # Source Documents
│   │   └── faq.jsonl            # Knowledge Base (JSONL format)
│   └── 📁 vector_db/            # FAISS Vector Store
│       ├── index.faiss          # (generated)
│       └── index.pkl            # (generated)
├── 📁 logs/                     # Application Logs
├── 📁 deployment/               # Deployment Scripts
│   └── deploy.sh
├── .env                         # Environment Variables
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Core Components

### 1. Configuration (`src/config.py`)
- Centralized settings using Pydantic BaseSettings
- Environment variable management
- API keys, model configs, paths

### 2. Data Models (`src/models.py`)
- Pydantic models for request/response validation
- Type safety across the pipeline
- Clear data contracts

### 3. Classifier (`src/classifier.py`)
- Intent classification using LLM
- Structured output (categories, confidence, reasoning)
- Decides routing logic

### 4. Retriever (`src/retriever.py`)
- Vector similarity search (FAISS)
- Loads knowledge base (JSONL)
- Returns top-k relevant documents

### 5. Generator (`src/generator.py`)
- LLM-based response generation
- Uses retrieved context + classification
- Structured prompts with guidelines

### 6. Quality Check (`src/quality_check.py`)
- Post-generation validation
- Checks: relevance, completeness, politeness, etc.
- Pass/fail + explanations

### 7. Answer Judge (`src/answer_judge.py`)
- Overall quality scoring (0-100)
- Weighted evaluation criteria
- Decision: accept/reject/manual_review

### 8. Pipeline (`src/pipeline.py`)
- Orchestrates all components
- Main `process(query)` method
- Returns complete result with metadata

### 9. API (`api/main.py`)
- FastAPI endpoints
- `/process` - full pipeline
- `/classify-only` - classification only
- Rate limiting, CORS, error handling

## Data Flow

```
User Query
    ↓
[Sanitize Input]
    ↓
[Classifier] → Intent + Category + Confidence (optional)
    ↓
[Retriever] → Top-K Relevant Docs (Vector Search)
    ↓
[Generator] → LLM Response (with context)
    ↓
[Quality Check] → Validation Checks incl. Answer Judge (optional)
    ↓
API Response (JSON)
```

Barebones Structure:

User Query
    ↓
Retreive
    ↓
Generate
    ↓
Response

## Key Patterns

1. **Modular Components**: Each step is isolated, testable
2. **Structured Outputs**: LLMs return JSON for reliability
3. **Multi-Stage Validation**: Classification → Generation → Quality → Judging
4. **JSONL Knowledge Base**: Easy to update, one Q&A per line
5. **Vector Search**: Fast semantic retrieval with FAISS
6. **Rate Limiting**: Protect API from abuse
7. **Environment Config**: Secrets in .env, never committed

## Technology Stack

- **Framework**: FastAPI
- **LLM**: OpenAI (GPT-4/3.5)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: FAISS (in-memory)
- **Validation**: Pydantic
- **Orchestration**: LangChain (optional)
- **Deployment**: Docker

## Environment Variables (.env)

```
OPENAI_API_KEY=your_api_key_here
# Optional: Azure Blob Storage for knowledge base
BLOB_CONNECTION_STRING=your_connection_string
BLOB_CONTAINER_NAME=your_container
```

## Usage Pattern

```python
# Initialize Pipeline
pipeline = CustomerSupportPipeline()

# Process Query
result = pipeline.process("Where is my order?")

# Returns:
{
    "classification": {...},
    "retrieved_docs": [...],
    "answer": "...",
    "quality_checks": {...},
    "quality_score": 92,
    "decision": "accept",
    "processing_time_ms": 1234
}
```
