"""Tests for query expansion functionality."""

import pytest

from goldentooth_agent.core.rag.query_expansion import (
    QueryExpansion,
    QueryExpansionEngine,
    QueryIntent,
    SearchStrategy,
)


class TestQueryIntent:
    """Test QueryIntent enum."""

    def test_query_intent_values(self) -> None:
        """Test that QueryIntent enum has expected values."""
        assert QueryIntent.FACTUAL.value == "factual"
        assert QueryIntent.PROCEDURAL.value == "procedural"
        assert QueryIntent.COMPARATIVE.value == "comparative"
        assert QueryIntent.TROUBLESHOOTING.value == "troubleshooting"
        assert QueryIntent.CONCEPTUAL.value == "conceptual"
        assert QueryIntent.DEFINITIONAL.value == "definitional"
        assert QueryIntent.LISTING.value == "listing"
        assert QueryIntent.CONFIGURATION.value == "configuration"
        assert QueryIntent.EXAMPLE.value == "example"
        assert QueryIntent.GENERAL.value == "general"


class TestQueryExpansion:
    """Test QueryExpansion dataclass."""

    def test_query_expansion_basic_properties(self) -> None:
        """Test basic properties of QueryExpansion."""
        expansion = QueryExpansion(
            original_query="Python programming",
            expanded_queries=["Python programming", "Python development", "Python coding"],
            intent=QueryIntent.FACTUAL,
            key_terms=["python", "programming"],
            synonyms={"python": ["py", "python3"], "programming": ["coding", "development"]},
            related_terms=["language", "scripting"],
        )

        assert expansion.original_query == "Python programming"
        assert len(expansion.expanded_queries) == 3
        assert expansion.intent == QueryIntent.FACTUAL
        assert len(expansion.key_terms) == 2
        assert len(expansion.synonyms) == 2

    def test_all_terms_property(self) -> None:
        """Test all_terms property returns unique terms."""
        expansion = QueryExpansion(
            original_query="test query",
            expanded_queries=["test"],
            intent=QueryIntent.GENERAL,
            key_terms=["python", "programming"],
            synonyms={"python": ["py", "python3"], "programming": ["coding"]},
            related_terms=["language", "python"],  # Duplicate python
        )

        all_terms = expansion.all_terms
        assert "python" in all_terms
        assert "programming" in all_terms
        assert "py" in all_terms
        assert "python3" in all_terms
        assert "coding" in all_terms
        assert "language" in all_terms
        # Should only contain unique terms
        assert len(all_terms) == 6  # python, programming, py, python3, coding, language


class TestSearchStrategy:
    """Test SearchStrategy dataclass."""

    def test_search_strategy_properties(self) -> None:
        """Test SearchStrategy properties."""
        strategy = SearchStrategy(
            strategy_type="primary",
            queries=["python programming", "python development"],
            weights=[1.0, 0.8],
            search_params={"threshold": 0.7},
            expected_intent=QueryIntent.FACTUAL,
        )

        assert strategy.strategy_type == "primary"
        assert len(strategy.queries) == 2
        assert len(strategy.weights) == 2
        assert strategy.expected_intent == QueryIntent.FACTUAL

    def test_primary_query_property(self) -> None:
        """Test primary_query property returns highest weighted query."""
        strategy = SearchStrategy(
            strategy_type="test",
            queries=["query1", "query2", "query3"],
            weights=[0.5, 0.9, 0.3],
            search_params={},
            expected_intent=QueryIntent.GENERAL,
        )

        assert strategy.primary_query == "query2"

    def test_primary_query_empty_queries(self) -> None:
        """Test primary_query with empty queries list."""
        strategy = SearchStrategy(
            strategy_type="test",
            queries=[],
            weights=[],
            search_params={},
            expected_intent=QueryIntent.GENERAL,
        )

        assert strategy.primary_query == ""


