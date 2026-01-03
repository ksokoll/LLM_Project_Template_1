# LLM Project Template

> **A production-ready template for building LLM-powered applications with RAG (Retrieval-Augmented Generation)**
---

## Table of Contents

- [Purpose & Scope](#-purpose--scope)
- [Why This Template?](#-why-this-template)
- [Quick Start](#-quick-start)
- [Architecture Overview](#-architecture-overview)
- [Core Components](#-core-components)
- [Optional Components](#-optional-components)
- [Example Response](#-example-response)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Deployment](#-deployment)
- [Best Practices](#-best-practices)
- [Limitations & When NOT to Use](#-limitations--when-not-to-use)

---

## Purpose & Scope

When working with LLM systems for over a year now, I intuitively refined the way working with the technology. By heart, creating a system that
uses LLM-calls via API follows basic software-engineering principles that are decates old. Therefore, I tried to incorporate these best-practises
in my projects. The focus lays on output validation, as in my experience it is most critical in customer facing tools to really check what the LLM is telling the user.
Therefore the framework contains a lot of different safety checks, like relevance, coherence, accuracy, clarity, etc.

The framework changed from project to project, more components were added, others ditched. In the current state, I am very satisfied with it's functionality,
as it enables me to start from a pre-build framework for prototyping without copy-pasting from previous projects a lot.

My recommendation is that you test it out, and go module by module to really understand what's going on underneath the hood. Then, adjust it to your needs:
Cut out building blocks that are not particulary necessary for your project, or build new ones that enhance the system to your needs.

Overall, this template is designed for rapid prototyping and proof-of-concept development of LLM-powered applications, specifically focusing on:

- POCs and MVPs for LLM applications
- Customer-facing chatbots and Q&A systems
- Internal tools with AI-powered search

it is not recommended for:
- Enterprise-grade applications requiring complex state management
- Mission-critical systems needing state machines or workflow engines
- High-compliance environments (finance, healthcare) without modifications

### Design Philosophy

Key principles that guided the architecture:

1. **Separation of Concerns**: Business logic (Pipeline) is completely decoupled from API concerns (main.py)
2. **Type Safety**: Pydantic models ensure data validation throughout the pipeline
3. **Modularity**: Each component (Classifier, Retriever, Generator) is independently testable
4. **Production-Ready Patterns**: Includes rate limiting, CORS, health checks, and structured logging
5. **Extensibility**: Easy to add new steps, swap components, or integrate with other systems

### Why These Components?

** Optional: Classification**
- Enables conditional logic (skip retrieval for simple queries)
- Provides routing capability for future multi-pipeline architectures
- Enables tracking of categories for BI

**Vector Search (FAISS):**
- Semantic search finds relevant content beyond keyword matching
- Lightweight and fast for <100K documents
- No external database dependency for getting started

**Two-Step Quality Validation:**
- Catches hallucinations and off-topic responses before they reach users
- Enables Human-in-the-Loop (HITL) workflows for edge cases by an internal answer-judge
- Provides metrics for continuous improvement
- Can produce high inference costs though, can be setup more lightweight if needed

**Pydantic Models:**
- Ensures type safety across the entire pipeline
- Automatic API documentation via FastAPI
- Runtime validation prevents silent failures

---

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API Key
- (Optional) Azure Blob Storage for knowledge base
- .env setup (see Chapter "Configuration")

### Installation

```bash
# Clone the repository
git clone https://github.com/ksokoll/LLM-Project-Template-1.git
cd LLM-Project-Template-1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### First Run

Setup the .env varible like discibed in the Chapter "Config". You can copy-paste the values and manually adjust them afterwards.
Then:
```bash
# Start the API server
uvicorn api.main:app --reload

# Open your browser
# - API Docs: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health

# Test with example script
python example_usage.py
```

### Your First Query

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "How do I reset my password?"}'
```

---

## Architecture Overview

**API Layer** (`main.py`)
- Rate Limiter
- CORS
- Request Validation

↓

**Application Layer** (`pipeline.py` & Helper-Files)
- User Query
  - **1. Classifier** → Intent + Category + Confidence
  - **2. Retriever** → Top-K Relevant Documents (Vector Search)
  - **3. Generator** → LLM Response with Context
  - **4. Quality Check** → Multi-Criteria Validation
  - **5. Judge** → Accept / Reject / Manual Review
  - Response (JSON)

↓

**Infrastructure Layer** (`config.py`)
- OpenAI API
- FAISS Index
- Config (Pydantic)


### Data Flow

```python
# 1. Request arrives
POST /process
Body: {"text": "How do I reset my password?"}

# 2. API Layer
→ Rate Limiting: Check request count
→ Validation: Parse JSON → UserQuery model
→ Sanitization: Clean input text

# 3. Pipeline Orchestration
→ Classification: 
   Result: {category: "technical_support", confidence: 0.95, needs_context: true}

→ Retrieval (conditional):
   Query: "How do I reset my password?"
   Result: [Doc1, Doc2, Doc3] (vector similarity search)

→ Generation:
   Input: Query + Classification + Retrieved Docs
   Result: {answer: "To reset your password...", confidence: 0.88}

→ Quality Check:
   Checks: [relevance, completeness, accuracy, clarity, professionalism]
   Result: {overall_score: 87.5, passed_all: true}

→ Judge:
   Decision: "accept" (score >= threshold, confidence high)

# 4. Response
{
  "classification": {...},
  "retrieved_docs": [...],
  "answer": "To reset your password...",
  "quality_checks": {...},
  "judge_decision": {...},
  "processing_time_ms": 1234
}
```

---

## Core Components: Without these componends, the App will not run properly.

### 1. Config (`src/config.py`)

the config offers Centralized settings management using Pydantic

It offers:
- Environment variable loading from `.env`
- Type validation for all settings
- Sensible defaults for rapid prototyping

```python
class Settings(BaseSettings):
    openai_api_key: str
    classifier_model: str = "gpt-4o-mini"
    generator_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    retrieval_top_k: int = 3
    quality_score_threshold: int = 70
```

Why do we use pydantic?
- Automatic type conversion (string → int, string → bool)
- Validation on startup (fails fast if config is wrong)
- Easy to extend for new parameters
- Works seamlessly with `.env` files

Pydantic is not necessary to run the system. It proved as a worthy compagnion though, as it lifts a lot of the 
validation and standardizing-burden from you. If you create such a system for the first time, it can be useful
not to use pydantic by purpose to learn conversion/validation on your own, so you konw what pydantic does and what it doesn't.
---

### 2. Data Models (`src/models.py`)

Data Models provide Type-safe data structures for the entire pipeline

```python
UserQuery          # API input
Classification     # Classifier output
GeneratedAnswer    # Generator output
QualityCheckResult # Quality checker output
JudgeDecision      # Final judgment
PipelineResult     # Complete pipeline response
```

Pydantic models help with:
- **Type Safety:** IDE autocomplete, compile-time checks
- **Validation:** Automatic data validation at runtime
- **Documentation:** Self-documenting code, auto-generated API docs
- **Serialization:** Easy JSON conversion with `.model_dump()`

Example:
```python
class Classification(BaseModel):
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)  # Validates 0-1 range
    reasoning: str
    needs_context: bool
```

---

### 3. Classifier (`src/classifier.py`)

Purpose: Determine user intent and query category

1. Receives user query
2. Calls LLM with structured output format (JSON)
3. Returns classification with confidence score
4. Decides if knowledge retrieval is needed

Features:
- Customizable categories
- Confidence scoring
- Conditional retrieval logic

```python
class IntentClassifier:
    CATEGORIES = [
        "general_inquiry",
        "technical_support",
        "billing_question",
        "product_info",
        "complaint",
        "other"
    ]
    
    def classify(self, query: str) -> Classification:
        # LLM call with structured output
        # Returns: category, confidence, reasoning, needs_context
```

The classification:
Skips expensive retrieval for simple queries
Enables multi-pipeline architectures
Tracks user intent patterns

---

### 4. Retriever (`src/retriever.py`)

Finds relevant documents using semantic search.

The retriever:
1. Loads knowledge base from `faq.jsonl`
2. Creates embeddings for all Q&A pairs
3. Builds FAISS vector index
4. Performs similarity search on user query

```python
class KnowledgeRetriever:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = self._load_or_create_db()
    
    def retrieve(self, query: str, k: int = 3) -> list[str]:
        # Returns top-k most similar documents
```

FAISS advantages:
- No database required - runs in-memory, persists to disk
- Fast - optimized for vector similarity
- Handles 100K+ documents efficiently
- Simple - no external dependencies or setup

**Knowledge Base Format (`faq.jsonl`):**
```json
{"id": "q001", "category": "technical", "query": "How do I reset my password?", "answer": "...", "source": "KB_Auth"}
{"id": "q002", "category": "billing", "query": "How do I update my payment method?", "answer": "...", "source": "KB_Billing"}
```

---

### 5. Generator (`src/generator.py`)

Generates contextual responses using LLM.

The generator:
1. Receives query, classification, and retrieved documents
2. Builds system prompt based on classification
3. Builds user prompt with query + context
4. Calls LLM with structured output
5. Returns answer with metadata

```python
class ResponseGenerator:
    def generate(
        self, 
        query: str, 
        classification: Classification,
        context_docs: list[str]
    ) -> GeneratedAnswer:
        # Builds prompts
        # LLM call
        # Returns: answer, sources_used, confidence
```

Structured output benefits:
- Guarantees valid JSON format
- No need for regex or string manipulation
- Easy to extract confidence, sources, etc.

---

### 6. Quality Checker (`src/quality_check.py`)

Validates response quality before returning to user.

How it works:
1. Runs multiple quality checks via LLM
2. Each check returns: pass/fail, explanation, score
3. Calculates overall quality score
4. Identifies which checks failed

**Quality Criteria:**
- **Relevance:** Does it address the query?
- **Completeness:** Is it thorough?
- **Accuracy:** Is it factually correct?
- **Clarity:** Is it easy to understand?
- **Professionalism:** Is the tone appropriate?

```python
class QualityChecker:
    def check_quality(
        self,
        query: str,
        answer: str,
        context_docs: list[str]
    ) -> QualityCheckResult:
        # Runs 5+ quality checks
        # Returns: checks[], overall_score, passed_all
```

This catches:
- Hallucinations and off-topic responses
- Low-quality answers before they reach users
- Weak areas in your system for improvement

---

### 7. Answer Judge (`src/answer_judge.py`)

Makes final decision on response quality, sets Human-in-the-Loop if necessary.

The judge:
1. Evaluates quality score + classification confidence
2. Applies decision thresholds
3. Returns: accept, reject, or manual_review

**Decision Logic:**
```python
if quality_score >= 90 and classification_confidence >= 0.8:
    return "accept"
elif quality_score >= threshold and classification_confidence >= 0.6:
    return "accept"
elif quality_score >= 50:
    return "manual_review"  # HITL
else:
    return "reject"
```

Benefits:
- Easy to adjust thresholds without touching other code
- Clear decision points for human intervention
- Track accept/reject ratios over time

---

### 8. Pipeline (`src/pipeline.py`)

Orchestrates all components into a cohesive workflow.

```python
class Pipeline:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.retriever = KnowledgeRetriever()
        self.generator = ResponseGenerator()
        self.quality_checker = QualityChecker()
        self.judge = AnswerJudge()
    
    def process(self, query: str) -> dict:
        # Step 1: Classify
        classification = self.classifier.classify(query)
        
        # Step 2: Retrieve (conditional)
        docs = []
        if classification.needs_context:
            docs = self.retriever.retrieve(query)
        
        # Step 3: Generate
        answer = self.generator.generate(query, classification, docs)
        
        # Step 4: Quality Check
        quality = self.quality_checker.check(query, answer.answer, docs)
        
        # Step 5: Judge
        decision = self.judge.judge(quality, classification.confidence)
        
        return {
            "classification": classification.model_dump(),
            "retrieved_docs": docs,
            "answer": answer.answer,
            "quality_checks": quality.model_dump(),
            "judge_decision": decision.model_dump(),
            "processing_time_ms": elapsed_time
        }
```

Separate pipeline means:
- Can be used in API, CLI, batch jobs, tests
- No HTTP or API-specific logic
- Easy to test without mocking HTTP
- Clear workflow

---

### 9. API Layer (`api/main.py`)

Exposes pipeline via REST API.

```python
GET  /              # Quick health check
GET  /health        # Detailed health status
POST /process       # Full pipeline
POST /classify      # Classification only
POST /retrieve      # Retrieval only
```

Features:
- Automatic docs at `/docs` (Swagger UI)
- Type validation via Pydantic
- CORS for frontend integration
- Rate limiting (optional, see below)
- Clean error responses

The separation means:
- API logic ≠ Business logic
- Same pipeline works in API, CLI, batch, tests
- Test business logic without HTTP mocking

---

## Optional Components

### Rate Limiter (`src/rate_limiter.py`)

Prevents API abuse and controls costs.

```python
class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = defaultdict(list)
    
    def check(self, request: Request):
        if not self.is_allowed(request.client.host):
            raise HTTPException(429, "Too many requests")
```

Use cases:
- Public APIs without authentication
- Cost control for expensive LLM calls
- Protection against DoS attacks

**Limitations:**
- In-memory only (resets on server restart)
- Not suitable for multi-server deployments
- For production, consider Redis-based rate limiting

---

### CORS Middleware

Allows cross-origin requests from web frontends.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # Development: all origins
    # allow_origins=["https://myapp.com"],  # Production: specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Security:**
- **Development:** `allow_origins=["*"]` is fine
- **Production:** Specify exact domains to prevent CSRF

---


### Lifecycle Events

**Purpose:** Initialization and cleanup

```python
@app.on_event("startup")
async def startup_event():
    print("API Server Starting...")
    # Validate configuration
    # Check API keys
    # Warm up models

@app.on_event("shutdown")
async def shutdown_event():
    print("API Server Shutting Down...")
    # Save cache
    # Close connections
    # Cleanup resources
```

**Use Cases:**
- Configuration validation on startup
- Database connection pooling
- Cache warmup
- Graceful shutdown


#### Example Final Response:

```python
# pipeline.py returns:
result = {
    "query": "How do I reset my password?",
    "classification": {
        "category": "technical_support",
        "confidence": 0.95,
        "reasoning": "User is asking about password reset procedure",
        "needs_context": True
    },
    "retrieved_docs": [
        "Q: How do I reset my password?\nA: Click 'Forgot Password'...",
        "Q: I forgot my login credentials\nA: Use the password reset...",
        "Q: Change password procedure\nA: Go to Settings > Security..."
    ],
    "answer": "To reset your password, follow these steps:\n\n1. Go to the login page\n2. Click 'Forgot Password'\n3. Enter your email address\n4. Check your email for the reset link\n5. Click the link and create a new password\n\nThe reset link expires in 24 hours. If you have any issues, contact support.",
    "quality_checks": {
        "checks": [
            {"check_name": "relevance", "passed": True, "score": 0.95, "explanation": "Directly answers query"},
            {"check_name": "completeness", "passed": True, "score": 0.90, "explanation": "Provides step-by-step guide"},
            {"check_name": "accuracy", "passed": True, "score": 0.92, "explanation": "Matches knowledge base"},
            {"check_name": "clarity", "passed": True, "score": 0.88, "explanation": "Well-structured, easy to follow"},
            {"check_name": "professionalism", "passed": True, "score": 0.85, "explanation": "Helpful and courteous"}
        ],
        "overall_score": 90.0,
        "passed_all": True
    },
    "judge_decision": {
        "decision": "accept",
        "confidence": 0.915,
        "reasoning": "High quality score and high classification confidence",
        "quality_score": 90.0
    },
    "processing_time_ms": 1847.23,
    "metadata": {
        "sources_used": ["q001", "q002"],
        "generator_confidence": 0.88
    }
}

# → FastAPI converts to JSON
# → Returns HTTP 200 with JSON body
```

#### **Client Receives Response**

```json
{
  "classification": {
    "category": "technical_support",
    "confidence": 0.95,
    "reasoning": "User is asking about password reset procedure",
    "needs_context": true
  },
  "retrieved_docs": ["...", "...", "..."],
  "answer": "To reset your password, follow these steps:\n\n1. Go to the login page\n2. Click 'Forgot Password'\n3. Enter your email address\n4. Check your email for the reset link\n5. Click the link and create a new password\n\nThe reset link expires in 24 hours. If you have any issues, contact support.",
  "quality_checks": {
    "overall_score": 90.0,
    "passed_all": true,
    "checks": [...]
  },
  "judge_decision": {
    "decision": "accept",
    "confidence": 0.915,
    "reasoning": "High quality score and high classification confidence",
    "quality_score": 90.0
  },
  "processing_time_ms": 1847.23
}
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional: Azure Blob Storage
BLOB_CONNECTION_STRING=your_azure_connection_string
BLOB_CONTAINER_NAME=your_container_name
KNOWLEDGE_BLOB_NAME=example.jsonl

# Model Configuration
CLASSIFIER_MODEL=gpt-4o-mini
GENERATOR_MODEL=gpt-4o-mini
QUALITY_CHECK_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Pipeline Settings
RETRIEVAL_TOP_K=3
MIN_CONFIDENCE_THRESHOLD=0.7
QUALITY_SCORE_THRESHOLD=70

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
```

### Customizing Categories

Edit `src/classifier.py`:

```python
class IntentClassifier:
    CATEGORIES = [
        "your_category_1",
        "your_category_2",
        "your_category_3"
    ]
```

### Customizing Quality Checks

Edit `src/quality_check.py`:

```python
check_criteria = [
    {"name": "relevance", "description": "Does the answer..."},
    {"name": "your_custom_check", "description": "Check if..."},
    # Add more checks
]
```

### Adjusting Judge Thresholds

Edit `src/answer_judge.py`:

```python
def judge(self, quality_result, classification_confidence):
    if quality_score >= 95:  # Your custom threshold
        decision = "accept"
    elif quality_score >= 80:  # Your custom threshold
        decision = "manual_review"
    else:
        decision = "reject"
```

---

## API Endpoints

### `GET /`
Quick health check

**Response:**
```json
{
  "message": "AI Pipeline API",
  "status": "running",
  "version": "1.0.0"
}
```

---

### `GET /health`
Detailed health status

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "classifier": "ok",
    "retriever": "ok",
    "generator": "ok",
    "quality_checker": "ok",
    "judge": "ok"
  }
}
```

---

### `POST /process`
Complete pipeline processing

**Request:**
```json
{
  "text": "How do I reset my password?",
  "metadata": {
    "user_id": "123",
    "session_id": "abc"
  }
}
```

**Response:**
```json
{
  "classification": {
    "category": "technical_support",
    "confidence": 0.95,
    "reasoning": "...",
    "needs_context": true
  },
  "retrieved_docs": ["...", "...", "..."],
  "answer": "To reset your password...",
  "quality_checks": {
    "overall_score": 90.0,
    "passed_all": true,
    "checks": [...]
  },
  "judge_decision": {
    "decision": "accept",
    "confidence": 0.92,
    "reasoning": "...",
    "quality_score": 90.0
  },
  "processing_time_ms": 1234.56
}
```

---

### `POST /classify`
Classification only (debugging)

**Request:**
```json
{
  "text": "How do I reset my password?"
}
```

**Response:**
```json
{
  "category": "technical_support",
  "confidence": 0.95,
  "reasoning": "User is asking about password reset",
  "needs_context": true
}
```

---

### `POST /retrieve`
Retrieval only (debugging)

**Request:**
```json
{
  "text": "How do I reset my password?"
}
```

**Response:**
```json
{
  "query": "How do I reset my password?",
  "retrieved_docs": [
    "Q: How do I reset my password?\nA: Click 'Forgot Password'...",
    "Q: I forgot my login credentials\nA: Use the password reset...",
    "Q: Change password procedure\nA: Go to Settings > Security..."
  ]
}
```

---

## Deployment

### Docker

```bash
# Build image
docker build -t llm-api .

# Run container
docker run -p 8000:8000 --env-file .env llm-api
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Checklist

- [ ] Set specific CORS origins (not `["*"]`)
- [ ] Use environment-specific `.env` files
- [ ] Set up proper logging (file/service)
- [ ] Add authentication middleware
- [ ] Configure rate limiting per user/API key
- [ ] Set up monitoring (Prometheus, DataDog, etc.)
- [ ] Add error tracking (Sentry)
- [ ] Use production vector DB (Pinecone, Weaviate)
- [ ] Set up CI/CD pipeline
- [ ] Add comprehensive tests
- [ ] Configure backup for knowledge base

---

## Best Practices

### 1. Knowledge Base Maintenance

- Keep answers concise (2-3 paragraphs max)
- Include sources for fact-checking
- Use consistent formatting

**Rebuild Vector Index:**
```bash
# Delete existing index
rm -rf data/vector_db/

# Restart server (rebuilds automatically)
uvicorn api.main:app --reload
```

---

### 2. Monitoring & Analytics

**Track These Metrics:**
- Requests per endpoint
- Average processing time
- Classification distribution
- Quality score distribution
- Accept/reject/manual_review ratios
- Top failed queries

**Implementation:**
```python
# Add logging to pipeline.py
import logging

logger = logging.getLogger(__name__)

class Pipeline:
    def process(self, query: str):
        logger.info(f"Processing query: {query[:50]}...")
        
        classification = self.classifier.classify(query)
        logger.info(f"Classification: {classification.category} ({classification.confidence})")
        
        # ... rest of pipeline
        
        logger.info(f"Decision: {decision.decision}, Score: {quality.overall_score}")
```

---

### 3. Cost Optimization

**LLM Call Costs:**
- Classification: ~500 tokens/query
- Generation: ~1500 tokens/query
- Quality Check: ~2000 tokens/query (5 checks)

**Total:** ~4000 tokens/query

**Optimization Strategies:**
1. **Skip Quality Checks for High Confidence:**
   ```python
   if classification.confidence >= 0.95:
       # Skip quality checks, auto-accept
   ```

2. **Reduce Quality Checks:**
   ```python
   # Only check relevance + accuracy (not all 5)
   ```

3. **Use Cheaper Models:**
   ```python
   # Classification: gpt-3.5-turbo (cheaper)
   # Generation: gpt-4o-mini (quality)
   ```

4. **Cache Common Queries:**
   ```python
   # Add caching layer in pipeline
   if query in cache:
       return cache[query]
   ```

---

### 4. Testing

**Unit Tests:**
```python
# test_classifier.py
def test_classifier():
    classifier = IntentClassifier()
    result = classifier.classify("How do I reset my password?")
    
    assert result.category == "technical_support"
    assert result.confidence > 0.7
    assert result.needs_context == True
```

**Integration Tests:**
```python
# test_pipeline.py
def test_pipeline():
    pipeline = Pipeline()
    result = pipeline.process("How do I reset my password?")
    
    assert result["classification"]["category"] == "technical_support"
    assert result["answer"] != ""
    assert result["judge_decision"]["decision"] in ["accept", "reject", "manual_review"]
```

**API Tests:**
```python
# test_api.py
from fastapi.testclient import TestClient

client = TestClient(app)

def test_process_endpoint():
    response = client.post("/process", json={"text": "test query"})
    assert response.status_code == 200
    assert "answer" in response.json()
```

---

### 5. Extending the Template

**Add a New Component:**

```python
# src/sentiment_analyzer.py
class SentimentAnalyzer:
    def analyze(self, text: str) -> SentimentResult:
        # LLM call
        return SentimentResult(sentiment="positive", confidence=0.9)

# src/pipeline.py
class Pipeline:
    def __init__(self):
        # ... existing components
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def process(self, query: str):
        # ... existing steps
        sentiment = self.sentiment_analyzer.analyze(query)
        # Add to result
```

**Add a New Endpoint:**

```python
# api/main.py
@app.post("/sentiment")
async def analyze_sentiment(query: UserQuery):
    result = pipeline.sentiment_analyzer.analyze(query.text)
    return result.model_dump()
```

---

## Limitations & When NOT to Use

### Technical Limitations

**1. Vector Database (FAISS):**
- In-memory only (limited by RAM)
- Not suitable for >1M documents
- No real-time updates (requires rebuild)
- Single-server only (not distributed)

---

**2. Rate Limiting:**
- In-memory (resets on restart)
- IP-based only (not user-based)
- No distributed rate limiting

---

**3. State Management:**
- Stateless design (no conversation history)
- Each query is independent
- No multi-turn dialogue support

If yu need conversations (chatbot):
- Add conversation history to context
- Use session storage (Redis)
- Consider LangGraph for complex state machines

---

**4. Quality Checks:**
- LLM-based (slow, expensive)
- May give false positives/negatives
- No ground truth validation

**Solution:**
- Use rule-based checks for known patterns
- Implement few-shot learning for quality checks
- Add human feedback loop for continuous improvement

---


## License

MIT License

---

## Acknowledgments

This template was built on the shoulders of giants:

- **FastAPI** - For the excellent web framework
- **Pydantic** - For making Python type-safe
- **LangChain** - For LLM abstractions and tooling
- **OpenAI** - For the powerful language models
- **FAISS** - For fast vector similarity search

Special thanks to the open-source community for inspiration and best practices.

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Contact

**Kevin Sokoll**
- GitHub: [@ksokoll](https://github.com/ksokoll)
- LinkedIn: https://www.linkedin.com/in/kevin-sokoll-51a492179/

---

Happy Building!
