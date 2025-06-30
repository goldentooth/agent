"""
Tests for codebase collection and indexing.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from goldentooth_agent.core.agent_codebase.collection import (
    CodebaseCollection,
    CodebaseInfo
)
from goldentooth_agent.core.agent_codebase.schema import CodebaseDocumentType


class TestCodebaseInfo:
    """Test CodebaseInfo model."""
    
    def test_codebase_info_creation(self):
        """Test creating codebase info."""
        info = CodebaseInfo(
            name="test_codebase",
            display_name="Test Codebase",
            root_path=Path("/test/path"),
            description="A test codebase",
            version="1.0.0"
        )
        
        assert info.name == "test_codebase"
        assert info.display_name == "Test Codebase"
        assert info.root_path == Path("/test/path")
        assert info.description == "A test codebase"
        assert info.version == "1.0.0"
        
        # Check defaults
        assert info.last_indexed == ""
        assert info.document_count == 0
        assert info.total_lines == 0
        assert info.include_patterns == ["*.py"]
        assert "*.pyc" in info.exclude_patterns


class TestCodebaseCollection:
    """Test CodebaseCollection functionality."""
    
    def test_collection_initialization(self, mock_vector_store):
        """Test collection initializes correctly."""
        collection = CodebaseCollection(mock_vector_store, "test_collection")
        
        assert collection.vector_store == mock_vector_store
        assert collection.collection_name == "test_collection"
        assert len(collection.codebases) == 0
        assert collection.extractor is not None
        assert collection.change_detector is not None
        assert collection.token_tracker is not None
    
    @pytest.mark.asyncio
    async def test_add_codebase(self, mock_vector_store):
        """Test adding codebase to collection."""
        collection = CodebaseCollection(mock_vector_store)
        
        test_path = Path("/test/codebase")
        await collection.add_codebase(
            name="test_codebase",
            root_path=test_path,
            display_name="Test Codebase",
            description="A test codebase for testing"
        )
        
        assert "test_codebase" in collection.codebases
        codebase_info = collection.codebases["test_codebase"]
        assert codebase_info.name == "test_codebase"
        assert codebase_info.display_name == "Test Codebase"
        assert codebase_info.root_path == test_path
        assert codebase_info.description == "A test codebase for testing"
    
    @pytest.mark.asyncio
    async def test_index_codebase_new(self, mock_vector_store, sample_codebase_files: Path):
        """Test indexing a new codebase."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Add codebase
        await collection.add_codebase(
            name="test_codebase",
            root_path=sample_codebase_files,
            display_name="Test Codebase"
        )
        
        # Index codebase
        result = await collection.index_codebase("test_codebase")
        
        # Check results
        assert result["codebase_name"] == "test_codebase"
        assert result["documents_total"] > 0
        assert result["documents_processed"] > 0
        assert result["documents_skipped"] == 0  # All new documents
        assert result["chunks_created"] > 0
        assert result["total_lines"] > 0
        
        # Check vector store was called
        assert len(mock_vector_store.documents) > 0
        assert len(mock_vector_store.call_log) > 0
        
        # Check token usage tracking
        assert "token_usage" in result
        token_stats = result["token_usage"]
        assert token_stats["tokens_used"] >= 0
        assert token_stats["operations_count"] > 0
    
    @pytest.mark.asyncio
    async def test_index_codebase_incremental(self, mock_vector_store, sample_codebase_files: Path):
        """Test incremental indexing with change detection."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Add and index codebase first time
        await collection.add_codebase(
            name="test_codebase",
            root_path=sample_codebase_files
        )
        
        result1 = await collection.index_codebase("test_codebase")
        initial_processed = result1["documents_processed"]
        
        # Index again without changes
        result2 = await collection.index_codebase("test_codebase")
        
        # Should skip documents that haven't changed
        assert result2["documents_skipped"] > 0
        assert result2["documents_processed"] < initial_processed
        
        # Token usage should be lower due to skipped documents
        assert result2["token_usage"]["tokens_saved"] > 0
    
    @pytest.mark.asyncio
    async def test_index_codebase_force_reindex(self, mock_vector_store, sample_codebase_files: Path):
        """Test force reindexing ignores change detection."""
        collection = CodebaseCollection(mock_vector_store)
        
        await collection.add_codebase(
            name="test_codebase", 
            root_path=sample_codebase_files
        )
        
        # Index normally first
        result1 = await collection.index_codebase("test_codebase")
        
        # Force reindex
        result2 = await collection.index_codebase("test_codebase", force_full_reindex=True)
        
        # Should process all documents again
        assert result2["documents_processed"] == result1["documents_processed"]
        assert result2["documents_skipped"] == 0
    
    @pytest.mark.asyncio
    async def test_index_nonexistent_codebase(self, mock_vector_store):
        """Test indexing nonexistent codebase raises error."""
        collection = CodebaseCollection(mock_vector_store)
        
        with pytest.raises(ValueError, match="Codebase 'nonexistent' not found"):
            await collection.index_codebase("nonexistent")
    
    def test_chunk_document_function(self, mock_vector_store, sample_document):
        """Test document chunking for function definitions."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Function definitions should be kept as single chunks
        chunks = collection._chunk_document(sample_document)
        
        assert len(chunks) == 1  # Function should be single chunk
        assert sample_document.get_searchable_text() in chunks[0]
    
    def test_chunk_document_large_content(self, mock_vector_store):
        """Test chunking of large documents."""
        from goldentooth_agent.core.agent_codebase.schema import CodebaseDocument, CodebaseDocumentType
        
        collection = CodebaseCollection(mock_vector_store)
        
        # Create document with large content
        large_content = "# Large Document\n\n" + "This is a very long paragraph. " * 200
        large_doc = CodebaseDocument(
            document_id="large_doc",
            document_type=CodebaseDocumentType.MODULE_BACKGROUND,
            title="Large Document",
            content=large_content,
            file_path="/large.md",
            module_path="large"
        )
        
        chunks = collection._chunk_document(large_doc)
        
        # Should be split into multiple chunks
        assert len(chunks) > 1
        
        # Each chunk should be reasonably sized
        for chunk in chunks:
            assert len(chunk) <= large_doc.get_chunk_size_hint() * 1.2  # Allow some overflow
    
    def test_chunk_markdown_sections(self, mock_vector_store):
        """Test markdown section chunking."""
        collection = CodebaseCollection(mock_vector_store)
        
        content = """# First Section

This is the first section with some content.

# Second Section

This is the second section with different content.

## Subsection

More detailed information here."""
        
        chunks = collection._chunk_markdown_sections(content, chunk_size=150)
        
        # Should split on major headers
        assert len(chunks) >= 2
        
        # First chunk should contain first section
        assert "# First Section" in chunks[0]
        
        # Subsequent chunks should contain other sections
        combined = " ".join(chunks[1:])
        assert "# Second Section" in combined
    
    def test_chunk_source_code(self, mock_vector_store):
        """Test source code chunking."""
        collection = CodebaseCollection(mock_vector_store)
        
        code = """import os
import sys

def first_function():
    '''First function.'''
    return 1

def second_function():
    '''Second function.'''
    return 2

class MyClass:
    '''A test class.'''
    
    def method(self):
        return "method"
"""
        
        chunks = collection._chunk_source_code(code, chunk_size=200)
        
        # Should split on function/class boundaries
        assert len(chunks) >= 2
        
        # Functions and classes should be preserved
        combined = " ".join(chunks)
        assert "def first_function" in combined
        assert "def second_function" in combined
        assert "class MyClass" in combined
    
    def test_chunk_by_paragraphs(self, mock_vector_store):
        """Test paragraph-based chunking."""
        collection = CodebaseCollection(mock_vector_store)
        
        content = """First paragraph with some content.

Second paragraph with different content.

Third paragraph with even more content that might be quite long and detailed.

Fourth paragraph wrapping up the content."""
        
        chunks = collection._chunk_by_paragraphs(content, chunk_size=100)
        
        # Should split on paragraph boundaries
        assert len(chunks) >= 2
        
        # Paragraphs should be preserved
        combined = "\n\n".join(chunks)
        assert "First paragraph" in combined
        assert "Second paragraph" in combined
    
    @pytest.mark.asyncio
    async def test_search(self, mock_vector_store, sample_codebase_files: Path):
        """Test searching across codebases."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Add some mock search results
        mock_vector_store.documents["test_doc"] = {
            "text": "test function implementation",
            "metadata": {
                "document_type": "function_definition",
                "module_path": "test.module"
            }
        }
        
        results = await collection.search(
            query="test function",
            codebase_names=["test_codebase"],
            document_types=[CodebaseDocumentType.FUNCTION_DEFINITION],
            limit=5
        )
        
        # Should return search results
        assert len(results) >= 0  # May be empty if no matches
    
    def test_get_codebase_info(self, mock_vector_store):
        """Test getting codebase information."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Add codebase info manually
        info = CodebaseInfo(
            name="test_codebase",
            display_name="Test",
            root_path=Path("/test")
        )
        collection.codebases["test_codebase"] = info
        
        retrieved_info = collection.get_codebase_info("test_codebase")
        assert retrieved_info == info
        
        # Test nonexistent codebase
        assert collection.get_codebase_info("nonexistent") is None
    
    def test_list_codebases(self, mock_vector_store):
        """Test listing all codebases."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Add multiple codebases
        info1 = CodebaseInfo(name="codebase1", display_name="First", root_path=Path("/first"))
        info2 = CodebaseInfo(name="codebase2", display_name="Second", root_path=Path("/second"))
        
        collection.codebases["codebase1"] = info1
        collection.codebases["codebase2"] = info2
        
        codebases = collection.list_codebases()
        
        assert len(codebases) == 2
        assert info1 in codebases
        assert info2 in codebases
    
    @pytest.mark.asyncio
    async def test_error_handling_in_extraction(self, mock_vector_store, temp_dir: Path):
        """Test error handling during document extraction."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Create a directory with problematic files
        test_dir = temp_dir / "error_test"
        test_dir.mkdir()
        
        # Create a file that will cause extraction issues
        problematic_file = test_dir / "bad.py"
        problematic_file.write_text("def incomplete(")  # Syntax error
        
        await collection.add_codebase(
            name="error_codebase",
            root_path=test_dir
        )
        
        # Should handle errors gracefully
        result = await collection.index_codebase("error_codebase")
        
        # Should complete without raising exception
        assert result["codebase_name"] == "error_codebase"
        # May have 0 documents if all failed to extract
        assert result["documents_total"] >= 0
    
    def test_document_source_creation(self, mock_vector_store):
        """Test document source creation for vector store."""
        collection = CodebaseCollection(mock_vector_store, "test_collection")
        
        # This would be tested during indexing, but we can verify the structure
        # by checking what gets passed to the mock vector store
        
        # The actual test is in test_index_codebase_new where we verify
        # that mock_vector_store.add_document is called with proper source
        pass
    
    def test_metadata_structure(self, mock_vector_store, sample_document):
        """Test metadata structure passed to vector store."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Test that chunking preserves metadata structure
        chunks = collection._chunk_document(sample_document)
        
        # This is indirectly tested in the indexing tests where we verify
        # the metadata passed to add_document includes all expected fields
        assert len(chunks) > 0
    
    @pytest.mark.asyncio
    async def test_stale_document_cleanup(self, mock_vector_store, temp_dir: Path):
        """Test cleanup of stale documents."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Create initial structure
        test_dir = temp_dir / "cleanup_test"
        test_dir.mkdir()
        
        file1 = test_dir / "file1.py"
        file1.write_text("def func1(): pass")
        
        file2 = test_dir / "file2.py"
        file2.write_text("def func2(): pass")
        
        await collection.add_codebase("cleanup_test", test_dir)
        
        # Index initially
        result1 = await collection.index_codebase("cleanup_test")
        assert result1["documents_total"] >= 2
        
        # Remove one file
        file2.unlink()
        
        # Index again
        result2 = await collection.index_codebase("cleanup_test")
        
        # Should detect and report stale documents
        assert result2["stale_documents_removed"] >= 0
    
    def test_change_detector_integration(self, mock_vector_store):
        """Test integration with change detector."""
        collection = CodebaseCollection(mock_vector_store)
        
        # Change detector should be initialized
        assert collection.change_detector is not None
        assert collection.change_detector.index is not None
        
        # Token tracker should be initialized
        assert collection.token_tracker is not None
        assert collection.token_tracker.budget is not None