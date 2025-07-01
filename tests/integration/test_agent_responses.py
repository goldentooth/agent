"""Integration tests for agent response consistency."""

from typing import Any

import pytest

from goldentooth_agent.core.rag.simple_rag_agent import SimpleRAGAgent
from goldentooth_agent.core.schema.agent_response import AgentResponse


@pytest.mark.integration
class TestAgentResponseConsistency:
    """Ensure all agents return consistent response formats."""

    @pytest.mark.asyncio
    async def test_rag_agent_response_format(
        self, mock_rag_dependencies: dict[str, Any]
    ) -> None:
        """Test that RAG agent returns proper dictionary format."""
        # Create agent with mocked dependencies
        agent = SimpleRAGAgent(
            rag_service=mock_rag_dependencies["rag_service"],
        )

        # Process a test question
        result = await agent.process_question("What is the project about?")

        # Verify it's a dictionary with expected keys
        assert isinstance(result, dict)
        assert "response" in result
        assert isinstance(result["response"], str)

        # Check optional keys
        assert isinstance(result.get("sources", []), list)
        assert isinstance(result.get("confidence", 0.0), (int, float))
        assert isinstance(result.get("suggestions", []), list)

    @pytest.mark.asyncio
    async def test_agent_response_schema_validation(self) -> None:
        """Test that responses can be validated with AgentResponse schema."""
        # Test valid response
        valid_data = {
            "response": "This is a test response",
            "sources": [{"title": "Test Doc", "content": "Test content"}],
            "confidence": 0.85,
            "suggestions": ["Follow up question 1", "Follow up question 2"],
        }

        # Should create without errors
        response = AgentResponse.from_dict(valid_data)
        assert response.response == "This is a test response"
        assert len(response.sources) == 1
        assert response.confidence == 0.85
        assert len(response.suggestions) == 2

    @pytest.mark.asyncio
    async def test_agent_response_schema_validation_minimal(self) -> None:
        """Test AgentResponse with minimal required fields."""
        minimal_data = {"response": "Minimal response"}

        response = AgentResponse.from_dict(minimal_data)
        assert response.response == "Minimal response"
        assert response.sources == []
        assert response.confidence == 0.0
        assert response.suggestions == []

    @pytest.mark.asyncio
    async def test_agent_response_schema_validation_invalid(self) -> None:
        """Test AgentResponse validation with invalid data."""
        # Missing required field
        with pytest.raises(ValueError):
            AgentResponse.from_dict({})

        # Invalid confidence value
        with pytest.raises(ValueError):
            AgentResponse.from_dict(
                {"response": "Test", "confidence": 1.5}  # Out of range
            )

        # Extra fields not allowed
        with pytest.raises(ValueError):
            AgentResponse.from_dict({"response": "Test", "unknown_field": "value"})

    def test_dict_access_vs_attribute_access(self) -> None:
        """Demonstrate the difference between dict and object access."""
        # Dictionary response (current RAG implementation)
        dict_response = {
            "response": "Dictionary response",
            "sources": [],
            "confidence": 0.9,
        }

        # Accessing dictionary - this works
        assert dict_response["response"] == "Dictionary response"
        assert dict_response.get("confidence", 0.0) == 0.9

        # This would fail with AttributeError
        with pytest.raises(AttributeError):
            _ = dict_response.response  # type: ignore

        # AgentResponse object - supports attribute access
        obj_response = AgentResponse(response="Object response", confidence=0.9)

        # Both access patterns work with Pydantic
        assert obj_response.response == "Object response"
        assert obj_response.model_dump()["response"] == "Object response"


@pytest.fixture
def mock_rag_dependencies(mocker: Any) -> dict[str, Any]:
    """Mock dependencies for RAG agent testing."""
    mock_rag_service = mocker.Mock()
    # Use AsyncMock for async method
    mock_rag_service.query = mocker.AsyncMock(
        return_value={
            "answer": "Mocked RAG response",
            "retrieved_documents": [],
            "metadata": {"search_time": 0.1},
        }
    )

    mock_llm_client = mocker.Mock()
    mock_llm_client.generate.return_value = mocker.Mock(content="Mocked LLM response")

    return {"rag_service": mock_rag_service, "llm_client": mock_llm_client}


@pytest.fixture
def mock_llm_client(mocker: Any) -> Any:
    """Mock LLM client for testing."""
    mock = mocker.Mock()
    mock.generate.return_value = mocker.Mock(content="Mocked response")
    return mock
