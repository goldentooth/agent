from collections import defaultdict
from datetime import datetime
from typing import Any

from antidote import inject, injectable

from ..document_store import DocumentStore
from ..embeddings import EmbeddingsService, OpenAIEmbeddingsService, VectorStore
from ..embeddings.hybrid_search import HybridSearchEngine
from ..llm.claude_client import ClaudeFlowClient
from .chunk_fusion import ChunkFusion
from .query_expansion import QueryExpansion, QueryExpansionEngine


@injectable
class RAGService:
    """Retrieval-Augmented Generation service for intelligent document querying."""

    def __init__(
        self,
        document_store: DocumentStore = inject.me(),
        embeddings_service: OpenAIEmbeddingsService | EmbeddingsService = inject.me(),
        vector_store: VectorStore = inject.me(),
        claude_client: ClaudeFlowClient | None = None,
        hybrid_search_engine: HybridSearchEngine = inject.me(),
        chunk_fusion: ChunkFusion | None = None,
        query_expansion_engine: QueryExpansionEngine | None = None,
    ) -> None:
        """Initialize the RAG service.

        Args:
            document_store: Document store for accessing YAML documents
            embeddings_service: Service for creating embeddings
            vector_store: Vector database for similarity search
            claude_client: Claude client for generating responses
            hybrid_search_engine: Hybrid search engine for combining semantic and keyword search
            chunk_fusion: Chunk fusion engine for multi-chunk answer synthesis
            query_expansion_engine: Query expansion engine for intelligent query enhancement
        """
        self.document_store = document_store
        self.embeddings_service = embeddings_service
        self.vector_store = vector_store
        self.hybrid_search_engine = hybrid_search_engine
        self.chunk_fusion = chunk_fusion or ChunkFusion()
        self.query_expansion_engine = query_expansion_engine or QueryExpansionEngine()

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
                        {
                            doc.get("chunk_type")
                            for doc in filtered_docs
                            if doc.get("is_chunk", False) and doc.get("chunk_type")
                        }
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
                # chunk_id available but not currently used
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
                for _j, chunk in enumerate(chunks):
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
            # chunks = []  # TODO: Implement when VectorStore has get_chunk_by_id
            for _chunk_id in chunk_ids:
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
            for _rel_type, rel_list in relationship_data["relationships"].items():
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

        # Group results by search method contribution (for future analysis)
        # semantic_results = [r for r in search_results if r.get("semantic_score", 0) > 0]
        # keyword_results = [r for r in search_results if r.get("keyword_score", 0) > 0]

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
            semantic_docs = {
                self._get_doc_id_from_result(r)
                for r in semantic_results.get("retrieved_documents", [])
            }
            keyword_docs = {
                self._get_doc_id_from_result(r)
                for r in keyword_results.get("retrieved_documents", [])
            }
            hybrid_docs = {
                self._get_doc_id_from_result(r)
                for r in hybrid_results.get("retrieved_documents", [])
            }

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

    async def query_with_fusion(
        self,
        question: str,
        max_results: int = 10,
        store_type: str | None = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        max_clusters: int = 3,
        fusion_coherence_threshold: float = 0.6,
        include_unfused: bool = True,
    ) -> dict[str, Any]:
        """Execute a hybrid query with intelligent chunk fusion.

        Args:
            question: Query question
            max_results: Maximum number of results to retrieve before fusion
            store_type: Optional filter by document store type
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            max_clusters: Maximum number of fused answer clusters to create
            fusion_coherence_threshold: Minimum coherence for chunk clustering
            include_unfused: Whether to include unfused results as well

        Returns:
            Dictionary with fused answers, unfused results, and metadata
        """
        try:
            # First perform hybrid search to get relevant chunks
            hybrid_result = await self.hybrid_query(
                question=question,
                max_results=max_results * 2,  # Get more results for fusion
                store_type=store_type,
                semantic_weight=semantic_weight,
                keyword_weight=keyword_weight,
                include_metadata=True,
                include_explanations=True,
            )

            retrieved_docs = hybrid_result.get("retrieved_documents", [])

            if not retrieved_docs:
                return {
                    "fused_answers": [],
                    "unfused_results": [],
                    "context": "No relevant documents found.",
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "fusion_attempted": False,
                        "reason": "No documents retrieved",
                    },
                }

            # Convert retrieved documents to SearchResult format for fusion
            from ..embeddings.models import Chunk, SearchResult

            search_results = []
            for doc in retrieved_docs:
                if doc.get("is_chunk", False):
                    chunk = Chunk(
                        chunk_id=doc["chunk_id"],
                        document_id=doc["document_id"],
                        content=doc["content"],
                        position=doc.get("chunk_position", 0),
                        metadata=doc.get("metadata", {}),
                        chunk_type=doc.get("chunk_type", "unknown"),
                    )

                    # Use combined score from hybrid search
                    relevance_score = doc.get(
                        "combined_score", doc.get("similarity", 0.5)
                    )

                    search_result = SearchResult(
                        chunk=chunk,
                        relevance_score=relevance_score,
                        metadata={
                            "search_method": doc.get("search_method", "hybrid"),
                            "explanation": doc.get("explanation", ""),
                        },
                    )
                    search_results.append(search_result)

            # Attempt chunk fusion if we have enough chunks
            fused_answers = []
            if len(search_results) >= self.chunk_fusion.min_chunks_for_fusion:
                # Configure chunk fusion with custom threshold if provided
                if fusion_coherence_threshold != self.chunk_fusion.coherence_threshold:
                    self.chunk_fusion.coherence_threshold = fusion_coherence_threshold

                # Perform fusion
                fused_answers = self.chunk_fusion.fuse_chunks(
                    search_results=search_results,
                    query=question,
                    max_clusters=max_clusters,
                )

            # Generate response context from fused answers
            context_parts = []

            if fused_answers:
                context_parts.append("=== Synthesized Answers ===\n")

                for i, answer in enumerate(fused_answers, 1):
                    context_parts.append(
                        f"Answer {i} (Confidence: {answer.confidence_score:.2f}):"
                    )
                    context_parts.append(answer.content)

                    if answer.contradictions:
                        context_parts.append("\nPotential Contradictions:")
                        for contradiction in answer.contradictions:
                            context_parts.append(f"  - {contradiction}")

                    context_parts.append(
                        f"\nBased on {answer.num_sources} chunks from {len(answer.source_documents)} documents\n"
                    )

            # Include unfused results if requested
            unfused_results = []
            if include_unfused and search_results:
                # Get chunks that weren't part of any fusion
                fused_chunk_ids = set()
                for answer in fused_answers:
                    fused_chunk_ids.update({c.chunk_id for c in answer.source_chunks})

                unfused_results = [
                    sr
                    for sr in search_results
                    if sr.chunk.chunk_id not in fused_chunk_ids
                ][:max_results]

                if unfused_results:
                    context_parts.append("\n=== Additional Relevant Chunks ===\n")

                    for result in unfused_results:
                        chunk = result.chunk
                        context_parts.append(
                            f"[{chunk.chunk_type}] From {chunk.document_id} (Relevance: {result.relevance_score:.2f}):"
                        )
                        context_parts.append(
                            chunk.content[:500] + "..."
                            if len(chunk.content) > 500
                            else chunk.content
                        )
                        context_parts.append("")

            context = (
                "\n".join(context_parts)
                if context_parts
                else "No relevant context found."
            )

            # Generate final response
            response = ""
            if context != "No relevant context found.":
                response = await self._generate_response(question, context)

            # Prepare result
            return {
                "response": response,
                "context": context,
                "fused_answers": [
                    {
                        "content": answer.content,
                        "confidence_score": answer.confidence_score,
                        "coherence_score": answer.coherence_score,
                        "completeness_score": answer.completeness_score,
                        "num_sources": answer.num_sources,
                        "source_documents": list(answer.source_documents),
                        "key_points": answer.key_points,
                        "contradictions": answer.contradictions,
                        "metadata": answer.metadata,
                    }
                    for answer in fused_answers
                ],
                "unfused_results": [
                    {
                        "chunk_id": result.chunk.chunk_id,
                        "document_id": result.chunk.document_id,
                        "content": (
                            result.chunk.content[:200] + "..."
                            if len(result.chunk.content) > 200
                            else result.chunk.content
                        ),
                        "relevance_score": result.relevance_score,
                        "chunk_type": result.chunk.chunk_type,
                    }
                    for result in unfused_results
                ],
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "fusion_attempted": True,
                    "num_chunks_retrieved": len(search_results),
                    "num_fused_answers": len(fused_answers),
                    "num_unfused_results": len(unfused_results),
                    "fusion_settings": {
                        "coherence_threshold": fusion_coherence_threshold,
                        "max_clusters": max_clusters,
                        "min_chunks_for_fusion": self.chunk_fusion.min_chunks_for_fusion,
                        "max_chunks_for_fusion": self.chunk_fusion.max_chunks_for_fusion,
                    },
                    "search_settings": {
                        "semantic_weight": semantic_weight,
                        "keyword_weight": keyword_weight,
                    },
                },
            }

        except Exception as e:
            return {
                "response": "",
                "context": f"Error during fusion query: {str(e)}",
                "fused_answers": [],
                "unfused_results": [],
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "error": True,
                    "error_message": str(e),
                },
            }

    async def analyze_fusion_quality(
        self,
        question: str,
        max_results: int = 15,
        test_configurations: list[dict[str, float]] | None = None,
    ) -> dict[str, Any]:
        """Analyze and compare different fusion configurations.

        Args:
            question: Query question to test
            max_results: Maximum results per configuration
            test_configurations: List of fusion configurations to test

        Returns:
            Analysis of fusion quality across configurations
        """
        if test_configurations is None:
            test_configurations = [
                {"coherence_threshold": 0.5, "max_clusters": 2},
                {"coherence_threshold": 0.6, "max_clusters": 3},
                {"coherence_threshold": 0.7, "max_clusters": 3},
                {"coherence_threshold": 0.8, "max_clusters": 4},
            ]

        results = []

        for config in test_configurations:
            fusion_result = await self.query_with_fusion(
                question=question,
                max_results=max_results,
                fusion_coherence_threshold=config.get("coherence_threshold", 0.6),
                max_clusters=config.get("max_clusters", 3),
                include_unfused=True,
            )

            # Analyze fusion quality
            fused_answers = fusion_result.get("fused_answers", [])

            quality_metrics = {
                "configuration": config,
                "num_fused_answers": len(fused_answers),
                "avg_confidence": (
                    sum(a["confidence_score"] for a in fused_answers)
                    / len(fused_answers)
                    if fused_answers
                    else 0
                ),
                "avg_coherence": (
                    sum(a["coherence_score"] for a in fused_answers)
                    / len(fused_answers)
                    if fused_answers
                    else 0
                ),
                "avg_completeness": (
                    sum(a["completeness_score"] for a in fused_answers)
                    / len(fused_answers)
                    if fused_answers
                    else 0
                ),
                "total_chunks_used": sum(a["num_sources"] for a in fused_answers),
                "has_contradictions": any(a["contradictions"] for a in fused_answers),
                "avg_key_points": (
                    sum(len(a["key_points"]) for a in fused_answers)
                    / len(fused_answers)
                    if fused_answers
                    else 0
                ),
            }

            results.append(
                {
                    "configuration": config,
                    "metrics": quality_metrics,
                    "fused_answers": fused_answers[
                        :2
                    ],  # Include top 2 answers for inspection
                }
            )

        # Find best configuration
        best_config = max(
            results,
            key=lambda r: r["metrics"]["avg_confidence"]
            * r["metrics"]["avg_coherence"],
        )

        return {
            "question": question,
            "configurations_tested": len(test_configurations),
            "results": results,
            "best_configuration": best_config["configuration"],
            "best_metrics": best_config["metrics"],
            "recommendations": self._generate_fusion_recommendations(results),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
            },
        }

    def _generate_fusion_recommendations(
        self, results: list[dict[str, Any]]
    ) -> list[str]:
        """Generate recommendations based on fusion analysis results."""
        recommendations = []

        # Analyze confidence scores
        confidences = [r["metrics"]["avg_confidence"] for r in results]
        if max(confidences) < 0.5:
            recommendations.append(
                "Consider adjusting coherence threshold lower to allow more chunks to fuse"
            )

        # Analyze coherence
        coherences = [r["metrics"]["avg_coherence"] for r in results]
        if max(coherences) < 0.6:
            recommendations.append(
                "Low coherence suggests chunks may be from disparate sources - consider more focused queries"
            )

        # Analyze completeness
        completenesses = [r["metrics"]["avg_completeness"] for r in results]
        if max(completenesses) < 0.7:
            recommendations.append(
                "Low completeness scores - consider retrieving more chunks or improving chunk quality"
            )

        # Check for contradictions
        has_contradictions = any(r["metrics"]["has_contradictions"] for r in results)
        if has_contradictions:
            recommendations.append(
                "Contradictions detected - review source documents for consistency"
            )

        # Optimal cluster count
        cluster_counts = [r["metrics"]["num_fused_answers"] for r in results]
        if max(cluster_counts) == 1:
            recommendations.append(
                "Only single clusters formed - coherence threshold may be too high"
            )
        elif max(cluster_counts) > 5:
            recommendations.append(
                "Many clusters formed - consider raising coherence threshold for more focused answers"
            )

        return recommendations

    async def enhanced_query(
        self,
        question: str,
        max_results: int = 10,
        store_type: str | None = None,
        domain_context: str | None = None,
        enable_expansion: bool = True,
        enable_fusion: bool = True,
        expansion_strategies: int = 2,
        auto_reformulate: bool = True,
    ) -> dict[str, Any]:
        """Enhanced query with intelligent expansion, multi-strategy search, and fusion.

        Args:
            question: User's question
            max_results: Maximum number of results per strategy
            store_type: Optional filter by document store type
            domain_context: Optional domain context for better expansion
            enable_expansion: Whether to use query expansion
            enable_fusion: Whether to use chunk fusion
            expansion_strategies: Number of expansion strategies to try
            auto_reformulate: Whether to auto-reformulate on poor results

        Returns:
            Enhanced query results with expansion metadata and fused answers
        """
        try:
            start_time = datetime.now()

            # Step 1: Analyze and expand the query
            expansion_result = None
            strategies = []

            if enable_expansion:
                expansion_result = self.query_expansion_engine.expand_query(
                    question,
                    domain_context=domain_context,
                    include_synonyms=True,
                    include_related=True,
                    max_expansions=expansion_strategies + 2,
                )

                strategies = self.query_expansion_engine.create_search_strategies(
                    expansion_result,
                    max_strategies=expansion_strategies,
                )
                # If no strategies returned, create a fallback strategy
                if not strategies:
                    from .query_expansion import QueryIntent, SearchStrategy

                    strategies = [
                        SearchStrategy(
                            strategy_type="fallback",
                            queries=[question],
                            weights=[1.0],
                            search_params={
                                "similarity_threshold": 0.1,
                                "max_results": max_results,
                            },
                            expected_intent=QueryIntent.GENERAL,
                        )
                    ]
            else:
                # Create single strategy with original query
                from .query_expansion import QueryIntent, SearchStrategy

                strategies = [
                    SearchStrategy(
                        strategy_type="original",
                        queries=[question],
                        weights=[1.0],
                        search_params={
                            "similarity_threshold": 0.1,
                            "max_results": max_results,
                        },
                        expected_intent=QueryIntent.GENERAL,
                    )
                ]

            # Step 2: Execute multiple search strategies
            strategy_results = []
            all_retrieved_docs = []

            for _i, strategy in enumerate(strategies):
                strategy_docs = []

                for j, query in enumerate(strategy.queries):
                    weight = strategy.weights[j] if j < len(strategy.weights) else 0.5

                    # Execute hybrid search for this query
                    # Prepare search params, ensuring no duplicate max_results and mapping parameters
                    search_params = self._map_search_params_for_hybrid_query(
                        strategy.search_params, max_results
                    )

                    search_result = await self.hybrid_query(
                        question=query,
                        store_type=store_type,
                        **search_params,
                    )

                    # Weight and collect results
                    for doc in search_result.get("retrieved_documents", []):
                        doc["strategy_weight"] = weight
                        doc["strategy_type"] = strategy.strategy_type
                        doc["query_variant"] = query
                        doc["weighted_score"] = doc.get("hybrid_score", 0) * weight
                        strategy_docs.append(doc)

                strategy_results.append(
                    {
                        "strategy": strategy.strategy_type,
                        "queries": strategy.queries,
                        "results_count": len(strategy_docs),
                        "docs": strategy_docs,
                    }
                )

                all_retrieved_docs.extend(strategy_docs)

            # Step 3: Merge and deduplicate results
            merged_docs = self._merge_strategy_results(all_retrieved_docs)

            # Step 4: Check if reformulation is needed
            if auto_reformulate and len(merged_docs) < 3:
                reformulated_queries = self.query_expansion_engine.reformulate_query(
                    question,
                    search_results_count=len(merged_docs),
                    search_quality_score=0.3,  # Low quality due to few results
                )

                # Try best reformulated query
                if reformulated_queries:
                    reformulated_result = await self.hybrid_query(
                        question=reformulated_queries[0],
                        max_results=max_results,
                        store_type=store_type,
                    )

                    for doc in reformulated_result.get("retrieved_documents", []):
                        doc["strategy_type"] = "reformulated"
                        doc["query_variant"] = reformulated_queries[0]
                        # Ensure hybrid_score exists for proper weighted_score calculation
                        if "hybrid_score" not in doc:
                            doc["hybrid_score"] = doc.get(
                                "combined_score", doc.get("similarity_score", 0.5)
                            )
                        doc["weighted_score"] = doc.get("hybrid_score", 0) * 0.8

                    merged_docs.extend(
                        reformulated_result.get("retrieved_documents", [])
                    )
                    merged_docs = self._merge_strategy_results(merged_docs)

            # Step 5: Apply chunk fusion if enabled
            fused_answers = []
            if enable_fusion and merged_docs:
                # Convert to SearchResult format for fusion
                from ..embeddings.models import Chunk, SearchResult

                search_results = []
                for doc in merged_docs:
                    if doc.get("is_chunk", False):
                        chunk = Chunk(
                            chunk_id=doc["chunk_id"],
                            document_id=doc["document_id"],
                            content=doc["content"],
                            position=doc.get("chunk_position", 0),
                            metadata=doc.get("metadata", {}),
                            chunk_type=doc.get("chunk_type", "unknown"),
                        )

                        search_result = SearchResult(
                            chunk=chunk,
                            relevance_score=doc.get(
                                "weighted_score", doc.get("hybrid_score", 0.5)
                            ),
                            metadata={
                                "strategy_type": doc.get("strategy_type", "unknown"),
                                "query_variant": doc.get("query_variant", question),
                            },
                        )
                        search_results.append(search_result)

                if len(search_results) >= self.chunk_fusion.min_chunks_for_fusion:
                    fused_answers = self.chunk_fusion.fuse_chunks(
                        search_results=search_results,
                        query=question,
                        max_clusters=3,
                    )

            # Step 6: Build enhanced context
            context = self._build_enhanced_context(
                merged_docs, fused_answers, expansion_result, question
            )

            # Step 7: Generate response
            response = ""
            if context != "No relevant context found.":
                response = await self._generate_enhanced_response(
                    question, context, expansion_result
                )

            # Step 8: Prepare comprehensive result
            end_time = datetime.now()

            return {
                "response": response,
                "context": context,
                "question": question,
                "expanded_query": (
                    {
                        "original_query": question,
                        "expanded_queries": (
                            expansion_result.expanded_queries
                            if expansion_result
                            else [question]
                        ),
                        "intent": (
                            expansion_result.intent.value
                            if expansion_result
                            else "general"
                        ),
                        "key_terms": (
                            expansion_result.key_terms if expansion_result else []
                        ),
                        "synonyms": (
                            expansion_result.synonyms if expansion_result else {}
                        ),
                        "related_terms": (
                            expansion_result.related_terms if expansion_result else []
                        ),
                        "confidence": (
                            expansion_result.confidence if expansion_result else 0.5
                        ),
                        "suggestions": (
                            expansion_result.suggestions if expansion_result else []
                        ),
                    }
                    if expansion_result
                    else None
                ),
                "search_strategies": [
                    {
                        "strategy": sr["strategy"],
                        "queries": sr["queries"],
                        "results_count": sr["results_count"],
                    }
                    for sr in strategy_results
                ],
                "fused_answers": [
                    {
                        "content": answer.content,
                        "confidence_score": answer.confidence_score,
                        "coherence_score": answer.coherence_score,
                        "completeness_score": answer.completeness_score,
                        "num_sources": answer.num_sources,
                        "source_documents": list(answer.source_documents),
                        "key_points": answer.key_points,
                        "contradictions": answer.contradictions,
                        "metadata": answer.metadata,
                    }
                    for answer in fused_answers
                ],
                "merged_results": {
                    "documents": merged_docs,
                    "strategy_performance": {
                        sr["strategy"]: {
                            "queries": sr["queries"],
                            "results_count": sr["results_count"],
                        }
                        for sr in strategy_results
                    },
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_ms": int(
                        (end_time - start_time).total_seconds() * 1000
                    ),
                    "expansion_enabled": enable_expansion,
                    "fusion_enabled": enable_fusion,
                    "strategies_used": len(strategies),
                    "total_docs_found": len(merged_docs),
                    "fused_answers_count": len(fused_answers),
                    "reformulation_attempted": auto_reformulate
                    and len(all_retrieved_docs) < 3,
                    "domain_context": domain_context,
                },
            }

        except Exception as e:
            return {
                "response": f"I encountered an error during enhanced query processing: {str(e)}",
                "context": "",
                "question": question,
                "expanded_query": None,
                "search_strategies": [],
                "fused_answers": [],
                "merged_results": {"documents": [], "strategy_performance": {}},
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "error": True,
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "expansion_enabled": False,
                    "fusion_enabled": enable_fusion,
                    "strategies_used": 0,
                    "total_docs_found": 0,
                    "fused_answers_count": 0,
                    "reformulation_attempted": False,
                    "domain_context": domain_context,
                },
            }

    async def analyze_query_intelligence(
        self,
        question: str,
        domain_context: str | None = None,
    ) -> dict[str, Any]:
        """Analyze query intelligence and provide enhancement suggestions.

        Args:
            question: Query to analyze
            domain_context: Optional domain context

        Returns:
            Comprehensive query analysis with suggestions
        """
        try:
            # Get query expansion analysis
            expansion = self.query_expansion_engine.expand_query(
                question,
                domain_context=domain_context,
                include_synonyms=True,
                include_related=True,
            )

            # Get quality analysis
            quality_analysis = self.query_expansion_engine.analyze_query_quality(
                question
            )

            # Get search strategies
            strategies = self.query_expansion_engine.create_search_strategies(expansion)

            # Generate reformulations
            reformulations = self.query_expansion_engine.reformulate_query(
                question,
                search_results_count=5,  # Simulate moderate results
                search_quality_score=0.6,  # Simulate moderate quality
            )

            return {
                "original_query": question,
                "domain_context": domain_context,
                "expansion_analysis": {
                    "intent": expansion.intent.value,
                    "confidence": expansion.confidence,
                    "key_terms": expansion.key_terms,
                    "synonyms_found": len(expansion.synonyms),
                    "related_terms_found": len(expansion.related_terms),
                    "expanded_queries": expansion.expanded_queries,
                    "suggestions": expansion.suggestions,
                },
                "query_analysis": quality_analysis,
                "search_strategies": [
                    {
                        "type": strategy.strategy_type,
                        "queries": strategy.queries,
                        "expected_intent": strategy.expected_intent.value,
                        "search_params": strategy.search_params,
                    }
                    for strategy in strategies
                ],
                "alternative_queries": reformulations,
                "suggestions": self._generate_query_recommendations(
                    expansion, quality_analysis
                ),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "analysis_version": "1.0",
                },
            }

        except Exception as e:
            return {
                "original_query": question,
                "error": True,
                "error_message": str(e),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                },
            }

    def _map_search_params_for_hybrid_query(
        self, strategy_params: dict[str, Any], default_max_results: int
    ) -> dict[str, Any]:
        """Map search strategy parameters to hybrid_query method parameters.

        Args:
            strategy_params: Parameters from search strategy
            default_max_results: Default max_results if not in strategy_params

        Returns:
            Mapped parameters compatible with hybrid_query method
        """
        # Known hybrid_query parameters
        valid_params = {
            "max_results",
            "include_chunks",
            "semantic_weight",
            "keyword_weight",
            "min_semantic_score",
            "min_keyword_score",
            "boost_exact_matches",
            "boost_title_matches",
            "explain_results",
        }

        # Parameter mapping from strategy params to hybrid_query params
        param_mapping = {
            "similarity_threshold": "min_semantic_score",
            "boost_synonyms": None,  # Not supported, ignore
            "expand_context": None,  # Not supported, ignore
            "boost_structured_content": None,  # Not supported, ignore
            "prefer_step_by_step": None,  # Not supported, ignore
            "boost_error_contexts": None,  # Not supported, ignore
            "include_related_issues": None,  # Not supported, ignore
            "boost_code_examples": None,  # Not supported, ignore
            "include_demonstrations": None,  # Not supported, ignore
            "prefer_authoritative": "boost_title_matches",  # Map to closest equivalent
            "include_partial_matches": None,  # Not supported, ignore
        }

        mapped_params = {}

        # Set default max_results
        mapped_params["max_results"] = strategy_params.get(
            "max_results", default_max_results
        )

        # Map strategy parameters to hybrid_query parameters
        for strategy_key, strategy_value in strategy_params.items():
            if strategy_key in valid_params:
                # Direct parameter match
                mapped_params[strategy_key] = strategy_value
            elif strategy_key in param_mapping:
                # Mapped parameter
                mapped_key = param_mapping[strategy_key]
                if mapped_key is not None:
                    mapped_params[mapped_key] = strategy_value
            # Ignore unsupported parameters

        return mapped_params

    def _merge_strategy_results(
        self, all_docs: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Merge and deduplicate results from multiple strategies."""
        if not all_docs:
            return []

        # Group by document/chunk ID
        doc_groups = defaultdict(list)

        for doc in all_docs:
            # Create unique key for deduplication
            if doc.get("is_chunk", False):
                key = f"chunk_{doc.get('chunk_id', 'unknown')}"
            else:
                key = f"doc_{doc.get('store_type', 'unknown')}_{doc.get('document_id', 'unknown')}"

            doc_groups[key].append(doc)

        # Merge duplicate documents by taking best scores
        merged = []
        for docs in doc_groups.values():
            if len(docs) == 1:
                merged.append(docs[0])
            else:
                # Merge multiple versions of same document
                best_doc = max(docs, key=lambda d: d.get("weighted_score", 0))

                # Combine strategy information
                strategies = list({d.get("strategy_type", "unknown") for d in docs})
                query_variants = list({d.get("query_variant", "") for d in docs})

                best_doc["strategy_types"] = strategies
                best_doc["query_variants"] = query_variants
                best_doc["occurrence_count"] = len(docs)

                # Boost score for multiple strategy hits
                boost = min(0.2, (len(docs) - 1) * 0.05)
                best_doc["weighted_score"] = best_doc.get("weighted_score", 0) + boost

                merged.append(best_doc)

        # Sort by weighted score
        merged.sort(key=lambda d: d.get("weighted_score", 0), reverse=True)

        return merged

    def _build_enhanced_context(
        self,
        documents: list[dict[str, Any]],
        fused_answers: list,
        expansion: QueryExpansion | None,
        original_question: str,
    ) -> str:
        """Build enhanced context with expansion and fusion information."""
        if not documents and not fused_answers:
            return "No relevant context found."

        context_parts = []

        # Add query enhancement summary
        if expansion:
            context_parts.append("=== Query Analysis ===")
            context_parts.append(f"Intent: {expansion.intent.value.title()}")
            context_parts.append(f"Key Terms: {', '.join(expansion.key_terms)}")
            if expansion.related_terms:
                context_parts.append(
                    f"Related Terms: {', '.join(expansion.related_terms[:5])}"
                )
            context_parts.append("")

        # Add fused answers first (highest priority)
        if fused_answers:
            context_parts.append("=== Synthesized Information ===")
            for i, answer in enumerate(fused_answers, 1):
                context_parts.append(
                    f"Synthesis {i} (Confidence: {answer.confidence_score:.2f}):"
                )
                context_parts.append(
                    answer.content[:1000] + "..."
                    if len(answer.content) > 1000
                    else answer.content
                )
                context_parts.append("")

        # Add individual documents grouped by strategy
        strategy_docs = defaultdict(list)
        for doc in documents:
            strategy = doc.get("strategy_type", "unknown")
            strategy_docs[strategy].append(doc)

        if strategy_docs:
            context_parts.append("=== Source Documents ===")

            for strategy, docs in strategy_docs.items():
                context_parts.append(f"\n--- From {strategy.title()} Strategy ---")

                for i, doc in enumerate(docs[:5], 1):  # Limit to top 5 per strategy
                    doc_id = doc.get("document_id", "unknown")
                    store_type = doc.get("store_type", "unknown")
                    score = doc.get("weighted_score", 0)

                    if doc.get("is_chunk", False):
                        chunk_title = doc.get("chunk_title", "Untitled")
                        context_parts.append(
                            f"{i}. {store_type}/{doc_id} - {chunk_title} (Score: {score:.3f})"
                        )
                    else:
                        context_parts.append(
                            f"{i}. {store_type}/{doc_id} (Score: {score:.3f})"
                        )

                    # Add query variant if different from original
                    query_variant = doc.get("query_variant", "")
                    if (
                        query_variant
                        and query_variant.lower() != original_question.lower()
                    ):
                        context_parts.append(f'   Found via: "{query_variant}"')

                    content = doc.get("content", "")
                    preview = content[:300] + "..." if len(content) > 300 else content
                    context_parts.append(f"   {preview}")
                    context_parts.append("")

        return "\n".join(context_parts)

    async def _generate_enhanced_response(
        self,
        question: str,
        context: str,
        expansion: QueryExpansion | None,
    ) -> str:
        """Generate enhanced response using expansion context."""
        system_prompt = f"""You are an intelligent assistant with access to a comprehensive knowledge base. You have analyzed the user's query and found relevant information using advanced search techniques.

Query Analysis:
{f"- Intent: {expansion.intent.value.title()}" if expansion else "- Intent: General"}
{f"- Key Terms: {', '.join(expansion.key_terms)}" if expansion and expansion.key_terms else ""}
{f"- Confidence: {expansion.confidence:.2f}" if expansion else ""}

The context below includes both synthesized information from multiple sources and individual source documents. Pay special attention to:
1. Synthesized information (marked with confidence scores) - this represents intelligent fusion of multiple sources
2. Source documents found through different search strategies
3. Query variants that helped find relevant information

Context:
{context}

Instructions:
1. Provide a comprehensive answer based on the available information
2. Acknowledge when information comes from synthesis vs individual sources
3. Mention if multiple search strategies were used to find information
4. Be specific about which sources support different parts of your answer
5. If the query intent was detected, ensure your response format matches that intent
6. Highlight any contradictions or uncertainties found in the sources

Provide a well-structured, accurate response that leverages the intelligent search and analysis performed."""

        try:
            response = await self.claude_client.create_chat_completion(
                messages=[{"role": "user", "content": question}],
                system=system_prompt,
                temperature=0.1,
                max_tokens=self.claude_client.default_max_tokens,
            )

            return (
                response
                if isinstance(response, str)
                else "Unable to generate enhanced response."
            )

        except Exception as e:
            return f"Error generating enhanced response: {str(e)}"

    def _generate_query_recommendations(
        self,
        expansion: QueryExpansion,
        quality_analysis: dict[str, Any] | None = None,
        strategy_performance: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate recommendations for query improvement."""
        query_improvements = []
        search_strategy = []
        expansion_quality = []

        # Based on expansion confidence
        if expansion.confidence < 0.6:
            query_improvements.append(
                "Query could be more specific - consider adding technical terms or context"
            )
            expansion_quality.append("Low confidence expansion detected")

        # Based on intent detection
        if expansion.intent.value == "general":
            query_improvements.append(
                "Add intent words like 'how to', 'what is', or 'example of' for better results"
            )

        # Based on quality metrics
        if quality_analysis:
            quality = quality_analysis.get("overall_quality", 0)
            if quality < 0.7:
                query_improvements.extend(quality_analysis.get("improvements", []))
                expansion_quality.append(f"Query quality score: {quality:.2f}")

        # Based on strategy performance
        if strategy_performance:
            low_performers = [
                strategy
                for strategy, perf in strategy_performance.items()
                if perf.get("num_results", 0) < 2 or perf.get("avg_relevance", 0) < 0.6
            ]
            if low_performers:
                search_strategy.append(
                    f"Consider refining query - strategies {', '.join(low_performers)} had limited results"
                )

            high_performers = [
                strategy
                for strategy, perf in strategy_performance.items()
                if perf.get("num_results", 0) >= 5
                and perf.get("avg_relevance", 0) >= 0.8
            ]
            if high_performers:
                search_strategy.append(
                    f"Focus on {', '.join(high_performers)} strategies for best results"
                )

        # Based on available expansions
        if expansion.suggestions:
            expansion_quality.extend(expansion.suggestions[:2])

        return {
            "query_improvements": query_improvements,
            "search_strategy": search_strategy,
            "expansion_quality": expansion_quality,
        }