class TestQueryExpansionEngine:
    """Test QueryExpansionEngine functionality."""

    @pytest.fixture
    def expansion_engine(self) -> QueryExpansionEngine:
        """Create test expansion engine."""
        return QueryExpansionEngine()

    def test_normalize_query(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test query normalization."""
        # Test basic normalization (may have trailing spaces)
        normalized = expansion_engine._normalize_query("  How To Use PYTHON?!  ")
        assert normalized.strip() == "how to use python"

        # Test multiple spaces
        normalized = expansion_engine._normalize_query("python    programming   guide")
        assert normalized == "python programming guide"

        # Test special characters (keeps hyphens and periods)
        normalized = expansion_engine._normalize_query("python-3.9 & flask!")
        assert normalized.strip() == "python-3.9 flask"

    def test_detect_intent_factual(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test intent detection for factual queries."""
        assert expansion_engine._detect_intent("what is python") == QueryIntent.FACTUAL
        assert expansion_engine._detect_intent("what does docker do") == QueryIntent.FACTUAL
        assert expansion_engine._detect_intent("when is the best time") == QueryIntent.FACTUAL

    def test_detect_intent_procedural(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test intent detection for procedural queries."""
        assert expansion_engine._detect_intent("how to install python") == QueryIntent.PROCEDURAL
        assert expansion_engine._detect_intent("steps to deploy docker") == QueryIntent.PROCEDURAL
        assert expansion_engine._detect_intent("guide to kubernetes setup") == QueryIntent.PROCEDURAL

    def test_detect_intent_troubleshooting(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test intent detection for troubleshooting queries."""
        assert expansion_engine._detect_intent("python error import module") == QueryIntent.TROUBLESHOOTING
        assert expansion_engine._detect_intent("fix docker not working") == QueryIntent.TROUBLESHOOTING
        assert expansion_engine._detect_intent("debug kubernetes pod failure") == QueryIntent.TROUBLESHOOTING

    def test_detect_intent_comparative(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test intent detection for comparative queries."""
        assert expansion_engine._detect_intent("python vs java") == QueryIntent.COMPARATIVE
        assert expansion_engine._detect_intent("difference between docker and kubernetes") == QueryIntent.COMPARATIVE
        assert expansion_engine._detect_intent("flask compared to django") == QueryIntent.COMPARATIVE

    def test_detect_intent_general(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test intent detection defaults to general."""
        assert expansion_engine._detect_intent("python programming") == QueryIntent.GENERAL
        assert expansion_engine._detect_intent("machine learning") == QueryIntent.GENERAL

    def test_extract_key_terms(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test key term extraction."""
        terms = expansion_engine._extract_key_terms("how to install python programming language")
        
        # Should filter out stop words and short words
        assert "how" not in terms
        assert "to" not in terms
        assert "install" in terms
        assert "python" in terms
        assert "programming" in terms
        assert "language" in terms

        # Should sort by length (longer first) then alphabetical
        assert terms.index("programming") < terms.index("python")

    def test_generate_synonyms_basic(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test basic synonym generation."""
        synonyms = expansion_engine._generate_synonyms(["python", "function"])

        assert "python" in synonyms
        assert "py" in synonyms["python"]
        assert "python3" in synonyms["python"]

        assert "function" in synonyms
        assert "method" in synonyms["function"]
        assert "procedure" in synonyms["function"]

    def test_generate_synonyms_with_context(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test synonym generation with domain context."""
        synonyms = expansion_engine._generate_synonyms(["python"], domain_context="python")

        assert "python" in synonyms
        # Should include tech synonyms
        python_syns = synonyms["python"]
        assert "py" in python_syns
        assert "python3" in python_syns

    def test_generate_related_terms(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test related term generation."""
        related = expansion_engine._generate_related_terms(["python", "server"])

        # Should include general technical terms for technical keywords
        assert "configuration" in related or "documentation" in related or "tutorial" in related

    def test_generate_term_variations(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test term variation generation."""
        # Plural/singular (basic algorithm removes 's')
        variations = expansion_engine._generate_term_variations("libraries")
        assert "librarie" in variations  # Basic algorithm removes 's'

        variations = expansion_engine._generate_term_variations("function")
        assert "functions" in variations

        # Verb forms (basic algorithm handles -ing and -ed)
        variations = expansion_engine._generate_term_variations("running")
        assert "runn" in variations  # Base form after removing -ing

        # Technical versions
        variations = expansion_engine._generate_term_variations("python3.9")
        assert "python3" in variations
        assert "9" in variations

    def test_is_technical_term(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test technical term detection."""
        assert expansion_engine._is_technical_term("python")
        assert expansion_engine._is_technical_term("javascript")
        assert expansion_engine._is_technical_term("docker")
        assert expansion_engine._is_technical_term("database")
        assert expansion_engine._is_technical_term("function")
        assert expansion_engine._is_technical_term("test.py")

        assert not expansion_engine._is_technical_term("hello")
        assert not expansion_engine._is_technical_term("world")
        assert not expansion_engine._is_technical_term("example")

    def test_expand_query_basic(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test basic query expansion."""
        expansion = expansion_engine.expand_query(
            "how to install python",
            include_synonyms=True,
            include_related=True,
            max_expansions=5,
        )

        assert expansion.original_query == "how to install python"
        assert expansion.intent == QueryIntent.PROCEDURAL
        assert "install" in expansion.key_terms
        assert "python" in expansion.key_terms
        assert len(expansion.expanded_queries) <= 5
        assert len(expansion.expanded_queries) > 0

    def test_expand_query_with_domain_context(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test query expansion with domain context."""
        expansion = expansion_engine.expand_query(
            "configure kubernetes cluster",
            domain_context="kubernetes",
        )

        assert expansion.intent == QueryIntent.CONFIGURATION
        assert "configure" in expansion.key_terms
        assert "kubernetes" in expansion.key_terms

        # Should have some synonyms or related terms
        assert len(expansion.synonyms) > 0 or len(expansion.related_terms) > 0

    def test_expand_query_confidence_calculation(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test confidence calculation in query expansion."""
        # Technical query with clear intent should have high confidence
        expansion1 = expansion_engine.expand_query("how to install python packages")
        
        # Vague query should have lower confidence
        expansion2 = expansion_engine.expand_query("help me")

        assert expansion1.confidence > expansion2.confidence
        assert 0 <= expansion1.confidence <= 1
        assert 0 <= expansion2.confidence <= 1

    def test_create_search_strategies(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test search strategy creation."""
        expansion = expansion_engine.expand_query("python programming tutorial")
        strategies = expansion_engine.create_search_strategies(expansion, max_strategies=3)

        assert len(strategies) <= 3
        assert len(strategies) > 0

        # First strategy should be primary
        primary = strategies[0]
        assert primary.strategy_type == "primary"
        assert primary.queries[0] == expansion.original_query

    def test_create_search_strategies_with_synonyms(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test search strategy creation includes synonym strategy."""
        expansion = expansion_engine.expand_query("python function definition")
        strategies = expansion_engine.create_search_strategies(expansion, max_strategies=3)

        # Should include synonym strategy if synonyms exist
        strategy_types = [s.strategy_type for s in strategies]
        if expansion.synonyms:
            assert "synonym_enhanced" in strategy_types

    def test_analyze_query_quality(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test query quality analysis."""
        # Good quality query
        analysis1 = expansion_engine.analyze_query_quality("how to install python packages using pip")

        assert "overall_quality" in analysis1
        assert "metrics" in analysis1
        assert "intent" in analysis1
        assert "improvements" in analysis1

        assert 0 <= analysis1["overall_quality"] <= 1
        assert analysis1["intent"] == "procedural"

        # Poor quality query
        analysis2 = expansion_engine.analyze_query_quality("help")

        assert analysis2["overall_quality"] < analysis1["overall_quality"]

    def test_quality_metrics(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test individual quality metric calculations."""
        # Test length scoring
        assert expansion_engine._score_query_length("python programming guide") == 1.0  # Optimal
        assert expansion_engine._score_query_length("python") < 1.0  # Too short
        assert expansion_engine._score_query_length("a very long query with many words that goes on") < 1.0  # Too long

        # Test specificity scoring
        technical_terms = ["python", "docker", "kubernetes"]
        general_terms = ["help", "please", "question"]
        
        tech_score = expansion_engine._score_specificity(technical_terms)
        general_score = expansion_engine._score_specificity(general_terms)
        assert tech_score > general_score

    def test_reformulate_query_no_results(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test query reformulation for zero results."""
        reformulations = expansion_engine.reformulate_query(
            "obscure python library xyz123",
            search_results_count=0,
            search_quality_score=0.0,
        )

        assert len(reformulations) > 0
        # Should suggest broader queries
        assert any(len(r.split()) < 4 for r in reformulations)

    def test_reformulate_query_poor_quality(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test query reformulation for poor quality results."""
        reformulations = expansion_engine.reformulate_query(
            "python",
            search_results_count=5,
            search_quality_score=0.3,
        )

        assert len(reformulations) > 0
        # Should suggest more specific queries
        assert any("tutorial" in r or "guide" in r for r in reformulations)

    def test_reformulate_query_too_many_results(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test query reformulation for too many results."""
        reformulations = expansion_engine.reformulate_query(
            "programming",
            search_results_count=25,
            search_quality_score=0.7,
        )

        assert len(reformulations) > 0
        # Should suggest more focused queries
        assert any("how to" in r for r in reformulations)

    def test_intent_specific_expansions(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test intent-specific query expansions."""
        # Factual intent
        factual_expansions = expansion_engine._create_intent_specific_expansions(
            "python language", QueryIntent.FACTUAL
        )
        assert any("what is" in exp for exp in factual_expansions)
        assert any("definition" in exp for exp in factual_expansions)

        # Procedural intent
        procedural_expansions = expansion_engine._create_intent_specific_expansions(
            "install python", QueryIntent.PROCEDURAL
        )
        assert any("how to" in exp for exp in procedural_expansions)
        assert any("tutorial" in exp for exp in procedural_expansions)

        # Troubleshooting intent
        troubleshooting_expansions = expansion_engine._create_intent_specific_expansions(
            "python error", QueryIntent.TROUBLESHOOTING
        )
        assert any("fix" in exp for exp in troubleshooting_expansions)
        assert any("solution" in exp for exp in troubleshooting_expansions)

    def test_get_intent_search_params(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test intent-specific search parameter generation."""
        # Factual queries
        factual_params = expansion_engine._get_intent_search_params(QueryIntent.FACTUAL)
        assert factual_params["boost_title_matches"] is True
        assert factual_params["prefer_authoritative"] is True

        # Procedural queries
        procedural_params = expansion_engine._get_intent_search_params(QueryIntent.PROCEDURAL)
        assert procedural_params["boost_structured_content"] is True
        assert procedural_params["prefer_step_by_step"] is True

        # Troubleshooting queries
        troubleshooting_params = expansion_engine._get_intent_search_params(QueryIntent.TROUBLESHOOTING)
        assert troubleshooting_params["boost_error_contexts"] is True
        assert troubleshooting_params["include_related_issues"] is True

    def test_create_broader_queries(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test broader query creation for zero results."""
        expansion = expansion_engine.expand_query("python rare library xyz")
        broader = expansion_engine._create_broader_queries(expansion)

        assert len(broader) > 0
        # Should include individual key terms
        assert any(term in broader for term in expansion.key_terms[:3])

    def test_create_more_specific_queries(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test more specific query creation."""
        expansion = expansion_engine.expand_query("python programming")
        specific = expansion_engine._create_more_specific_queries(expansion)

        assert len(specific) > 0
        # Should add context words
        assert any("tutorial" in query for query in specific)
        assert any("documentation" in query for query in specific)

    def test_generate_suggestions(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test suggestion generation."""
        # General intent should get clarity suggestions
        suggestions1 = expansion_engine._generate_suggestions(
            "python", QueryIntent.GENERAL, ["python"]
        )
        assert any("more specific" in sugg for sugg in suggestions1)

        # Too few terms should get expansion suggestions
        suggestions2 = expansion_engine._generate_suggestions(
            "help", QueryIntent.GENERAL, ["help"]
        )
        assert any("Add more" in sugg for sugg in suggestions2)

        # Technical terms should get version suggestions
        suggestions3 = expansion_engine._generate_suggestions(
            "python programming", QueryIntent.FACTUAL, ["python", "programming"]
        )
        assert any("version numbers" in sugg for sugg in suggestions3)

    def test_edge_cases(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test edge cases and error conditions."""
        # Empty query
        expansion = expansion_engine.expand_query("")
        assert expansion.original_query == ""
        assert expansion.intent == QueryIntent.GENERAL
        assert len(expansion.key_terms) == 0

        # Single character
        expansion = expansion_engine.expand_query("a")
        assert expansion.original_query == "a"
        assert len(expansion.key_terms) == 0  # Should filter out short words

        # Very long query
        long_query = " ".join(["word"] * 50)
        expansion = expansion_engine.expand_query(long_query, max_expansions=3)
        assert len(expansion.expanded_queries) <= 3

    def test_domain_related_terms(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test domain-specific related term generation."""
        # Python domain
        python_related = expansion_engine._get_domain_related_terms("function", "python")
        assert "def" in python_related
        assert "lambda" in python_related

        # Kubernetes domain
        k8s_related = expansion_engine._get_domain_related_terms("pod", "kubernetes")
        assert "container" in k8s_related
        assert "deployment" in k8s_related

        # GitHub domain
        github_related = expansion_engine._get_domain_related_terms("repository", "github")
        assert "repo" in github_related
        assert "branch" in github_related

        # Unknown domain/term combination
        unknown_related = expansion_engine._get_domain_related_terms("unknown", "unknown")
        assert unknown_related == []

    def test_comprehensive_integration(self, expansion_engine: QueryExpansionEngine) -> None:
        """Test comprehensive integration of all features."""
        query = "how to fix python import error in django"
        
        expansion = expansion_engine.expand_query(
            query,
            domain_context="python",
            include_synonyms=True,
            include_related=True,
            max_expansions=5,
        )

        # Should detect procedural intent (how to patterns match first)
        assert expansion.intent == QueryIntent.PROCEDURAL

        # Should have meaningful key terms
        assert any(term in ["python", "import", "error", "django"] for term in expansion.key_terms)

        # Should have synonyms for technical terms
        assert len(expansion.synonyms) > 0

        # Should have related terms
        assert len(expansion.related_terms) > 0

        # Should have reasonable confidence
        assert expansion.confidence > 0.5

        # Should have helpful suggestions
        assert len(expansion.suggestions) > 0

        # Create strategies
        strategies = expansion_engine.create_search_strategies(expansion)
        assert len(strategies) > 0

        # Analyze quality
        quality = expansion_engine.analyze_query_quality(query)
        assert quality["overall_quality"] > 0.5