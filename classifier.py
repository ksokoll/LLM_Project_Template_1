# src/classifier.py
from openai import OpenAI
from src.config import settings
from src.models import Classification
import json

class IntentClassifier:
    """Classify user query intent and category."""
    
    # Define your categories here
    CATEGORIES = [
        "general_inquiry",
        "technical_support",
        "billing_question",
        "product_info",
        "complaint",
        "other"
    ]
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.classifier_model
    
    def classify(self, query: str) -> Classification:
        """
        Classify user query using LLM with structured output.
        
        Returns:
            Classification with category, confidence, reasoning, needs_context
        """
        
        system_prompt = f"""You are a query classification system.

Categories: {', '.join(self.CATEGORIES)}

Analyze the query and return:
- category: one of the defined categories
- confidence: float between 0.0 and 1.0
- reasoning: brief explanation (1-2 sentences)
- needs_context: boolean - does this query require knowledge retrieval?

Return valid JSON only."""

        user_prompt = f"Query: {query}"
        
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
        
        return Classification(
            category=result["category"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            needs_context=result["needs_context"]
        )
