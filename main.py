# api/main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from src.models import UserQuery
from src.pipeline import Pipeline
from src.utils import sanitize_input
from src.rate_limiter import RateLimiter
from src.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="AI Pipeline API",
    description="RAG-based pipeline with classification, retrieval, generation, and quality checks",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pipeline = Pipeline()
rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds
)

# Dependency to get pipeline
def get_pipeline():
    return pipeline


# ==================== Routes ====================

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "AI Pipeline API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "classifier": "ok",
            "retriever": "ok",
            "generator": "ok",
            "quality_checker": "ok",
            "judge": "ok"
        }
    }


@app.post("/process")
async def process_query(
    request: Request,
    query: UserQuery,
    pipeline: Pipeline = Depends(get_pipeline)
):
    """
    Process a user query through the complete pipeline.
    
    Steps:
    1. Classify intent
    2. Retrieve context (if needed)
    3. Generate response
    4. Check quality
    5. Make judgment
    
    Returns complete result with all intermediate steps.
    """
    
    # Rate limiting
    rate_limiter.check(request)
    
    try:
        # Sanitize input
        clean_text = sanitize_input(query.text)
        
        # Process through pipeline
        result = pipeline.process(clean_text)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {str(e)}"
        )


@app.post("/classify")
async def classify_only(
    request: Request,
    query: UserQuery,
    pipeline: Pipeline = Depends(get_pipeline)
):
    """
    Only classify the query without full processing.
    Useful for testing or routing decisions.
    """
    
    rate_limiter.check(request)
    
    try:
        clean_text = sanitize_input(query.text)
        classification = pipeline.classifier.classify(clean_text)
        return classification.model_dump()
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification error: {str(e)}"
        )


@app.post("/retrieve")
async def retrieve_only(
    request: Request,
    query: UserQuery,
    pipeline: Pipeline = Depends(get_pipeline)
):
    """
    Only retrieve relevant documents without generating response.
    Useful for debugging retrieval quality.
    """
    
    rate_limiter.check(request)
    
    try:
        clean_text = sanitize_input(query.text)
        docs = pipeline.retriever.retrieve(clean_text)
        return {"query": clean_text, "retrieved_docs": docs}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval error: {str(e)}"
        )


# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("\n" + "="*50)
    print("🚀 API Server Starting...")
    print("="*50 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("\n" + "="*50)
    print("🛑 API Server Shutting Down...")
    print("="*50 + "\n")
