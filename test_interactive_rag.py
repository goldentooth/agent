#!/usr/bin/env python3
"""Test the simplified RAG system interactively."""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from goldentooth_agent.core.rag.simple_rag_agent import create_simple_rag_agent


async def test_interactive_rag():
    """Test the RAG system with multiple queries."""
    print("🤖 Testing Simplified RAG System")
    print("=" * 50)

    # Create RAG agent
    rag_agent = create_simple_rag_agent()

    # Test queries
    test_queries = [
        "What is the Goldentooth Agent?",
        "What repositories do you know about?",
        "Tell me about Python projects",
        "What is the purpose of the terraform repositories?",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 30)

        try:
            result = await rag_agent.process_question(query)

            print(f"📄 Sources: {len(result.sources)}")
            print(f"🎯 Confidence: {result.confidence}")
            print(f"💬 Response: {result.response[:200]}...")

            if result.suggestions:
                print(f"💡 Suggestions: {', '.join(result.suggestions[:2])}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n✅ Interactive test completed!")


if __name__ == "__main__":
    asyncio.run(test_interactive_rag())
