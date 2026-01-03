# src/models.py
from pydantic import BaseModel, Field
from typing import Literal, Optional

# ==================== Request Models ====================

class UserQuery(BaseModel):
    """Input model for user queries."""
    text: str = Field(..., min_length=1, max_length=1000)
    metadata: Optional[dict] = None


# ==================== Classification Models ====================

class Classification(BaseModel):
    """Classification result from LLM."""
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    needs_context: bool


# ==================== Generation Models ====================

class GeneratedAnswer(BaseModel):
    """LLM-generated response."""
    answer: str
    sources_used: list[str] = []
    confidence: float = Field(..., ge=0.0, le=1.0)


# ==================== Quality Check Models ====================

class QualityCheck(BaseModel):
    """Individual quality check result."""
    check_name: str
    passed: bool
    explanation: str
    score: float = Field(..., ge=0.0, le=1.0)


class QualityCheckResult(BaseModel):
    """Complete quality assessment."""
    checks: list[QualityCheck]
    overall_score: float = Field(..., ge=0.0, le=100.0)
    passed_all: bool


# ==================== Judge Models ====================

class JudgeDecision(BaseModel):
    """Final quality judgment."""
    decision: Literal["accept", "reject", "manual_review"]
    confidence: float
    reasoning: str
    quality_score: float


# ==================== Pipeline Output ====================

class PipelineResult(BaseModel):
    """Complete pipeline response."""
    query: str
    classification: Classification
    retrieved_docs: list[str]
    answer: str
    quality_checks: QualityCheckResult
    judge_decision: JudgeDecision
    processing_time_ms: float
    metadata: dict = {}
