# src/answer_judge.py
from src.models import JudgeDecision, QualityCheckResult
from src.config import settings

class AnswerJudge:
    """Make final decision on answer quality."""
    
    def __init__(self):
        self.threshold = settings.quality_score_threshold
    
    def judge(
        self,
        quality_result: QualityCheckResult,
        classification_confidence: float
    ) -> JudgeDecision:
        """
        Make final decision based on quality checks and classification confidence.
        
        Args:
            quality_result: Quality check results
            classification_confidence: Confidence from classification step
        
        Returns:
            Judge decision with accept/reject/manual_review
        """
        
        quality_score = quality_result.overall_score
        
        # Decision logic
        if quality_score >= 90 and classification_confidence >= 0.8:
            decision = "accept"
            reasoning = "High quality score and high classification confidence"
            
        elif quality_score >= self.threshold and classification_confidence >= 0.6:
            decision = "accept"
            reasoning = "Quality score meets threshold with reasonable confidence"
            
        elif quality_score >= 50 and quality_score < self.threshold:
            decision = "manual_review"
            reasoning = "Quality score borderline, requires human review"
            
        elif not quality_result.passed_all:
            decision = "manual_review"
            reasoning = "Some quality checks failed"
            
        else:
            decision = "reject"
            reasoning = "Quality score below threshold or low confidence"
        
        # Overall confidence in the decision
        decision_confidence = self._calculate_decision_confidence(
            quality_score, classification_confidence
        )
        
        return JudgeDecision(
            decision=decision,
            confidence=decision_confidence,
            reasoning=reasoning,
            quality_score=quality_score
        )
    
    def _calculate_decision_confidence(
        self,
        quality_score: float,
        classification_confidence: float
    ) -> float:
        """Calculate confidence in the judge's decision."""
        
        # Weighted average
        confidence = (
            quality_score / 100 * 0.7 +
            classification_confidence * 0.3
        )
        
        return round(confidence, 2)
