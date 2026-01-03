# src/generator.py
from openai import OpenAI
from src.config import settings
from src.models import Classification, GeneratedAnswer
import json

class ResponseGenerator:
    """Generate responses using LLM with retrieved context."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.generator_model
    
    def generate(
        self,
        query: str,
        classification: Classification,
        context_docs: list[str]
    ) -> GeneratedAnswer:
        """
        Generate response based on query, classification, and retrieved context.
        
        Args:
            query: User's question
            classification: Classification result
            context_docs: Retrieved relevant documents
        
        Returns:
            Generated answer with metadata
        """
        
        system_prompt = self._build_system_prompt(classification)
        user_prompt = self._build_user_prompt(query, context_docs)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return GeneratedAnswer(
            answer=result["answer"],
            sources_used=result.get("sources_used", []),
            confidence=result.get("confidence", 0.8)
        )
    
    def _build_system_prompt(self, classification: Classification) -> str:
        """Build system prompt based on classification."""
        
        base_prompt = """You are a helpful assistant.

Guidelines:
- Be clear, concise, and professional
- Use the provided context when available
- If context doesn't fully answer the question, acknowledge limitations
- Maintain a friendly tone

Category: {category}
Confidence: {confidence}

Return valid JSON with:
- answer: your response
- sources_used: list of source IDs used (if any)
- confidence: float 0.0-1.0 indicating your certainty"""
        
        return base_prompt.format(
            category=classification.category,
            confidence=classification.confidence
        )
    
    def _build_user_prompt(self, query: str, context_docs: list[str]) -> str:
        """Build user prompt with query and context."""
        
        if context_docs:
            context_str = "\n\n".join([f"[Doc {i+1}]\n{doc}" for i, doc in enumerate(context_docs)])
            prompt = f"""Context from knowledge base:

{context_str}

User Query: {query}

Based on the context above, provide a helpful response."""
        else:
            prompt = f"""User Query: {query}

Provide a helpful response based on your general knowledge."""
        
        return prompt
