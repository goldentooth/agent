"""Query expansion and semantic understanding for enhanced RAG search.

This module provides advanced query understanding and expansion capabilities:

- Semantic expansion with synonyms and related terms
- Intent detection and classification
- Multi-query strategies for better recall
- Query reformulation for poor results
- Context-aware query enhancement
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QueryIntent(Enum):
    """Types of query intents for different search strategies."""

    FACTUAL = "factual"  # "What is X?", "How does Y work?"
    PROCEDURAL = "procedural"  # "How to do X?", "Steps for Y"
    COMPARATIVE = "comparative"  # "X vs Y", "Difference between"
    TROUBLESHOOTING = "troubleshooting"  # "Error with X", "Fix Y problem"
    CONCEPTUAL = "conceptual"  # "Explain X concept", "Theory of Y"
    DEFINITIONAL = "definitional"  # "Define X", "Meaning of Y"
    LISTING = "listing"  # "List all X", "What are the Y"
    CONFIGURATION = "configuration"  # "Configure X", "Settings for Y"
    EXAMPLE = "example"  # "Example of X", "Show me Y"
    GENERAL = "general"  # General or unclear intent


@dataclass
class QueryExpansion:
    """Result of query expansion with enhanced terms and strategies."""

    original_query: str
    expanded_queries: list[str]
    intent: QueryIntent
    key_terms: list[str]
    synonyms: dict[str, list[str]]
    related_terms: list[str]
    filters: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    suggestions: list[str] = field(default_factory=list)

    @property
    def all_terms(self) -> set[str]:
        """Get all unique terms from expansion."""
        terms = set(self.key_terms + self.related_terms)
        for synonym_list in self.synonyms.values():
            terms.update(synonym_list)
        return terms


@dataclass
class SearchStrategy:
    """Strategy for executing enhanced searches."""

    strategy_type: str
    queries: list[str]
    weights: list[float]
    search_params: dict[str, Any]
    expected_intent: QueryIntent

    @property
    def primary_query(self) -> str:
        """Get the primary query with highest weight."""
        if not self.queries:
            return ""
        max_weight_idx = self.weights.index(max(self.weights))
        return self.queries[max_weight_idx]


class QueryExpansionEngine:
    """Advanced query expansion and semantic understanding engine."""

    def __init__(self) -> None:
        """Initialize the query expansion engine."""
        # Technical domain synonyms and related terms
        self.tech_synonyms = {
            # Programming languages
            "python": ["py", "python3", "cpython"],
            "javascript": ["js", "ecmascript", "node.js", "nodejs"],
            "typescript": ["ts"],
            "java": ["openjdk"],
            # Development concepts
            "function": ["method", "procedure", "routine", "callable"],
            "variable": ["var", "parameter", "argument", "field"],
            "class": ["object", "type", "entity"],
            "module": ["package", "library", "component"],
            "framework": ["library", "toolkit", "platform"],
            # Infrastructure terms
            "server": ["host", "machine", "instance", "node"],
            "database": ["db", "datastore", "repository"],
            "api": ["endpoint", "service", "interface"],
            "container": ["docker", "pod"],
            "cluster": ["farm", "pool", "group"],
            # Operations terms
            "deploy": ["deployment", "release", "rollout"],
            "configure": ["config", "setup", "settings"],
            "monitor": ["monitoring", "observability", "tracking"],
            "debug": ["debugging", "troubleshoot", "diagnose"],
            "test": ["testing", "validation", "verification"],
            # General tech terms
            "error": ["exception", "failure", "bug", "issue"],
            "fix": ["repair", "resolve", "solve", "correct"],
            "install": ["setup", "configure", "deploy"],
            "update": ["upgrade", "patch", "modify"],
            "delete": ["remove", "uninstall", "drop"],
        }

        # Context-specific term expansions
        self.contextual_expansions = {
            "github": ["repository", "repo", "git", "version control", "source code"],
            "kubernetes": ["k8s", "orchestration", "containers", "pods", "clusters"],
            "docker": ["containers", "images", "containerization"],
            "aws": ["amazon", "cloud", "ec2", "s3", "lambda"],
            "monitoring": ["metrics", "alerts", "dashboards", "observability"],
            "security": ["authentication", "authorization", "encryption", "ssl", "tls"],
        }

        # Intent detection patterns
        self.intent_patterns = {
            QueryIntent.FACTUAL: [
                r"what is|what are|what does|what's",
                r"who is|who are|who does",
                r"when is|when does|when did",
                r"where is|where does|where can",
                r"which is|which are|which does",
            ],
            QueryIntent.PROCEDURAL: [
                r"how to|how do|how can|how should",
                r"steps to|steps for",
                r"guide to|guide for",
                r"tutorial|walkthrough",
                r"process for|procedure for",
            ],
            QueryIntent.COMPARATIVE: [
                r"vs|versus|compared to|compare",
                r"difference between|differences between",
                r"better than|worse than",
                r"pros and cons|advantages and disadvantages",
            ],
            QueryIntent.TROUBLESHOOTING: [
                r"error|exception|failure|failing",
                r"not working|doesn't work|broken",
                r"fix|solve|resolve|repair",
                r"problem with|issue with|trouble with",
                r"debug|debugging|troubleshoot",
            ],
            QueryIntent.CONCEPTUAL: [
                r"explain|explanation of",
                r"concept of|theory of",
                r"understand|understanding",
                r"principle|principles",
                r"architecture|design pattern",
            ],
            QueryIntent.DEFINITIONAL: [
                r"define|definition of|meaning of",
                r"what does .+ mean",
                r"terminology|glossary",
            ],
            QueryIntent.LISTING: [
                r"list|listing|all|every",
                r"show me all|give me all",
                r"enumerate|count",
                r"types of|kinds of|examples of",
            ],
            QueryIntent.CONFIGURATION: [
                r"configure|configuration|config",
                r"setup|set up|setting up",
                r"install|installation",
                r"settings|parameters|options",
            ],
            QueryIntent.EXAMPLE: [
                r"example|examples|sample|samples",
                r"show me|demonstrate|demo",
                r"use case|usage|implementation",
            ],
        }

        # Stop words to filter out
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
            "were",
            "will",
            "with",
            "would",
            "could",
            "should",
            "this",
            "these",
            "those",
            "them",
            "they",
            "their",
            "there",
            "then",
            "than",
            "very",
            "more",
            "most",
            "some",
            "any",
            "all",
            "each",
            "when",
            "where",
            "why",
            "how",
            "what",
            "which",
            "who",
            "whom",
        }

    def expand_query(
        self,
        query: str,
        domain_context: str | None = None,
        include_synonyms: bool = True,
        include_related: bool = True,
        max_expansions: int = 5,
    ) -> QueryExpansion:
        """Expand a query with semantic understanding and enhancement.

        Args:
            query: Original query string
            domain_context: Optional domain context (e.g., "python", "kubernetes")
            include_synonyms: Whether to include synonym expansions
            include_related: Whether to include related terms
            max_expansions: Maximum number of expanded queries to generate

        Returns:
            QueryExpansion with enhanced queries and metadata
        """
        # Normalize query
        normalized_query = self._normalize_query(query)

        # Detect intent
        intent = self._detect_intent(normalized_query)

        # Extract key terms
        key_terms = self._extract_key_terms(normalized_query)

        # Generate synonyms
        synonyms = {}
        if include_synonyms:
            synonyms = self._generate_synonyms(key_terms, domain_context)

        # Generate related terms
        related_terms = []
        if include_related:
            related_terms = self._generate_related_terms(key_terms, domain_context)

        # Create expanded queries
        expanded_queries = self._create_expanded_queries(
            normalized_query, key_terms, synonyms, related_terms, intent, max_expansions
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(normalized_query, intent, key_terms)

        # Calculate confidence
        confidence = self._calculate_expansion_confidence(
            key_terms, synonyms, related_terms, intent
        )

        return QueryExpansion(
            original_query=query,
            expanded_queries=expanded_queries,
            intent=intent,
            key_terms=key_terms,
            synonyms=synonyms,
            related_terms=related_terms,
            confidence=confidence,
            suggestions=suggestions,
        )

    def create_search_strategies(
        self,
        expansion: QueryExpansion,
        max_strategies: int = 3,
    ) -> list[SearchStrategy]:
        """Create multiple search strategies from query expansion.

        Args:
            expansion: Query expansion result
            max_strategies: Maximum number of strategies to create

        Returns:
            List of search strategies with different approaches
        """
        strategies = []

        # Strategy 1: Original query with intent-specific parameters
        primary_strategy = self._create_primary_strategy(expansion)
        strategies.append(primary_strategy)

        # Strategy 2: Synonym-enhanced queries
        if expansion.synonyms:
            synonym_strategy = self._create_synonym_strategy(expansion)
            strategies.append(synonym_strategy)

        # Strategy 3: Related terms strategy
        if expansion.related_terms:
            related_strategy = self._create_related_terms_strategy(expansion)
            strategies.append(related_strategy)

        # Strategy 4: Broad context strategy (for low-result cases)
        if len(strategies) < max_strategies:
            broad_strategy = self._create_broad_strategy(expansion)
            strategies.append(broad_strategy)

        return strategies[:max_strategies]

    def analyze_query_quality(self, query: str) -> dict[str, Any]:
        """Analyze query quality and provide improvement suggestions.

        Args:
            query: Query to analyze

        Returns:
            Quality analysis with scores and suggestions
        """
        normalized = self._normalize_query(query)
        key_terms = self._extract_key_terms(normalized)
        intent = self._detect_intent(normalized)

        # Quality metrics
        metrics = {
            "length_score": self._score_query_length(normalized),
            "specificity_score": self._score_specificity(key_terms),
            "clarity_score": self._score_clarity(normalized, intent),
            "technical_depth": self._score_technical_depth(key_terms),
        }

        # Overall quality
        overall_quality = sum(metrics.values()) / len(metrics)

        # Generate improvement suggestions
        improvements = self._generate_improvements(normalized, metrics, intent)

        return {
            "query": query,
            "overall_quality": overall_quality,
            "metrics": metrics,
            "intent": intent.value,
            "key_terms": key_terms,
            "improvements": improvements,
            "analysis": {
                "word_count": len(normalized.split()),
                "unique_terms": len(set(key_terms)),
                "technical_terms": len(
                    [t for t in key_terms if self._is_technical_term(t)]
                ),
            },
        }

    def reformulate_query(
        self,
        original_query: str,
        search_results_count: int,
        search_quality_score: float,
    ) -> list[str]:
        """Reformulate query based on search performance.

        Args:
            original_query: Original query that performed poorly
            search_results_count: Number of results returned
            search_quality_score: Quality score of returned results

        Returns:
            List of reformulated queries to try
        """
        expansion = self.expand_query(original_query)
        reformulations = []

        if search_results_count == 0:
            # No results - try broader queries
            reformulations.extend(self._create_broader_queries(expansion))
        elif search_results_count > 0 and search_quality_score < 0.5:
            # Poor quality results - try more specific queries
            reformulations.extend(self._create_more_specific_queries(expansion))
        elif search_results_count > 20:
            # Too many results - try more focused queries
            reformulations.extend(self._create_focused_queries(expansion))

        # Always add intent-based alternatives
        reformulations.extend(self._create_intent_alternatives(expansion))

        # Remove duplicates and limit
        unique_reformulations = list(dict.fromkeys(reformulations))
        return unique_reformulations[:5]

    def _normalize_query(self, query: str) -> str:
        """Normalize query text."""
        # Convert to lowercase
        normalized = query.lower().strip()

        # Remove punctuation except hyphens and periods in technical terms
        normalized = re.sub(r"[^\w\s\-\.]", " ", normalized)

        # Remove extra whitespace (after punctuation removal)
        normalized = re.sub(r"\s+", " ", normalized)

        return normalized

    def _detect_intent(self, query: str) -> QueryIntent:
        """Detect the intent of a query."""
        query_lower = query.lower()

        # Check patterns for each intent type
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent

        # Default to general if no specific intent detected
        return QueryIntent.GENERAL

    def _extract_key_terms(self, query: str) -> list[str]:
        """Extract key terms from query."""
        words = query.split()

        # Filter out stop words and short words
        key_terms = [
            word for word in words if word not in self.stop_words and len(word) > 2
        ]

        # Sort by potential importance (longer words first, then alphabetical)
        key_terms.sort(key=lambda x: (-len(x), x))

        return key_terms

    def _generate_synonyms(
        self,
        key_terms: list[str],
        domain_context: str | None = None,
    ) -> dict[str, list[str]]:
        """Generate synonyms for key terms."""
        synonyms = {}

        for term in key_terms:
            term_synonyms = []

            # Check technical synonyms
            if term in self.tech_synonyms:
                term_synonyms.extend(self.tech_synonyms[term])

            # Check contextual expansions
            if domain_context and domain_context in self.contextual_expansions:
                context_terms = self.contextual_expansions[domain_context]
                if term in context_terms or any(
                    syn in context_terms for syn in term_synonyms
                ):
                    term_synonyms.extend(context_terms)

            # Add common variations
            term_synonyms.extend(self._generate_term_variations(term))

            if term_synonyms:
                # Remove duplicates and the original term
                unique_synonyms = list(set(term_synonyms))
                if term in unique_synonyms:
                    unique_synonyms.remove(term)
                synonyms[term] = unique_synonyms[:5]  # Limit to top 5

        return synonyms

    def _generate_related_terms(
        self,
        key_terms: list[str],
        domain_context: str | None = None,
    ) -> list[str]:
        """Generate related terms for broader context."""
        related = []

        for term in key_terms:
            # Add contextual expansions
            if term in self.contextual_expansions:
                related.extend(self.contextual_expansions[term])

            # Add domain-specific related terms
            if domain_context:
                related.extend(self._get_domain_related_terms(term, domain_context))

        # Add general technical terms if we have technical keywords
        if any(self._is_technical_term(term) for term in key_terms):
            related.extend(["configuration", "documentation", "examples", "tutorial"])

        # Remove duplicates and original terms
        unique_related = list(set(related))
        for term in key_terms:
            if term in unique_related:
                unique_related.remove(term)

        return unique_related[:10]  # Limit to top 10

    def _generate_term_variations(self, term: str) -> list[str]:
        """Generate common variations of a term."""
        variations = []

        # Plural/singular forms
        if term.endswith("s") and len(term) > 3:
            variations.append(term[:-1])  # Remove 's'
        elif not term.endswith("s"):
            variations.append(term + "s")  # Add 's'

        # Common endings
        if term.endswith("ing"):
            base = term[:-3]
            variations.extend([base, base + "e", base + "ed"])
        elif term.endswith("ed"):
            base = term[:-2]
            variations.extend([base, base + "ing"])

        # Technical term variations
        if "." in term:
            # Handle versions like "python3.9" -> "python", "python3"
            parts = term.split(".")
            variations.extend(parts)

        return variations

    def _get_domain_related_terms(self, term: str, domain: str) -> list[str]:
        """Get domain-specific related terms."""
        domain_relations = {
            "python": {
                "function": ["def", "lambda", "method", "class"],
                "package": ["pip", "pypi", "requirements", "setup.py"],
                "framework": ["django", "flask", "fastapi", "pyramid"],
            },
            "kubernetes": {
                "pod": ["container", "deployment", "service", "ingress"],
                "cluster": ["node", "namespace", "kubectl"],
                "config": ["yaml", "manifest", "helm", "kustomize"],
            },
            "github": {
                "repository": ["repo", "branch", "commit", "pull request"],
                "action": ["workflow", "ci/cd", "pipeline"],
                "issue": ["bug", "feature", "enhancement"],
            },
        }

        if domain in domain_relations and term in domain_relations[domain]:
            return domain_relations[domain][term]

        return []

    def _is_technical_term(self, term: str) -> bool:
        """Check if a term is technical/domain-specific."""
        technical_indicators = [
            # Programming languages
            "python",
            "javascript",
            "java",
            "go",
            "rust",
            "c++",
            # Technologies
            "docker",
            "kubernetes",
            "git",
            "api",
            "database",
            "server",
            # Concepts
            "function",
            "class",
            "method",
            "variable",
            "algorithm",
            # File extensions or technical formats
            ".py",
            ".js",
            ".yaml",
            ".json",
            ".xml",
        ]

        return any(indicator in term.lower() for indicator in technical_indicators)

    def _create_expanded_queries(
        self,
        original: str,
        key_terms: list[str],
        synonyms: dict[str, list[str]],
        related_terms: list[str],
        intent: QueryIntent,
        max_expansions: int,
    ) -> list[str]:
        """Create expanded query variations."""
        expansions = [original]  # Always include original

        # Create synonym-based expansions
        for term, term_synonyms in synonyms.items():
            for synonym in term_synonyms[:2]:  # Top 2 synonyms per term
                expanded = original.replace(term, synonym)
                if expanded != original:
                    expansions.append(expanded)

        # Create related term expansions
        if related_terms:
            # Add most relevant related terms to original query
            for related in related_terms[:3]:
                expanded = f"{original} {related}"
                expansions.append(expanded)

        # Create intent-specific expansions
        intent_expansions = self._create_intent_specific_expansions(original, intent)
        expansions.extend(intent_expansions)

        # Remove duplicates and limit
        unique_expansions = list(dict.fromkeys(expansions))
        return unique_expansions[:max_expansions]

    def _create_intent_specific_expansions(
        self,
        query: str,
        intent: QueryIntent,
    ) -> list[str]:
        """Create expansions based on detected intent."""
        expansions = []

        if intent == QueryIntent.FACTUAL:
            expansions.extend(
                [
                    f"what is {query}",
                    f"explain {query}",
                    f"{query} definition",
                ]
            )
        elif intent == QueryIntent.PROCEDURAL:
            expansions.extend(
                [
                    f"how to {query}",
                    f"{query} tutorial",
                    f"{query} guide",
                    f"{query} steps",
                ]
            )
        elif intent == QueryIntent.TROUBLESHOOTING:
            expansions.extend(
                [
                    f"{query} fix",
                    f"{query} solution",
                    f"{query} debug",
                    f"resolve {query}",
                ]
            )
        elif intent == QueryIntent.CONFIGURATION:
            expansions.extend(
                [
                    f"{query} setup",
                    f"{query} configuration",
                    f"{query} install",
                    f"configure {query}",
                ]
            )
        elif intent == QueryIntent.EXAMPLE:
            expansions.extend(
                [
                    f"{query} example",
                    f"{query} sample",
                    f"{query} demo",
                    f"{query} use case",
                ]
            )

        return expansions

    def _generate_suggestions(
        self,
        query: str,
        intent: QueryIntent,
        key_terms: list[str],
    ) -> list[str]:
        """Generate helpful query suggestions."""
        suggestions = []

        # Intent-based suggestions
        if intent == QueryIntent.GENERAL:
            suggestions.append("Try being more specific about what you want to know")
            suggestions.append(
                "Add context words like 'how to', 'what is', or 'example of'"
            )

        # Term-based suggestions
        if len(key_terms) < 2:
            suggestions.append("Add more specific terms to narrow your search")
        elif len(key_terms) > 6:
            suggestions.append("Try using fewer, more focused terms")

        # Technical suggestions
        if any(self._is_technical_term(term) for term in key_terms):
            suggestions.append(
                "Include version numbers or specific technologies if relevant"
            )

        return suggestions

    def _calculate_expansion_confidence(
        self,
        key_terms: list[str],
        synonyms: dict[str, list[str]],
        related_terms: list[str],
        intent: QueryIntent,
    ) -> float:
        """Calculate confidence in query expansion quality."""
        confidence = 0.5  # Base confidence

        # Boost for clear intent
        if intent != QueryIntent.GENERAL:
            confidence += 0.2

        # Boost for good key terms
        if 2 <= len(key_terms) <= 5:
            confidence += 0.2

        # Boost for available synonyms
        if synonyms:
            confidence += min(0.2, len(synonyms) * 0.05)

        # Boost for related terms
        if related_terms:
            confidence += min(0.1, len(related_terms) * 0.01)

        # Boost for technical terms (usually more precise)
        technical_count = sum(1 for term in key_terms if self._is_technical_term(term))
        if technical_count > 0:
            confidence += min(0.1, technical_count * 0.05)

        return min(1.0, confidence)

    def _create_primary_strategy(self, expansion: QueryExpansion) -> SearchStrategy:
        """Create primary search strategy using original query."""
        search_params = self._get_intent_search_params(expansion.intent)

        return SearchStrategy(
            strategy_type="primary",
            queries=[expansion.original_query],
            weights=[1.0],
            search_params=search_params,
            expected_intent=expansion.intent,
        )

    def _create_synonym_strategy(self, expansion: QueryExpansion) -> SearchStrategy:
        """Create search strategy using synonyms."""
        queries = []
        weights = []

        # Add original query with high weight
        queries.append(expansion.original_query)
        weights.append(0.7)

        # Add top synonym expansions
        for expanded in expansion.expanded_queries[1:4]:  # Skip original, take next 3
            if any(
                syn in expanded
                for synonyms in expansion.synonyms.values()
                for syn in synonyms
            ):
                queries.append(expanded)
                weights.append(0.5)

        search_params = self._get_intent_search_params(expansion.intent)
        search_params["boost_synonyms"] = True

        return SearchStrategy(
            strategy_type="synonym_enhanced",
            queries=queries,
            weights=weights,
            search_params=search_params,
            expected_intent=expansion.intent,
        )

    def _create_related_terms_strategy(
        self, expansion: QueryExpansion
    ) -> SearchStrategy:
        """Create search strategy using related terms."""
        queries = []
        weights = []

        # Add original query
        queries.append(expansion.original_query)
        weights.append(0.6)

        # Add queries with related terms
        for related in expansion.related_terms[:3]:
            enhanced_query = f"{expansion.original_query} {related}"
            queries.append(enhanced_query)
            weights.append(0.4)

        search_params = self._get_intent_search_params(expansion.intent)
        search_params["expand_context"] = True

        return SearchStrategy(
            strategy_type="related_terms",
            queries=queries,
            weights=weights,
            search_params=search_params,
            expected_intent=expansion.intent,
        )

    def _create_broad_strategy(self, expansion: QueryExpansion) -> SearchStrategy:
        """Create broad search strategy for better recall."""
        queries = []
        weights = []

        # Use key terms for broader matching
        if expansion.key_terms:
            broad_query = " ".join(expansion.key_terms[:3])  # Top 3 key terms
            queries.append(broad_query)
            weights.append(0.8)

        # Add any related terms as separate queries
        for related in expansion.related_terms[:2]:
            queries.append(related)
            weights.append(0.3)

        search_params = {
            "similarity_threshold": 0.05,  # Very low threshold
            "max_results": 20,  # More results
            "include_partial_matches": True,
        }

        return SearchStrategy(
            strategy_type="broad_recall",
            queries=queries,
            weights=weights,
            search_params=search_params,
            expected_intent=expansion.intent,
        )

    def _get_intent_search_params(self, intent: QueryIntent) -> dict[str, Any]:
        """Get search parameters optimized for specific intent."""
        base_params = {
            "similarity_threshold": 0.1,
            "max_results": 10,
            "boost_exact_matches": True,
        }

        if intent == QueryIntent.FACTUAL:
            base_params.update(
                {
                    "boost_title_matches": True,
                    "prefer_authoritative": True,
                }
            )
        elif intent == QueryIntent.PROCEDURAL:
            base_params.update(
                {
                    "boost_structured_content": True,
                    "prefer_step_by_step": True,
                }
            )
        elif intent == QueryIntent.TROUBLESHOOTING:
            base_params.update(
                {
                    "boost_error_contexts": True,
                    "include_related_issues": True,
                }
            )
        elif intent == QueryIntent.EXAMPLE:
            base_params.update(
                {
                    "boost_code_examples": True,
                    "include_demonstrations": True,
                }
            )

        return base_params

    def _score_query_length(self, query: str) -> float:
        """Score query based on optimal length."""
        word_count = len(query.split())

        if 2 <= word_count <= 6:
            return 1.0  # Optimal length
        elif word_count == 1 or word_count == 7:
            return 0.8  # Acceptable
        elif word_count == 8 or word_count == 9:
            return 0.6  # Getting too long
        else:
            return 0.3  # Too short or too long

    def _score_specificity(self, key_terms: list[str]) -> float:
        """Score query specificity based on key terms."""
        if not key_terms:
            return 0.0

        # Count technical/specific terms
        technical_count = sum(1 for term in key_terms if self._is_technical_term(term))
        specificity = technical_count / len(key_terms)

        # Boost for good number of specific terms
        if 1 <= technical_count <= 3:
            specificity += 0.2

        return min(1.0, specificity)

    def _score_clarity(self, query: str, intent: QueryIntent) -> float:
        """Score query clarity based on intent detection."""
        clarity = 0.5  # Base score

        # Boost for clear intent
        if intent != QueryIntent.GENERAL:
            clarity += 0.3

        # Boost for clear question words
        question_words = ["what", "how", "why", "when", "where", "which", "who"]
        if any(word in query.lower() for word in question_words):
            clarity += 0.2

        return min(1.0, clarity)

    def _score_technical_depth(self, key_terms: list[str]) -> float:
        """Score technical depth of query."""
        if not key_terms:
            return 0.0

        technical_terms = [term for term in key_terms if self._is_technical_term(term)]
        depth = len(technical_terms) / len(key_terms)

        return depth

    def _generate_improvements(
        self,
        query: str,
        metrics: dict[str, float],
        intent: QueryIntent,
    ) -> list[str]:
        """Generate improvement suggestions based on quality metrics."""
        improvements = []

        if metrics["length_score"] < 0.7:
            word_count = len(query.split())
            if word_count < 2:
                improvements.append("Add more descriptive terms to your query")
            elif word_count > 8:
                improvements.append("Try using fewer, more focused terms")

        if metrics["specificity_score"] < 0.5:
            improvements.append("Include more specific technical terms or context")

        if metrics["clarity_score"] < 0.6:
            improvements.append(
                "Add question words like 'how to', 'what is', or 'why does'"
            )

        if intent == QueryIntent.GENERAL:
            improvements.append(
                "Be more specific about what you want to learn or accomplish"
            )

        return improvements

    def _create_broader_queries(self, expansion: QueryExpansion) -> list[str]:
        """Create broader queries for zero-result scenarios."""
        broader = []

        # Use individual key terms
        for term in expansion.key_terms[:3]:
            broader.append(term)

        # Use related terms
        for related in expansion.related_terms[:3]:
            broader.append(related)

        # Create more general versions
        if expansion.intent == QueryIntent.TROUBLESHOOTING:
            broader.extend(
                [
                    " ".join(expansion.key_terms[:2]) + " problem",
                    " ".join(expansion.key_terms[:2]) + " issue",
                ]
            )

        return broader

    def _create_more_specific_queries(self, expansion: QueryExpansion) -> list[str]:
        """Create more specific queries for poor quality results."""
        specific = []

        # Add context words
        for term in expansion.key_terms[:2]:
            specific.extend(
                [
                    f"{term} tutorial",
                    f"{term} documentation",
                    f"{term} example",
                    f"{term} guide",
                ]
            )

        return specific

    def _create_focused_queries(self, expansion: QueryExpansion) -> list[str]:
        """Create more focused queries for too many results."""
        focused = []

        # Combine more terms for specificity
        if len(expansion.key_terms) >= 2:
            focused.append(" ".join(expansion.key_terms[:2]))

        # Add intent-specific focus
        if expansion.intent != QueryIntent.GENERAL:
            for term in expansion.key_terms[:2]:
                if expansion.intent == QueryIntent.PROCEDURAL:
                    focused.append(f"how to {term}")
                elif expansion.intent == QueryIntent.TROUBLESHOOTING:
                    focused.append(f"{term} error fix")

        return focused

    def _create_intent_alternatives(self, expansion: QueryExpansion) -> list[str]:
        """Create alternative queries based on different possible intents."""
        alternatives = []
        primary_term = expansion.key_terms[0] if expansion.key_terms else ""

        if primary_term:
            alternatives.extend(
                [
                    f"what is {primary_term}",
                    f"how to use {primary_term}",
                    f"{primary_term} examples",
                    f"{primary_term} configuration",
                ]
            )

        return alternatives
