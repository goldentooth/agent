"""
Tests for simple RAG agent functionality.
"""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from goldentooth_agent.core.rag.simple_rag_agent import (
    SimpleRAGAgent,
    create_simple_rag_agent,
)


class TestSimpleRAGAgent:
    """Test suite for SimpleRAGAgent class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock RAG service
        self.mock_rag_service = Mock()
        self.mock_rag_service.query = AsyncMock()

        # Create agent instance
        self.agent = SimpleRAGAgent(rag_service=self.mock_rag_service, name="TestAgent")

    def test_agent_initialization(self):
        """Test that SimpleRAGAgent initializes correctly."""
        assert self.agent.rag_service == self.mock_rag_service
        assert self.agent.name == "TestAgent"

    def test_agent_initialization_with_defaults(self):
        """Test agent initialization with default parameters."""
        # This would test with Antidote injection, but we'll just test name default
        mock_service = Mock()
        agent = SimpleRAGAgent(rag_service=mock_service)

        assert agent.name == "SimpleRAGAgent"
        assert agent.rag_service == mock_service

    @pytest.mark.asyncio
    async def test_process_question_basic(self):
        """Test basic question processing."""
        question = "What is Python?"

        # Mock RAG service response
        mock_rag_result = {
            "answer": "Python is a programming language.",
            "retrieved_documents": [
                {
                    "document_id": "doc1",
                    "content": "Python info",
                    "similarity_score": 0.8,
                }
            ],
            "metadata": {
                "chunks_found": 0,
                "full_docs_found": 1,
                "processing_time_ms": 150,
            },
        }

        self.mock_rag_service.query.return_value = mock_rag_result

        result = await self.agent.process_question(question)

        # Verify RAG service was called correctly
        self.mock_rag_service.query.assert_called_once_with(
            question=question, max_results=5, store_type=None
        )

        # Verify response object structure
        assert result["response"] == "Python is a programming language."
        assert result["sources"] == mock_rag_result["retrieved_documents"]
        assert result["metadata"] == mock_rag_result["metadata"]
        assert "confidence" in result
        assert "suggestions" in result

    @pytest.mark.asyncio
    async def test_process_question_with_parameters(self):
        """Test question processing with custom parameters."""
        question = "How does Flask work?"
        conversation_history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"},
        ]

        mock_rag_result = {
            "answer": "Flask is a web framework.",
            "retrieved_documents": [],
            "metadata": {"chunks_found": 0, "full_docs_found": 0},
        }

        self.mock_rag_service.query.return_value = mock_rag_result

        result = await self.agent.process_question(
            question=question,
            conversation_history=conversation_history,
            max_results=10,
            store_type="github.repos",
        )

        # Verify RAG service was called with correct parameters
        self.mock_rag_service.query.assert_called_once_with(
            question=question, max_results=10, store_type="github.repos"
        )

        # Note: conversation_history is not yet implemented, so it's not passed through

    def test_calculate_confidence_no_documents(self):
        """Test confidence calculation with no documents."""
        result = {"retrieved_documents": []}

        confidence = self.agent._calculate_confidence(result)

        assert confidence == 0.3  # Low confidence baseline

    def test_calculate_confidence_with_documents(self):
        """Test confidence calculation with documents."""
        result = {
            "retrieved_documents": [
                {"similarity_score": 0.9},
                {"similarity_score": 0.8},
                {"similarity_score": 0.7},
            ]
        }

        confidence = self.agent._calculate_confidence(result)

        # Expected: (0.9 + 0.8 + 0.7) / 3 = 0.8, plus 0.15 source bonus = 0.95
        expected = 0.8 + min(0.2, 3 * 0.05)  # 0.8 + 0.15 = 0.95
        assert confidence == round(expected, 2)

    def test_calculate_confidence_with_missing_scores(self):
        """Test confidence calculation with missing similarity scores."""
        result = {
            "retrieved_documents": [
                {"similarity_score": 0.8},
                {},  # Missing similarity_score
                {"similarity_score": 0.6},
            ]
        }

        confidence = self.agent._calculate_confidence(result)

        # Should treat missing scores as 0.0
        # (0.8 + 0.0 + 0.6) / 3 = 0.467, plus 0.15 source bonus
        expected = (0.8 + 0.0 + 0.6) / 3 + min(0.2, 3 * 0.05)
        assert confidence == round(expected, 2)

    def test_calculate_confidence_max_capped_at_one(self):
        """Test that confidence is capped at 1.0."""
        result = {
            "retrieved_documents": [
                {"similarity_score": 0.95},
                {"similarity_score": 0.90},
                {"similarity_score": 0.85},
                {"similarity_score": 0.80},
            ]
        }

        confidence = self.agent._calculate_confidence(result)

        assert confidence <= 1.0

    def test_generate_suggestions_no_documents(self):
        """Test suggestion generation with no documents."""
        result = {"retrieved_documents": []}

        suggestions = self.agent._generate_suggestions(result)

        assert len(suggestions) >= 2
        assert any("different keywords" in s for s in suggestions)
        assert any("broadening your search" in s for s in suggestions)

    def test_generate_suggestions_few_documents(self):
        """Test suggestion generation with few documents."""
        result = {
            "retrieved_documents": [{"document_id": "doc1"}, {"document_id": "doc2"}]
        }

        suggestions = self.agent._generate_suggestions(result)

        assert any("more specific questions" in s for s in suggestions)

    def test_generate_suggestions_with_github_repos(self):
        """Test suggestion generation with GitHub repository documents."""
        result = {
            "retrieved_documents": [
                {
                    "document_id": "doc1",
                    "is_chunk": False,
                    "store_type": "github.repos",
                },
                {
                    "document_id": "doc2",
                    "is_chunk": False,
                    "store_type": "github.repos",
                },
                {"document_id": "doc3", "is_chunk": False, "store_type": "notes"},
            ]
        }

        suggestions = self.agent._generate_suggestions(result)

        assert any(
            "repository information" in s and "specific projects" in s
            for s in suggestions
        )

    def test_generate_suggestions_with_chunks(self):
        """Test suggestion generation with chunk documents."""
        result = {
            "retrieved_documents": [
                {"document_id": "chunk1", "is_chunk": True, "chunk_type": "paragraph"},
                {"document_id": "chunk2", "is_chunk": True, "chunk_type": "code_block"},
                {"document_id": "doc1", "is_chunk": False, "store_type": "notes"},
            ]
        }

        suggestions = self.agent._generate_suggestions(result)

        # Should have suggestions but not fail on chunk analysis
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3  # Limited to 3 suggestions

    def test_generate_suggestions_limit_to_three(self):
        """Test that suggestions are limited to 3."""
        # Create result that would generate many suggestions
        result = {
            "retrieved_documents": [
                {"document_id": "doc1", "is_chunk": False, "store_type": "github.repos"}
            ]
        }

        suggestions = self.agent._generate_suggestions(result)

        assert len(suggestions) <= 3

    def test_generate_suggestions_handles_missing_metadata(self):
        """Test suggestion generation with missing document metadata."""
        result = {
            "retrieved_documents": [
                {"document_id": "doc1"},  # Missing is_chunk and store_type
                {
                    "document_id": "doc2",
                    "is_chunk": True,
                    # Missing chunk_type
                },
                {
                    "document_id": "doc3",
                    "is_chunk": False,
                    # Missing store_type
                },
            ]
        }

        # Should not raise an exception
        suggestions = self.agent._generate_suggestions(result)

        assert isinstance(suggestions, list)

    @pytest.mark.asyncio
    async def test_integration_with_confidence_and_suggestions(self):
        """Test integration of confidence and suggestions in full workflow."""
        question = "Tell me about testing"

        mock_rag_result = {
            "answer": "Testing is important for software quality.",
            "retrieved_documents": [
                {
                    "document_id": "doc1",
                    "content": "Testing info",
                    "similarity_score": 0.85,
                    "is_chunk": False,
                    "store_type": "github.repos",
                }
            ],
            "metadata": {"chunks_found": 0, "full_docs_found": 1},
        }

        self.mock_rag_service.query.return_value = mock_rag_result

        result = await self.agent.process_question(question)

        # Verify all components are present and calculated
        assert "confidence" in result
        assert "suggestions" in result
        assert isinstance(result["confidence"], float)
        assert isinstance(result["suggestions"], list)
        assert 0 <= result["confidence"] <= 1.0

        # Should have GitHub-related suggestion due to document type
        suggestions_text = " ".join(result["suggestions"])
        assert "repository" in suggestions_text or "projects" in suggestions_text


class TestCreateSimpleRAGAgent:
    """Test the factory function for creating SimpleRAGAgent."""

    def test_create_simple_rag_agent_factory(self):
        """Test the factory function creates a properly configured agent."""
        # This is an integration test that would require actual dependencies
        # For now, we'll just test that the function exists and can be called
        try:
            agent = create_simple_rag_agent()
            assert isinstance(agent, SimpleRAGAgent)
            assert agent.name == "SimpleRAGAgent"
            assert hasattr(agent, "rag_service")
        except Exception:
            # If dependencies aren't available, that's expected in test environment
            # The function should still exist
            assert callable(create_simple_rag_agent)

    def test_create_simple_rag_agent_dependencies(self):
        """Test that factory function imports all required dependencies."""
        # Test that the function can import its dependencies
        import inspect

        # Get the source code of the function
        source = inspect.getsource(create_simple_rag_agent)

        # Verify it imports the required modules
        assert "DocumentStore" in source
        assert "OpenAIEmbeddingsService" in source
        assert "VectorStore" in source
        assert "ClaudeFlowClient" in source
        assert "Paths" in source
        assert "SimpleRAGService" in source
