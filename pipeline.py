# src/pipeline.py
from src.classifier import IntentClassifier
from src.retriever import KnowledgeRetriever
from src.generator import ResponseGenerator
from src.quality_check import QualityChecker
from src.answer_judge import AnswerJudge
from src.models import PipelineResult
import time

class Pipeline:
    """Main pipeline orchestrating all components."""
    
    def __init__(self):
        print("Initializing pipeline components...")
        
        self.classifier = IntentClassifier()
        print("✓ Classifier ready")
        
        self.retriever = KnowledgeRetriever()
        print("✓ Retriever ready")
        
        self.generator = ResponseGenerator()
        print("✓ Generator ready")
        
        self.quality_checker = QualityChecker()
        print("✓ Quality Checker ready")
        
        self.judge = AnswerJudge()
        print("✓ Judge ready")
        
        print("✅ Pipeline initialized successfully\n")
    
    def process(self, query: str) -> dict:
        """
        Process a user query through the complete pipeline.
        
        Args:
            query: User's question
        
        Returns:
            Dictionary with complete pipeline results
        """
        
        start_time = time.time()
        
        # Step 1: Classify intent
        print(f"\n[1/5] Classifying query...")
        classification = self.classifier.classify(query)
        print(f"  → Category: {classification.category}")
        print(f"  → Confidence: {classification.confidence:.2f}")
        print(f"  → Needs context: {classification.needs_context}")
        
        # Step 2: Retrieve relevant context (if needed)
        retrieved_docs = []
        if classification.needs_context:
            print(f"\n[2/5] Retrieving context...")
            retrieved_docs = self.retriever.retrieve(query)
            print(f"  → Found {len(retrieved_docs)} relevant documents")
        else:
            print(f"\n[2/5] Skipping retrieval (not needed)")
        
        # Step 3: Generate response
        print(f"\n[3/5] Generating answer...")
        generated = self.generator.generate(query, classification, retrieved_docs)
        print(f"  → Answer length: {len(generated.answer)} chars")
        print(f"  → Confidence: {generated.confidence:.2f}")
        
        # Step 4: Check quality
        print(f"\n[4/5] Checking quality...")
        quality_result = self.quality_checker.check_quality(
            query, generated.answer, retrieved_docs
        )
        print(f"  → Overall score: {quality_result.overall_score:.1f}/100")
        print(f"  → Passed all checks: {quality_result.passed_all}")
        
        # Step 5: Final judgment
        print(f"\n[5/5] Making judgment...")
        judge_decision = self.judge.judge(quality_result, classification.confidence)
        print(f"  → Decision: {judge_decision.decision}")
        print(f"  → Confidence: {judge_decision.confidence:.2f}")
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Build result
        result = {
            "query": query,
            "classification": classification.model_dump(),
            "retrieved_docs": retrieved_docs,
            "answer": generated.answer,
            "quality_checks": quality_result.model_dump(),
            "judge_decision": judge_decision.model_dump(),
            "processing_time_ms": round(processing_time, 2),
            "metadata": {
                "sources_used": generated.sources_used,
                "generator_confidence": generated.confidence
            }
        }
        
        print(f"\n✅ Processing complete in {processing_time:.0f}ms")
        
        return result
