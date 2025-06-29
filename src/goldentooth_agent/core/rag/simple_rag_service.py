"""
Simplified RAG service focusing on core functionality.
Removes complex enhanced features that are causing errors.
"""

from datetime import datetime
from typing import Any

from antidote import inject, injectable

from ..document_store import DocumentStore
from ..embeddings import OpenAIEmbeddingsService, VectorStore
from ..llm.claude_client import ClaudeFlowClient


@injectable
class SimpleRAGService:
    """Simplified RAG service for reliable document-based question answering."""

    def __init__(
        self,
        document_store: DocumentStore = inject.me(),
        embeddings_service: OpenAIEmbeddingsService = inject.me(),
        vector_store: VectorStore = inject.me(),
        claude_client: ClaudeFlowClient | None = None,
    ) -> None:
        """Initialize the simplified RAG service."""
        self.document_store = document_store
        self.embeddings_service = embeddings_service
        self.vector_store = vector_store

        # Initialize Claude client with default settings if not provided
        self.claude_client = claude_client or ClaudeFlowClient(
            default_model="claude-3-5-sonnet-20241022",
            default_max_tokens=2000,
        )

    async def query(
        self,
        question: str,
        max_results: int = 5,
        store_type: str | None = None,
        similarity_threshold: float = 0.1,
        include_chunks: bool = True,
    ) -> dict[str, Any]:
        """Answer a question using simple RAG with retrieved documents.

        Args:
            question: User's question
            max_results: Maximum number of documents/chunks to retrieve
            store_type: Optional filter by document store type
            similarity_threshold: Minimum similarity score for retrieved documents
            include_chunks: Whether to include chunks in search results

        Returns:
            Dictionary with answer, retrieved documents, and metadata
        """
        try:
            start_time = datetime.now()

            # Step 1: Create embedding for the question
            question_embedding = await self.embeddings_service.create_embedding(
                question
            )

            # Step 2: Retrieve similar documents/chunks
            retrieved_docs = self.vector_store.search_similar(
                question_embedding,
                limit=max_results,
                store_type=store_type,
                include_chunks=include_chunks,
            )

            # Step 3: Filter by similarity threshold
            filtered_docs = [
                doc
                for doc in retrieved_docs
                if doc.get("similarity_score", 0.0) >= similarity_threshold
            ]

            # Step 4: Generate answer using Claude
            if filtered_docs:
                answer = await self._generate_answer_with_context(
                    question, filtered_docs
                )
            else:
                answer = "I couldn't find relevant information to answer your question. Try rephrasing or asking about something else."

            end_time = datetime.now()

            return {
                "answer": answer,
                "question": question,
                "retrieved_documents": filtered_docs,
                "metadata": {
                    "chunks_found": len(
                        [doc for doc in filtered_docs if doc.get("is_chunk", False)]
                    ),
                    "full_docs_found": len(
                        [doc for doc in filtered_docs if not doc.get("is_chunk", False)]
                    ),
                    "query_timestamp": start_time.isoformat(),
                    "processing_time_ms": int(
                        (end_time - start_time).total_seconds() * 1000
                    ),
                    "similarity_threshold": similarity_threshold,
                    "total_results": len(filtered_docs),
                    "embedding_dimensions": len(question_embedding),
                },
            }

        except Exception as e:
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "question": question,
                "retrieved_documents": [],
                "metadata": {
                    "error": True,
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "query_timestamp": datetime.now().isoformat(),
                },
            }

    async def _generate_answer_with_context(
        self, question: str, documents: list[dict[str, Any]]
    ) -> str:
        """Generate an answer using Claude with document context."""

        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(documents[:5], 1):  # Limit to top 5 for context
            content = doc.get("content", "")
            doc_id = doc.get("document_id", "unknown")
            similarity = doc.get("similarity_score", 0.0)

            # Truncate very long content
            if len(content) > 500:
                content = content[:500] + "..."

            context_parts.append(
                f"Document {i} (ID: {doc_id}, Similarity: {similarity:.3f}):\n{content}"
            )

        context = "\n\n".join(context_parts)

        # Create prompt for Claude
        prompt = f"""Please answer the following question based on the provided document context.
Be helpful and informative, but only use information from the provided context.

Question: {question}

Context from relevant documents:
{context}

Answer:"""

        try:
            # Generate response using Claude
            messages = [{"role": "user", "content": prompt}]
            response = await self.claude_client.create_chat_completion(
                messages=messages,
                max_tokens=1000,
            )

            return response.strip() if isinstance(response, str) else str(response)

        except Exception as e:
            return f"I found relevant documents but encountered an error generating the response: {str(e)}"

    def get_document_count(self) -> dict[str, int]:
        """Get count of documents in each store."""
        return self.document_store.get_document_count()

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the RAG system."""
        return {
            "document_counts": self.get_document_count(),
            "vector_store_stats": self.vector_store.get_stats(),
            "embeddings_service": {
                "model": self.embeddings_service.model,
                "dimensions": self.embeddings_service.dimensions,
            },
        }
