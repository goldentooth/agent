from datetime import datetime
from typing import Any, Dict, List, Optional

from antidote import inject, injectable

from ..document_store import DocumentStore
from ..embeddings import EmbeddingsService, VectorStore
from ..llm.claude_client import ClaudeFlowClient


@injectable
class RAGService:
    """Retrieval-Augmented Generation service for intelligent document querying."""
    
    def __init__(
        self,
        document_store: DocumentStore = inject.me(),
        embeddings_service: EmbeddingsService = inject.me(),
        vector_store: VectorStore = inject.me(),
        claude_client: Optional[ClaudeFlowClient] = None,
    ) -> None:
        """Initialize the RAG service.
        
        Args:
            document_store: Document store for accessing YAML documents
            embeddings_service: Service for creating embeddings
            vector_store: Vector database for similarity search
            claude_client: Claude client for generating responses
        """
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
        store_type: Optional[str] = None,
        include_metadata: bool = True,
        similarity_threshold: float = 0.1,
    ) -> Dict[str, Any]:
        """Answer a question using RAG with retrieved documents.
        
        Args:
            question: User's question
            max_results: Maximum number of documents to retrieve
            store_type: Optional filter by document store type
            include_metadata: Whether to include retrieval metadata in response
            similarity_threshold: Minimum similarity score for retrieved documents
            
        Returns:
            Dictionary with answer, retrieved documents, and metadata
        """
        try:
            # Step 1: Create embedding for the question
            question_embedding = await self.embeddings_service.create_embedding(question)
            
            # Step 2: Retrieve similar documents
            retrieved_docs = self.vector_store.search_similar(
                question_embedding,
                limit=max_results,
                store_type=store_type
            )
            
            # Filter by similarity threshold
            filtered_docs = [
                doc for doc in retrieved_docs 
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
                    }
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
                    "query_timestamp": datetime.now().isoformat(),
                    "similarity_threshold": similarity_threshold,
                    "model_used": self.claude_client.default_model,
                }
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
                }
            }
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents.
        
        Args:
            documents: List of retrieved document metadata
            
        Returns:
            Formatted context string for Claude
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            doc_id = doc["document_id"]
            store_type = doc["store_type"]
            content = doc["content"]
            similarity = doc["similarity_score"]
            
            # Create a structured context entry
            context_entry = f"""Document {i}: {store_type}/{doc_id} (similarity: {similarity:.3f})
Content: {content}

"""
            context_parts.append(context_entry)
        
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

Your task is to answer questions using ONLY the information provided in the context documents. Follow these guidelines:

1. Base your answers strictly on the provided context documents
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Always cite which documents you're referencing (e.g., "According to github.repos/goldentooth/agent...")
4. Provide specific, actionable information when possible
5. If multiple documents contain relevant information, synthesize them coherently
6. Use clear, technical language appropriate for developers and system administrators

Context Documents:
{context}

Remember: Only use information from the context documents above. Do not add information from your general knowledge."""

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
        store_type: Optional[str] = None,
        max_documents: int = 10,
    ) -> Dict[str, Any]:
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
                    docs = self.document_store.goldentooth_services.list()[:max_documents]
                    doc_type = "Goldentooth Services"
                elif store_type == "notes":
                    docs = self.document_store.notes.list()[:max_documents]
                    doc_type = "Notes"
                else:
                    return {
                        "summary": f"Unknown store type: {store_type}",
                        "metadata": {"error": True}
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
                }
            }
            
        except Exception as e:
            return {
                "summary": f"Error generating summary: {str(e)}",
                "metadata": {
                    "error": True,
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            }
    
    async def get_document_insights(self, document_id: str, store_type: str) -> Dict[str, Any]:
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
                    "metadata": {"error": True, "error_type": "DocumentNotFound"}
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
            
            user_message = f"Analyze this {store_type} document for {document_id}:\n\n{content}"
            
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
                }
            }
            
        except Exception as e:
            return {
                "insights": f"Error generating insights: {str(e)}",
                "metadata": {
                    "error": True,
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            }