#!/usr/bin/env python3
"""
Example usage script demonstrating how to use the pipeline.

Run this after starting the API server:
    python example_usage.py
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*60)
    print("Testing /health endpoint")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_classification(query: str):
    """Test classification endpoint."""
    print("\n" + "="*60)
    print(f"Testing /classify with: '{query}'")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/classify",
        json={"text": query}
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_retrieval(query: str):
    """Test retrieval endpoint."""
    print("\n" + "="*60)
    print(f"Testing /retrieve with: '{query}'")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/retrieve",
        json={"text": query}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Query: {result['query']}")
    print(f"Retrieved {len(result['retrieved_docs'])} documents:")
    for i, doc in enumerate(result['retrieved_docs'], 1):
        print(f"\n  [{i}] {doc[:200]}...")


def test_full_pipeline(query: str):
    """Test complete pipeline."""
    print("\n" + "="*60)
    print(f"Testing /process with: '{query}'")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/process",
        json={"text": query}
    )
    print(f"Status: {response.status_code}")
    
    result = response.json()
    
    print("\n--- CLASSIFICATION ---")
    print(f"Category: {result['classification']['category']}")
    print(f"Confidence: {result['classification']['confidence']:.2f}")
    print(f"Reasoning: {result['classification']['reasoning']}")
    
    print("\n--- RETRIEVAL ---")
    print(f"Retrieved {len(result['retrieved_docs'])} documents")
    
    print("\n--- GENERATED ANSWER ---")
    print(result['answer'])
    
    print("\n--- QUALITY CHECKS ---")
    print(f"Overall Score: {result['quality_checks']['overall_score']:.1f}/100")
    print(f"Passed All: {result['quality_checks']['passed_all']}")
    for check in result['quality_checks']['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['check_name']}: {check['score']:.2f}")
    
    print("\n--- JUDGE DECISION ---")
    print(f"Decision: {result['judge_decision']['decision'].upper()}")
    print(f"Confidence: {result['judge_decision']['confidence']:.2f}")
    print(f"Reasoning: {result['judge_decision']['reasoning']}")
    
    print(f"\n--- PERFORMANCE ---")
    print(f"Processing Time: {result['processing_time_ms']:.0f}ms")


def main():
    """Run example tests."""
    
    print("\n" + "="*60)
    print("RAG PIPELINE USAGE EXAMPLES")
    print("="*60)
    
    # Test queries
    queries = [
        "How do I reset my password?",
        "What are your business hours?",
        "Do you offer refunds?"
    ]
    
    try:
        # Health check
        test_health()
        
        # Test classification
        test_classification(queries[0])
        
        # Test retrieval
        test_retrieval(queries[1])
        
        # Test full pipeline
        for query in queries:
            test_full_pipeline(query)
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the server is running: uvicorn api.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
