"""
Tests for smart change detection system.
"""

import pytest
from pathlib import Path
from datetime import datetime

from goldentooth_agent.core.agent_codebase.change_detection import (
    SmartChangeDetector,
    ContentFingerprint,
    ChangeDetectionIndex
)
from goldentooth_agent.core.agent_codebase.schema import CodebaseDocument, CodebaseDocumentType


class TestContentFingerprint:
    """Test ContentFingerprint model."""
    
    def test_fingerprint_creation(self):
        """Test creating content fingerprint."""
        fingerprint = ContentFingerprint(
            document_id="test_doc",
            file_path="/test/file.py",
            content_hash="abc123",
            structure_hash="def456",
            semantic_hash="ghi789",
            file_mtime=1234567890.0,
            last_indexed=datetime.now().isoformat()
        )
        
        assert fingerprint.document_id == "test_doc"
        assert fingerprint.file_path == "/test/file.py"
        assert fingerprint.content_hash == "abc123"
        assert fingerprint.structure_hash == "def456"
        assert fingerprint.semantic_hash == "ghi789"
    
    def test_has_content_changed(self):
        """Test content change detection."""
        original = ContentFingerprint(
            document_id="test",
            file_path="/test.py",
            content_hash="abc",
            structure_hash="def",
            semantic_hash="original_semantic",
            file_mtime=1000.0,
            last_indexed="2024-01-01T00:00:00"
        )
        
        # Same semantic hash - no content change
        unchanged = ContentFingerprint(
            document_id="test",
            file_path="/test.py", 
            content_hash="xyz",  # Raw content changed
            structure_hash="uvw",  # Structure changed
            semantic_hash="original_semantic",  # Semantic unchanged
            file_mtime=2000.0,
            last_indexed="2024-01-02T00:00:00"
        )
        
        assert not original.has_content_changed(unchanged)
        
        # Different semantic hash - content changed
        changed = ContentFingerprint(
            document_id="test",
            file_path="/test.py",
            content_hash="xyz",
            structure_hash="uvw", 
            semantic_hash="new_semantic",  # Semantic changed
            file_mtime=2000.0,
            last_indexed="2024-01-02T00:00:00"
        )
        
        assert original.has_content_changed(changed)
    
    def test_needs_re_embedding(self):
        """Test re-embedding decision logic."""
        original = ContentFingerprint(
            document_id="test",
            file_path="/test.py",
            content_hash="abc",
            structure_hash="def",
            semantic_hash="original_semantic",
            file_mtime=1000.0,
            last_indexed="2024-01-01T00:00:00"
        )
        
        # Semantic change - needs re-embedding
        semantic_change = ContentFingerprint(
            document_id="test",
            file_path="/test.py",
            content_hash="abc",
            structure_hash="def",
            semantic_hash="new_semantic",
            file_mtime=1000.0,
            last_indexed="2024-01-01T00:00:00"
        )
        
        assert original.needs_re_embedding(semantic_change)
        
        # Structure change with newer file - needs re-embedding
        structure_change = ContentFingerprint(
            document_id="test",
            file_path="/test.py",
            content_hash="abc",
            structure_hash="new_structure",
            semantic_hash="original_semantic",
            file_mtime=2000.0,  # Newer file
            last_indexed="2024-01-02T00:00:00"
        )
        
        assert original.needs_re_embedding(structure_change)
        
        # Only cosmetic changes - no re-embedding needed
        cosmetic_change = ContentFingerprint(
            document_id="test",
            file_path="/test.py",
            content_hash="xyz",  # Raw content changed (formatting)
            structure_hash="def",  # Structure unchanged
            semantic_hash="original_semantic",  # Semantic unchanged
            file_mtime=1000.0,  # Same time
            last_indexed="2024-01-01T00:00:00"
        )
        
        assert not original.needs_re_embedding(cosmetic_change)


