"""Tests for document chunking functionality."""

from goldentooth_agent.core.embeddings.document_chunker import (
    DocumentChunk,
    DocumentChunker,
)


class TestDocumentChunker:
    """Test the DocumentChunker class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.chunker = DocumentChunker()

    def test_github_repo_chunking(self):
        """Test chunking of GitHub repository documents."""
        doc_data = {
            "name": "test-repo",
            "full_name": "user/test-repo",
            "description": "A test repository for demonstration purposes",
            "language": "Python",
            "languages": ["Python", "JavaScript", "Shell"],
            "topics": ["testing", "automation", "ci-cd"],
            "stars": 42,
            "forks": 8,
            "open_issues": 3,
            "is_private": False,
            "is_fork": False,
            "is_archived": False,
            "priority": "high",
            "size_kb": 1024,
            "updated_at": "2024-01-01T00:00:00Z",
            "pushed_at": "2024-01-01T00:00:00Z",
            "default_branch": "main",
        }

        chunks = self.chunker.chunk_document("github.repos", "test-repo", doc_data)

        # Should create multiple chunks for a GitHub repo
        assert len(chunks) >= 2

        # Check chunk types - our implementation uses specific chunk types
        chunk_types = [chunk.chunk_type for chunk in chunks]
        assert "repo_core" in chunk_types
        assert "repo_technical" in chunk_types

        # May also have activity chunk if data is present
        if doc_data.get("stars") or doc_data.get("forks"):
            assert "repo_activity" in chunk_types

        # Verify chunk structure
        for chunk in chunks:
            assert isinstance(chunk, DocumentChunk)
            assert chunk.chunk_id.startswith("github.repos.test-repo.")
            assert chunk.parent_doc_id == "github.repos.test-repo"
            assert chunk.store_type == "github.repos"
            assert chunk.document_id == "test-repo"
            assert len(chunk.content) > 0
            assert chunk.sequence >= 1

        # Verify metadata structure
        for chunk in chunks:
            metadata = chunk.metadata
            assert "chunk_type" in metadata
            assert "chunk_index" in metadata
            assert "parent_document_id" in metadata
            assert "parent_store_type" in metadata
            assert "title" in metadata
            assert "size_chars" in metadata
            assert "start_position" in metadata
            assert "end_position" in metadata

    def test_github_org_chunking(self):
        """Test chunking of GitHub organization documents."""
        doc_data = {
            "name": "Test Organization",
            "description": "A test organization for development",
            "public_repos": 25,
            "updated_at": "2024-01-01T00:00:00Z",
        }

        chunks = self.chunker.chunk_document("github.orgs", "test-org", doc_data)

        # Organizations should typically be single chunks
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "org_main"
        assert chunks[0].parent_doc_id == "github.orgs.test-org"
        assert chunks[0].store_type == "github.orgs"
        assert chunks[0].document_id == "test-org"

    def test_note_chunking_short(self):
        """Test chunking of short note documents."""
        doc_data = {
            "title": "Quick Note",
            "content": "This is a short note that should not be chunked.",
            "category": "general",
            "tags": ["quick", "simple"],
        }

        chunks = self.chunker.chunk_document("notes", "quick-note", doc_data)

        # Short notes should be single chunks (generic chunking)
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "generic"
        assert chunks[0].parent_doc_id == "notes.quick-note"

    def test_note_chunking_with_headers(self):
        """Test chunking of notes with markdown headers."""
        doc_data = {
            "title": "Technical Guide",
            "content": """# Introduction
This is an introduction to the technical guide.

## Setup
First, you need to set up your environment:
1. Install Python
2. Install dependencies
3. Configure settings

## Usage
Here's how to use the system:
- Start the application
- Configure your settings
- Begin processing

## Troubleshooting
Common issues and solutions:
- Problem 1: Solution
- Problem 2: Solution
""",
            "category": "technical",
            "tags": ["guide", "documentation"],
        }

        chunks = self.chunker.chunk_document("notes", "tech-guide", doc_data)

        # Should create multiple chunks for sections
        assert len(chunks) > 1

        # All chunks should be note_section type
        for chunk in chunks:
            assert chunk.chunk_type == "note_section"

        # Check that headers are preserved in chunk metadata
        chunk_titles = [chunk.metadata.get("title", "") for chunk in chunks]
        assert any("Introduction" in title for title in chunk_titles)
        assert any("Setup" in title for title in chunk_titles)
        assert any("Usage" in title for title in chunk_titles)

    def test_note_chunking_single_section(self):
        """Test chunking of notes with only one section."""
        doc_data = {
            "title": "Simple Note",
            "content": """# Single Section
