"""
Test fixtures for agent_codebase module.
"""

import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from goldentooth_agent.core.agent_codebase.change_detection import SmartChangeDetector
from goldentooth_agent.core.agent_codebase.token_tracking import TokenTracker
from goldentooth_agent.core.agent_codebase.extraction import CodebaseDocumentExtractor
from goldentooth_agent.core.agent_codebase.schema import CodebaseDocument, CodebaseDocumentType


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp:
        yield Path(temp)


@pytest.fixture
def change_detector(temp_dir: Path) -> SmartChangeDetector:
    """Change detector with temporary index file."""
    index_file = temp_dir / "test_change_index.json"
    return SmartChangeDetector(index_file)


@pytest.fixture
def token_tracker(temp_dir: Path) -> TokenTracker:
    """Token tracker with temporary database."""
    db_file = temp_dir / "test_tokens.db"
    return TokenTracker(db_file)


@pytest.fixture
def document_extractor() -> CodebaseDocumentExtractor:
    """Document extractor instance."""
    return CodebaseDocumentExtractor()


@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code for testing."""
    return '''"""Sample module for testing."""

import os
from typing import List

class TestClass:
    """A test class."""
    
    def __init__(self, name: str) -> None:
        """Initialize with name."""
        self.name = name
    
    def process_data(self, items: List[str]) -> dict:
        """Process a list of items."""
        return {"count": len(items), "items": items}

def utility_function(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y

# Constants
MAX_ITEMS = 100
'''


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample markdown content for testing."""
    return '''# Test Module

This is a test module for the agent codebase introspection system.

## Overview

The module provides functionality for:
- Document extraction
- Change detection  
- Token tracking

## API Reference

### TestClass

Main class for testing purposes.

#### Methods

- `process_data(items)`: Process list of items
- `__init__(name)`: Initialize with name

### Functions

- `utility_function(x, y)`: Add two numbers
'''


@pytest.fixture
def sample_codebase_files(temp_dir: Path, sample_python_code: str, sample_markdown_content: str) -> Path:
    """Create a sample codebase structure."""
    # Create directory structure
    src_dir = temp_dir / "src" / "test_package"
    src_dir.mkdir(parents=True)
    
    # Python files
    (src_dir / "__init__.py").write_text('"""Test package."""\n')
    (src_dir / "main.py").write_text(sample_python_code)
    (src_dir / "utils.py").write_text('''
def helper_function(data: str) -> str:
    """Help with data processing."""
    return data.upper()
''')
    
    # Documentation files
    (src_dir / "README.md").write_text(sample_markdown_content)
    (src_dir / "README.bg.md").write_text('''# Background: Test Module

## Motivation

This module was created to test the codebase introspection system.

## Design Decisions

- Simple structure for easy testing
- Clear documentation for validation
''')
    
    # Subdirectory
    subdir = src_dir / "submodule"
    subdir.mkdir()
    (subdir / "__init__.py").write_text('')
    (subdir / "worker.py").write_text('''
class Worker:
    """A worker class."""
    
    def work(self) -> str:
        """Do some work."""
        return "working"
''')
    
    return temp_dir


@pytest.fixture
def sample_document() -> CodebaseDocument:
    """Sample codebase document for testing."""
    return CodebaseDocument(
        document_id="test_doc_123",
        document_type=CodebaseDocumentType.FUNCTION_DEFINITION,
        title="Function: test_module.sample_function",
        content="def sample_function(x: int) -> int:\n    return x * 2",
        summary="A sample function that doubles input",
        file_path="/test/path/test_module.py",
        line_start=10,
        line_end=12,
        module_path="test_module",
        tags=["function", "python"],
        signature="def sample_function(x: int) -> int",
        docstring="A sample function that doubles input",
        complexity_score=0.1
    )


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    class MockVectorStore:
        def __init__(self):
            self.documents = {}
            self.call_log = []
        
        async def add_document(self, text: str, document_id: str, source: Any, metadata: dict) -> None:
            self.documents[document_id] = {
                "text": text,
                "source": source,
                "metadata": metadata
            }
            self.call_log.append(("add_document", document_id, len(text)))
        
        async def search(self, query: str, limit: int = 10, metadata_filters: dict = None) -> list:
            # Simple mock search - return documents containing query terms
            results = []
            for doc_id, doc_data in self.documents.items():
                if query.lower() in doc_data["text"].lower():
                    results.append({
                        "document_id": doc_id,
                        "content": doc_data["text"],
                        "score": 0.8,
                        "metadata": doc_data["metadata"]
                    })
            return results[:limit]
    
    return MockVectorStore()