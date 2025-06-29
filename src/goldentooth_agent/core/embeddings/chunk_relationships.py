"""Semantic chunk relationship analysis and cross-referencing."""

from collections import defaultdict
from typing import Any

import numpy as np
from antidote import inject, injectable

from .document_chunker import DocumentChunk
from .embeddings_service import EmbeddingsService


@injectable
class ChunkRelationshipAnalyzer:
    """Analyzes semantic relationships between document chunks."""

    def __init__(self, embeddings_service: EmbeddingsService = inject.me()) -> None:
        """Initialize the relationship analyzer.

        Args:
            embeddings_service: Service for creating embeddings
        """
        self.embeddings_service = embeddings_service

        # Thresholds for different relationship types
        self.similarity_thresholds = {
            "strong": 0.85,  # Very similar content/concepts
            "moderate": 0.70,  # Related concepts
            "weak": 0.55,  # Potentially related
        }

        # Relationship types
        self.relationship_types = {
            "sequential": "Sequential chunks from same document",
            "topical": "Similar topics or concepts",
            "reference": "Cross-references between documents",
            "hierarchical": "Parent-child content relationships",
            "supplementary": "Complementary information",
        }

    async def analyze_chunk_relationships(
        self,
        chunks: list[DocumentChunk],
        chunk_embeddings: list[list[float]],
        include_cross_document: bool = True,
    ) -> dict[str, Any]:
        """Analyze relationships between chunks.

        Args:
            chunks: List of document chunks to analyze
            chunk_embeddings: Corresponding embeddings for chunks
            include_cross_document: Whether to analyze relationships across documents

        Returns:
            Dictionary containing relationship analysis results
        """
        if len(chunks) != len(chunk_embeddings):
            raise ValueError("Chunks and embeddings lists must have same length")

        # Convert embeddings to numpy arrays for efficiency
        embeddings_matrix = np.array(chunk_embeddings)

        # Calculate similarity matrix
        similarity_matrix = self._calculate_similarity_matrix(embeddings_matrix)

        # Analyze different types of relationships
        relationships = {
            "sequential": self._find_sequential_relationships(chunks),
            "topical": self._find_topical_relationships(chunks, similarity_matrix),
            "hierarchical": self._find_hierarchical_relationships(chunks),
            "reference": [],  # Placeholder for future cross-reference detection
        }

        if include_cross_document:
            relationships["cross_document"] = self._find_cross_document_relationships(
                chunks, similarity_matrix
            )

        # Build relationship graph
        relationship_graph = self._build_relationship_graph(chunks, relationships)

        # Generate insights
        insights = self._generate_relationship_insights(
            chunks, relationships, similarity_matrix
        )

        return {
            "chunks_analyzed": len(chunks),
            "relationships": relationships,
            "relationship_graph": relationship_graph,
            "insights": insights,
            "similarity_matrix": similarity_matrix.tolist(),
        }

    def _calculate_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity matrix between embeddings."""
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / np.maximum(norms, 1e-8)  # Avoid division by zero

        # Calculate cosine similarity matrix
        similarity_matrix = np.dot(normalized, normalized.T)

        return similarity_matrix

    def _find_sequential_relationships(
        self, chunks: list[DocumentChunk]
    ) -> list[dict[str, Any]]:
        """Find sequential relationships (adjacent chunks in same document)."""
        relationships = []

        # Group chunks by parent document
        doc_chunks = defaultdict(list)
        for i, chunk in enumerate(chunks):
            doc_chunks[chunk.parent_doc_id].append((i, chunk))

        # Find sequential relationships within each document
        for doc_id, doc_chunk_list in doc_chunks.items():
            # Sort by sequence number
            doc_chunk_list.sort(key=lambda x: x[1].sequence)

            # Connect adjacent chunks
            for i in range(len(doc_chunk_list) - 1):
                curr_idx, curr_chunk = doc_chunk_list[i]
                next_idx, next_chunk = doc_chunk_list[i + 1]

                relationships.append(
                    {
                        "type": "sequential",
                        "source_chunk_id": curr_chunk.chunk_id,
                        "target_chunk_id": next_chunk.chunk_id,
                        "source_index": curr_idx,
                        "target_index": next_idx,
                        "strength": 1.0,  # Sequential relationships are always strong
                        "metadata": {
                            "document_id": doc_id,
                            "sequence_gap": next_chunk.sequence - curr_chunk.sequence,
                        },
                    }
                )

        return relationships

    def _find_topical_relationships(
        self, chunks: list[DocumentChunk], similarity_matrix: np.ndarray
    ) -> list[dict[str, Any]]:
        """Find topical relationships based on semantic similarity."""
        relationships = []

        for i in range(len(chunks)):
            for j in range(i + 1, len(chunks)):
                similarity = similarity_matrix[i, j]

                # Skip if chunks are from same document (handled by sequential)
                if chunks[i].parent_doc_id == chunks[j].parent_doc_id:
                    continue

                # Determine relationship strength
                strength_category = None
                if similarity >= self.similarity_thresholds["strong"]:
                    strength_category = "strong"
                elif similarity >= self.similarity_thresholds["moderate"]:
                    strength_category = "moderate"
                elif similarity >= self.similarity_thresholds["weak"]:
                    strength_category = "weak"

                if strength_category:
                    relationships.append(
                        {
                            "type": "topical",
                            "source_chunk_id": chunks[i].chunk_id,
                            "target_chunk_id": chunks[j].chunk_id,
                            "source_index": i,
                            "target_index": j,
                            "strength": float(similarity),
                            "strength_category": strength_category,
                            "metadata": {
                                "chunk_types": [
                                    chunks[i].chunk_type,
                                    chunks[j].chunk_type,
                                ],
                                "different_stores": chunks[i].store_type
                                != chunks[j].store_type,
                            },
                        }
                    )

        return relationships

    def _find_hierarchical_relationships(
        self, chunks: list[DocumentChunk]
    ) -> list[dict[str, Any]]:
        """Find hierarchical relationships (parent-child content structures)."""
        relationships = []

        # Group chunks by document and analyze within-document hierarchy
        doc_chunks = defaultdict(list)
        for i, chunk in enumerate(chunks):
            doc_chunks[chunk.parent_doc_id].append((i, chunk))

        for doc_id, doc_chunk_list in doc_chunks.items():
            # Look for hierarchical patterns based on chunk types and titles
            for i, (idx_i, chunk_i) in enumerate(doc_chunk_list):
                for j, (idx_j, chunk_j) in enumerate(doc_chunk_list):
                    if i == j:
                        continue

                    # Check for hierarchical patterns
                    is_hierarchical = self._is_hierarchical_relationship(
                        chunk_i, chunk_j
                    )

                    if is_hierarchical:
                        relationships.append(
                            {
                                "type": "hierarchical",
                                "source_chunk_id": chunk_i.chunk_id,
                                "target_chunk_id": chunk_j.chunk_id,
                                "source_index": idx_i,
                                "target_index": idx_j,
                                "strength": 0.8,  # Hierarchical relationships are strong
                                "metadata": {
                                    "hierarchy_type": is_hierarchical,
                                    "document_id": doc_id,
                                },
                            }
                        )

        return relationships

    def _find_cross_document_relationships(
        self, chunks: list[DocumentChunk], similarity_matrix: np.ndarray
    ) -> list[dict[str, Any]]:
        """Find relationships that span across different documents."""
        relationships = []

        # Find high-similarity chunks from different documents
        for i in range(len(chunks)):
            for j in range(i + 1, len(chunks)):
                if chunks[i].parent_doc_id == chunks[j].parent_doc_id:
                    continue  # Same document

                similarity = similarity_matrix[i, j]

                # Only include strong cross-document relationships
                if similarity >= self.similarity_thresholds["moderate"]:
                    relationships.append(
                        {
                            "type": "cross_document",
                            "source_chunk_id": chunks[i].chunk_id,
                            "target_chunk_id": chunks[j].chunk_id,
                            "source_index": i,
                            "target_index": j,
                            "strength": float(similarity),
                            "metadata": {
                                "source_document": chunks[i].parent_doc_id,
                                "target_document": chunks[j].parent_doc_id,
                                "source_store": chunks[i].store_type,
                                "target_store": chunks[j].store_type,
                                "chunk_types": [
                                    chunks[i].chunk_type,
                                    chunks[j].chunk_type,
                                ],
                            },
                        }
                    )

        return relationships

    def _is_hierarchical_relationship(
        self, chunk_a: DocumentChunk, chunk_b: DocumentChunk
    ) -> str | None:
        """Check if two chunks have a hierarchical relationship."""
        # Check chunk types for hierarchy
        if chunk_a.chunk_type == "repo_core" and chunk_b.chunk_type == "repo_technical":
            return "core_to_technical"
        elif (
            chunk_a.chunk_type == "repo_core" and chunk_b.chunk_type == "repo_activity"
        ):
            return "core_to_activity"

        # Check title hierarchy for notes
        if (
            chunk_a.chunk_type == "note_section"
            and chunk_b.chunk_type == "note_section"
        ):
            title_a = chunk_a.metadata.get("title", "")
            title_b = chunk_b.metadata.get("title", "")

            # Simple hierarchy detection based on title patterns
            if "introduction" in title_a.lower() and any(
                word in title_b.lower() for word in ["setup", "usage", "example"]
            ):
                return "intro_to_content"
            elif "overview" in title_a.lower() and "detail" in title_b.lower():
                return "overview_to_detail"

        return None

    def _build_relationship_graph(
        self,
        chunks: list[DocumentChunk],
        relationships: dict[str, list[dict[str, Any]]],
    ) -> dict[str, Any]:
        """Build a graph representation of chunk relationships."""
        # Create nodes for each chunk
        nodes = {}
        for i, chunk in enumerate(chunks):
            nodes[chunk.chunk_id] = {
                "index": i,
                "chunk_type": chunk.chunk_type,
                "parent_document": chunk.parent_doc_id,
                "store_type": chunk.store_type,
                "sequence": chunk.sequence,
                "content_length": len(chunk.content),
                "title": chunk.metadata.get("title", ""),
            }

        # Create edges from relationships
        edges = []
        edge_types = set()

        for rel_type, rel_list in relationships.items():
            for relationship in rel_list:
                edge = {
                    "source": relationship["source_chunk_id"],
                    "target": relationship["target_chunk_id"],
                    "type": rel_type,
                    "strength": relationship["strength"],
                    "metadata": relationship.get("metadata", {}),
                }
                edges.append(edge)
                edge_types.add(rel_type)

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "edge_types": list(edge_types),
        }

    def _generate_relationship_insights(
        self,
        chunks: list[DocumentChunk],
        relationships: dict[str, list[dict[str, Any]]],
        similarity_matrix: np.ndarray,
    ) -> dict[str, Any]:
        """Generate insights about chunk relationships."""
        total_relationships = sum(len(rel_list) for rel_list in relationships.values())

        # Calculate relationship density
        max_possible_relationships = len(chunks) * (len(chunks) - 1) // 2
        relationship_density = (
            total_relationships / max_possible_relationships
            if max_possible_relationships > 0
            else 0
        )

        # Find most connected chunks
        chunk_connections = defaultdict(int)
        for rel_list in relationships.values():
            for rel in rel_list:
                chunk_connections[rel["source_chunk_id"]] += 1
                chunk_connections[rel["target_chunk_id"]] += 1

        most_connected = sorted(
            chunk_connections.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Analyze cross-document connections
        cross_doc_count = len(relationships.get("cross_document", []))

        # Calculate average similarity
        upper_triangle_indices = np.triu_indices_from(similarity_matrix, k=1)
        similarities = similarity_matrix[upper_triangle_indices]
        avg_similarity = float(np.mean(similarities)) if len(similarities) > 0 else 0.0

        return {
            "total_relationships": total_relationships,
            "relationship_density": relationship_density,
            "relationship_counts": {
                rel_type: len(rel_list) for rel_type, rel_list in relationships.items()
            },
            "most_connected_chunks": most_connected,
            "cross_document_relationships": cross_doc_count,
            "average_similarity": avg_similarity,
            "highly_similar_pairs": int(
                np.sum(similarities >= self.similarity_thresholds["strong"])
            ),
            "moderately_similar_pairs": int(
                np.sum(similarities >= self.similarity_thresholds["moderate"])
            ),
        }

    async def find_related_chunks(
        self,
        target_chunk_id: str,
        relationship_data: dict[str, Any],
        max_related: int = 10,
        min_strength: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Find chunks related to a target chunk.

        Args:
            target_chunk_id: ID of chunk to find relationships for
            relationship_data: Output from analyze_chunk_relationships
            max_related: Maximum number of related chunks to return
            min_strength: Minimum relationship strength to include

        Returns:
            List of related chunks with relationship metadata
        """
        related_chunks = []

        # Search through all relationship types
        for rel_type, rel_list in relationship_data["relationships"].items():
            for relationship in rel_list:
                if relationship["strength"] < min_strength:
                    continue

                related_chunk_id = None
                if relationship["source_chunk_id"] == target_chunk_id:
                    related_chunk_id = relationship["target_chunk_id"]
                elif relationship["target_chunk_id"] == target_chunk_id:
                    related_chunk_id = relationship["source_chunk_id"]

                if related_chunk_id:
                    related_chunks.append(
                        {
                            "chunk_id": related_chunk_id,
                            "relationship_type": rel_type,
                            "strength": relationship["strength"],
                            "metadata": relationship.get("metadata", {}),
                        }
                    )

        # Sort by strength and limit results
        related_chunks.sort(key=lambda x: x["strength"], reverse=True)
        return related_chunks[:max_related]

    def get_chunk_context_expansion(
        self,
        chunk_ids: list[str],
        relationship_data: dict[str, Any],
        expansion_radius: int = 1,
    ) -> set[str]:
        """Expand a set of chunks to include related chunks.

        Args:
            chunk_ids: Initial set of chunk IDs
            relationship_data: Relationship analysis data
            expansion_radius: How many relationship hops to include

        Returns:
            Expanded set of chunk IDs including related chunks
        """
        expanded_chunks = set(chunk_ids)
        current_chunks = set(chunk_ids)

        for _ in range(expansion_radius):
            next_chunks = set()

            for chunk_id in current_chunks:
                # Find all chunks related to this one
                for rel_type, rel_list in relationship_data["relationships"].items():
                    for relationship in rel_list:
                        if relationship["source_chunk_id"] == chunk_id:
                            next_chunks.add(relationship["target_chunk_id"])
                        elif relationship["target_chunk_id"] == chunk_id:
                            next_chunks.add(relationship["source_chunk_id"])

            # Add new chunks to expanded set
            new_chunks = next_chunks - expanded_chunks
            if not new_chunks:
                break  # No new chunks found

            expanded_chunks.update(new_chunks)
            current_chunks = new_chunks

        return expanded_chunks
