#!/usr/bin/env python3
"""
Simple script to populate vector store with OpenAI embeddings.
No migration complexity - just direct population.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from goldentooth_agent.core.document_store import DocumentStore
from goldentooth_agent.core.embeddings import OpenAIEmbeddingsService
from goldentooth_agent.core.embeddings.vector_store import VectorStore
from goldentooth_agent.core.paths import Paths


async def populate_vector_store():
    """Populate vector store with OpenAI embeddings."""
    print("🔄 Populating vector store with OpenAI embeddings...")

    # Initialize services
    paths = Paths()
    document_store = DocumentStore(paths=paths)
    openai_embeddings = OpenAIEmbeddingsService(paths=paths)
    vector_store = VectorStore(paths=paths)

    print(f"📁 Data directory: {paths.data()}")

    # Get all documents
    all_documents = document_store.list_all_documents()
    store_types = [store_type for store_type, docs in all_documents.items() if docs]

    print(f"📊 Found store types: {store_types}")

    total_processed = 0

    for store_type in store_types:
        print(f"\n🔍 Processing store type: {store_type}")

        document_ids = all_documents[store_type]
        print(f"  📄 Found {len(document_ids)} documents")

        store = document_store._get_store_by_type(store_type)

        for doc_id in document_ids:
            try:
                # Load and convert document
                doc_obj = store.load(doc_id)
                doc_data = store.adapter.to_dict(doc_id, doc_obj)

                # Create embedding
                embedding_result = await openai_embeddings.create_document_embedding(
                    doc_data
                )

                # Store directly
                vector_store.store_document(
                    store_type=store_type,
                    document_id=doc_id,
                    content=embedding_result["text_content"],
                    embedding=embedding_result["embedding"],
                    metadata=embedding_result["metadata"],
                )

                # Also create chunks if appropriate
                if openai_embeddings.should_use_chunking(store_type, doc_data):
                    chunk_result = (
                        await openai_embeddings.create_document_chunks_with_embeddings(
                            store_type, doc_id, doc_data
                        )
                    )

                    vector_store.store_document_chunks(
                        store_type=store_type,
                        document_id=doc_id,
                        chunks=chunk_result["chunks"],
                        embeddings=chunk_result["embeddings"],
                    )

                    print(f"  ✅ {doc_id} + {len(chunk_result['chunks'])} chunks")
                    total_processed += 1 + len(chunk_result["chunks"])
                else:
                    print(f"  ✅ {doc_id}")
                    total_processed += 1

            except Exception as e:
                print(f"  ❌ Error processing {doc_id}: {e}")
                continue

    print("\n🎉 Population completed!")
    print(f"📊 Total items processed: {total_processed}")

    # Test the system
    print("\n🔍 Testing system...")
    test_embedding = await openai_embeddings.create_embedding("Python programming")
    results = vector_store.search_similar(test_embedding, limit=3)
    print(f"  📐 Test embedding dimensions: {len(test_embedding)}")
    print(f"  🎯 Found {len(results)} test results")

    if results:
        print("  ✅ System working correctly!")
        return True
    else:
        print("  ⚠️  No results found")
        return False


if __name__ == "__main__":
    success = asyncio.run(populate_vector_store())
    sys.exit(0 if success else 1)
