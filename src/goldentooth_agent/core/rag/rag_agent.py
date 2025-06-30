"""RAG-powered FlowAgent for intelligent document querying and conversation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from pydantic import Field

from goldentooth_agent.flow_engine import Flow

from ..context import Context, ContextKey
from ..flow_agent.agent import FlowAgent
from ..flow_agent.schema import FlowIOSchema
from .rag_service import RAGService


class RAGInput(FlowIOSchema):
    """Input schema for RAG agent interactions."""

    question: str = Field(..., description="User's question or query")
    max_results: int = Field(
        default=10, description="Maximum number of documents to retrieve"
    )
    enable_expansion: bool = Field(default=True, description="Enable query expansion")
    enable_fusion: bool = Field(default=True, description="Enable chunk fusion")
    domain_context: str | None = Field(
        default=None, description="Optional domain context for query expansion"
    )
    conversation_history: list[dict[str, str]] = Field(
        default_factory=list, description="Previous conversation messages for context"
    )


class RAGOutput(FlowIOSchema):
    """Output schema for RAG agent responses."""

    response: str = Field(..., description="Agent's response to the question")
    sources: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Source documents used to generate the response",
    )
    confidence: float = Field(
        default=0.0, description="Confidence score for the response"
    )
    query_analysis: dict[str, Any] = Field(
        default_factory=dict, description="Analysis of the user's query"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Suggestions for improving the query"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional response metadata"
    )


class RAGAgent:
    """RAG-powered agent using FlowAgent architecture."""

    def __init__(
        self,
        rag_service: RAGService,
        name: str = "RAGAgent",
        conversation_memory_size: int = 10,
    ):
        """Initialize the RAG agent.

        Args:
            rag_service: RAG service for document retrieval and generation
            name: Name of the agent
            conversation_memory_size: Number of previous conversation turns to remember
        """
        self.rag_service = rag_service
        self.name = name
        self.conversation_memory_size = conversation_memory_size

        # Create the FlowAgent with RAG-specific flows
        self.flow_agent = FlowAgent(
            name=name,
            input_schema=RAGInput,
            output_schema=RAGOutput,
            system_flow=self._create_system_flow(),
            processing_flow=self._create_processing_flow(),
        )

    def _create_system_flow(self) -> Flow[Context, Context]:
        """Create the system flow for RAG agent."""
        return Flow(self._system_pipeline, name=f"{self.name}:system")

    def _create_processing_flow(self) -> Flow[Context, Context]:
        """Create the processing flow for RAG agent."""
        return Flow(self._processing_pipeline, name=f"{self.name}:processing")

    async def _system_pipeline(
        self, stream: AsyncIterator[Context]
    ) -> AsyncIterator[Context]:
        """System pipeline for preparing RAG context."""
        async for context in stream:
            # Extract input data
            try:
                question = context["schema.RAGInput.question"]
                conversation_history = context.get(
                    "schema.RAGInput.conversation_history", []
                )
                domain_context = context.get("schema.RAGInput.domain_context")
            except KeyError:
                # Input data not properly set, pass through
                yield context
                continue

            # Analyze the query for better understanding
            try:
                query_analysis = await self.rag_service.analyze_query_intelligence(
                    question=question,
                    suggest_alternatives=True,
                )

                # Store query analysis in context
                analysis_key = ContextKey.create(
                    "rag.query_analysis", dict, "Analysis of the user's query"
                )
                context = context.fork().set(analysis_key.path, query_analysis)

            except Exception:
                # If query analysis fails, continue without it
                pass

            # Prepare conversation context
            if conversation_history:
                conversation_context = self._build_conversation_context(
                    conversation_history
                )
                conv_key = ContextKey.create(
                    "rag.conversation_context", str, "Conversation history context"
                )
                context = context.fork().set(conv_key.path, conversation_context)

            yield context

    async def _processing_pipeline(
        self, stream: AsyncIterator[Context]
    ) -> AsyncIterator[Context]:
        """Processing pipeline for RAG retrieval and generation."""
        async for context in stream:
            try:
                # Extract input parameters
                question = context["schema.RAGInput.question"]
                max_results = context.get("schema.RAGInput.max_results", 10)
                enable_expansion = context.get("schema.RAGInput.enable_expansion", True)
                enable_fusion = context.get("schema.RAGInput.enable_fusion", True)
                domain_context = context.get("schema.RAGInput.domain_context")

                # Get conversation context if available
                conversation_context = context.get("rag.conversation_context")

                # Enhance question with conversation context if available
                enhanced_question = question
                if conversation_context:
                    enhanced_question = (
                        f"Context: {conversation_context}\n\nQuestion: {question}"
                    )

                # Perform enhanced RAG query
                rag_result = await self.rag_service.enhanced_query(
                    question=enhanced_question,
                    max_results=max_results,
                    enable_expansion=enable_expansion,
                    enable_fusion=enable_fusion,
                    domain_context=domain_context,
                )

                # Extract response and metadata
                response = rag_result.get(
                    "response",
                    "I couldn't find relevant information to answer your question.",
                )
                sources = self._extract_sources(rag_result)
                confidence = self._calculate_confidence(rag_result)

                # Get query analysis from context or result
                query_analysis = context.get("rag.query_analysis", {})
                if not query_analysis and "expanded_query" in rag_result:
                    query_analysis = rag_result["expanded_query"]

                # Generate suggestions
                suggestions = self._generate_suggestions(rag_result, query_analysis)

                # Store results in context
                self._store_results_in_context(
                    context,
                    response,
                    sources,
                    confidence,
                    query_analysis,
                    suggestions,
                    rag_result,
                )

            except Exception as e:
                # Handle errors gracefully
                error_response = (
                    f"I encountered an error while processing your question: {str(e)}"
                )
                self._store_error_in_context(context, error_response)

            yield context

    def _build_conversation_context(
        self, conversation_history: list[dict[str, str]]
    ) -> str:
        """Build conversation context from history."""
        if not conversation_history:
            return ""

        # Take the last N messages
        recent_history = conversation_history[-self.conversation_memory_size :]

        context_parts = []
        for msg in recent_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                context_parts.append(f"{role.title()}: {content}")

        return "\n".join(context_parts)

    def _extract_sources(self, rag_result: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract source information from RAG result."""
        sources = []

        # Extract from merged results
        merged_results = rag_result.get("merged_results", {})
        documents = merged_results.get("documents", [])

        for doc in documents:
            source = {
                "document_id": doc.get("document_id", ""),
                "chunk_id": doc.get("chunk_id", ""),
                "content": doc.get("content", ""),
                "relevance_score": doc.get("relevance_score", 0.0),
                "metadata": doc.get("metadata", {}),
            }
            sources.append(source)

        # Limit number of sources
        return sources[:5]

    def _calculate_confidence(self, rag_result: dict[str, Any]) -> float:
        """Calculate confidence score for the response."""
        # Base confidence on various factors
        confidence = 0.5  # Base confidence

        # Factor in number of sources
        merged_results = rag_result.get("merged_results", {})
        documents = merged_results.get("documents", [])
        if documents:
            # More sources generally means higher confidence
            source_factor = min(len(documents) / 5.0, 1.0) * 0.2
            confidence += source_factor

        # Factor in average relevance scores
        if documents:
            avg_relevance = sum(
                doc.get("relevance_score", 0.0) for doc in documents
            ) / len(documents)
            confidence += avg_relevance * 0.3

        # Factor in query expansion confidence
        expanded_query = rag_result.get("expanded_query", {})
        if expanded_query and "confidence" in expanded_query:
            expansion_confidence = expanded_query["confidence"]
            confidence += expansion_confidence * 0.2

        return min(confidence, 1.0)

    def _generate_suggestions(
        self, rag_result: dict[str, Any], query_analysis: dict[str, Any]
    ) -> list[str]:
        """Generate suggestions for improving the query."""
        suggestions = []

        # Add suggestions from query analysis
        if query_analysis and "suggestions" in query_analysis:
            suggestions.extend(query_analysis["suggestions"]["query_improvements"])

        # Add suggestions based on results
        merged_results = rag_result.get("merged_results", {})
        documents = merged_results.get("documents", [])

        if not documents:
            suggestions.append("Try using different keywords or more specific terms")
            suggestions.append("Consider broadening your search with related concepts")
        elif len(documents) == 1:
            suggestions.append(
                "Your query was very specific - try broadening it for more results"
            )

        # Limit suggestions
        return suggestions[:3]

    def _store_results_in_context(
        self,
        context: Context,
        response: str,
        sources: list[dict[str, Any]],
        confidence: float,
        query_analysis: dict[str, Any],
        suggestions: list[str],
        rag_result: dict[str, Any],
    ) -> None:
        """Store RAG results in context for output schema."""
        # Create context keys for output schema
        response_key = ContextKey.create(
            "schema.RAGOutput.response", str, "Agent response"
        )
        sources_key = ContextKey.create(
            "schema.RAGOutput.sources", list, "Source documents"
        )
        confidence_key = ContextKey.create(
            "schema.RAGOutput.confidence", float, "Response confidence"
        )
        analysis_key = ContextKey.create(
            "schema.RAGOutput.query_analysis", dict, "Query analysis"
        )
        suggestions_key = ContextKey.create(
            "schema.RAGOutput.suggestions", list, "Query suggestions"
        )
        metadata_key = ContextKey.create(
            "schema.RAGOutput.metadata", dict, "Response metadata"
        )

        # Update context with results
        updated_context = context.fork()
        updated_context.set(response_key.path, response)
        updated_context.set(sources_key.path, sources)
        updated_context.set(confidence_key.path, confidence)
        updated_context.set(analysis_key.path, query_analysis)
        updated_context.set(suggestions_key.path, suggestions)
        updated_context.set(
            metadata_key.path,
            {
                "rag_metadata": rag_result.get("metadata", {}),
                "num_sources": len(sources),
                "processing_time": rag_result.get("metadata", {}).get(
                    "processing_time", 0
                ),
            },
        )

        # Update the original context by merging from updated context
        for key in updated_context.keys():
            context.set(key, updated_context[key])

    def _store_error_in_context(self, context: Context, error_response: str) -> None:
        """Store error response in context."""
        response_key = ContextKey.create(
            "schema.RAGOutput.response", str, "Agent response"
        )
        sources_key = ContextKey.create(
            "schema.RAGOutput.sources", list, "Source documents"
        )
        confidence_key = ContextKey.create(
            "schema.RAGOutput.confidence", float, "Response confidence"
        )
        analysis_key = ContextKey.create(
            "schema.RAGOutput.query_analysis", dict, "Query analysis"
        )
        suggestions_key = ContextKey.create(
            "schema.RAGOutput.suggestions", list, "Query suggestions"
        )
        metadata_key = ContextKey.create(
            "schema.RAGOutput.metadata", dict, "Response metadata"
        )

        updated_context = context.fork()
        updated_context.set(response_key.path, error_response)
        updated_context.set(sources_key.path, [])
        updated_context.set(confidence_key.path, 0.0)
        updated_context.set(analysis_key.path, {})
        updated_context.set(
            suggestions_key.path, ["Please try rephrasing your question"]
        )
        updated_context.set(metadata_key.path, {"error": True})

        # Update the original context by merging from updated context
        for key in updated_context.keys():
            context.set(key, updated_context[key])

    async def process_question(
        self,
        question: str,
        conversation_history: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> RAGOutput:
        """Process a question and return a RAG response.

        Args:
            question: User's question
            conversation_history: Previous conversation messages
            **kwargs: Additional parameters for RAGInput

        Returns:
            RAG response with sources and metadata
        """
        # Create input
        input_data = RAGInput(
            question=question,
            conversation_history=conversation_history or [],
            **kwargs,
        )

        # Process through the flow agent
        flow = self.flow_agent.as_flow()

        # Create input stream
        async def input_stream():
            yield input_data

        # Process and get result
        results = []
        async for result in flow(input_stream()):
            results.append(result)

        # Return the last result
        if results:
            return results[-1]
        else:
            # Fallback if no results
            return RAGOutput(
                response="I couldn't process your question. Please try again.",
                sources=[],
                confidence=0.0,
                query_analysis={},
                suggestions=["Please try rephrasing your question"],
                metadata={"error": True},
            )

    def as_flow(self) -> Flow[RAGInput, RAGOutput]:
        """Convert the RAG agent to a Flow for composition."""
        return self.flow_agent.as_flow()
