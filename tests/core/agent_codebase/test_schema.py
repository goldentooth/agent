"""
Tests for codebase document schema and types.
"""

import pytest
from goldentooth_agent.core.agent_codebase.schema import (
    CodebaseDocument,
    CodebaseDocumentType,
)


class TestCodebaseDocumentType:
    """Test CodebaseDocumentType enum."""
    
    def test_all_types_available(self):
        """Test that all expected document types are available."""
        expected_types = {
            "MODULE_API",
            "MODULE_BACKGROUND", 
            "SOURCE_CODE",
            "FUNCTION_DEFINITION",
            "CLASS_DEFINITION",
            "TEST_CODE",
            "EXAMPLE_CODE",
            "CONFIGURATION",
            "ARCHITECTURE_OVERVIEW"
        }
        
        available_types = {attr for attr in dir(CodebaseDocumentType) if not attr.startswith('_')}
        assert expected_types.issubset(available_types)
    
    def test_type_values(self):
        """Test that document types have correct string values."""
        assert CodebaseDocumentType.MODULE_API.value == "module_api"
        assert CodebaseDocumentType.FUNCTION_DEFINITION.value == "function_definition"
        assert CodebaseDocumentType.CLASS_DEFINITION.value == "class_definition"


class TestCodebaseDocument:
    """Test CodebaseDocument model."""
    
    def test_minimal_document_creation(self):
        """Test creating document with minimal required fields."""
        doc = CodebaseDocument(
            document_id="test_123",
            document_type=CodebaseDocumentType.SOURCE_CODE,
            title="Test Document",
            content="print('hello')",
            file_path="/test/file.py",
            module_path="test.module"
        )
        
        assert doc.document_id == "test_123"
        assert doc.document_type == CodebaseDocumentType.SOURCE_CODE
        assert doc.title == "Test Document"
        assert doc.content == "print('hello')"
        assert doc.file_path == "/test/file.py"
        assert doc.module_path == "test.module"
        
        # Check defaults
        assert doc.summary == ""
        assert doc.line_start == 0
        assert doc.line_end == 0
        assert doc.tags == []
        assert doc.dependencies == []
        assert doc.signature == ""
        assert doc.docstring == ""
        assert doc.complexity_score == 0.0
        assert doc.related_documents == []
        assert doc.metadata == {}
    
    def test_complete_document_creation(self):
        """Test creating document with all fields."""
        doc = CodebaseDocument(
            document_id="test_456",
            document_type=CodebaseDocumentType.FUNCTION_DEFINITION,
            title="Function: mymodule.my_function",
            content="def my_function(x: int) -> str:\n    return str(x)",
            summary="Converts integer to string",
            file_path="/src/mymodule.py",
            line_start=10,
            line_end=12,
            module_path="mymodule",
            tags=["function", "python", "utility"],
            dependencies=["typing"],
            signature="def my_function(x: int) -> str",
            docstring="Converts integer to string representation",
            complexity_score=0.2,
            related_documents=["test_123"],
            metadata={"author": "test", "version": "1.0"}
        )
        
        assert doc.document_id == "test_456"
        assert doc.summary == "Converts integer to string"
        assert doc.line_start == 10
        assert doc.line_end == 12
        assert doc.tags == ["function", "python", "utility"]
        assert doc.dependencies == ["typing"]
        assert doc.signature == "def my_function(x: int) -> str"
        assert doc.docstring == "Converts integer to string representation"
        assert doc.complexity_score == 0.2
        assert doc.related_documents == ["test_123"]
        assert doc.metadata == {"author": "test", "version": "1.0"}
    
    def test_get_searchable_text(self):
        """Test searchable text generation."""
        doc = CodebaseDocument(
            document_id="test_789",
            document_type=CodebaseDocumentType.CLASS_DEFINITION,
            title="Class MyClass",
            content="class MyClass:\n    pass",
            summary="A test class",
            file_path="/test.py",
            module_path="test",
            tags=["class", "test"],
            docstring="This is a test class"
        )
        
        searchable = doc.get_searchable_text()
        
        # Should contain all relevant text fields
        assert "Class MyClass" in searchable
        assert "A test class" in searchable
        assert "class MyClass:\n    pass" in searchable
        assert "This is a test class" in searchable
        assert "class test" in searchable  # tags joined
        assert "test" in searchable  # module_path
    
    def test_get_chunk_size_hint(self):
        """Test chunk size hints for different document types."""
        test_cases = [
            (CodebaseDocumentType.MODULE_API, 2000),
            (CodebaseDocumentType.MODULE_BACKGROUND, 3000),
            (CodebaseDocumentType.SOURCE_CODE, 1000),
            (CodebaseDocumentType.FUNCTION_DEFINITION, 800),
            (CodebaseDocumentType.CLASS_DEFINITION, 1500),
            (CodebaseDocumentType.TEST_CODE, 1000),
            (CodebaseDocumentType.EXAMPLE_CODE, 1200),
            (CodebaseDocumentType.CONFIGURATION, 800),
            (CodebaseDocumentType.ARCHITECTURE_OVERVIEW, 4000),
        ]
        
        for doc_type, expected_size in test_cases:
            doc = CodebaseDocument(
                document_id="test",
                document_type=doc_type,
                title="Test",
                content="test content",
                file_path="/test.py",
                module_path="test"
            )
            assert doc.get_chunk_size_hint() == expected_size
    
    def test_validation_errors(self):
        """Test validation errors for invalid data."""
        # Missing required fields
        with pytest.raises(ValueError):
            CodebaseDocument(
                # Missing document_id
                document_type=CodebaseDocumentType.SOURCE_CODE,
                title="Test",
                content="test",
                file_path="/test.py",
                module_path="test"
            )
        
        # Invalid document type
        with pytest.raises(ValueError):
            CodebaseDocument(
                document_id="test",
                document_type="invalid_type",  # Should be enum
                title="Test", 
                content="test",
                file_path="/test.py",
                module_path="test"
            )
    
    def test_model_serialization(self):
        """Test that documents can be serialized and deserialized."""
        original = CodebaseDocument(
            document_id="test_serialize",
            document_type=CodebaseDocumentType.MODULE_API,
            title="Serialization Test",
            content="test content",
            file_path="/test.py",
            module_path="test",
            tags=["serialization", "test"],
            metadata={"test": True}
        )
        
        # Convert to dict and back
        doc_dict = original.model_dump()
        restored = CodebaseDocument.model_validate(doc_dict)
        
        assert original == restored
        assert original.document_id == restored.document_id
        assert original.document_type == restored.document_type
        assert original.tags == restored.tags
        assert original.metadata == restored.metadata