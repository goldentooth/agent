#!/usr/bin/env python3
"""Test basic RAG functionality without enhanced features."""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from goldentooth_agent.core.paths import Paths
from goldentooth_agent.core.embeddings import OpenAIEmbeddingsService, VectorStore


async def test_basic_rag():
    """Test basic RAG components."""
    print("🔍 Testing basic RAG functionality...")
    
    # Initialize services
    paths = Paths()
    openai_embeddings = OpenAIEmbeddingsService(paths=paths)
    vector_store = VectorStore(paths=paths)
    
    # Test 1: Create a query embedding
    query = "What is the Goldentooth Agent?"
    print(f"📝 Query: {query}")
    
    query_embedding = await openai_embeddings.create_embedding(query)
    print(f"📐 Query embedding dimensions: {len(query_embedding)}")
    
    # Test 2: Search for similar documents
    results = vector_store.search_similar(
        query_embedding,
        limit=5,
        store_type=None,
        include_chunks=True
    )
    
    print(f"🎯 Found {len(results)} results")
    
    for i, result in enumerate(results[:3], 1):
        doc_id = result.get("document_id", "unknown")
        similarity = result.get("similarity_score", 0.0)
        content_preview = result.get("content", "")[:100]
        
        print(f"  {i}. {doc_id} (similarity: {similarity:.3f})")
        print(f"     Preview: {content_preview}...")
        print()
    
    return len(results) > 0


if __name__ == "__main__":
    success = asyncio.run(test_basic_rag())
    print(f"✅ Basic RAG test {'passed' if success else 'failed'}")
    sys.exit(0 if success else 1)