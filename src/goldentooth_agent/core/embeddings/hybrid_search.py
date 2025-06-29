"""Hybrid search engine combining semantic similarity and BM25 keyword scoring."""

import math
import re
from collections import Counter, defaultdict
from typing import Any

from antidote import inject, injectable

from .embeddings_service import EmbeddingsService
from .vector_store import VectorStore


@injectable
class HybridSearchEngine:
    """Hybrid search engine combining semantic and keyword-based retrieval."""

    def __init__(
        self,
        vector_store: VectorStore = inject.me(),
        embeddings_service: EmbeddingsService = inject.me(),
    ) -> None:
        """Initialize the hybrid search engine.

        Args:
            vector_store: Vector store for semantic search
            embeddings_service: Service for creating embeddings
        """
        self.vector_store = vector_store
        self.embeddings_service = embeddings_service

        # BM25 parameters
        self.k1 = 1.5  # Term frequency saturation parameter
        self.b = 0.75  # Length normalization parameter

        # Hybrid scoring weights
        self.semantic_weight = 0.7  # Weight for semantic similarity
        self.keyword_weight = 0.3  # Weight for BM25 keyword score

        # Document corpus for BM25 (cached)
        self._document_corpus = None
        self._corpus_stats = None
        self._term_frequencies = None
        self._document_lengths = None

        # Text preprocessing
        self.stop_words = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "has",
            "he",
            "in",
            "is",
            "it",
            "its",
            "of",
            "on",
            "that",
            "the",
            "to",
            "was",
            "will",
            "with",
            "this",
            "but",
            "they",
            "have",
            "had",
            "what",
            "said",
            "each",
            "which",
            "she",
            "do",
            "how",
            "their",
            "if",
            "up",
            "out",
            "many",
            "then",
            "them",
            "these",
            "so",
            "some",
            "her",
            "would",
            "make",
            "like",
            "into",
            "him",
            "time",
            "two",
            "more",
            "go",
            "no",
            "way",
            "could",
            "my",
            "than",
            "first",
            "been",
            "call",
            "who",
            "oil",
            "sit",
            "now",
            "find",
            "down",
            "day",
            "did",
            "get",
            "come",
            "made",
            "may",
            "part",
        }

    async def hybrid_search(
        self,
        query: str,
        max_results: int = 10,
        store_type: str = None,
        include_chunks: bool = True,
        semantic_weight: float = None,
        keyword_weight: float = None,
        min_semantic_score: float = 0.1,
        min_keyword_score: float = 0.0,
        boost_exact_matches: bool = True,
        boost_title_matches: bool = True,
    ) -> list[dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword scoring.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            store_type: Optional store type filter
            include_chunks: Whether to include chunk results
            semantic_weight: Weight for semantic similarity (0.0-1.0)
            keyword_weight: Weight for keyword scoring (0.0-1.0)
            min_semantic_score: Minimum semantic similarity threshold
            min_keyword_score: Minimum keyword score threshold
            boost_exact_matches: Whether to boost exact phrase matches
            boost_title_matches: Whether to boost title/metadata matches

        Returns:
            List of search results with combined scores
        """
        # Use configured weights if not provided
        if semantic_weight is None:
            semantic_weight = self.semantic_weight
        if keyword_weight is None:
            keyword_weight = self.keyword_weight

        # Normalize weights
        total_weight = semantic_weight + keyword_weight
        if total_weight > 0:
            semantic_weight = semantic_weight / total_weight
            keyword_weight = keyword_weight / total_weight

        # Get semantic search results
        semantic_results = await self._get_semantic_results(
            query, max_results * 2, store_type, include_chunks, min_semantic_score
        )

        # Get keyword search results
        keyword_results = await self._get_keyword_results(
            query, max_results * 2, store_type, include_chunks, min_keyword_score
        )

        # Combine and score results
        combined_results = self._combine_results(
            query,
            semantic_results,
            keyword_results,
            semantic_weight,
            keyword_weight,
            boost_exact_matches,
            boost_title_matches,
        )

        # Sort by combined score and return top results
        combined_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return combined_results[:max_results]

    async def _get_semantic_results(
        self,
        query: str,
        limit: int,
        store_type: str,
        include_chunks: bool,
        min_score: float,
    ) -> list[dict[str, Any]]:
        """Get semantic search results using vector similarity."""
        try:
            # Create query embedding
            query_embedding = await self.embeddings_service.create_embedding(query)

            # Perform vector search
            results = self.vector_store.search_similar(
                query_embedding,
                limit=limit,
                store_type=store_type,
                include_chunks=include_chunks,
                similarity_threshold=min_score,
            )

            # Add search method metadata
            for result in results:
                result["search_method"] = "semantic"
                result["semantic_score"] = result.get("similarity_score", 0.0)

            return results

        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    async def _get_keyword_results(
        self,
        query: str,
        limit: int,
        store_type: str,
        include_chunks: bool,
        min_score: float,
    ) -> list[dict[str, Any]]:
        """Get keyword search results using BM25 scoring."""
        try:
            # Build document corpus if not cached
            await self._build_corpus_if_needed(store_type, include_chunks)

            if not self._document_corpus:
                return []

            # Calculate BM25 scores for query
            bm25_scores = self._calculate_bm25_scores(query)

            # Convert to result format
            results = []
            for doc_id, score in bm25_scores:
                if score < min_score:
                    continue

                # Get document details from corpus
                doc_info = self._document_corpus.get(doc_id)
                if doc_info:
                    result = {
                        **doc_info,
                        "search_method": "keyword",
                        "keyword_score": score,
                        "similarity_score": score,  # For compatibility
                    }
                    results.append(result)

                if len(results) >= limit:
                    break

            return results

        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []

    def _combine_results(
        self,
        query: str,
        semantic_results: list[dict[str, Any]],
        keyword_results: list[dict[str, Any]],
        semantic_weight: float,
        keyword_weight: float,
        boost_exact_matches: bool,
        boost_title_matches: bool,
    ) -> list[dict[str, Any]]:
        """Combine semantic and keyword results with hybrid scoring."""
        # Create lookup for efficient combining
        results_map = {}

        # Add semantic results
        for result in semantic_results:
            doc_id = self._get_doc_id(result)
            results_map[doc_id] = {
                **result,
                "semantic_score": result.get("semantic_score", 0.0),
                "keyword_score": 0.0,
            }

        # Add keyword results
        for result in keyword_results:
            doc_id = self._get_doc_id(result)
            if doc_id in results_map:
                # Update existing result
                results_map[doc_id]["keyword_score"] = result.get("keyword_score", 0.0)
                # Keep the richer metadata from semantic results
            else:
                # Add new result
                results_map[doc_id] = {
                    **result,
                    "semantic_score": 0.0,
                    "keyword_score": result.get("keyword_score", 0.0),
                }

        # Calculate hybrid scores
        combined_results = []
        for doc_id, result in results_map.items():
            semantic_score = result["semantic_score"]
            keyword_score = result["keyword_score"]

            # Base hybrid score
            hybrid_score = (
                semantic_weight * semantic_score + keyword_weight * keyword_score
            )

            # Apply boosting
            if boost_exact_matches:
                hybrid_score += self._calculate_exact_match_boost(query, result)

            if boost_title_matches:
                hybrid_score += self._calculate_title_match_boost(query, result)

            result["hybrid_score"] = hybrid_score
            result["scoring_breakdown"] = {
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "semantic_weight": semantic_weight,
                "keyword_weight": keyword_weight,
                "base_hybrid_score": semantic_weight * semantic_score
                + keyword_weight * keyword_score,
                "boosting_applied": hybrid_score
                - (semantic_weight * semantic_score + keyword_weight * keyword_score),
            }

            combined_results.append(result)

        return combined_results

    def _get_doc_id(self, result: dict[str, Any]) -> str:
        """Get a unique document ID for result deduplication."""
        if result.get("is_chunk") and result.get("chunk_id"):
            return result["chunk_id"]
        else:
            return f"{result.get('store_type', 'unknown')}.{result.get('document_id', 'unknown')}"

    def _calculate_exact_match_boost(self, query: str, result: dict[str, Any]) -> float:
        """Calculate boost for exact phrase matches."""
        query_lower = query.lower()
        content = result.get("content", "").lower()

        # Exact phrase match
        if query_lower in content:
            return 0.2

        # Partial phrase matches (for multi-word queries)
        query_words = self._tokenize(query_lower)
        if len(query_words) > 1:
            # Check for consecutive word matches
            content_words = self._tokenize(content)
            for i in range(len(content_words) - len(query_words) + 1):
                if content_words[i : i + len(query_words)] == query_words:
                    return 0.15

        return 0.0

    def _calculate_title_match_boost(self, query: str, result: dict[str, Any]) -> float:
        """Calculate boost for title/metadata matches."""
        query_lower = query.lower()
        boost = 0.0

        # Check title matches
        title = result.get("title", "").lower()
        if title and query_lower in title:
            boost += 0.15

        # Check chunk title matches
        chunk_title = result.get("chunk_title", "").lower()
        if chunk_title and query_lower in chunk_title:
            boost += 0.1

        # Check document ID matches
        doc_id = result.get("document_id", "").lower()
        if doc_id and query_lower in doc_id:
            boost += 0.05

        return boost

    async def _build_corpus_if_needed(
        self, store_type: str, include_chunks: bool
    ) -> None:
        """Build document corpus for BM25 if not already cached."""
        # For now, we'll rebuild the corpus each time
        # In production, this should be cached and updated incrementally
        await self._build_document_corpus(store_type, include_chunks)

    async def _build_document_corpus(
        self, store_type: str, include_chunks: bool
    ) -> None:
        """Build document corpus from vector store."""
        try:
            # Get all documents
            documents = self.vector_store.search_similar(
                [0.0] * 768,  # Dummy embedding
                limit=10000,  # Large limit to get all documents
                store_type=store_type,
                include_chunks=include_chunks,
                similarity_threshold=0.0,
            )

            # Build corpus
            self._document_corpus = {}
            document_texts = []

            for doc in documents:
                doc_id = self._get_doc_id(doc)
                content = doc.get("content", "")

                # Store document info
                self._document_corpus[doc_id] = doc

                # Store text for BM25 analysis
                document_texts.append(content)

            # Calculate corpus statistics
            self._calculate_corpus_stats(document_texts)

        except Exception as e:
            print(f"Error building document corpus: {e}")
            self._document_corpus = {}

    def _calculate_corpus_stats(self, document_texts: list[str]) -> None:
        """Calculate corpus statistics for BM25."""
        if not document_texts:
            self._corpus_stats = None
            self._term_frequencies = None
            self._document_lengths = None
            return

        # Tokenize all documents
        tokenized_docs = [self._tokenize(text) for text in document_texts]

        # Calculate document lengths
        self._document_lengths = [len(tokens) for tokens in tokenized_docs]
        avg_doc_length = sum(self._document_lengths) / len(self._document_lengths)

        # Calculate term frequencies
        self._term_frequencies = []
        document_frequencies = defaultdict(int)

        for tokens in tokenized_docs:
            term_freq = Counter(tokens)
            self._term_frequencies.append(term_freq)

            # Count document frequency for each term
            unique_terms = set(tokens)
            for term in unique_terms:
                document_frequencies[term] += 1

        # Store corpus statistics
        self._corpus_stats = {
            "total_documents": len(document_texts),
            "average_document_length": avg_doc_length,
            "document_frequencies": dict(document_frequencies),
        }

    def _calculate_bm25_scores(self, query: str) -> list[tuple[str, float]]:
        """Calculate BM25 scores for query against corpus."""
        if (
            not self._corpus_stats
            or not self._term_frequencies
            or not self._document_corpus
        ):
            return []

        query_terms = self._tokenize(query.lower())
        if not query_terms:
            return []

        scores = []
        doc_ids = list(self._document_corpus.keys())

        for i, doc_id in enumerate(doc_ids):
            if i >= len(self._term_frequencies):
                continue

            score = self._calculate_document_bm25_score(query_terms, i)
            scores.append((doc_id, score))

        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def _calculate_document_bm25_score(
        self, query_terms: list[str], doc_index: int
    ) -> float:
        """Calculate BM25 score for a single document."""
        if doc_index >= len(self._term_frequencies) or doc_index >= len(
            self._document_lengths
        ):
            return 0.0

        term_freq = self._term_frequencies[doc_index]
        doc_length = self._document_lengths[doc_index]
        avg_doc_length = self._corpus_stats["average_document_length"]
        total_docs = self._corpus_stats["total_documents"]
        doc_frequencies = self._corpus_stats["document_frequencies"]

        score = 0.0

        for term in query_terms:
            if term not in term_freq:
                continue

            # Term frequency in document
            tf = term_freq[term]

            # Document frequency
            df = doc_frequencies.get(term, 0)
            if df == 0:
                continue

            # Inverse document frequency (ensure positive values)
            idf = math.log(total_docs / df)
            if idf <= 0:
                idf = 0.01  # Minimum IDF to avoid zero scores

            # BM25 score component
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (
                1 - self.b + self.b * (doc_length / avg_doc_length)
            )

            score += idf * (numerator / denominator)

        # Normalize score by query length
        if len(query_terms) > 0:
            score = score / len(query_terms)

        return max(0.0, score)

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text for BM25 processing."""
        if not text:
            return []

        # Convert to lowercase
        text = text.lower()

        # Remove special characters and split on whitespace
        text = re.sub(r"[^\w\s]", " ", text)
        tokens = text.split()

        # Remove stop words and short tokens
        tokens = [
            token for token in tokens if len(token) > 2 and token not in self.stop_words
        ]

        return tokens

    def get_search_stats(self) -> dict[str, Any]:
        """Get statistics about the search corpus."""
        if not self._corpus_stats:
            return {"corpus_built": False}

        return {
            "corpus_built": True,
            "total_documents": self._corpus_stats["total_documents"],
            "average_document_length": self._corpus_stats["average_document_length"],
            "unique_terms": len(self._corpus_stats["document_frequencies"]),
            "bm25_parameters": {
                "k1": self.k1,
                "b": self.b,
            },
            "hybrid_weights": {
                "semantic_weight": self.semantic_weight,
                "keyword_weight": self.keyword_weight,
            },
        }

    def update_hybrid_weights(
        self, semantic_weight: float, keyword_weight: float
    ) -> None:
        """Update the weights for hybrid scoring.

        Args:
            semantic_weight: Weight for semantic similarity (0.0-1.0)
            keyword_weight: Weight for keyword scoring (0.0-1.0)
        """
        total = semantic_weight + keyword_weight
        if total > 0:
            self.semantic_weight = semantic_weight / total
            self.keyword_weight = keyword_weight / total
        else:
            self.semantic_weight = 0.7
            self.keyword_weight = 0.3

    def update_bm25_parameters(self, k1: float = None, b: float = None) -> None:
        """Update BM25 parameters.

        Args:
            k1: Term frequency saturation parameter (default: 1.5)
            b: Length normalization parameter (default: 0.75)
        """
        if k1 is not None:
            self.k1 = max(0.0, k1)
        if b is not None:
            self.b = max(0.0, min(1.0, b))

    async def explain_search_results(
        self, query: str, results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Provide detailed explanation of how search results were scored.

        Args:
            query: Original search query
            results: Search results with scoring breakdown

        Returns:
            Detailed explanation of scoring methodology
        """
        if not results:
            return {"message": "No results to explain"}

        query_analysis = {
            "query": query,
            "query_tokens": self._tokenize(query.lower()),
            "query_length": len(query.split()),
        }

        scoring_explanation = {
            "hybrid_scoring": {
                "semantic_weight": self.semantic_weight,
                "keyword_weight": self.keyword_weight,
                "description": "Final score = (semantic_weight * semantic_score) + (keyword_weight * keyword_score) + boosting",
            },
            "semantic_scoring": {
                "method": "Cosine similarity between query and document embeddings",
                "range": "0.0 to 1.0 (higher is more similar)",
            },
            "keyword_scoring": {
                "method": "BM25 relevance scoring",
                "parameters": {"k1": self.k1, "b": self.b},
                "description": "BM25 considers term frequency, document frequency, and document length normalization",
            },
            "boosting": {
                "exact_match_boost": "0.2 for exact phrase matches, 0.15 for consecutive word matches",
                "title_match_boost": "0.15 for title matches, 0.1 for chunk titles, 0.05 for document IDs",
            },
        }

        # Analyze top results
        top_results_analysis = []
        for i, result in enumerate(results[:5]):
            breakdown = result.get("scoring_breakdown", {})
            analysis = {
                "rank": i + 1,
                "document_id": self._get_doc_id(result),
                "content_preview": result.get("content", "")[:100] + "...",
                "scores": {
                    "final_hybrid_score": result.get("hybrid_score", 0.0),
                    "semantic_score": breakdown.get("semantic_score", 0.0),
                    "keyword_score": breakdown.get("keyword_score", 0.0),
                    "boosting_applied": breakdown.get("boosting_applied", 0.0),
                },
                "search_methods": [
                    method
                    for method in ["semantic", "keyword"]
                    if breakdown.get(f"{method}_score", 0.0) > 0
                ],
            }
            top_results_analysis.append(analysis)

        return {
            "query_analysis": query_analysis,
            "scoring_explanation": scoring_explanation,
            "top_results_analysis": top_results_analysis,
            "corpus_stats": self.get_search_stats(),
        }
