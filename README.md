# RAG Pipeline Skeleton

A production-ready skeleton for building RAG-based AI applications with classification, retrieval, generation, and quality validation.

## 🏗️ Architecture

```
User Query
    ↓
[1. Classifier] → Category + Confidence + Needs Context?
    ↓
[2. Retriever] → Top-K Relevant Documents (FAISS)
    ↓
[3. Generator] → LLM Response with Context
    ↓
[4. Quality Checker] → Multiple Validation Checks
    ↓
[5. Judge] → Accept / Reject / Manual Review
    ↓
API Response
```

## 📁 Project Structure

```
project/
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI endpoints
├── src/
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic data models
│   ├── classifier.py        # Intent classification
│   ├── retriever.py         # Vector search
│   ├── generator.py         # Response generation
│   ├── quality_check.py     # Quality validation
│   ├── answer_judge.py      # Final judgment
│   ├── pipeline.py          # Main orchestration
│   ├── rate_limiter.py      # API rate limiting
│   └── utils.py             # Helper functions
├── data/
│   ├── knowledge_base/
│   │   └── faq.jsonl        # Your knowledge base
│   └── vector_db/           # Auto-generated FAISS index
├── logs/                    # Application logs
├── .env                     # Environment variables (create from .env.example)
├── .env.example             # Environment template
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-...
```

### 3. Prepare Knowledge Base

Create your knowledge base in JSONL format:

```json
{"id": "q001", "category": "support", "query": "How do I reset my password?", "answer": "Click 'Forgot Password' on the login page...", "source": "KB_Auth"}
{"id": "q002", "category": "billing", "query": "How do I update my payment method?", "answer": "Go to Account Settings > Billing...", "source": "KB_Billing"}
```

Save as `data/knowledge_base/faq.jsonl`

### 4. Run the API

```bash
# Development mode
uvicorn api.main:app --reload

# Production mode
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Process a query
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "How do I reset my password?"}'
```

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📚 API Endpoints

### `POST /process`
Complete pipeline processing

**Request:**
```json
{
  "text": "Your query here",
  "metadata": {}  // optional
}
```

**Response:**
```json
{
  "query": "Your query",
  "classification": {
    "category": "support",
    "confidence": 0.95,
    "reasoning": "...",
    "needs_context": true
  },
  "retrieved_docs": ["...", "..."],
  "answer": "Generated response...",
  "quality_checks": {
    "checks": [...],
    "overall_score": 87.5,
    "passed_all": true
  },
  "judge_decision": {
    "decision": "accept",
    "confidence": 0.92,
    "reasoning": "...",
    "quality_score": 87.5
  },
  "processing_time_ms": 1234,
  "metadata": {}
}
```

### `POST /classify`
Classification only (no generation)

### `POST /retrieve`
Retrieval only (no generation)

### `GET /health`
Health check endpoint

## 🔧 Configuration

Edit `src/config.py` or use environment variables:

```python
# Model Configuration
CLASSIFIER_MODEL = "gpt-4o-mini"
GENERATOR_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# Pipeline Settings
RETRIEVAL_TOP_K = 3
MIN_CONFIDENCE_THRESHOLD = 0.7
QUALITY_SCORE_THRESHOLD = 70

# Rate Limiting
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60
```

## 🎯 Customization Guide

### 1. Update Classification Categories

Edit `src/classifier.py`:

```python
CATEGORIES = [
    "your_category_1",
    "your_category_2",
    "your_category_3"
]
```

### 2. Customize Quality Checks

Edit `src/quality_check.py` and add/modify check criteria:

```python
check_criteria = [
    {
        "name": "your_custom_check",
        "description": "Check description..."
    }
]
```

### 3. Adjust Judge Logic

Edit `src/answer_judge.py` to customize acceptance thresholds and decision logic.

### 4. Modify Response Generation

Edit `src/generator.py` to customize prompts, tone, and output format.

## 📊 Monitoring and Logging

The pipeline prints detailed logs for each step:

```
[1/5] Classifying query...
  → Category: support
  → Confidence: 0.95
  → Needs context: True

[2/5] Retrieving context...
  → Found 3 relevant documents

[3/5] Generating answer...
  → Answer length: 247 chars
  → Confidence: 0.88

[4/5] Checking quality...
  → Overall score: 87.5/100
  → Passed all checks: True

[5/5] Making judgment...
  → Decision: accept
  → Confidence: 0.92

✅ Processing complete in 1234ms
```

## 🔒 Security Considerations

- ✅ Input sanitization
- ✅ Rate limiting
- ✅ Environment variable management
- ✅ No secrets in code
- ⚠️ Configure CORS for production
- ⚠️ Add authentication/authorization as needed

## 📦 Production Checklist

- [ ] Configure production CORS origins
- [ ] Set up proper logging (e.g., to file/service)
- [ ] Add authentication middleware
- [ ] Configure rate limiting per user/API key
- [ ] Set up monitoring (e.g., Prometheus, DataDog)
- [ ] Add proper error tracking (e.g., Sentry)
- [ ] Use production-grade vector DB (e.g., Pinecone, Weaviate)
- [ ] Set up CI/CD pipeline
- [ ] Add comprehensive tests
- [ ] Configure backup for knowledge base

## 🧪 Testing

```bash
# Run with pytest (add tests in tests/ directory)
pytest tests/

# Test specific endpoint
pytest tests/test_api.py -v
```

## 📝 Knowledge Base Format

Your `data/knowledge_base/faq.jsonl` should contain one JSON object per line:

```json
{"id": "unique_id", "category": "category_name", "query": "Question?", "answer": "Answer text", "source": "Source identifier"}
```

**Fields:**
- `id`: Unique identifier
- `category`: Classification category
- `query`: The question/query
- `answer`: The gold standard answer
- `source`: Source document/section identifier

## 🤝 Contributing

This is a skeleton template. Customize it for your specific use case:

1. Update classification categories
2. Modify quality check criteria
3. Adjust judge decision logic
4. Customize prompts and tone
5. Add your domain-specific knowledge

## 📄 License

MIT License - use freely for your projects

## 🆘 Troubleshooting

**Vector DB not found:**
- Delete `data/vector_db/` and restart - it will rebuild

**Rate limit errors:**
- Adjust `RATE_LIMIT_REQUESTS` in config

**Low quality scores:**
- Review quality check criteria
- Adjust judge thresholds
- Improve knowledge base content

**Slow responses:**
- Use faster models (e.g., gpt-3.5-turbo)
- Reduce `RETRIEVAL_TOP_K`
- Consider caching common queries
