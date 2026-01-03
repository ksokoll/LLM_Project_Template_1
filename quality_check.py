# src/quality_check.py
from openai import OpenAI
from src.config import settings
from src.models import QualityCheck, QualityCheckResult
import json

class QualityChecker:
    """Validate response quality with multiple checks."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.quality_check_model
    
    def check_quality(
        self,
        query: str,
        answer: str,
        context_docs: list[str]
    ) -> QualityCheckResult:
        """
        Run multiple quality checks on generated answer.
        
        Args:
            query: Original user query
            answer: Generated response
            context_docs: Retrieved context used
        
        Returns:
            Quality check results with individual checks and overall score
        """
        
        checks = []
        
        # Define check criteria
        check_criteria = [
            {
                "name": "relevance",
                "description": "Does the answer directly address the user's query?"
            },
            {
                "name": "completeness",
                "description": "Is the answer complete and thorough?"
            },
            {
                "name": "accuracy",
                "description": "Is the information factually correct based on context?"
            },
            {
                "name": "clarity",
                "description": "Is the answer clear and easy to understand?"
            },
            {
                "name": "professionalism",
                "description": "Is the tone professional and appropriate?"
            }
        ]
        
        # Run each check
        for criterion in check_criteria:
            check_result = self._run_single_check(
                query, answer, context_docs, criterion
            )
            checks.append(check_result)
        
        # Calculate overall score
        overall_score = sum(check.score for check in checks) / len(checks) * 100
        passed_all = all(check.passed for check in checks)
        
        return QualityCheckResult(
            checks=checks,
            overall_score=round(overall_score, 2),
            passed_all=passed_all
        )
    
    def _run_single_check(
        self,
        query: str,
        answer: str,
        context_docs: list[str],
        criterion: dict
    ) -> QualityCheck:
        """Run a single quality check using LLM."""
        
        system_prompt = f"""You are a quality evaluator.

Evaluate the answer based on: {criterion['description']}

Return JSON:
- passed: boolean
- explanation: brief explanation (1-2 sentences)
- score: float 0.0-1.0"""

        user_prompt = f"""Query: {query}

Answer: {answer}

Context Used:
{chr(10).join(context_docs[:2])}

Evaluate the answer quality."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return QualityCheck(
            check_name=criterion["name"],
            passed=result["passed"],
            explanation=result["explanation"],
            score=result["score"]
        )
