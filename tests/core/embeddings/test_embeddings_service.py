import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from goldentooth_agent.core.embeddings import EmbeddingsService
from goldentooth_agent.core.paths import Paths


class TestEmbeddingsService:
    """Test suite for EmbeddingsService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "test_data"
        
        # Mock the Paths dependency
        self.mock_paths = Mock(spec=Paths)
        self.mock_paths.data.return_value = self.data_path
        
        # Mock environment variable
        self.original_api_key = os.environ.get("ANTHROPIC_API_KEY")
        os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
        
        # Restore original API key
        if self.original_api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.original_api_key
        elif "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
    
    def test_embeddings_service_requires_api_key(self):
        """Test that EmbeddingsService requires an API key."""
        # Remove API key
        del os.environ["ANTHROPIC_API_KEY"]
        
        with pytest.raises(ValueError, match="Anthropic API key is required"):
            EmbeddingsService(self.mock_paths)
    
    @patch("goldentooth_agent.core.embeddings.embeddings_service.AsyncAnthropic")
    @pytest.mark.asyncio
    async def test_create_embedding_with_mock_client(self, mock_anthropic):
        """Test creating an embedding with mocked Anthropic client."""
        # Mock the Anthropic response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "semantic features: machine learning, algorithms, data science, python, tensorflow"
        
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Create service
        service = EmbeddingsService(self.mock_paths)
        
        # Test embedding creation
        text = "This is a machine learning repository using Python and TensorFlow"
        embedding = await service.create_embedding(text)
        
        # Verify embedding properties
        assert isinstance(embedding, list)
        assert len(embedding) == 768  # Default dimensions
        assert all(isinstance(x, float) for x in embedding)
        
        # Verify client was called
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert "claude-3-5-sonnet-20241022" in str(call_args)
        assert text[:100] in str(call_args)  # Text should be in the call
    
    def test_text_to_vector_consistency(self):
        """Test that text_to_vector produces consistent results."""
        # Create service (will fail on client init, but we only need the method)
        try:
            service = EmbeddingsService(self.mock_paths)
        except ValueError:
            # If API key missing, create instance manually for testing
            service = object.__new__(EmbeddingsService)
        
        text = "machine learning algorithms data science"
        
        # Generate vectors multiple times
        vector1 = service._text_to_vector(text)
        vector2 = service._text_to_vector(text)
        
        # Should be identical (deterministic)
        assert vector1.shape == vector2.shape
        assert (vector1 == vector2).all()
        
        # Should be normalized
        norm = (vector1 ** 2).sum() ** 0.5
        assert abs(norm - 1.0) < 1e-6
    
    def test_text_to_vector_different_texts(self):
        """Test that different texts produce different vectors."""
        # Create service object manually for testing
        service = object.__new__(EmbeddingsService)
        
        text1 = "machine learning algorithms"
        text2 = "web development javascript"
        
        vector1 = service._text_to_vector(text1)
        vector2 = service._text_to_vector(text2)
        
        # Vectors should be different
        assert vector1.shape == vector2.shape
        assert not (vector1 == vector2).all()
        
        # Both should be normalized
        norm1 = (vector1 ** 2).sum() ** 0.5
        norm2 = (vector2 ** 2).sum() ** 0.5
        assert abs(norm1 - 1.0) < 1e-6
        assert abs(norm2 - 1.0) < 1e-6
    
    def test_extract_embeddable_text_github_repo(self):
        """Test extracting embeddable text from GitHub repo data."""
        service = object.__new__(EmbeddingsService)
        
        repo_data = {
            "id": "owner/repo",
            "name": "awesome-ml",
            "description": "An awesome machine learning library",
            "language": "Python",
            "topics": ["machine-learning", "python", "tensorflow"],
            "stars": 1500,
            "is_private": False,
        }
        
        text = service._extract_embeddable_text(repo_data)
        
        # Should contain key information
        assert "awesome-ml" in text
        assert "An awesome machine learning library" in text
        assert "machine-learning" in text
        assert "python" in text
        assert "tensorflow" in text
    
    def test_extract_embeddable_text_goldentooth_service(self):
        """Test extracting embeddable text from Goldentooth service data."""
        service = object.__new__(EmbeddingsService)
        
        service_data = {
            "id": "consul",
            "name": "Consul",
            "description": "Service discovery and configuration management",
            "service_type": "discovery",
            "status": "running",
            "port": 8500,
        }
        
        text = service._extract_embeddable_text(service_data)
        
        # Should contain key information
        assert "Consul" in text
        assert "Service discovery and configuration management" in text
        assert "Type: discovery" in text
        assert "Status: running" in text
    
    def test_extract_embeddable_text_note(self):
        """Test extracting embeddable text from note data."""
        service = object.__new__(EmbeddingsService)
        
        note_data = {
            "id": "deployment-guide",
            "title": "Production Deployment Guide",
            "content": "This guide covers best practices for deploying services to production",
            "category": "operations",
            "tags": ["deployment", "production", "devops"],
            "keywords": ["kubernetes", "docker", "monitoring"],
        }
        
        text = service._extract_embeddable_text(note_data)
        
        # Should contain key information
        assert "Production Deployment Guide" in text
        assert "This guide covers best practices" in text
        assert "deployment" in text
        assert "production" in text
        assert "devops" in text
        assert "kubernetes" in text
        assert "Type: operations" in text
    
    def test_extract_embeddable_text_minimal_data(self):
        """Test extracting text from minimal document data."""
        service = object.__new__(EmbeddingsService)
        
        minimal_data = {
            "id": "test-doc",
        }
        
        text = service._extract_embeddable_text(minimal_data)
        
        # Should fallback to ID
        assert text == "test-doc"
    
    def test_extract_embeddable_text_empty_data(self):
        """Test extracting text from empty document data."""
        service = object.__new__(EmbeddingsService)
        
        empty_data = {}
        
        text = service._extract_embeddable_text(empty_data)
        
        # Should fallback to default
        assert text == "Unknown document"
    
    @patch("goldentooth_agent.core.embeddings.embeddings_service.AsyncAnthropic")
    @pytest.mark.asyncio
    async def test_create_document_embedding(self, mock_anthropic):
        """Test creating a document embedding with metadata."""
        # Mock the Anthropic response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "semantic features: python, web, framework"
        
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Create service
        service = EmbeddingsService(self.mock_paths)
        
        # Test document data
        document_data = {
            "id": "flask/flask",
            "name": "Flask",
            "description": "A lightweight WSGI web application framework",
            "language": "Python",
            "topics": ["web", "framework", "python"],
        }
        
        # Create document embedding
        result = await service.create_document_embedding(document_data)
        
        # Verify result structure
        assert "embedding" in result
        assert "text_content" in result
        assert "metadata" in result
        
        # Verify embedding
        embedding = result["embedding"]
        assert isinstance(embedding, list)
        assert len(embedding) == 768
        assert all(isinstance(x, float) for x in embedding)
        
        # Verify text content
        text_content = result["text_content"]
        assert "Flask" in text_content
        assert "A lightweight WSGI web application framework" in text_content
        assert "web" in text_content
        
        # Verify metadata
        metadata = result["metadata"]
        assert "created_at" in metadata
        assert "text_length" in metadata
        assert "embedding_dimensions" in metadata
        assert "embedding_method" in metadata
        assert metadata["embedding_dimensions"] == 768
        assert metadata["text_length"] == len(text_content)
    
    @patch("goldentooth_agent.core.embeddings.embeddings_service.AsyncAnthropic")
    @pytest.mark.asyncio
    async def test_embed_batch(self, mock_anthropic):
        """Test creating embeddings for a batch of texts."""
        # Mock the Anthropic response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "semantic features: test content"
        
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Create service
        service = EmbeddingsService(self.mock_paths)
        
        # Test batch embedding
        texts = [
            "First document about machine learning",
            "Second document about web development", 
            "Third document about data science",
        ]
        
        embeddings = await service.embed_batch(texts)
        
        # Verify results
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) == 768 for emb in embeddings)
        
        # Verify client was called for each text
        assert mock_client.messages.create.call_count == 3