class TestChangeDetectionIndex:
    """Test ChangeDetectionIndex model."""
    
    def test_index_operations(self):
        """Test index CRUD operations."""
        index = ChangeDetectionIndex()
        
        fingerprint = ContentFingerprint(
            document_id="test_doc",
            file_path="/test.py",
            content_hash="abc",
            structure_hash="def", 
            semantic_hash="ghi",
            file_mtime=1000.0,
            last_indexed="2024-01-01T00:00:00"
        )
        
        # Test adding fingerprint
        index.update_fingerprint(fingerprint)
        assert len(index.fingerprints) == 1
        assert index.get_fingerprint("test_doc") == fingerprint
        
        # Test updating fingerprint
        updated_fingerprint = ContentFingerprint(
            document_id="test_doc",
            file_path="/test.py",
            content_hash="xyz",
            structure_hash="def",
            semantic_hash="ghi", 
            file_mtime=2000.0,
            last_indexed="2024-01-02T00:00:00"
        )
        
        index.update_fingerprint(updated_fingerprint)
        assert len(index.fingerprints) == 1  # Still one document
        assert index.get_fingerprint("test_doc") == updated_fingerprint
        
        # Test removing fingerprint
        index.remove_fingerprint("test_doc")
        assert len(index.fingerprints) == 0
        assert index.get_fingerprint("test_doc") is None
    
    def test_get_stale_documents(self):
        """Test stale document detection."""
        index = ChangeDetectionIndex()
        
        # Add some fingerprints
        fp1 = ContentFingerprint(
            document_id="doc1",
            file_path="/file1.py",
            content_hash="a", structure_hash="b", semantic_hash="c",
            file_mtime=1000.0, last_indexed="2024-01-01T00:00:00"
        )
        fp2 = ContentFingerprint(
            document_id="doc2", 
            file_path="/file2.py",
            content_hash="d", structure_hash="e", semantic_hash="f",
            file_mtime=1000.0, last_indexed="2024-01-01T00:00:00"
        )
        fp3 = ContentFingerprint(
            document_id="doc3",
            file_path="/file3.py", 
            content_hash="g", structure_hash="h", semantic_hash="i",
            file_mtime=1000.0, last_indexed="2024-01-01T00:00:00"
        )
        
        index.update_fingerprint(fp1)
        index.update_fingerprint(fp2)
        index.update_fingerprint(fp3)
        
        # Current files only include file1 and file2
        current_files = {"/file1.py", "/file2.py"}
        
        stale_docs = index.get_stale_documents(current_files)
        assert stale_docs == ["doc3"]  # file3.py no longer exists


