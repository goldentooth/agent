from datetime import datetime
from typing import Any

from antidote import inject, injectable

from ..document_store import DocumentStore
from ..embeddings import EmbeddingsService, VectorStore
from ..embeddings.hybrid_search import HybridSearchEngine
from ..llm.claude_client import ClaudeFlowClient


@injectable
class RAGService:
    """Retrieval-Augmented Generation service for intelligent document querying."""

    def __init__(
        self,
        document_store: DocumentStore = inject.me(),
        embeddings_service: EmbeddingsService = inject.me(),
        vector_store: VectorStore = inject.me(),
        claude_client: ClaudeFlowClient | None = None,
        hybrid_search_engine: HybridSearchEngine = inject.me(),
    ) -> None:
        """Initialize the RAG service.

        Args:
            document_store: Document store for accessing YAML documents
            embeddings_service: Service for creating embeddings
            vector_store: Vector database for similarity search
            claude_client: Claude client for generating responses
            hybrid_search_engine: Hybrid search engine for combining semantic and keyword search
        """
        self.document_store = document_store
        self.embeddings_service = embeddings_service
        self.vector_store = vector_store
        self.hybrid_search_engine = hybrid_search_engine

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
        include_metadata: bool = True,
        similarity_threshold: float = 0.1,
        include_chunks: bool = True,
        chunk_types: list[str] | None = None,
        prioritize_chunks: bool = False,
    ) -> dict[str, Any]:
        """Answer a question using RAG with retrieved documents.

        Args:
            question: User's question
            max_results: Maximum number of documents/chunks to retrieve
            store_type: Optional filter by document store type
            include_metadata: Whether to include retrieval metadata in response
            similarity_threshold: Minimum similarity score for retrieved documents
            include_chunks: Whether to include chunks in search results
            chunk_types: Optional filter for specific chunk types (e.g., ['repo_core', 'note_section'])
            prioritize_chunks: If True, prioritize chunks over full documents in ranking

        Returns:
            Dictionary with answer, retrieved documents/chunks, and metadata
        """
        try:
            # Step 1: Create embedding for the question
            question_embedding = await self.embeddings_service.create_embedding(
                question
            )

            # Step 2: Retrieve similar documents/chunks
            retrieved_docs = self.vector_store.search_similar(
                question_embedding,
                limit=(
                    max_results * 2 if chunk_types or prioritize_chunks else max_results
                ),
                store_type=store_type,
                include_chunks=include_chunks,
            )

            # Step 2.5: Apply chunk type filtering and prioritization
            if chunk_types:
                retrieved_docs = [
                    doc
                    for doc in retrieved_docs
                    if not doc.get("is_chunk", False)
                    or doc.get("chunk_type") in chunk_types
                ]

            if prioritize_chunks:
                # Sort chunks first, then documents
                chunks = [doc for doc in retrieved_docs if doc.get("is_chunk", False)]
                documents = [
                    doc for doc in retrieved_docs if not doc.get("is_chunk", False)
                ]
                retrieved_docs = chunks + documents

            # Limit results after filtering
            retrieved_docs = retrieved_docs[:max_results]

            # Filter by similarity threshold
            filtered_docs = [
                doc
                for doc in retrieved_docs
                if doc["similarity_score"] >= similarity_threshold
            ]

            if not filtered_docs:
                return {
                    "answer": "I couldn't find any relevant documents to answer your question. The knowledge base may not contain information about this topic.",
                    "question": question,
                    "retrieved_documents": [],
                    "metadata": {
                        "documents_found": 0,
                        "documents_used": 0,
                        "query_timestamp": datetime.now().isoformat(),
                        "similarity_threshold": similarity_threshold,
                    },
                }

            # Step 3: Build context from retrieved documents
            context = self._build_context(filtered_docs)

            # Step 4: Generate response using Claude
            response = await self._generate_response(question, context)

            # Step 5: Prepare result
            result = {
                "answer": response,
                "question": question,
                "retrieved_documents": filtered_docs if include_metadata else [],
                "metadata": {
                    "documents_found": len(retrieved_docs),
                    "documents_used": len(filtered_docs),
                    "chunks_used": len(
                        [doc for doc in filtered_docs if doc.get("is_chunk", False)]
                    ),
                    "full_docs_used": len(
                        [doc for doc in filtered_docs if not doc.get("is_chunk", False)]
                    ),
                    "query_timestamp": datetime.now().isoformat(),
                    "similarity_threshold": similarity_threshold,
                    "model_used": self.claude_client.default_model,
                    "chunk_types_found": list(
                        set(
                            doc.get("chunk_type")
                            for doc in filtered_docs
                            if doc.get("is_chunk", False) and doc.get("chunk_type")
                        )
                    ),
                },
            }

            return result

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

    async def get_document_chunks_info(
        self, document_id: str, store_type: str
    ) -> dict[str, Any]:
        """Get information about the chunks for a specific document.

        Args:
            document_id: ID of the document
            store_type: Type of document store

        Returns:
            Dictionary with chunk information and metadata
        """
        try:
            # Check if document exists
            if not self.document_store.document_exists(store_type, document_id):
                return {
                    "error": True,
                    "message": f"Document {store_type}/{document_id} not found.",
                }

            # Get chunks from vector store
            chunks = self.vector_store.get_document_chunks(store_type, document_id)

            if not chunks:
                return {
                    "document_id": document_id,
                    "store_type": store_type,
                    "chunks": [],
                    "total_chunks": 0,
                    "message": "Document has no chunks (may use full-document embedding)",
                }

            # Calculate statistics
            total_chars = sum(chunk["size_chars"] for chunk in chunks)
            chunk_types = {}
            for chunk in chunks:
                chunk_type = chunk["chunk_type"]
                if chunk_type not in chunk_types:
                    chunk_types[chunk_type] = 0
                chunk_types[chunk_type] += 1

            return {
                "document_id": document_id,
                "store_type": store_type,
                "chunks": chunks,
                "total_chunks": len(chunks),
                "total_characters": total_chars,
                "chunk_types": chunk_types,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "error": True,
                "message": f"Error retrieving chunk information: {str(e)}",
                "document_id": document_id,
                "store_type": store_type,
            }

    def _build_context(self, documents: list[dict[str, Any]]) -> str:
        """Build context string from retrieved documents and chunks.

        Args:
            documents: List of retrieved document/chunk metadata

        Returns:
            Formatted context string for Claude
        """
        context_parts = []

        # Group chunks by parent document for better context
        chunks_by_doc = {}
        standalone_docs = []

        for doc in documents:
            if doc.get("is_chunk", False):
                parent_key = f"{doc['store_type']}/{doc['document_id']}"
                if parent_key not in chunks_by_doc:
                    chunks_by_doc[parent_key] = []
                chunks_by_doc[parent_key].append(doc)
            else:
                standalone_docs.append(doc)

        entry_num = 1

        # Process grouped chunks first (they're usually more relevant)
        for parent_key, chunks in chunks_by_doc.items():
            # Sort chunks by index for logical order
            chunks.sort(key=lambda x: x.get("chunk_index", 0))

            if len(chunks) == 1:
                # Single chunk from document
                chunk = chunks[0]
                doc_id = chunk["document_id"]
                store_type = chunk["store_type"]
                content = chunk["content"]
                similarity = chunk["similarity_score"]
                chunk_id = chunk.get("chunk_id", "unknown")
                chunk_type = chunk.get("chunk_type", "unknown")
                chunk_title = chunk.get("chunk_title", "Untitled")
                chunk_index = chunk.get("chunk_index", 0)

                context_entry = f"""Source {entry_num}: {store_type}/{doc_id} - {chunk_title} (similarity: {similarity:.3f})
Type: {chunk_type} chunk | Section {chunk_index}
Content: {content}

"""
                context_parts.append(context_entry)
                entry_num += 1
            else:
                # Multiple chunks from same document
                context_entry = f"""Source {entry_num}: {parent_key} - Multiple Sections
"""
                for j, chunk in enumerate(chunks):
                    content = chunk["content"]
                    similarity = chunk["similarity_score"]
                    chunk_type = chunk.get("chunk_type", "unknown")
                    chunk_title = chunk.get("chunk_title", "Untitled")
                    chunk_index = chunk.get("chunk_index", 0)

                    context_entry += f"""  Section {chunk_index}: {chunk_title} ({chunk_type}, similarity: {similarity:.3f})
  {content}

"""

                context_parts.append(context_entry)
                entry_num += 1

        # Process standalone documents
        for doc in standalone_docs:
            doc_id = doc["document_id"]
            store_type = doc["store_type"]
            content = doc["content"]
            similarity = doc["similarity_score"]

            context_entry = f"""Source {entry_num}: {store_type}/{doc_id} (similarity: {similarity:.3f})
Content: {content}

"""
            context_parts.append(context_entry)
            entry_num += 1

        return "".join(context_parts)

    async def _generate_response(self, question: str, context: str) -> str:
        """Generate a response using Claude with the retrieved context.

        Args:
            question: User's question
            context: Context from retrieved documents

        Returns:
            Generated response text
        """
        system_prompt = """You are a knowledgeable assistant with access to a technical knowledge base containing information about GitHub repositories, services, infrastructure nodes, and documentation.

Your task is to answer questions using ONLY the information provided in the context sources. Follow these guidelines:

1. Base your answers strictly on the provided context sources
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Always cite which sources you're referencing:
   - For full documents: "According to github.repos/goldentooth/agent..."
   - For document chunks: "According to the [chunk title] section of github.repos/goldentooth/agent..."
   - For multiple sections: "Based on sections [A] and [B] from github.repos/goldentooth/agent..."
4. Provide specific, actionable information when possible
5. If multiple sources contain relevant information, synthesize them coherently
6. When referencing chunks, use their titles and types for context (e.g., "the Setup section" vs "the technical details chunk")
7. Pay attention to chunk relationships - related chunks from the same document often provide complementary information
8. Use clear, technical language appropriate for developers and system administrators

Context Sources:
{context}

Remember: Only use information from the context sources above. Do not add information from your general knowledge. When document chunks are present, they represent focused sections of larger documents that have been identified as most relevant to your query. Multiple chunks from the same document may provide complementary information that should be considered together."""

        user_message = f"Question: {question}"

        try:
            response = await self.claude_client.create_chat_completion(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt.format(context=context),
                temperature=0.1,  # Low temperature for factual responses
                max_tokens=self.claude_client.default_max_tokens,
            )

            if isinstance(response, str):
                return response
            else:
                return "I was unable to generate a proper response. Please try again."

        except Exception as e:
            return f"I encountered an error while generating the response: {str(e)}"

    async def summarize_documents(
        self,
        store_type: str | None = None,
        max_documents: int = 10,
    ) -> dict[str, Any]:
        """Generate a summary of documents in the knowledge base.

        Args:
            store_type: Optional filter by document store type
            max_documents: Maximum number of documents to include in summary

        Returns:
            Dictionary with summary and metadata
        """
        try:
            # Get document counts and examples
            if store_type:
                if store_type == "github.orgs":
                    docs = self.document_store.github_orgs.list()[:max_documents]
                    doc_type = "GitHub Organizations"
                elif store_type == "github.repos":
                    docs = self.document_store.github_repos.list()[:max_documents]
                    doc_type = "GitHub Repositories"
                elif store_type == "goldentooth.nodes":
                    docs = self.document_store.goldentooth_nodes.list()[:max_documents]
                    doc_type = "Goldentooth Nodes"
                elif store_type == "goldentooth.services":
                    docs = self.document_store.goldentooth_services.list()[
                        :max_documents
                    ]
                    doc_type = "Goldentooth Services"
                elif store_type == "notes":
                    docs = self.document_store.notes.list()[:max_documents]
                    doc_type = "Notes"
                else:
                    return {
                        "summary": f"Unknown store type: {store_type}",
                        "metadata": {"error": True},
                    }

                doc_count = len(docs)
                context = f"Store Type: {doc_type}\nDocument Count: {doc_count}\nDocument IDs: {', '.join(docs)}"

            else:
                # Summarize all document types
                all_docs = self.document_store.list_all_documents()
                total_docs = sum(len(doc_list) for doc_list in all_docs.values())

                context_parts = [f"Total Documents: {total_docs}\n"]
                for store_name, doc_list in all_docs.items():
                    count = len(doc_list)
                    examples = doc_list[:3] if doc_list else []
                    context_parts.append(f"{store_name}: {count} documents")
                    if examples:
                        context_parts.append(f"  Examples: {', '.join(examples)}")

                context = "\n".join(context_parts)

            # Generate summary using Claude
            system_prompt = """You are a technical documentation assistant. Create a concise, informative summary of the knowledge base contents based on the provided information.

Focus on:
1. What types of information are available
2. The scope and scale of the knowledge base
3. Key areas that users can ask about
4. Any notable patterns or highlights from the document names

Keep the summary under 200 words and make it useful for someone wanting to understand what they can learn from this knowledge base."""

            user_message = f"Please summarize this knowledge base:\n\n{context}"

            response = await self.claude_client.create_chat_completion(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                temperature=0.3,
                max_tokens=500,
            )

            if isinstance(response, str):
                summary = response
            else:
                summary = "Unable to generate summary."

            return {
                "summary": summary,
                "metadata": {
                    "store_type": store_type,
                    "documents_analyzed": len(docs) if store_type else total_docs,
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "summary": f"Error generating summary: {str(e)}",
                "metadata": {
                    "error": True,
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            }

    async def get_document_insights(
        self, document_id: str, store_type: str
    ) -> dict[str, Any]:
        """Get AI-generated insights about a specific document.

        Args:
            document_id: ID of the document
            store_type: Type of document store

        Returns:
            Dictionary with insights and metadata
        """
        try:
            # Check if document exists and load it
            if not self.document_store.document_exists(store_type, document_id):
                return {
                    "insights": f"Document {store_type}/{document_id} not found.",
                    "metadata": {"error": True, "error_type": "DocumentNotFound"},
                }

            # Get document content
            doc_path = self.document_store.get_document_path(store_type, document_id)
            content = doc_path.read_text()

            # Generate insights using Claude
            system_prompt = """You are a technical analyst. Analyze the provided YAML document and generate insights about:

1. Purpose and function of this resource
2. Key configuration or characteristics
3. Dependencies or relationships mentioned
4. Current status or health indicators
5. Potential areas of interest for system administrators or developers
6. Any security or operational considerations

Provide concise, actionable insights in a structured format."""

            user_message = (
                f"Analyze this {store_type} document for {document_id}:\n\n{content}"
            )

            response = await self.claude_client.create_chat_completion(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                temperature=0.2,
                max_tokens=1000,
            )

            if isinstance(response, str):
                insights = response
            else:
                insights = "Unable to generate insights."

            return {
                "insights": insights,
                "document_id": document_id,
                "store_type": store_type,
                "metadata": {
                    "content_length": len(content),
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "insights": f"Error generating insights: {str(e)}",
                "metadata": {
                    "error": True,
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            }

    async def search_chunks_by_type(
        self,
        chunk_types: list[str],
        question: str | None = None,
        max_results: int = 10,
        store_type: str | None = None,
    ) -> dict[str, Any]:
        """Search for chunks of specific types, optionally with semantic similarity.

        Args:
            chunk_types: List of chunk types to search for (e.g., ['repo_core', 'note_section'])
            question: Optional question for semantic similarity search
            max_results: Maximum number of chunks to return
            store_type: Optional filter by document store type

        Returns:
            Dictionary with found chunks and metadata
        """
        try:
            if question:
                # Use semantic search with chunk type filtering
                result = await self.query(
                    question=question,
                    max_results=max_results,
                    store_type=store_type,
                    chunk_types=chunk_types,
                    prioritize_chunks=True,
                    include_chunks=True,
                    include_metadata=True,  # Need metadata to get retrieved documents
                    similarity_threshold=0.0,  # Use very low threshold for chunk search
                )

                # Extract just the chunks from the result
                chunks = [
                    doc
                    for doc in result.get("retrieved_documents", [])
                    if doc.get("is_chunk", False)
                ]

                return {
                    "chunks": chunks,
                    "total_found": len(chunks),
                    "search_method": "semantic_with_types",
                    "chunk_types_requested": chunk_types,
                    "question": question,
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                    },
                }
            else:
                # Direct database query for chunk types
                # This would require adding a method to VectorStore
                # For now, return empty results with a message
                return {
                    "chunks": [],
                    "total_found": 0,
                    "search_method": "direct_type_query",
                    "chunk_types_requested": chunk_types,
                    "message": "Direct chunk type querying without semantic search not yet implemented",
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                    },
                }

        except Exception as e:
            return {
                "chunks": [],
                "total_found": 0,
                "error": True,
                "error_message": str(e),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                },
            }

    async def get_document_chunk_summary(
        self, store_type: str, document_id: str, include_content_preview: bool = False
    ) -> dict[str, Any]:
        """Get a summary of all chunks for a specific document.

        Args:
            store_type: Type of document store
            document_id: ID of the document
            include_content_preview: Whether to include content previews for each chunk

        Returns:
            Dictionary with chunk summary and statistics
        """
        try:
            # Get chunks from vector store
            chunks = self.vector_store.get_document_chunks(store_type, document_id)

            if not chunks:
                return {
                    "document_id": document_id,
                    "store_type": store_type,
                    "has_chunks": False,
                    "total_chunks": 0,
                    "message": "Document has no chunks (may use full-document embedding)",
                }

            # Calculate statistics
            chunk_stats = {
                "total_chunks": len(chunks),
                "total_characters": sum(chunk["size_chars"] for chunk in chunks),
                "chunk_types": {},
                "avg_chunk_size": 0,
                "chunks": [],
            }

            # Analyze chunk types and create summaries
            for chunk in chunks:
                chunk_type = chunk["chunk_type"]
                if chunk_type not in chunk_stats["chunk_types"]:
                    chunk_stats["chunk_types"][chunk_type] = 0
                chunk_stats["chunk_types"][chunk_type] += 1

                chunk_summary = {
                    "chunk_id": chunk["chunk_id"],
                    "chunk_type": chunk_type,
                    "chunk_index": chunk["chunk_index"],
                    "title": chunk["title"],
                    "size_chars": chunk["size_chars"],
                }

                if include_content_preview:
                    content = chunk["content"]
                    preview_length = 200
                    chunk_summary["content_preview"] = (
                        content[:preview_length] + "..."
                        if len(content) > preview_length
                        else content
                    )

                chunk_stats["chunks"].append(chunk_summary)

            # Calculate average chunk size
            if chunks:
                chunk_stats["avg_chunk_size"] = chunk_stats["total_characters"] // len(
                    chunks
                )

            # Sort chunks by index
            chunk_stats["chunks"].sort(key=lambda x: x["chunk_index"])

            return {
                "document_id": document_id,
                "store_type": store_type,
                "has_chunks": True,
                **chunk_stats,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "document_id": document_id,
                "store_type": store_type,
                "error": True,
                "error_message": str(e),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                },
            }

    async def compare_chunks(
        self, chunk_ids: list[str], comparison_question: str | None = None
    ) -> dict[str, Any]:
        """Compare multiple chunks, optionally with a specific comparison question.

        Args:
            chunk_ids: List of chunk IDs to compare
            comparison_question: Optional question to guide the comparison

        Returns:
            Dictionary with comparison analysis
        """
        try:
            # Get chunk details from vector store
            chunks = []
            for chunk_id in chunk_ids:
                # Note: This would require a get_chunk_by_id method in VectorStore
                # For now, we'll return a placeholder
                pass

            if not comparison_question:
                comparison_question = "Compare and contrast these chunks, highlighting their similarities, differences, and complementary information."

            # Build context from chunks
            context_parts = []
            for i, chunk_id in enumerate(chunk_ids, 1):
                context_parts.append(
                    f"Chunk {i} ID: {chunk_id}\n[Chunk content would be retrieved here]\n"
                )

            context = "\n".join(context_parts)

            # Generate comparison using Claude
            system_prompt = """You are a technical analyst. Compare the provided chunks and generate insights about:

1. Key similarities between the chunks
2. Important differences
3. Complementary information that emerges when considered together
4. Relationships and dependencies between the content
5. Overall insights from the combined information

Provide a structured analysis that helps understand how these chunks relate to each other."""

            user_message = f"Compare these chunks based on: {comparison_question}\n\nChunks to compare:\n{context}"

            response = await self.claude_client.create_chat_completion(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                temperature=0.2,
                max_tokens=1500,
            )

            if isinstance(response, str):
                comparison = response
            else:
                comparison = "Unable to generate comparison."

            return {
                "comparison": comparison,
                "chunk_ids": chunk_ids,
                "comparison_question": comparison_question,
                "metadata": {
                    "chunks_compared": len(chunk_ids),
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "comparison": f"Error generating comparison: {str(e)}",
                "chunk_ids": chunk_ids,
                "error": True,
                "error_message": str(e),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                },
            }

    # Chunk Relationship Methods

    async def analyze_document_relationships(
        self,
        store_type: str = None,
        document_id: str = None,
        include_cross_document: bool = True,
    ) -> dict[str, Any]:
        """Analyze relationships between chunks in documents.

        Args:
            store_type: Optional store type to filter documents
            document_id: Optional specific document to analyze
            include_cross_document: Whether to analyze cross-document relationships

        Returns:
            Dictionary with relationship analysis results
        """
        try:
            from ..embeddings.chunk_relationships import ChunkRelationshipAnalyzer

            # Get chunks to analyze
            if document_id and store_type:
                # Analyze specific document
                chunks_data = self.vector_store.get_document_chunks(
                    store_type, document_id
                )
            else:
                # Get all chunks (or filtered by store type)
                # This would need to be implemented in vector_store
                chunks_data = self._get_all_chunks(store_type)

            if not chunks_data:
                return {
                    "error": True,
                    "message": "No chunks found for analysis",
                    "chunks_analyzed": 0,
                }

            # Convert to DocumentChunk objects and get embeddings
            from ..embeddings.document_chunker import DocumentChunk

            chunks = []
            embeddings = []

            for chunk_data in chunks_data:
                # Create DocumentChunk object
                chunk = DocumentChunk(
                    chunk_id=chunk_data["chunk_id"],
                    parent_doc_id=chunk_data["parent_document_id"],
                    store_type=chunk_data["parent_store_type"],
                    document_id=chunk_data["parent_document_id"].split(".")[-1],
                    chunk_type=chunk_data["chunk_type"],
                    content=chunk_data["content"],
                    metadata=chunk_data,
                    sequence=chunk_data.get("chunk_index", 1),
                )
                chunks.append(chunk)

                # Create embedding for the chunk
                embedding = await self.embeddings_service.create_embedding(
                    chunk.content
                )
                embeddings.append(embedding)

            # Analyze relationships
            analyzer = ChunkRelationshipAnalyzer(self.embeddings_service)
            relationship_data = await analyzer.analyze_chunk_relationships(
                chunks, embeddings, include_cross_document
            )

            # Store relationships in vector store
            all_relationships = []
            for rel_type, rel_list in relationship_data["relationships"].items():
                all_relationships.extend(rel_list)

            stored_count = self.vector_store.store_chunk_relationships(
                all_relationships
            )

            return {
                **relationship_data,
                "relationships_stored": stored_count,
                "analysis_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "error": True,
                "error_message": str(e),
                "chunks_analyzed": 0,
                "analysis_timestamp": datetime.now().isoformat(),
            }

    async def query_with_relationships(
        self,
        question: str,
        max_results: int = 5,
        expand_with_related: bool = True,
        relationship_expansion_radius: int = 1,
        include_relationship_context: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        """Enhanced query that leverages chunk relationships for better context.

        Args:
            question: The question to ask
            max_results: Maximum number of initial results
            expand_with_related: Whether to expand results with related chunks
            relationship_expansion_radius: How many relationship hops to include
            include_relationship_context: Whether to include relationship info in context
            **kwargs: Additional arguments passed to base query method

        Returns:
            Enhanced query results with relationship-aware context
        """
        try:
            # Start with base query
            base_result = await self.query(question, max_results=max_results, **kwargs)

            if not expand_with_related or base_result.get("error"):
                return base_result

            # Get initial chunk IDs
            retrieved_docs = base_result.get("retrieved_documents", [])
            initial_chunk_ids = [
                doc.get("chunk_id")
                for doc in retrieved_docs
                if doc.get("is_chunk") and doc.get("chunk_id")
            ]

            if not initial_chunk_ids:
                # No chunks to expand, return base result
                return base_result

            # Expand with related chunks
            from ..embeddings.chunk_relationships import ChunkRelationshipAnalyzer

            # Get relationship data (this would ideally be cached)
            relationship_data = {
                "relationships": {
                    rel_type: self.vector_store.get_chunk_relationships(
                        relationship_types=[rel_type]
                    )
                    for rel_type in [
                        "sequential",
                        "topical",
                        "hierarchical",
                        "cross_document",
                    ]
                }
            }

            # Expand chunk context
            analyzer = ChunkRelationshipAnalyzer(self.embeddings_service)
            expanded_chunk_ids = analyzer.get_chunk_context_expansion(
                initial_chunk_ids, relationship_data, relationship_expansion_radius
            )

            # Get details for expanded chunks
            expanded_chunks = []
            for chunk_id in expanded_chunk_ids:
                if chunk_id not in initial_chunk_ids:
                    chunk_details = self.vector_store.get_document_chunks(
                        "", "", chunk_id=chunk_id
                    )
                    if chunk_details:
                        chunk_info = chunk_details[0]
                        chunk_info["is_chunk"] = True
                        chunk_info["similarity_score"] = (
                            0.5  # Relationship-based inclusion
                        )
                        chunk_info["inclusion_reason"] = "related_chunk"
                        expanded_chunks.append(chunk_info)

            # Combine original and expanded results
            all_documents = retrieved_docs + expanded_chunks

            # Rebuild context with relationship information
            if include_relationship_context:
                enhanced_context = self._build_relationship_aware_context(
                    all_documents, initial_chunk_ids, relationship_data
                )
            else:
                enhanced_context = self._build_context(all_documents)

            # Generate enhanced response
            enhanced_response = await self._generate_response(
                question, enhanced_context
            )

            return {
                **base_result,
                "answer": enhanced_response,
                "retrieved_documents": all_documents,
                "metadata": {
                    **base_result.get("metadata", {}),
                    "initial_chunks": len(initial_chunk_ids),
                    "expanded_chunks": len(expanded_chunks),
                    "total_chunks_used": len(all_documents),
                    "relationship_expansion_radius": relationship_expansion_radius,
                    "enhancement_method": "relationship_expansion",
                },
            }

        except Exception as e:
            # Fall back to base query on error
            base_result = await self.query(question, max_results=max_results, **kwargs)
            base_result["metadata"] = base_result.get("metadata", {})
            base_result["metadata"]["relationship_enhancement_error"] = str(e)
            return base_result

    def _build_relationship_aware_context(
        self,
        documents: list[dict[str, Any]],
        primary_chunk_ids: list[str],
        relationship_data: dict[str, Any],
    ) -> str:
        """Build context with relationship information highlighted.

        Args:
            documents: List of document dictionaries
            primary_chunk_ids: IDs of primary chunks from search
            relationship_data: Relationship analysis data

        Returns:
            Enhanced context string with relationship information
        """
        # Group documents by type (primary vs related)
        primary_docs = []
        related_docs = []

        for doc in documents:
            if doc.get("chunk_id") in primary_chunk_ids:
                primary_docs.append(doc)
            else:
                related_docs.append(doc)

        context_parts = []

        # Add primary results
        if primary_docs:
            context_parts.append("=== PRIMARY SEARCH RESULTS ===\n")
            context_parts.append(self._build_context(primary_docs))

        # Add related chunks with relationship info
        if related_docs:
            context_parts.append("\n=== RELATED CONTENT ===\n")

            for i, doc in enumerate(related_docs, 1):
                chunk_id = doc.get("chunk_id")
                if chunk_id:
                    # Find relationships to primary chunks
                    relationships = []
                    for rel_type, rel_list in relationship_data.get(
                        "relationships", {}
                    ).items():
                        for rel in rel_list:
                            if (
                                rel["source_chunk_id"] == chunk_id
                                and rel["target_chunk_id"] in primary_chunk_ids
                            ) or (
                                rel["target_chunk_id"] == chunk_id
                                and rel["source_chunk_id"] in primary_chunk_ids
                            ):
                                relationships.append(
                                    f"{rel_type} (strength: {rel['strength']:.2f})"
                                )

                    rel_info = (
                        ", ".join(relationships)
                        if relationships
                        else "indirect relationship"
                    )

                    context_parts.append(
                        f"Related Source {i}: {doc.get('store_type', 'unknown')}/{doc.get('document_id', 'unknown')}"
                    )
                    context_parts.append(f"Relationship: {rel_info}")
                    context_parts.append(f"Content: {doc.get('content', '')}")
                    context_parts.append("")

        return "\n".join(context_parts)

    def _get_all_chunks(self, store_type: str = None) -> list[dict[str, Any]]:
        """Get all chunks, optionally filtered by store type.

        Args:
            store_type: Optional store type filter

        Returns:
            List of chunk dictionaries
        """
        # This is a simplified implementation
        # In practice, you'd want pagination for large datasets

        # Get all documents from the store type
        all_chunks = []

        if store_type:
            # Get chunks for specific store type
            documents = self.document_store.get_store(store_type).list_documents()
            for doc_id in documents:
                chunks = self.vector_store.get_document_chunks(store_type, doc_id)
                all_chunks.extend(chunks)
        else:
            # Get chunks from all store types
            for store_name in [
                "github.repos",
                "github.orgs",
                "notes",
                "goldentooth.services",
            ]:
                try:
                    store = self.document_store.get_store(store_name)
                    documents = store.list_documents()
                    for doc_id in documents:
                        chunks = self.vector_store.get_document_chunks(
                            store_name, doc_id
                        )
                        all_chunks.extend(chunks)
                except Exception:
                    # Store might not exist or be accessible
                    continue

        return all_chunks

    async def get_chunk_relationship_insights(self, chunk_id: str) -> dict[str, Any]:
        """Get insights about a specific chunk's relationships.

        Args:
            chunk_id: ID of the chunk to analyze

        Returns:
            Dictionary with relationship insights
        """
        try:
            # Get related chunks
            related_chunks = self.vector_store.get_related_chunks(
                chunk_id, max_related=20, min_strength=0.3
            )

            # Get relationship statistics
            relationships = self.vector_store.get_chunk_relationships(chunk_id=chunk_id)

            # Analyze relationship patterns
            relationship_types = {}
            strength_distribution = {"strong": 0, "moderate": 0, "weak": 0}

            for rel in relationships:
                rel_type = rel["relationship_type"]
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1

                strength = rel["strength"]
                if strength >= 0.8:
                    strength_distribution["strong"] += 1
                elif strength >= 0.6:
                    strength_distribution["moderate"] += 1
                else:
                    strength_distribution["weak"] += 1

            # Get chunk details
            chunk_details = self.vector_store.get_document_chunks(
                "", "", chunk_id=chunk_id
            )
            chunk_info = chunk_details[0] if chunk_details else {}

            return {
                "chunk_id": chunk_id,
                "chunk_info": chunk_info,
                "total_relationships": len(relationships),
                "relationship_types": relationship_types,
                "strength_distribution": strength_distribution,
                "related_chunks": related_chunks,
                "most_similar_chunks": [
                    {
                        "chunk_id": (
                            rel["target_chunk_id"]
                            if rel["source_chunk_id"] == chunk_id
                            else rel["source_chunk_id"]
                        ),
                        "relationship_type": rel["relationship_type"],
                        "strength": rel["strength"],
                    }
                    for rel in sorted(
                        relationships, key=lambda x: x["strength"], reverse=True
                    )[:5]
                ],
                "insights": self._generate_chunk_insights(
                    chunk_info, relationships, related_chunks
                ),
            }

        except Exception as e:
            return {
                "chunk_id": chunk_id,
                "error": True,
                "error_message": str(e),
            }

    def _generate_chunk_insights(
        self,
        chunk_info: dict[str, Any],
        relationships: list[dict[str, Any]],
        related_chunks: list[dict[str, Any]],
    ) -> list[str]:
        """Generate human-readable insights about chunk relationships."""
        insights = []

        if not relationships:
            insights.append(
                "This chunk has no established relationships with other chunks."
            )
            return insights

        # Connection insights
        total_rels = len(relationships)
        if total_rels > 10:
            insights.append(f"Highly connected chunk with {total_rels} relationships.")
        elif total_rels > 5:
            insights.append(f"Well-connected chunk with {total_rels} relationships.")
        else:
            insights.append(
                f"Moderately connected chunk with {total_rels} relationships."
            )

        # Relationship type insights
        rel_types = {}
        for rel in relationships:
            rel_types[rel["relationship_type"]] = (
                rel_types.get(rel["relationship_type"], 0) + 1
            )

        if "sequential" in rel_types:
            insights.append(
                f"Part of a sequential document structure ({rel_types['sequential']} sequential links)."
            )

        if "topical" in rel_types:
            insights.append(
                f"Shares topical similarity with {rel_types['topical']} other chunks."
            )

        if "cross_document" in rel_types:
            insights.append(
                f"Has cross-document relationships with {rel_types['cross_document']} chunks."
            )

        # Strength insights
        strong_rels = [r for r in relationships if r["strength"] >= 0.8]
        if strong_rels:
            insights.append(
                f"Has {len(strong_rels)} strong relationships indicating high semantic similarity."
            )

        return insights

    # Hybrid Search Methods

    async def hybrid_query(
        self,
        question: str,
        max_results: int = 5,
        store_type: str = None,
        include_chunks: bool = True,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        min_semantic_score: float = 0.1,
        min_keyword_score: float = 0.0,
        boost_exact_matches: bool = True,
        boost_title_matches: bool = True,
        explain_results: bool = False,
    ) -> dict[str, Any]:
        """Enhanced query using hybrid search (semantic + keyword).

        Args:
            question: The question to ask
            max_results: Maximum number of results to return
            store_type: Optional store type filter
            include_chunks: Whether to include chunk results
            semantic_weight: Weight for semantic similarity (0.0-1.0)
            keyword_weight: Weight for keyword scoring (0.0-1.0)
            min_semantic_score: Minimum semantic similarity threshold
            min_keyword_score: Minimum keyword score threshold
            boost_exact_matches: Whether to boost exact phrase matches
            boost_title_matches: Whether to boost title/metadata matches
            explain_results: Whether to include detailed scoring explanation

        Returns:
            Query results with hybrid scoring
        """
        try:
            # Perform hybrid search
            search_results = await self.hybrid_search_engine.hybrid_search(
                query=question,
                max_results=max_results,
                store_type=store_type,
                include_chunks=include_chunks,
                semantic_weight=semantic_weight,
                keyword_weight=keyword_weight,
                min_semantic_score=min_semantic_score,
                min_keyword_score=min_keyword_score,
                boost_exact_matches=boost_exact_matches,
                boost_title_matches=boost_title_matches,
            )

            if not search_results:
                return {
                    "question": question,
                    "answer": "I couldn't find any relevant documents using hybrid search. The search combines both semantic understanding and keyword matching, but no results met the criteria.",
                    "retrieved_documents": [],
                    "metadata": {
                        "search_method": "hybrid",
                        "documents_found": 0,
                        "documents_used": 0,
                        "semantic_weight": semantic_weight,
                        "keyword_weight": keyword_weight,
                        "error": False,
                    },
                }

            # Build context from hybrid results
            context = self._build_hybrid_context(search_results)

            # Generate response with enhanced system prompt
            enhanced_system = self._build_hybrid_system_prompt(
                context, question, semantic_weight, keyword_weight
            )
            response = await self.claude_client.create_chat_completion(
                messages=[{"role": "user", "content": question}],
                system=enhanced_system,
            )

            result = {
                "question": question,
                "answer": response,
                "retrieved_documents": search_results,
                "metadata": {
                    "search_method": "hybrid",
                    "documents_found": len(search_results),
                    "documents_used": len(search_results),
                    "semantic_weight": semantic_weight,
                    "keyword_weight": keyword_weight,
                    "boosting": {
                        "exact_matches": boost_exact_matches,
                        "title_matches": boost_title_matches,
                    },
                    "avg_hybrid_score": sum(
                        doc.get("hybrid_score", 0) for doc in search_results
                    )
                    / len(search_results),
                    "score_range": {
                        "min": min(
                            doc.get("hybrid_score", 0) for doc in search_results
                        ),
                        "max": max(
                            doc.get("hybrid_score", 0) for doc in search_results
                        ),
                    },
                    "search_composition": self._analyze_search_composition(
                        search_results
                    ),
                    "error": False,
                },
            }

            # Add detailed explanation if requested
            if explain_results:
                explanation = await self.hybrid_search_engine.explain_search_results(
                    question, search_results
                )
                result["search_explanation"] = explanation

            return result

        except Exception as e:
            return {
                "question": question,
                "answer": f"I encountered an error while performing hybrid search: {str(e)}",
                "retrieved_documents": [],
                "metadata": {
                    "search_method": "hybrid",
                    "error": True,
                    "error_message": str(e),
                    "documents_found": 0,
                    "documents_used": 0,
                },
            }

    def _build_hybrid_context(self, search_results: list[dict[str, Any]]) -> str:
        """Build context specifically for hybrid search results."""
        if not search_results:
            return ""

        context_parts = []

        # Group results by search method contribution
        semantic_results = [r for r in search_results if r.get("semantic_score", 0) > 0]
        keyword_results = [r for r in search_results if r.get("keyword_score", 0) > 0]

        # Add introduction
        context_parts.append("=== HYBRID SEARCH RESULTS ===")
        context_parts.append(
            f"Found {len(search_results)} relevant sources using combined semantic and keyword analysis."
        )
        context_parts.append("")

        # Add results with scoring information
        for i, result in enumerate(search_results, 1):
            # Document header
            store_type = result.get("store_type", "unknown")
            doc_id = result.get("document_id", "unknown")

            if result.get("is_chunk"):
                title = result.get(
                    "chunk_title", result.get("title", "Untitled Section")
                )
                context_parts.append(f"Source {i}: {store_type}/{doc_id} - {title}")
            else:
                context_parts.append(f"Source {i}: {store_type}/{doc_id}")

            # Scoring breakdown
            scoring = result.get("scoring_breakdown", {})
            hybrid_score = result.get("hybrid_score", 0)
            semantic_score = scoring.get("semantic_score", 0)
            keyword_score = scoring.get("keyword_score", 0)

            score_info = f"Relevance: {hybrid_score:.3f} "
            if semantic_score > 0 and keyword_score > 0:
                score_info += (
                    f"(semantic: {semantic_score:.3f}, keyword: {keyword_score:.3f})"
                )
            elif semantic_score > 0:
                score_info += "(semantic match)"
            elif keyword_score > 0:
                score_info += "(keyword match)"

            context_parts.append(score_info)
            context_parts.append("")

            # Content
            content = result.get("content", "")
            if len(content) > 2000:
                content = content[:2000] + "..."
            context_parts.append(content)
            context_parts.append("")

        return "\n".join(context_parts)

    def _build_hybrid_system_prompt(
        self, context: str, question: str, semantic_weight: float, keyword_weight: float
    ) -> str:
        """Build enhanced system prompt for hybrid search results."""
        base_prompt = f"""You are an AI assistant helping users find information from a knowledge base. You have access to relevant documents found through hybrid search that combines semantic understanding and keyword matching.

SEARCH METHODOLOGY:
- Semantic matching (weight: {semantic_weight:.1f}): Finds documents with similar meaning and concepts
- Keyword matching (weight: {keyword_weight:.1f}): Finds documents containing specific terms and phrases
- Results are ranked by combined relevance score with additional boosting for exact matches

CONTEXT:
{context}

INSTRUCTIONS:
1. Answer the user's question using the provided context sources
2. Prioritize information from higher-scoring sources, but consider all relevant information
3. If sources contain conflicting information, acknowledge the differences
4. Mention when information comes from semantic matches vs keyword matches if relevant
5. Be specific about which sources support different parts of your answer
6. If the context doesn't fully answer the question, acknowledge the limitations

Provide a comprehensive, accurate response based on the hybrid search results."""

        return base_prompt

    def _analyze_search_composition(
        self, search_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze the composition of hybrid search results."""
        if not search_results:
            return {}

        semantic_only = []
        keyword_only = []
        both_methods = []

        for result in search_results:
            scoring = result.get("scoring_breakdown", {})
            semantic_score = scoring.get("semantic_score", 0)
            keyword_score = scoring.get("keyword_score", 0)

            if semantic_score > 0 and keyword_score > 0:
                both_methods.append(result)
            elif semantic_score > 0:
                semantic_only.append(result)
            elif keyword_score > 0:
                keyword_only.append(result)

        return {
            "total_results": len(search_results),
            "semantic_only": len(semantic_only),
            "keyword_only": len(keyword_only),
            "both_methods": len(both_methods),
            "semantic_results": len(semantic_only) + len(both_methods),
            "keyword_results": len(keyword_only) + len(both_methods),
        }

    async def compare_search_methods(
        self,
        question: str,
        max_results: int = 5,
        store_type: str = None,
        include_chunks: bool = True,
    ) -> dict[str, Any]:
        """Compare results from different search methods.

        Args:
            question: The question to search for
            max_results: Maximum results per method
            store_type: Optional store type filter
            include_chunks: Whether to include chunks

        Returns:
            Comparison of semantic, keyword, and hybrid search results
        """
        try:
            # Run all three search methods
            semantic_results = await self.query(
                question=question,
                max_results=max_results,
                store_type=store_type,
                include_chunks=include_chunks,
                similarity_threshold=0.1,
            )

            hybrid_results = await self.hybrid_query(
                question=question,
                max_results=max_results,
                store_type=store_type,
                include_chunks=include_chunks,
                semantic_weight=0.7,
                keyword_weight=0.3,
            )

            # Get keyword-only results (by setting semantic weight to 0)
            keyword_results = await self.hybrid_query(
                question=question,
                max_results=max_results,
                store_type=store_type,
                include_chunks=include_chunks,
                semantic_weight=0.0,
                keyword_weight=1.0,
            )

            # Analyze overlap and differences
            semantic_docs = set(
                self._get_doc_id_from_result(r)
                for r in semantic_results.get("retrieved_documents", [])
            )
            keyword_docs = set(
                self._get_doc_id_from_result(r)
                for r in keyword_results.get("retrieved_documents", [])
            )
            hybrid_docs = set(
                self._get_doc_id_from_result(r)
                for r in hybrid_results.get("retrieved_documents", [])
            )

            overlap_analysis = {
                "semantic_only": list(semantic_docs - keyword_docs),
                "keyword_only": list(keyword_docs - semantic_docs),
                "both_methods": list(semantic_docs & keyword_docs),
                "hybrid_unique": list(hybrid_docs - (semantic_docs | keyword_docs)),
                "total_unique_docs": len(semantic_docs | keyword_docs | hybrid_docs),
            }

            return {
                "question": question,
                "semantic_search": {
                    "method": "Semantic similarity (embeddings)",
                    "results_count": len(
                        semantic_results.get("retrieved_documents", [])
                    ),
                    "top_results": semantic_results.get("retrieved_documents", [])[:3],
                    "avg_similarity": self._calculate_avg_score(
                        semantic_results.get("retrieved_documents", []),
                        "similarity_score",
                    ),
                },
                "keyword_search": {
                    "method": "Keyword matching (BM25)",
                    "results_count": len(
                        keyword_results.get("retrieved_documents", [])
                    ),
                    "top_results": keyword_results.get("retrieved_documents", [])[:3],
                    "avg_score": self._calculate_avg_score(
                        keyword_results.get("retrieved_documents", []), "hybrid_score"
                    ),
                },
                "hybrid_search": {
                    "method": "Combined semantic + keyword",
                    "results_count": len(hybrid_results.get("retrieved_documents", [])),
                    "top_results": hybrid_results.get("retrieved_documents", [])[:3],
                    "avg_score": self._calculate_avg_score(
                        hybrid_results.get("retrieved_documents", []), "hybrid_score"
                    ),
                    "composition": self._analyze_search_composition(
                        hybrid_results.get("retrieved_documents", [])
                    ),
                },
                "overlap_analysis": overlap_analysis,
                "recommendations": self._generate_search_recommendations(
                    overlap_analysis, semantic_results, keyword_results, hybrid_results
                ),
            }

        except Exception as e:
            return {
                "question": question,
                "error": True,
                "error_message": str(e),
            }

    def _get_doc_id_from_result(self, result: dict[str, Any]) -> str:
        """Extract document ID from search result."""
        if result.get("is_chunk") and result.get("chunk_id"):
            return result["chunk_id"]
        else:
            return f"{result.get('store_type', 'unknown')}.{result.get('document_id', 'unknown')}"

    def _calculate_avg_score(
        self, results: list[dict[str, Any]], score_key: str
    ) -> float:
        """Calculate average score for results."""
        if not results:
            return 0.0
        scores = [r.get(score_key, 0) for r in results]
        return sum(scores) / len(scores)

    def _generate_search_recommendations(
        self,
        overlap_analysis: dict[str, Any],
        semantic_results: dict[str, Any],
        keyword_results: dict[str, Any],
        hybrid_results: dict[str, Any],
    ) -> list[str]:
        """Generate recommendations for search method selection."""
        recommendations = []

        semantic_count = len(semantic_results.get("retrieved_documents", []))
        keyword_count = len(keyword_results.get("retrieved_documents", []))
        hybrid_count = len(hybrid_results.get("retrieved_documents", []))

        both_methods_count = len(overlap_analysis.get("both_methods", []))

        if hybrid_count > max(semantic_count, keyword_count):
            recommendations.append(
                "Hybrid search found the most results by combining both approaches."
            )

        if both_methods_count > 0:
            recommendations.append(
                f"{both_methods_count} documents were found by both semantic and keyword methods, indicating high relevance."
            )

        if len(overlap_analysis.get("semantic_only", [])) > 0:
            recommendations.append(
                "Semantic search found unique conceptual matches that keyword search missed."
            )

        if len(overlap_analysis.get("keyword_only", [])) > 0:
            recommendations.append(
                "Keyword search found unique exact matches that semantic search missed."
            )

        if semantic_count == 0 and keyword_count > 0:
            recommendations.append(
                "Consider using keyword-focused search for this query type."
            )
        elif keyword_count == 0 and semantic_count > 0:
            recommendations.append(
                "Consider using semantic-focused search for this query type."
            )
        elif hybrid_count > semantic_count and hybrid_count > keyword_count:
            recommendations.append(
                "Hybrid search is recommended for optimal recall and precision."
            )

        return recommendations

    async def tune_hybrid_search(
        self,
        test_queries: list[str],
        semantic_weights: list[float] = None,
        keyword_weights: list[float] = None,
    ) -> dict[str, Any]:
        """Tune hybrid search parameters using test queries.

        Args:
            test_queries: List of test queries to evaluate
            semantic_weights: List of semantic weights to test
            keyword_weights: List of keyword weights to test

        Returns:
            Tuning results and recommendations
        """
        if semantic_weights is None:
            semantic_weights = [0.5, 0.6, 0.7, 0.8, 0.9]
        if keyword_weights is None:
            keyword_weights = [0.1, 0.2, 0.3, 0.4, 0.5]

        results = []

        for semantic_weight in semantic_weights:
            for keyword_weight in keyword_weights:
                # Normalize weights
                total = semantic_weight + keyword_weight
                if total == 0:
                    continue

                normalized_semantic = semantic_weight / total
                normalized_keyword = keyword_weight / total

                query_results = []

                for query in test_queries:
                    try:
                        result = await self.hybrid_query(
                            question=query,
                            semantic_weight=normalized_semantic,
                            keyword_weight=normalized_keyword,
                            max_results=10,
                        )

                        query_results.append(
                            {
                                "query": query,
                                "results_count": len(
                                    result.get("retrieved_documents", [])
                                ),
                                "avg_score": result.get("metadata", {}).get(
                                    "avg_hybrid_score", 0
                                ),
                                "composition": result.get("metadata", {}).get(
                                    "search_composition", {}
                                ),
                            }
                        )

                    except Exception as e:
                        query_results.append(
                            {
                                "query": query,
                                "error": str(e),
                            }
                        )

                results.append(
                    {
                        "semantic_weight": normalized_semantic,
                        "keyword_weight": normalized_keyword,
                        "query_results": query_results,
                        "avg_results_count": sum(
                            r.get("results_count", 0) for r in query_results
                        )
                        / len(query_results),
                        "avg_score": sum(r.get("avg_score", 0) for r in query_results)
                        / len(query_results),
                    }
                )

        # Find best configuration
        best_config = max(results, key=lambda x: x["avg_score"])

        return {
            "test_queries": test_queries,
            "configurations_tested": len(results),
            "results": results,
            "best_configuration": {
                "semantic_weight": best_config["semantic_weight"],
                "keyword_weight": best_config["keyword_weight"],
                "avg_score": best_config["avg_score"],
                "avg_results_count": best_config["avg_results_count"],
            },
            "recommendations": [
                f"Optimal semantic weight: {best_config['semantic_weight']:.2f}",
                f"Optimal keyword weight: {best_config['keyword_weight']:.2f}",
                f"This configuration achieved an average score of {best_config['avg_score']:.3f}",
            ],
        }
