"""Intelligent chunk fusion for multi-chunk answer generation.

This module provides advanced functionality for combining information from multiple
document chunks into coherent, comprehensive answers. It includes:

- Chunk coherence scoring and relevance analysis
- Answer synthesis with context blending
- Deduplication and information consolidation
- Confidence scoring for fused answers
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from goldentooth_agent.core.embeddings.models import Chunk, SearchResult


@dataclass
class ChunkCluster:
    """A cluster of related chunks that can be fused together."""

    chunks: list[Chunk]
    relevance_scores: dict[str, float]  # chunk_id -> relevance score
    topic_coherence: float = 0.0
    temporal_coherence: float = 0.0
    semantic_density: float = 0.0

    @property
    def average_relevance(self) -> float:
        """Get average relevance score across all chunks."""
        if not self.relevance_scores:
            return 0.0
        return sum(self.relevance_scores.values()) / len(self.relevance_scores)

    @property
    def chunk_ids(self) -> set[str]:
        """Get set of chunk IDs in this cluster."""
        return {chunk.chunk_id for chunk in self.chunks}


@dataclass
class FusedAnswer:
    """A synthesized answer created from multiple chunks."""

    content: str
    source_chunks: list[Chunk]
    confidence_score: float
    coherence_score: float
    completeness_score: float
    key_points: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def num_sources(self) -> int:
        """Get number of source chunks used."""
        return len(self.source_chunks)

    @property
    def source_documents(self) -> set[str]:
        """Get unique source document IDs."""
        return {chunk.document_id for chunk in self.source_chunks}


class ChunkFusion:
    """Intelligent chunk fusion for creating comprehensive answers from multiple chunks."""

    def __init__(
        self,
        coherence_threshold: float = 0.6,
        min_chunks_for_fusion: int = 2,
        max_chunks_for_fusion: int = 10,
        deduplication_threshold: float = 0.8,
        completeness_weight: float = 0.3,
        coherence_weight: float = 0.4,
        relevance_weight: float = 0.3,
    ) -> None:
        """Initialize chunk fusion engine.

        Args:
            coherence_threshold: Minimum coherence score for chunk clustering
            min_chunks_for_fusion: Minimum chunks needed to attempt fusion
            max_chunks_for_fusion: Maximum chunks to consider for fusion
            deduplication_threshold: Similarity threshold for deduplication
            completeness_weight: Weight for completeness in final score
            coherence_weight: Weight for coherence in final score
            relevance_weight: Weight for relevance in final score
        """
        self.coherence_threshold = coherence_threshold
        self.min_chunks_for_fusion = min_chunks_for_fusion
        self.max_chunks_for_fusion = max_chunks_for_fusion
        self.deduplication_threshold = deduplication_threshold
        self.completeness_weight = completeness_weight
        self.coherence_weight = coherence_weight
        self.relevance_weight = relevance_weight

    def fuse_chunks(
        self, search_results: list[SearchResult], query: str, max_clusters: int = 3
    ) -> list[FusedAnswer]:
        """Fuse multiple chunks into coherent answers.

        Args:
            search_results: Search results containing chunks to fuse
            query: Original query for context
            max_clusters: Maximum number of answer clusters to create

        Returns:
            List of fused answers sorted by confidence
        """
        if len(search_results) < self.min_chunks_for_fusion:
            # Not enough chunks for fusion
            return []

        # Limit chunks to maximum
        chunks_to_fuse = search_results[: self.max_chunks_for_fusion]

        # Create chunk clusters based on coherence
        clusters = self._cluster_chunks(chunks_to_fuse, query)

        # Limit to max clusters
        clusters = clusters[:max_clusters]

        # Synthesize answers from clusters
        fused_answers = []
        for cluster in clusters:
            answer = self._synthesize_answer(cluster, query)
            if answer:
                fused_answers.append(answer)

        # Sort by confidence score
        fused_answers.sort(key=lambda a: a.confidence_score, reverse=True)

        return fused_answers

    def _cluster_chunks(
        self, search_results: list[SearchResult], query: str
    ) -> list[ChunkCluster]:
        """Cluster chunks based on coherence and relevance.

        Args:
            search_results: Chunks to cluster
            query: Query for context

        Returns:
            List of chunk clusters
        """
        clusters = []
        used_chunks = set()

        for result in search_results:
            if result.chunk.chunk_id in used_chunks:
                continue

            # Start new cluster with this chunk
            cluster_chunks = [result.chunk]
            relevance_scores = {result.chunk.chunk_id: result.relevance_score}
            used_chunks.add(result.chunk.chunk_id)

            # Find coherent chunks to add to cluster
            for other_result in search_results:
                if other_result.chunk.chunk_id in used_chunks:
                    continue

                coherence = self._calculate_coherence(
                    result.chunk, other_result.chunk, query
                )

                if coherence >= self.coherence_threshold:
                    cluster_chunks.append(other_result.chunk)
                    relevance_scores[other_result.chunk.chunk_id] = (
                        other_result.relevance_score
                    )
                    used_chunks.add(other_result.chunk.chunk_id)

            if len(cluster_chunks) >= self.min_chunks_for_fusion:
                cluster = ChunkCluster(
                    chunks=cluster_chunks,
                    relevance_scores=relevance_scores,
                    topic_coherence=self._calculate_topic_coherence(cluster_chunks),
                    temporal_coherence=self._calculate_temporal_coherence(
                        cluster_chunks
                    ),
                    semantic_density=self._calculate_semantic_density(
                        cluster_chunks, query
                    ),
                )
                clusters.append(cluster)

        # Sort clusters by quality
        clusters.sort(
            key=lambda c: (
                c.average_relevance * c.topic_coherence * c.semantic_density
            ),
            reverse=True,
        )

        return clusters

    def _calculate_coherence(self, chunk1: Chunk, chunk2: Chunk, query: str) -> float:
        """Calculate coherence between two chunks.

        Args:
            chunk1: First chunk
            chunk2: Second chunk
            query: Query for context

        Returns:
            Coherence score between 0 and 1
        """
        score = 0.0

        # Document coherence - same document or related documents
        if chunk1.document_id == chunk2.document_id:
            score += 0.3

            # Adjacent chunks get bonus
            if abs(chunk1.position - chunk2.position) == 1:
                score += 0.2
            # Nearby chunks get smaller bonus
            elif abs(chunk1.position - chunk2.position) <= 3:
                score += 0.1

        # Metadata coherence
        common_metadata = set(chunk1.metadata.keys()) & set(chunk2.metadata.keys())
        for key in common_metadata:
            if chunk1.metadata[key] == chunk2.metadata[key]:
                score += 0.1

        # Content overlap (simple word-based)
        words1 = set(chunk1.content.lower().split())
        words2 = set(chunk2.content.lower().split())
        query_words = set(query.lower().split())

        # Common words related to query
        common_query_words = (words1 & words2) & query_words
        if common_query_words:
            score += min(0.3, len(common_query_words) * 0.15)

        # Overall content overlap
        if words1 and words2:
            overlap = len(words1 & words2) / min(len(words1), len(words2))
            score += overlap * 0.3

        # Boost for common important words
        important_words = words1 & words2
        if important_words:
            # Filter out common stop words
            stop_words = {
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "is",
                "are",
                "was",
                "were",
                "be",
                "been",
                "being",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
            }
            meaningful_overlap = important_words - stop_words
            if meaningful_overlap:
                score += min(0.2, len(meaningful_overlap) * 0.05)

        return min(1.0, score)

    def _calculate_topic_coherence(self, chunks: list[Chunk]) -> float:
        """Calculate topic coherence across chunks.

        Args:
            chunks: Chunks to analyze

        Returns:
            Topic coherence score between 0 and 1
        """
        if len(chunks) < 2:
            return 1.0

        # Extract key terms from all chunks
        all_words = []
        for chunk in chunks:
            words = chunk.content.lower().split()
            all_words.extend(words)

        # Calculate term frequency
        word_freq: dict[str, int] = defaultdict(int)
        for word in all_words:
            if len(word) > 3:  # Skip short words
                word_freq[word] += 1

        # Find common terms across chunks
        common_terms = 0
        total_unique_terms = len(word_freq)

        for _word, freq in word_freq.items():
            if freq >= len(chunks) * 0.4:  # Term appears in at least 40% of chunks
                common_terms += 1

        # Calculate coherence based on common terms ratio
        if not word_freq:
            return 0.5

        # Base coherence on proportion of common terms
        if total_unique_terms == 0:
            return 0.5

        base_coherence = common_terms / total_unique_terms

        # Boost for higher frequency terms
        high_freq_terms = sum(
            1 for freq in word_freq.values() if freq >= len(chunks) * 0.6
        )
        freq_boost = min(0.3, high_freq_terms / total_unique_terms)

        coherence = min(1.0, base_coherence * 2.0 + freq_boost)
        return coherence

    def _calculate_temporal_coherence(self, chunks: list[Chunk]) -> float:
        """Calculate temporal coherence for chunks.

        Args:
            chunks: Chunks to analyze

        Returns:
            Temporal coherence score between 0 and 1
        """
        # Group chunks by document
        doc_chunks = defaultdict(list)
        for chunk in chunks:
            doc_chunks[chunk.document_id].append(chunk)

        coherence_scores = []

        for _doc_id, doc_chunk_list in doc_chunks.items():
            if len(doc_chunk_list) < 2:
                coherence_scores.append(1.0)
                continue

            # Sort by position
            sorted_chunks = sorted(doc_chunk_list, key=lambda c: c.position)

            # Calculate position gaps
            gaps = []
            for i in range(1, len(sorted_chunks)):
                gap = sorted_chunks[i].position - sorted_chunks[i - 1].position
                gaps.append(gap)

            # Score based on gaps (smaller gaps = higher coherence)
            if gaps:
                avg_gap = sum(gaps) / len(gaps)
                # Exponential decay for larger gaps
                coherence = np.exp(-avg_gap / 5.0)
                coherence_scores.append(coherence)
            else:
                coherence_scores.append(1.0)

        return (
            sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5
        )

    def _calculate_semantic_density(self, chunks: list[Chunk], query: str) -> float:
        """Calculate semantic density relative to query.

        Args:
            chunks: Chunks to analyze
            query: Query for context

        Returns:
            Semantic density score between 0 and 1
        """
        query_words = set(query.lower().split())

        # Calculate query term coverage across chunks
        covered_terms = set()
        total_content_length = 0

        for chunk in chunks:
            chunk_words = set(chunk.content.lower().split())
            covered_terms.update(chunk_words & query_words)
            total_content_length += len(chunk.content)

        # Density factors
        coverage = len(covered_terms) / len(query_words) if query_words else 0

        # Information density (avoid too verbose or too brief)
        avg_chunk_length = total_content_length / len(chunks)
        optimal_length = 200  # Optimal chunk length in characters
        length_factor = 1.0 - abs(avg_chunk_length - optimal_length) / (
            optimal_length * 2
        )
        length_factor = max(0, length_factor)

        # Combine factors
        density = coverage * 0.7 + length_factor * 0.3

        return density

    def _synthesize_answer(
        self, cluster: ChunkCluster, query: str
    ) -> FusedAnswer | None:
        """Synthesize a coherent answer from a chunk cluster.

        Args:
            cluster: Chunk cluster to synthesize
            query: Original query

        Returns:
            Fused answer or None if synthesis fails
        """
        if not cluster.chunks:
            return None

        # Extract key information from chunks
        key_points = self._extract_key_points(cluster.chunks, query)

        # Detect contradictions
        contradictions = self._detect_contradictions(cluster.chunks)

        # Build synthesized content
        content = self._build_content(cluster.chunks, key_points, query)

        # Calculate quality scores
        completeness = self._calculate_completeness(key_points, query)
        coherence = cluster.topic_coherence * cluster.temporal_coherence
        relevance = cluster.average_relevance

        # Calculate overall confidence
        confidence = (
            completeness * self.completeness_weight
            + coherence * self.coherence_weight
            + relevance * self.relevance_weight
        )

        # Build metadata
        metadata = {
            "num_chunks": len(cluster.chunks),
            "chunk_positions": [c.position for c in cluster.chunks],
            "documents": list(cluster.chunk_ids),
            "topic_coherence": cluster.topic_coherence,
            "temporal_coherence": cluster.temporal_coherence,
            "semantic_density": cluster.semantic_density,
        }

        return FusedAnswer(
            content=content,
            source_chunks=cluster.chunks,
            confidence_score=confidence,
            coherence_score=coherence,
            completeness_score=completeness,
            key_points=key_points,
            contradictions=contradictions,
            metadata=metadata,
        )

    def _extract_key_points(self, chunks: list[Chunk], query: str) -> list[str]:
        """Extract key points from chunks.

        Args:
            chunks: Chunks to analyze
            query: Query for context

        Returns:
            List of key points
        """
        key_points: list[str] = []
        query_words = set(query.lower().split())

        for chunk in chunks:
            # Find sentences containing query terms
            sentences = chunk.content.split(".")
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                sentence_words = set(sentence.lower().split())
                if sentence_words & query_words:
                    # Deduplicate similar points
                    is_duplicate = False
                    for existing_point in key_points:
                        if (
                            self._calculate_similarity(sentence, existing_point)
                            > self.deduplication_threshold
                        ):
                            is_duplicate = True
                            break

                    if not is_duplicate and len(sentence) > 20:
                        key_points.append(sentence)

        return key_points[:10]  # Limit to top 10 points

    def _detect_contradictions(self, chunks: list[Chunk]) -> list[str]:
        """Detect potential contradictions between chunks.

        Args:
            chunks: Chunks to analyze

        Returns:
            List of detected contradictions
        """
        contradictions = []

        # Simple contradiction detection based on negations
        for i, chunk1 in enumerate(chunks):
            for chunk2 in chunks[i + 1 :]:
                sentences1 = [s.strip() for s in chunk1.content.split(".") if s.strip()]
                sentences2 = [s.strip() for s in chunk2.content.split(".") if s.strip()]

                for s1 in sentences1:
                    for s2 in sentences2:
                        if self._are_contradictory(s1, s2):
                            contradiction = f"Potential contradiction: '{s1}' vs '{s2}'"
                            contradictions.append(contradiction)

        return contradictions[:5]  # Limit to top 5 contradictions

    def _are_contradictory(self, sentence1: str, sentence2: str) -> bool:
        """Check if two sentences are potentially contradictory.

        Args:
            sentence1: First sentence
            sentence2: Second sentence

        Returns:
            True if potentially contradictory
        """
        # Simple heuristic: check for negation patterns
        negation_words = {
            "not",
            "no",
            "never",
            "none",
            "neither",
            "nor",
            "don't",
            "doesn't",
            "didn't",
            "won't",
            "wouldn't",
            "can't",
            "couldn't",
        }

        words1 = set(sentence1.lower().split())
        words2 = set(sentence2.lower().split())

        # High overlap but different negation
        overlap = words1 & words2
        if len(overlap) < 3:
            return False

        has_negation1 = bool(words1 & negation_words)
        has_negation2 = bool(words2 & negation_words)

        # One has negation, other doesn't
        if has_negation1 != has_negation2:
            return True

        return False

    def _build_content(
        self, chunks: list[Chunk], key_points: list[str], query: str
    ) -> str:
        """Build synthesized content from chunks and key points.

        Args:
            chunks: Source chunks
            key_points: Extracted key points
            query: Original query

        Returns:
            Synthesized content
        """
        # Sort chunks by position within documents
        sorted_chunks = sorted(chunks, key=lambda c: (c.document_id, c.position))

        # Build content sections
        sections = []

        # Add introduction if we have multiple sources
        unique_docs = {c.document_id for c in chunks}
        if len(unique_docs) > 1:
            intro = f"Based on information from {len(unique_docs)} sources regarding '{query}':\n"
            sections.append(intro)

        # Add key points if extracted
        if key_points:
            sections.append("Key Information:")
            for i, point in enumerate(key_points, 1):
                sections.append(f"{i}. {point}")
            sections.append("")  # Empty line

        # Add detailed information from chunks
        sections.append("Detailed Context:")

        current_doc = None
        for chunk in sorted_chunks:
            # Add document separator if switching documents
            if chunk.document_id != current_doc:
                current_doc = chunk.document_id
                if chunk.metadata.get("title"):
                    sections.append(f"\nFrom '{chunk.metadata['title']}':")
                else:
                    sections.append(f"\nFrom document {chunk.document_id}:")

            # Add chunk content with position indicator
            sections.append(f"[Section {chunk.position}] {chunk.content}")

        return "\n".join(sections)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def _calculate_completeness(self, key_points: list[str], query: str) -> float:
        """Calculate answer completeness relative to query.

        Args:
            key_points: Extracted key points
            query: Original query

        Returns:
            Completeness score between 0 and 1
        """
        if not key_points:
            return 0.0

        query_words = set(query.lower().split())
        covered_words = set()

        # Check query term coverage in key points
        for point in key_points:
            point_words = set(point.lower().split())
            covered_words.update(point_words & query_words)

        coverage = len(covered_words) / len(query_words) if query_words else 0.0

        # Factor in number of key points (more is generally better up to a point)
        point_factor = min(1.0, len(key_points) / 5.0)

        completeness = coverage * 0.7 + point_factor * 0.3

        return completeness