class TestSmartChangeDetector:
    """Test SmartChangeDetector functionality."""
    
    def test_detector_initialization(self, change_detector: SmartChangeDetector):
        """Test detector initializes with empty index."""
        assert len(change_detector.index.fingerprints) == 0
    
    def test_generate_fingerprint(self, change_detector: SmartChangeDetector, sample_document: CodebaseDocument, temp_dir: Path):
        """Test fingerprint generation."""
        # Create a test file
        test_file = temp_dir / "test.py"
        test_file.write_text(sample_document.content)
        
        fingerprint = change_detector._generate_fingerprint(sample_document, test_file)
        
        assert fingerprint.document_id == sample_document.document_id
        assert fingerprint.file_path == str(test_file)
        assert len(fingerprint.content_hash) == 16  # SHA256 truncated
        assert len(fingerprint.structure_hash) == 16
        assert len(fingerprint.semantic_hash) == 16
        assert fingerprint.file_mtime > 0
        assert fingerprint.line_count == sample_document.line_end - sample_document.line_start
    
    def test_extract_semantic_content(self, change_detector: SmartChangeDetector):
        """Test semantic content extraction."""
        doc = CodebaseDocument(
            document_id="test",
            document_type=CodebaseDocumentType.FUNCTION_DEFINITION,
            title="Function: test_func",
            content='def test_func(x: int) -> str:\n    """Test function."""\n    return str(x)',
            summary="Test function",
            file_path="/test.py",
            module_path="test",
            docstring="Test function that converts int to str",
            tags=["function", "test"]
        )
        
        semantic = change_detector._extract_semantic_content(doc)
        
        # Should contain key semantic elements
        assert "Function: test_func" in semantic
        assert "Test function" in semantic
        assert "Test function that converts int to str" in semantic
        assert "function test" in semantic  # sorted tags
        assert "test" in semantic  # module path
    
    def test_extract_code_semantics(self, change_detector: SmartChangeDetector):
        """Test code semantic extraction."""
        code = '''
def process_data(items: list) -> dict:
    """Process data items."""
    result = {}
    for item in items:
        result[item] = len(item)
    return result

class DataProcessor:
    """Processes data."""
    
    def __init__(self):
        self.count = 0
'''
        
        semantics = change_detector._extract_code_semantics(code)
        
        # Should extract function and class signatures
        assert "def process_data" in semantics
        assert "class DataProcessor" in semantics
        # Should include normalized docstrings
        assert "Process data items" in semantics
        assert "Processes data" in semantics
    
    def test_normalize_docstring(self, change_detector: SmartChangeDetector):
        """Test docstring normalization."""
        raw_docstring = '''"""
        This is a test docstring
        with multiple lines
        and various formatting.
        """'''
        
        normalized = change_detector._normalize_docstring(raw_docstring)
        
        # Should remove docstring markers and extra whitespace
        assert '"""' not in normalized
        assert "This is a test docstring" in normalized
        assert "with multiple lines" in normalized
    
    def test_analyze_document_changes_new_document(self, change_detector: SmartChangeDetector, sample_document: CodebaseDocument, temp_dir: Path):
        """Test analyzing changes for a new document."""
        test_file = temp_dir / "new_test.py"
        test_file.write_text(sample_document.content)
        
        needs_embedding, fingerprint = change_detector.analyze_document_changes(sample_document, test_file)
        
        # New document should need embedding
        assert needs_embedding
        assert fingerprint.document_id == sample_document.document_id
    
    def test_analyze_document_changes_unchanged(self, change_detector: SmartChangeDetector, sample_document: CodebaseDocument, temp_dir: Path):
        """Test analyzing unchanged document."""
        test_file = temp_dir / "unchanged_test.py"
        test_file.write_text(sample_document.content)
        
        # First analysis - new document
        needs_embedding, fingerprint = change_detector.analyze_document_changes(sample_document, test_file)
        assert needs_embedding
        
        # Store fingerprint
        change_detector.update_fingerprint(fingerprint)
        
        # Second analysis - unchanged document
        needs_embedding, new_fingerprint = change_detector.analyze_document_changes(sample_document, test_file)
        
        # Should not need re-embedding if content is the same
        assert not needs_embedding
    
    def test_analyze_document_changes_semantic_change(self, change_detector: SmartChangeDetector, sample_document: CodebaseDocument, temp_dir: Path):
        """Test analyzing document with semantic changes."""
        test_file = temp_dir / "semantic_test.py"
        test_file.write_text(sample_document.content)
        
        # First analysis - new document
        needs_embedding, fingerprint = change_detector.analyze_document_changes(sample_document, test_file)
        change_detector.update_fingerprint(fingerprint)
        
        # Create modified document with semantic change
        modified_doc = sample_document.model_copy()
        modified_doc.content = modified_doc.content.replace("x * 2", "x * 3")  # Change logic
        modified_doc.docstring = "A sample function that triples input"  # Change meaning
        
        # Update file content
        test_file.write_text(modified_doc.content)
        
        # Second analysis - semantic change
        needs_embedding, new_fingerprint = change_detector.analyze_document_changes(modified_doc, test_file)
        
        # Should need re-embedding due to semantic change
        assert needs_embedding
    
    def test_cleanup_stale_documents(self, change_detector: SmartChangeDetector, temp_dir: Path):
        """Test cleanup of stale documents."""
        # Add some fingerprints to the index
        fp1 = ContentFingerprint(
            document_id="doc1", file_path="/existing.py",
            content_hash="a", structure_hash="b", semantic_hash="c",
            file_mtime=1000.0, last_indexed="2024-01-01T00:00:00"
        )
        fp2 = ContentFingerprint(
            document_id="doc2", file_path="/deleted.py", 
            content_hash="d", structure_hash="e", semantic_hash="f",
            file_mtime=1000.0, last_indexed="2024-01-01T00:00:00"
        )
        
        change_detector.update_fingerprint(fp1)
        change_detector.update_fingerprint(fp2)
        
        assert len(change_detector.index.fingerprints) == 2
        
        # Cleanup with only one existing file
        current_files = {"/existing.py"}
        stale_docs = change_detector.cleanup_stale_documents(current_files)
        
        assert stale_docs == ["doc2"]
        assert len(change_detector.index.fingerprints) == 1
        assert "doc1" in change_detector.index.fingerprints
        assert "doc2" not in change_detector.index.fingerprints
    
    def test_hash_content_consistency(self, change_detector: SmartChangeDetector):
        """Test that content hashing is consistent."""
        content = "def test(): pass"
        
        hash1 = change_detector._hash_content(content)
        hash2 = change_detector._hash_content(content)
        
        assert hash1 == hash2
        assert len(hash1) == 16  # Truncated SHA256
        
        # Different content should have different hash
        different_content = "def other(): pass"
        hash3 = change_detector._hash_content(different_content)
        assert hash1 != hash3
    
    def test_persistence(self, temp_dir: Path):
        """Test index persistence across detector instances."""
        index_file = temp_dir / "test_index.json"
        
        # Create first detector and add fingerprint
        detector1 = SmartChangeDetector(index_file)
        fingerprint = ContentFingerprint(
            document_id="persistent_doc",
            file_path="/test.py",
            content_hash="abc", structure_hash="def", semantic_hash="ghi",
            file_mtime=1000.0, last_indexed="2024-01-01T00:00:00"
        )
        detector1.update_fingerprint(fingerprint)
        
        # Create second detector - should load persisted data
        detector2 = SmartChangeDetector(index_file)
        
        assert len(detector2.index.fingerprints) == 1
        loaded_fp = detector2.index.get_fingerprint("persistent_doc")
        assert loaded_fp is not None
        assert loaded_fp.content_hash == "abc"
        assert loaded_fp.file_path == "/test.py"
    
    def test_corrupted_index_handling(self, temp_dir: Path):
        """Test handling of corrupted index files."""
        index_file = temp_dir / "corrupted_index.json"
        
        # Create corrupted index file
        index_file.write_text("invalid json {")
        
        # Should handle corruption gracefully and start fresh
        detector = SmartChangeDetector(index_file)
        assert len(detector.index.fingerprints) == 0
    
    def test_chunk_markdown_sections(self, change_detector: SmartChangeDetector):
        """Test markdown section chunking - using collection method."""
        from goldentooth_agent.core.agent_codebase.collection import CodebaseCollection
        
        # Create a mock vector store for the collection
        class MockVectorStore:
            def store_document(self, **kwargs): pass
            def search_similar(self, **kwargs): return []
        
        collection = CodebaseCollection(MockVectorStore())
        
        content = """# Main Title

This is the first section with some content.

# Second Title

This is the second section with more content.
It has multiple paragraphs.

# Third Title

Final section here."""
        
        chunks = collection._chunk_markdown_sections(content, chunk_size=100)
        
        # Should split on major headers
        assert len(chunks) >= 2
        assert "# Main Title" in chunks[0]
        assert "# Second Title" in " ".join(chunks)
    
    def test_chunk_source_code(self, change_detector: SmartChangeDetector):
        """Test source code chunking - using collection method."""
        from goldentooth_agent.core.agent_codebase.collection import CodebaseCollection
        
        # Create a mock vector store for the collection
        class MockVectorStore:
            def store_document(self, **kwargs): pass
            def search_similar(self, **kwargs): return []
        
        collection = CodebaseCollection(MockVectorStore())
        
        content = """import os

def function_one():
    return 1

def function_two():
    return 2

class MyClass:
    def method(self):
        pass"""
        
        chunks = collection._chunk_source_code(content, chunk_size=100)
        
        # Should split on function/class boundaries
        assert len(chunks) >= 2
        # Functions should be in separate chunks or kept together if small
        combined = " ".join(chunks)
        assert "def function_one" in combined
        assert "def function_two" in combined
        assert "class MyClass" in combined