This note has only one section with some content.
""",
            "category": "simple",
        }

        chunks = self.chunker.chunk_document("notes", "simple-note", doc_data)

        # Should fall back to generic chunking for single section
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "generic"

    def test_get_chunk_summary(self):
        """Test the chunk summary functionality."""
        doc_data = {
            "name": "test-repo",
            "description": "A test repository",
            "language": "Python",
            "topics": ["testing"],
            "stars": 10,
            "forks": 2,
        }

        chunks = self.chunker.chunk_document("github.repos", "test-repo", doc_data)
        summary = self.chunker.get_chunk_summary(chunks)

        assert "total_chunks" in summary
        assert "total_content_length" in summary
        assert "chunk_types" in summary
        assert "chunk_type_counts" in summary
        assert "avg_chunk_length" in summary
        assert "sequences" in summary

        assert summary["total_chunks"] == len(chunks)
        assert isinstance(summary["chunk_types"], list)
        assert isinstance(summary["chunk_type_counts"], dict)
        assert len(summary["sequences"]) == len(chunks)

    def test_markdown_section_parsing(self):
        """Test markdown section parsing functionality."""
        content = """# Header 1
Content for header 1

## Header 2
Content for header 2

### Header 3
Content for header 3
"""
        sections = self.chunker._split_markdown_sections(content)

        assert len(sections) >= 3

        # Check that headers and content are extracted correctly
        for header, section_content in sections:
            if header:
                assert header.startswith("#")
            assert isinstance(section_content, str)

    def test_empty_document_handling(self):
        """Test handling of empty or minimal documents."""
        empty_doc = {}

        chunks = self.chunker.chunk_document("notes", "empty-doc", empty_doc)

        # Should create at least one chunk, even for empty documents
        assert len(chunks) >= 1
        assert chunks[0].parent_doc_id == "notes.empty-doc"
        assert chunks[0].document_id == "empty-doc"

    def test_goldentooth_service_chunking(self):
        """Test chunking of Goldentooth service documents."""
        doc_data = {
            "name": "test-service",
            "service_type": "web",
            "status": "active",
            "description": "A test service for demonstration",
            "role": "api",
        }

        chunks = self.chunker.chunk_document(
            "goldentooth.services", "test-service", doc_data
        )

        # Should create at least one chunk
        assert len(chunks) >= 1
        assert chunks[0].parent_doc_id == "goldentooth.services.test-service"
        assert chunks[0].store_type == "goldentooth.services"
        assert chunks[0].document_id == "test-service"

    def test_chunk_id_uniqueness(self):
        """Test that chunk IDs are unique within a document."""
        doc_data = {
            "title": "Multi-section Document",
            "content": """# Section 1
Content 1

# Section 2
Content 2

