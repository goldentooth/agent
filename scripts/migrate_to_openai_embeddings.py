#!/usr/bin/env python3
"""
Migrate existing embeddings to use OpenAI embeddings instead of Claude-based embeddings.

This script:
1. Reads all existing documents from the document stores
2. Re-embeds them using OpenAI embeddings
3. Updates the vector store with new embeddings
4. Preserves all document metadata and structure
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import project modules after path modification
from goldentooth_agent.core.document_store import DocumentStore
from goldentooth_agent.core.embeddings import OpenAIEmbeddingsService
from goldentooth_agent.core.embeddings.vector_store import VectorStore
from goldentooth_agent.core.paths import Paths


async def migrate_embeddings():
    """Main migration function."""
    print("🔄 Starting migration to OpenAI embeddings...")

    # Initialize services
    try:
        paths = Paths()
        document_store = DocumentStore(paths=paths)
        openai_embeddings = OpenAIEmbeddingsService(paths=paths)
        vector_store = VectorStore(paths=paths)

        print("✅ Services initialized")
        print(f"📁 Data directory: {paths.data()}")

    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False

    # Check available store types using DocumentStore interface
    all_documents = document_store.list_all_documents()
    store_types = [store_type for store_type, docs in all_documents.items() if docs]

    print(f"📊 Found store types: {store_types}")

    total_docs = 0
    total_processed = 0
    total_errors = 0

    for store_type in store_types:
        print(f"\n🔍 Processing store type: {store_type}")

        try:
            # Get all document IDs in this store type
            document_ids = all_documents[store_type]
            print(f"  📄 Found {len(document_ids)} documents")

            # Get the store instance for loading documents
            store = document_store._get_store_by_type(store_type)

            for doc_id in document_ids:
                total_docs += 1
                print(f"  🔄 Processing: {doc_id[:50]}...")

                try:
                    # Load the document data
                    doc_obj = store.load(doc_id)

                    # Convert object back to dictionary using adapter
                    doc_data = store.adapter.to_dict(doc_id, doc_obj)

                    # Re-embed the document using OpenAI
                    embedding_result = (
                        await openai_embeddings.create_document_embedding(doc_data)
                    )

                    # Store in vector store
                    vector_store.store_document(
                        store_type=store_type,
                        document_id=doc_id,
                        content=embedding_result["text_content"],
                        embedding=embedding_result["embedding"],
                        metadata=embedding_result["metadata"],
                    )

                    total_processed += 1
                    if total_processed % 10 == 0:
                        print(
                            f"    ✅ Processed {total_processed}/{total_docs} documents..."
                        )

                except Exception as e:
                    print(f"    ❌ Error processing {doc_id}: {e}")
                    total_errors += 1
                    continue

        except Exception as e:
            print(f"  ❌ Error processing store {store_type}: {e}")
            continue

    # Also handle chunked documents if they exist
    print("\n🧩 Processing chunked documents...")

    for store_type in store_types:
        try:
            document_ids = all_documents[store_type]
            store = document_store._get_store_by_type(store_type)

            for doc_id in document_ids:
                try:
                    # Load the document data
                    doc_obj = store.load(doc_id)

                    # Convert object back to dictionary using adapter
                    doc_data = store.adapter.to_dict(doc_id, doc_obj)

                    # Check if document should be chunked
                    if openai_embeddings.should_use_chunking(store_type, doc_data):
                        print(f"  🔄 Re-chunking and embedding: {doc_id[:50]}...")

                        # Create chunks with embeddings
                        chunk_result = await openai_embeddings.create_document_chunks_with_embeddings(
                            store_type, doc_id, doc_data
                        )

                        # Store chunks with embeddings
                        vector_store.store_document_chunks(
                            store_type=store_type,
                            document_id=doc_id,
                            chunks=chunk_result["chunks"],
                            embeddings=chunk_result["embeddings"],
                            document_metadata={
                                "embedding_method": "openai",
                                "model": openai_embeddings.model,
                                "migration_timestamp": datetime.now().isoformat(),
                            },
                        )

                        print(
                            f"    ✅ Created {len(chunk_result['chunks'])} chunks for {doc_id}"
                        )
                        total_processed += len(chunk_result["chunks"])

                except Exception as e:
                    print(f"    ❌ Error chunking {doc_id}: {e}")
                    total_errors += 1
                    continue

        except Exception as e:
            print(f"  ❌ Error processing chunks for store {store_type}: {e}")
            continue

    print("\n🎉 Migration completed!")
    print("📊 Summary:")
    print(f"  📄 Total documents found: {total_docs}")
    print(f"  ✅ Successfully processed: {total_processed}")
    print(f"  ❌ Errors: {total_errors}")
    print(f"  📈 Success rate: {total_processed/(total_docs or 1)*100:.1f}%")

    if total_errors > 0:
        print("\n⚠️  Some documents failed to process. Check the error messages above.")

    return total_errors == 0


async def verify_migration():
    """Verify the migration by testing a few embeddings."""
    print("\n🔍 Verifying migration...")

    try:
        paths = Paths()
        vector_store = VectorStore(paths=paths)
        openai_embeddings = OpenAIEmbeddingsService(paths=paths)

        # Create a test query embedding
        test_query = "Python programming language"
        test_embedding = await openai_embeddings.create_embedding(test_query)

        print(f"  🔍 Test query: '{test_query}'")
        print(f"  📐 Embedding dimensions: {len(test_embedding)}")

        # Search for similar documents
        results = vector_store.search_similar(
            test_embedding,
            limit=5,
            store_type=None,  # Search all stores
            include_chunks=True,
        )

        print(f"  🎯 Found {len(results)} similar documents")

        for i, result in enumerate(results[:3], 1):
            doc_id = result.get("document_id", "unknown")
            similarity = result.get("similarity_score", 0.0)
            is_chunk = result.get("is_chunk", False)
            chunk_type = (
                result.get("chunk_type", "document") if is_chunk else "document"
            )

            print(
                f"    {i}. {doc_id[:60]}... (similarity: {similarity:.3f}, type: {chunk_type})"
            )

        if results:
            print("  ✅ Migration verification successful!")
            return True
        else:
            print("  ⚠️  No results found - this might indicate an issue")
            return False

    except Exception as e:
        print(f"  ❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 OpenAI Embeddings Migration Script")
    print("=" * 50)

    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key and try again.")
        sys.exit(1)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key and try again.")
        sys.exit(1)

    print("✅ API keys found")

    # Run migration
    success = asyncio.run(migrate_embeddings())

    if success:
        # Verify migration
        verification_success = asyncio.run(verify_migration())

        if verification_success:
            print("\n🎉 Migration completed successfully!")
            print("The RAG agent is now ready to use with OpenAI embeddings.")
        else:
            print("\n⚠️  Migration completed but verification failed.")
            print("You may need to check the vector store manually.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)
