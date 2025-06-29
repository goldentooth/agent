"""Tests for chunk relationship analysis functionality."""

from unittest.mock import AsyncMock

import numpy as np
import pytest

from goldentooth_agent.core.embeddings.chunk_relationships import (
    ChunkRelationshipAnalyzer,
)
from goldentooth_agent.core.embeddings.document_chunker import DocumentChunk


class TestChunkRelationshipAnalyzer:
    """Test the ChunkRelationshipAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock embeddings service
        self.mock_embeddings_service = AsyncMock()
        self.analyzer = ChunkRelationshipAnalyzer(self.mock_embeddings_service)

    def test_analyzer_initialization(self):
        """Test that the analyzer initializes correctly."""
        assert self.analyzer.embeddings_service == self.mock_embeddings_service

        # Check threshold configuration
        assert "strong" in self.analyzer.similarity_thresholds
        assert "moderate" in self.analyzer.similarity_thresholds
        assert "weak" in self.analyzer.similarity_thresholds

        # Check relationship types
        assert "sequential" in self.analyzer.relationship_types
        assert "topical" in self.analyzer.relationship_types
        assert "hierarchical" in self.analyzer.relationship_types

    def test_calculate_similarity_matrix(self):
        """Test similarity matrix calculation."""
        # Create test embeddings
        embeddings = np.array(
            [
                [1.0, 0.0, 0.0],  # First embedding
                [0.0, 1.0, 0.0],  # Orthogonal to first
                [1.0, 0.0, 0.0],  # Same as first
            ]
        )

        similarity_matrix = self.analyzer._calculate_similarity_matrix(embeddings)

        # Check matrix properties
        assert similarity_matrix.shape == (3, 3)

        # Check diagonal (self-similarity should be 1.0)
        np.testing.assert_allclose(np.diag(similarity_matrix), [1.0, 1.0, 1.0])

        # Check symmetry
        np.testing.assert_allclose(similarity_matrix, similarity_matrix.T)

        # Check specific values
        assert abs(similarity_matrix[0, 1]) < 0.1  # Orthogonal vectors
        assert abs(similarity_matrix[0, 2] - 1.0) < 0.1  # Same vectors

    def test_find_sequential_relationships(self):
        """Test finding sequential relationships between chunks."""
        # Create test chunks from same document
        chunks = [
            DocumentChunk(
                chunk_id="notes.doc1.section1",
                parent_doc_id="notes.doc1",
                store_type="notes",
                document_id="doc1",
                chunk_type="note_section",
                content="First section",
                metadata={"title": "Section 1"},
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="notes.doc1.section2",
                parent_doc_id="notes.doc1",
                store_type="notes",
                document_id="doc1",
                chunk_type="note_section",
                content="Second section",
                metadata={"title": "Section 2"},
                sequence=2,
            ),
            DocumentChunk(
                chunk_id="notes.doc2.intro",
                parent_doc_id="notes.doc2",
                store_type="notes",
                document_id="doc2",
                chunk_type="note_section",
                content="Introduction",
                metadata={"title": "Introduction"},
                sequence=1,
            ),
        ]

        sequential_rels = self.analyzer._find_sequential_relationships(chunks)

        # Should find one sequential relationship (section1 -> section2)
        assert len(sequential_rels) == 1

        rel = sequential_rels[0]
        assert rel["type"] == "sequential"
        assert rel["source_chunk_id"] == "notes.doc1.section1"
        assert rel["target_chunk_id"] == "notes.doc1.section2"
        assert rel["strength"] == 1.0
        assert rel["metadata"]["document_id"] == "notes.doc1"
        assert rel["metadata"]["sequence_gap"] == 1

    def test_find_topical_relationships(self):
        """Test finding topical relationships based on similarity."""
        # Create test chunks from different documents
        chunks = [
            DocumentChunk(
                chunk_id="notes.doc1.python",
                parent_doc_id="notes.doc1",
                store_type="notes",
                document_id="doc1",
                chunk_type="note_section",
                content="Python programming",
                metadata={},
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="github.repos.repo1.core",
                parent_doc_id="github.repos.repo1",
                store_type="github.repos",
                document_id="repo1",
                chunk_type="repo_core",
                content="Python repository",
                metadata={},
                sequence=1,
            ),
        ]

        # Create similarity matrix with high similarity
        similarity_matrix = np.array(
            [
                [1.0, 0.9],  # High similarity between chunks
                [0.9, 1.0],
            ]
        )

        topical_rels = self.analyzer._find_topical_relationships(
            chunks, similarity_matrix
        )

        # Should find one topical relationship
        assert len(topical_rels) == 1

        rel = topical_rels[0]
        assert rel["type"] == "topical"
        assert rel["strength"] == 0.9
        assert rel["strength_category"] == "strong"
        assert rel["metadata"]["different_stores"] is True

    def test_find_hierarchical_relationships(self):
        """Test finding hierarchical relationships."""
        # Create test chunks with hierarchical structure
        chunks = [
            DocumentChunk(
                chunk_id="github.repos.repo1.core",
                parent_doc_id="github.repos.repo1",
                store_type="github.repos",
                document_id="repo1",
                chunk_type="repo_core",
                content="Core info",
                metadata={},
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="github.repos.repo1.technical",
                parent_doc_id="github.repos.repo1",
                store_type="github.repos",
                document_id="repo1",
                chunk_type="repo_technical",
                content="Technical details",
                metadata={},
                sequence=2,
            ),
        ]

        hierarchical_rels = self.analyzer._find_hierarchical_relationships(chunks)

        # Should find hierarchical relationship
        assert len(hierarchical_rels) == 1

        rel = hierarchical_rels[0]
        assert rel["type"] == "hierarchical"
        assert rel["strength"] == 0.8
        assert rel["metadata"]["hierarchy_type"] == "core_to_technical"

    def test_is_hierarchical_relationship(self):
        """Test hierarchical relationship detection."""
        # Test repo hierarchy
        core_chunk = DocumentChunk(
            chunk_id="test.core",
            parent_doc_id="test.doc",
            store_type="github.repos",
            document_id="doc",
            chunk_type="repo_core",
            content="Core",
            metadata={},
            sequence=1,
        )

        tech_chunk = DocumentChunk(
            chunk_id="test.tech",
            parent_doc_id="test.doc",
            store_type="github.repos",
            document_id="doc",
            chunk_type="repo_technical",
            content="Technical",
            metadata={},
            sequence=2,
        )

        hierarchy_type = self.analyzer._is_hierarchical_relationship(
            core_chunk, tech_chunk
        )
        assert hierarchy_type == "core_to_technical"

        # Test note hierarchy
        intro_chunk = DocumentChunk(
            chunk_id="notes.doc.intro",
            parent_doc_id="notes.doc",
            store_type="notes",
            document_id="doc",
            chunk_type="note_section",
            content="Introduction section",
            metadata={"title": "Introduction"},
            sequence=1,
        )

        setup_chunk = DocumentChunk(
            chunk_id="notes.doc.setup",
            parent_doc_id="notes.doc",
            store_type="notes",
            document_id="doc",
            chunk_type="note_section",
            content="Setup section",
            metadata={"title": "Setup Instructions"},
            sequence=2,
        )

        hierarchy_type = self.analyzer._is_hierarchical_relationship(
            intro_chunk, setup_chunk
        )
        assert hierarchy_type == "intro_to_content"

    def test_find_cross_document_relationships(self):
        """Test finding cross-document relationships."""
        chunks = [
            DocumentChunk(
                chunk_id="notes.doc1.ml",
                parent_doc_id="notes.doc1",
                store_type="notes",
                document_id="doc1",
                chunk_type="note_section",
                content="Machine learning notes",
                metadata={},
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="github.repos.ml-repo.core",
                parent_doc_id="github.repos.ml-repo",
                store_type="github.repos",
                document_id="ml-repo",
                chunk_type="repo_core",
                content="ML repository",
                metadata={},
                sequence=1,
            ),
        ]

        # High similarity between different documents
        similarity_matrix = np.array(
            [
                [1.0, 0.8],
                [0.8, 1.0],
            ]
        )

        cross_doc_rels = self.analyzer._find_cross_document_relationships(
            chunks, similarity_matrix
        )

        assert len(cross_doc_rels) == 1

        rel = cross_doc_rels[0]
        assert rel["type"] == "cross_document"
        assert rel["strength"] == 0.8
        assert rel["metadata"]["source_document"] == "notes.doc1"
        assert rel["metadata"]["target_document"] == "github.repos.ml-repo"
        assert rel["metadata"]["source_store"] == "notes"
        assert rel["metadata"]["target_store"] == "github.repos"

    @pytest.mark.asyncio
    async def test_analyze_chunk_relationships(self):
        """Test complete relationship analysis."""
        # Create test chunks
        chunks = [
            DocumentChunk(
                chunk_id="notes.guide.intro",
                parent_doc_id="notes.guide",
                store_type="notes",
                document_id="guide",
                chunk_type="note_section",
                content="Introduction to Python",
                metadata={"title": "Introduction"},
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="notes.guide.setup",
                parent_doc_id="notes.guide",
                store_type="notes",
                document_id="guide",
                chunk_type="note_section",
                content="Setting up Python environment",
                metadata={"title": "Setup"},
                sequence=2,
            ),
            DocumentChunk(
                chunk_id="github.repos.python-lib.core",
                parent_doc_id="github.repos.python-lib",
                store_type="github.repos",
                document_id="python-lib",
                chunk_type="repo_core",
                content="Python library for data science",
                metadata={},
                sequence=1,
            ),
        ]

        # Create embeddings with some similarities
        embeddings = [
            [1.0, 0.0, 0.0],  # intro
            [0.8, 0.6, 0.0],  # setup (similar to intro)
            [0.9, 0.0, 0.4],  # python-lib (similar to intro)
        ]

        # Analyze relationships
        result = await self.analyzer.analyze_chunk_relationships(
            chunks, embeddings, include_cross_document=True
        )

        # Verify result structure
        assert "chunks_analyzed" in result
        assert "relationships" in result
        assert "relationship_graph" in result
        assert "insights" in result
        assert "similarity_matrix" in result

        assert result["chunks_analyzed"] == 3

        # Check relationship types
        relationships = result["relationships"]
        assert "sequential" in relationships
        assert "topical" in relationships
        assert "hierarchical" in relationships
        assert "cross_document" in relationships

        # Should have sequential relationship between guide chunks
        sequential_rels = relationships["sequential"]
        assert len(sequential_rels) == 1
        assert sequential_rels[0]["source_chunk_id"] == "notes.guide.intro"
        assert sequential_rels[0]["target_chunk_id"] == "notes.guide.setup"

        # Check graph structure
        graph = result["relationship_graph"]
        assert "nodes" in graph
        assert "edges" in graph
        assert graph["node_count"] == 3
        assert len(graph["nodes"]) == 3

        # Check insights
        insights = result["insights"]
        assert "total_relationships" in insights
        assert "relationship_density" in insights
        assert "relationship_counts" in insights

    @pytest.mark.asyncio
    async def test_find_related_chunks(self):
        """Test finding related chunks for a target chunk."""
        # Mock relationship data
        relationship_data = {
            "relationships": {
                "sequential": [
                    {
                        "source_chunk_id": "chunk1",
                        "target_chunk_id": "chunk2",
                        "strength": 1.0,
                        "metadata": {},
                    }
                ],
                "topical": [
                    {
                        "source_chunk_id": "chunk1",
                        "target_chunk_id": "chunk3",
                        "strength": 0.8,
                        "metadata": {},
                    }
                ],
            }
        }

        related_chunks = await self.analyzer.find_related_chunks(
            "chunk1", relationship_data, max_related=5, min_strength=0.5
        )

        # Should find 2 related chunks
        assert len(related_chunks) == 2

        # Check chunk details
        chunk_ids = [chunk["chunk_id"] for chunk in related_chunks]
        assert "chunk2" in chunk_ids
        assert "chunk3" in chunk_ids

        # Should be sorted by strength (sequential=1.0, topical=0.8)
        assert related_chunks[0]["chunk_id"] == "chunk2"
        assert related_chunks[1]["chunk_id"] == "chunk3"

    def test_get_chunk_context_expansion(self):
        """Test chunk context expansion."""
        # Mock relationship data
        relationship_data = {
            "relationships": {
                "sequential": [
                    {
                        "source_chunk_id": "chunk1",
                        "target_chunk_id": "chunk2",
                        "strength": 1.0,
                    },
                    {
                        "source_chunk_id": "chunk2",
                        "target_chunk_id": "chunk3",
                        "strength": 1.0,
                    },
                ],
                "topical": [
                    {
                        "source_chunk_id": "chunk1",
                        "target_chunk_id": "chunk4",
                        "strength": 0.8,
                    },
                ],
            }
        }

        # Test expansion with radius 1
        expanded = self.analyzer.get_chunk_context_expansion(
            ["chunk1"], relationship_data, expansion_radius=1
        )

        # Should include original chunk plus direct neighbors
        expected = {"chunk1", "chunk2", "chunk4"}
        assert expanded == expected

        # Test expansion with radius 2
        expanded = self.analyzer.get_chunk_context_expansion(
            ["chunk1"], relationship_data, expansion_radius=2
        )

        # Should include chunk3 through chunk2
        expected = {"chunk1", "chunk2", "chunk3", "chunk4"}
        assert expanded == expected

    def test_build_relationship_graph(self):
        """Test building relationship graph structure."""
        chunks = [
            DocumentChunk(
                chunk_id="chunk1",
                parent_doc_id="doc1",
                store_type="notes",
                document_id="doc1",
                chunk_type="note_section",
                content="Content 1",
                metadata={"title": "Section 1"},
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="chunk2",
                parent_doc_id="doc1",
                store_type="notes",
                document_id="doc1",
                chunk_type="note_section",
                content="Content 2",
                metadata={"title": "Section 2"},
                sequence=2,
            ),
        ]

        relationships = {
            "sequential": [
                {
                    "source_chunk_id": "chunk1",
                    "target_chunk_id": "chunk2",
                    "strength": 1.0,
                    "metadata": {"type": "sequential"},
                }
            ]
        }

        graph = self.analyzer._build_relationship_graph(chunks, relationships)

        # Check graph structure
        assert graph["node_count"] == 2
        assert graph["edge_count"] == 1
        assert len(graph["edge_types"]) == 1
        assert "sequential" in graph["edge_types"]

        # Check nodes
        nodes = graph["nodes"]
        assert "chunk1" in nodes
        assert "chunk2" in nodes
        assert nodes["chunk1"]["chunk_type"] == "note_section"
        assert nodes["chunk1"]["title"] == "Section 1"

        # Check edges
        edges = graph["edges"]
        assert len(edges) == 1
        edge = edges[0]
        assert edge["source"] == "chunk1"
        assert edge["target"] == "chunk2"
        assert edge["type"] == "sequential"
        assert edge["strength"] == 1.0

    def test_generate_relationship_insights(self):
        """Test generating relationship insights."""
        chunks = [
            DocumentChunk(
                chunk_id="chunk1",
                parent_doc_id="doc1",
                store_type="notes",
                document_id="doc1",
                chunk_type="note_section",
                content="Content 1",
                metadata={},
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="chunk2",
                parent_doc_id="doc2",
                store_type="notes",
                document_id="doc2",
                chunk_type="note_section",
                content="Content 2",
                metadata={},
                sequence=1,
            ),
        ]

        relationships = {
            "topical": [
                {
                    "source_chunk_id": "chunk1",
                    "target_chunk_id": "chunk2",
                    "strength": 0.9,
                }
            ]
        }

        similarity_matrix = np.array(
            [
                [1.0, 0.9],
                [0.9, 1.0],
            ]
        )

        insights = self.analyzer._generate_relationship_insights(
            chunks, relationships, similarity_matrix
        )

        # Check insight structure
        assert "total_relationships" in insights
        assert "relationship_density" in insights
        assert "relationship_counts" in insights
        assert "most_connected_chunks" in insights
        assert "cross_document_relationships" in insights
        assert "average_similarity" in insights

        # Check values
        assert insights["total_relationships"] == 1
        assert insights["relationship_counts"]["topical"] == 1
        assert insights["average_similarity"] == 0.9

    def test_empty_chunks_handling(self):
        """Test handling of empty chunk lists."""
        # Test with empty embeddings should raise an error
        with pytest.raises((ValueError, np.exceptions.AxisError)):
            self.analyzer._calculate_similarity_matrix(np.array([]))

        # Test relationship finding with empty chunks
        empty_rels = self.analyzer._find_sequential_relationships([])
        assert empty_rels == []

        empty_rels = self.analyzer._find_topical_relationships([], np.array([]))
        assert empty_rels == []

    def test_similarity_threshold_configuration(self):
        """Test that similarity thresholds are properly configured."""
        thresholds = self.analyzer.similarity_thresholds

        # Check that thresholds are in descending order
        assert thresholds["strong"] > thresholds["moderate"]
        assert thresholds["moderate"] > thresholds["weak"]

        # Check reasonable values
        assert 0.0 <= thresholds["weak"] <= 1.0
        assert 0.0 <= thresholds["moderate"] <= 1.0
        assert 0.0 <= thresholds["strong"] <= 1.0