# Section 3
Content 3
""",
            "category": "test",
        }

        chunks = self.chunker.chunk_document("notes", "multi-section", doc_data)

        chunk_ids = [chunk.chunk_id for chunk in chunks]

        # All chunk IDs should be unique
        assert len(chunk_ids) == len(set(chunk_ids))

        # All chunk IDs should start with the parent document ID
        for chunk_id in chunk_ids:
            assert chunk_id.startswith("notes.multi-section.")

    def test_chunk_metadata_completeness(self):
        """Test that chunk metadata is complete and correct."""
        doc_data = {
            "name": "test-repo",
            "description": "Test repository",
            "language": "Python",
            "stars": 5,
        }

        chunks = self.chunker.chunk_document("github.repos", "test-repo", doc_data)

        for chunk in chunks:
            metadata = chunk.metadata

            # Required metadata fields
            assert "chunk_type" in metadata
            assert "chunk_index" in metadata
            assert "parent_document_id" in metadata
            assert "parent_store_type" in metadata
            assert "title" in metadata
            assert "size_chars" in metadata
            assert "start_position" in metadata
            assert "end_position" in metadata

            # Verify values
            assert metadata["chunk_index"] >= 1  # Should be positive integer
            assert metadata["parent_document_id"] == "github.repos.test-repo"
            assert metadata["parent_store_type"] == "github.repos"
            assert metadata["size_chars"] == len(chunk.content)
            assert isinstance(metadata["chunk_type"], str)

    def test_chunk_content_building_repo_core(self):
        """Test that repo core content is built correctly."""
        doc_data = {
            "name": "awesome-repo",
            "description": "An awesome repository for testing",
            "language": "Python",
            "size_kb": 512,
            "priority": "high",
        }

        core_content = self.chunker._build_repo_core_content(doc_data)

        assert "Repository: awesome-repo" in core_content
        assert "Description: An awesome repository for testing" in core_content
        assert "Primary Language: Python" in core_content
        assert "Size: 512 KB" in core_content
        assert "Priority: high" in core_content

    def test_chunk_content_building_repo_tech(self):
        """Test that repo technical content is built correctly."""
        doc_data = {
            "languages": ["Python", "JavaScript", "CSS"],
            "topics": ["web", "api", "automation"],
            "default_branch": "main",
        }

        tech_content = self.chunker._build_repo_tech_content(doc_data)

        assert "Languages: Python, JavaScript, CSS" in tech_content
        assert "Topics: web, api, automation" in tech_content
        assert "Default Branch: main" in tech_content

    def test_chunk_content_building_repo_activity(self):
        """Test that repo activity content is built correctly."""
        doc_data = {
            "stars": 100,
            "forks": 25,
            "open_issues": 5,
            "updated_at": "2024-01-15T10:30:00Z",
            "pushed_at": "2024-01-14T15:45:00Z",
            "is_archived": True,
        }

        activity_content = self.chunker._build_repo_activity_content(doc_data)

        assert "Activity: 100 stars, 25 forks, 5 open issues" in activity_content
        assert "Last Updated: 2024-01-15T10:30:00Z" in activity_content
        assert "Last Push: 2024-01-14T15:45:00Z" in activity_content
        assert "Status: Archived" in activity_content

    def test_note_metadata_building(self):
        """Test that note metadata is built correctly."""
        doc_data = {
            "title": "Important Note",
            "category": "documentation",
            "tags": ["important", "reference"],
            "keywords": ["api", "tutorial", "guide"],
        }

        metadata_content = self.chunker._build_note_metadata(doc_data)

        assert "Title: Important Note" in metadata_content
        assert "Category: documentation" in metadata_content
        assert "Tags: important, reference" in metadata_content
        assert "Keywords: api, tutorial, guide" in metadata_content

    def test_generic_chunking_fallback(self):
        """Test generic chunking for unknown document types."""
        doc_data = {
            "name": "Unknown Document",
            "description": "This is an unknown document type",
            "topics": ["test", "unknown"],
            "some_field": "some_value",
        }

        chunks = self.chunker.chunk_document("unknown.type", "test-doc", doc_data)

        # Should create exactly one generic chunk
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "generic"
        assert chunks[0].parent_doc_id == "unknown.type.test-doc"

        # Content should include extracted text fields
        content = chunks[0].content
        assert "Name: Unknown Document" in content
        assert "Description: This is an unknown document type" in content
        assert "Topics: test, unknown" in content

    def test_chunk_sequence_ordering(self):
        """Test that chunks maintain proper sequence ordering."""
        doc_data = {
            "title": "Ordered Document",
            "content": """# First Section
First content

# Second Section
Second content

# Third Section
Third content
""",
            "category": "test",
        }

        chunks = self.chunker.chunk_document("notes", "ordered-doc", doc_data)

        # Check that sequences are properly ordered
        sequences = [chunk.sequence for chunk in chunks]
        assert sequences == sorted(sequences)
        assert sequences[0] == 1  # Should start at 1

        # Check that chunk_index in metadata matches sequence
        for chunk in chunks:
            assert chunk.metadata["chunk_index"] == chunk.sequence

    def test_empty_content_handling(self):
        """Test handling of documents with empty content fields."""
        doc_data = {
            "title": "Empty Content Note",
            "content": "",
            "category": "test",
        }

        chunks = self.chunker.chunk_document("notes", "empty-content", doc_data)

        # Should still create a chunk, falling back to generic
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "generic"

    def test_note_with_no_headers(self):
        """Test note chunking when content has no markdown headers."""
        doc_data = {
            "title": "Plain Note",
            "content": """This is just plain text without any headers.
It has multiple paragraphs but no structured sections.

This should be treated as a single chunk since there are no clear divisions.
""",
            "category": "plain",
        }

        chunks = self.chunker.chunk_document("notes", "plain-note", doc_data)

        # Should fall back to generic chunking
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "generic"
