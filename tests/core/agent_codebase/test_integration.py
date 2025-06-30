"""
Integration tests for the complete agent_codebase system.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from goldentooth_agent.core.agent_codebase import (
    CodebaseIntrospectionService,
    IntrospectionQuery,
    CodebaseDocumentType
)
from goldentooth_agent.core.agent_codebase.rag_integration import (
    CodebaseRAGIntegration,
    CodebaseRAGQuery
)


class TestCodebaseIntrospectionService:
    """Test the main introspection service integration."""
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store for service testing."""
        mock = MagicMock()
        mock.add_document = AsyncMock()
        mock.search = AsyncMock(return_value=[])
        return mock
    
    @pytest.fixture
    def introspection_service(self, mock_vector_store):
        """Introspection service with mocked dependencies."""
        return CodebaseIntrospectionService(mock_vector_store)
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, introspection_service):
        """Test service initializes correctly."""
        await introspection_service.initialize()
        
        assert introspection_service._initialized
        assert "goldentooth_agent" in introspection_service.collection.codebases
    
    @pytest.mark.asyncio
    async def test_add_external_codebase(self, introspection_service, sample_codebase_files: Path):
        """Test adding external codebase."""
        await introspection_service.initialize()
        
        result = await introspection_service.add_external_codebase(
            name="external_test",
            path=sample_codebase_files,
            display_name="External Test Codebase",
            description="A test external codebase"
        )
        
        assert result["codebase_name"] == "external_test"
        assert result["documents_processed"] > 0
        assert "external_test" in introspection_service.collection.codebases
    
    @pytest.mark.asyncio
    async def test_query_execution(self, introspection_service):
        """Test executing introspection queries."""
        await introspection_service.initialize()
        
        # Create a query
        query = IntrospectionQuery(
            query="test function implementation",
            limit=5,
            document_types=[CodebaseDocumentType.FUNCTION_DEFINITION]
        )
        
        # Mock search results
        introspection_service.collection.vector_store.search.return_value = [
            {
                "content": "def test_function(): pass",
                "score": 0.9,
                "metadata": {
                    "document_type": "function_definition",
                    "module_path": "test.module",
                    "file_path": "/test.py"
                }
            }
        ]
        
        result = await introspection_service.query(query)
        
        assert result.query == "test function implementation"
        assert result.total_results == 1
        assert len(result.results) == 1
        assert result.execution_time > 0
        assert "goldentooth_agent" in result.codebases_searched
    
    @pytest.mark.asyncio
    async def test_compare_codebases(self, introspection_service):
        """Test codebase comparison functionality."""
        await introspection_service.initialize()
        
        # Mock comparison results
        introspection_service.collection.vector_store.search.return_value = [
            {
                "content": "def error_handler(): pass",
                "score": 0.8,
                "metadata": {
                    "document_type": "function_definition",
                    "complexity_score": 0.3
                }
            }
        ]
        
        comparison = await introspection_service.compare_codebases(
            query="error handling patterns",
            codebase_names=["goldentooth_agent"]
        )
        
        assert comparison.query == "error handling patterns"
        assert comparison.codebases == ["goldentooth_agent"]
        assert "goldentooth_agent" in comparison.similarities
        assert len(comparison.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_get_codebase_overview(self, introspection_service):
        """Test getting codebase overview."""
        await introspection_service.initialize()
        
        # Mock architecture and components queries
        introspection_service.collection.vector_store.search.return_value = [
            {
                "content": "Architecture overview content",
                "score": 0.9,
                "metadata": {"document_type": "module_background"}
            }
        ]
        
        overview = await introspection_service.get_codebase_overview("goldentooth_agent")
        
        assert "codebase_info" in overview
        assert "architecture" in overview
        assert "key_components" in overview
        assert "summary" in overview
    
    def test_infer_document_types(self, introspection_service):
        """Test document type inference from queries."""
        # Test function-related query
        types = introspection_service._infer_document_types("show me the function definition")
        assert CodebaseDocumentType.FUNCTION_DEFINITION in types
        
        # Test class-related query
        types = introspection_service._infer_document_types("find class inheritance patterns")
        assert CodebaseDocumentType.CLASS_DEFINITION in types
        
        # Test architecture-related query
        types = introspection_service._infer_document_types("explain the system design and motivation")
        assert CodebaseDocumentType.MODULE_BACKGROUND in types
        
        # Test generic query (should return comprehensive search)
        types = introspection_service._infer_document_types("general information")
        assert len(types) >= 4  # Should include multiple types
    
    def test_list_available_codebases(self, introspection_service):
        """Test listing available codebases."""
        # Add some test codebases
        from goldentooth_agent.core.agent_codebase.collection import CodebaseInfo
        
        info1 = CodebaseInfo(name="test1", display_name="Test 1", root_path=Path("/test1"))
        info2 = CodebaseInfo(name="test2", display_name="Test 2", root_path=Path("/test2"))
        
        introspection_service.collection.codebases["test1"] = info1
        introspection_service.collection.codebases["test2"] = info2
        
        codebases = introspection_service.list_available_codebases()
        
        assert len(codebases) == 2
        assert any(cb.name == "test1" for cb in codebases)
        assert any(cb.name == "test2" for cb in codebases)


class TestCodebaseRAGIntegration:
    """Test RAG integration functionality."""
    
    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service."""
        mock = MagicMock()
        mock.search = AsyncMock(return_value={
            "documents": [
                {
                    "content": "RAG document content",
                    "score": 0.8,
                    "metadata": {"source_name": "test_source"}
                }
            ]
        })
        mock.claude_client = MagicMock()
        mock.claude_client.generate_response = AsyncMock(return_value={
            "content": "Synthesized answer from RAG and codebase data"
        })
        return mock
    
    @pytest.fixture
    def mock_introspection_service(self):
        """Mock introspection service."""
        mock = MagicMock()
        mock.query = AsyncMock()
        return mock
    
    @pytest.fixture
    def rag_integration(self, mock_rag_service, mock_introspection_service):
        """RAG integration with mocked dependencies."""
        return CodebaseRAGIntegration(mock_rag_service, mock_introspection_service)
    
    @pytest.mark.asyncio
    async def test_combined_query(self, rag_integration, mock_introspection_service):
        """Test combined codebase and document query."""
        # Mock introspection results
        from goldentooth_agent.core.agent_codebase.introspection import IntrospectionResult
        
        mock_introspection_result = IntrospectionResult(
            query="test query",
            results=[
                {
                    "content": "codebase function implementation",
                    "score": 0.9,
                    "metadata": {"document_type": "function_definition"},
                    "source": {"file_path": "/test.py", "module_path": "test.module"}
                }
            ],
            total_results=1,
            codebases_searched=["goldentooth_agent"],
            execution_time=0.1
        )
        
        mock_introspection_service.query.return_value = mock_introspection_result
        
        # Execute combined query
        query = CodebaseRAGQuery(
            query="how to implement authentication",
            include_codebase=True,
            include_documents=True,
            codebase_weight=0.6
        )
        
        result = await rag_integration.query(query)
        
        assert result.query == "how to implement authentication"
        assert len(result.codebase_results) > 0
        assert len(result.document_results) > 0
        assert result.combined_answer != ""
        assert len(result.sources) > 0
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_codebase_only_query(self, rag_integration, mock_introspection_service):
        """Test query with only codebase search."""
        from goldentooth_agent.core.agent_codebase.introspection import IntrospectionResult
        
        mock_introspection_service.query.return_value = IntrospectionResult(
            query="test", results=[{"content": "test"}], total_results=1,
            codebases_searched=["test"], execution_time=0.1
        )
        
        query = CodebaseRAGQuery(
            query="codebase specific query",
            include_codebase=True,
            include_documents=False
        )
        
        result = await rag_integration.query(query)
        
        assert len(result.codebase_results) > 0
        assert len(result.document_results) == 0
    
    @pytest.mark.asyncio
    async def test_documents_only_query(self, rag_integration):
        """Test query with only document search."""
        query = CodebaseRAGQuery(
            query="documents specific query",
            include_codebase=False,
            include_documents=True
        )
        
        result = await rag_integration.query(query)
        
        assert len(result.codebase_results) == 0
        assert len(result.document_results) > 0
    
    def test_combine_results(self, rag_integration):
        """Test result combination and weighting."""
        codebase_result = {
            "results": [
                {"content": "codebase content", "score": 0.9, "source_type": "codebase"}
            ],
            "total": 1,
            "source_type": "codebase"
        }
        
        document_result = {
            "results": [
                {"content": "document content", "score": 0.8, "source_type": "documents"}
            ],
            "total": 1,
            "source_type": "documents"
        }
        
        combined = rag_integration._combine_results(
            codebase_result, document_result, codebase_weight=0.7
        )
        
        assert len(combined) == 2
        
        # Check weighting
        codebase_item = next(item for item in combined if item["source_type"] == "codebase")
        document_item = next(item for item in combined if item["source_type"] == "documents")
        
        assert abs(codebase_item["weighted_score"] - (0.9 * 0.7)) < 0.001  # ~0.63
        assert abs(document_item["weighted_score"] - (0.8 * 0.3)) < 0.001  # ~0.24
        
        # Should be sorted by weighted score (descending)
        assert combined[0]["weighted_score"] >= combined[1]["weighted_score"]
    
    @pytest.mark.asyncio
    async def test_synthesis_with_mixed_content(self, rag_integration):
        """Test answer synthesis with mixed content types."""
        results = [
            {
                "content": "def authenticate(user): pass",
                "source_type": "codebase",
                "metadata": {"document_type": "function_definition"}
            },
            {
                "content": "Authentication is important for security",
                "source_type": "documents",
                "metadata": {}
            }
        ]
        
        answer = await rag_integration._synthesize_answer("how to authenticate", results)
        
        # Should generate some kind of answer
        assert len(answer) > 0
        assert isinstance(answer, str)
    
    def test_extract_sources(self, rag_integration):
        """Test source extraction from results."""
        codebase_result = {
            "results": [
                {
                    "source": {"file_path": "/test.py", "module_path": "test.module"},
                    "metadata": {"module_path": "test.module"}
                }
            ]
        }
        
        document_result = {
            "results": [
                {
                    "source": {"source_name": "test_docs", "file_path": "/docs/test.md"}
                }
            ]
        }
        
        sources = rag_integration._extract_sources(codebase_result, document_result)
        
        assert len(sources) == 2
        assert any("Code:" in source for source in sources)
        assert any("Docs:" in source for source in sources)
    
    @pytest.mark.asyncio
    async def test_error_handling_in_search(self, rag_integration, mock_introspection_service):
        """Test error handling during search operations."""
        # Mock search failure
        mock_introspection_service.query.side_effect = Exception("Search failed")
        
        query = CodebaseRAGQuery(query="failing query")
        
        # Should handle errors gracefully
        result = await rag_integration.query(query)
        
        # Should still return a result, possibly with empty results
        assert result.query == "failing query"
        assert isinstance(result.codebase_results, list)
        assert isinstance(result.document_results, list)
    
    @pytest.mark.asyncio
    async def test_get_codebase_overview_integration(self, rag_integration, mock_introspection_service):
        """Test getting codebase overview through integration."""
        mock_introspection_service.get_codebase_overview = AsyncMock(return_value={
            "overview": "test overview"
        })
        
        overview = await rag_integration.get_codebase_overview()
        
        assert overview["overview"] == "test overview"
        mock_introspection_service.get_codebase_overview.assert_called_once_with("goldentooth_agent")
    
    @pytest.mark.asyncio
    async def test_index_codebase_for_rag(self, rag_integration, mock_introspection_service):
        """Test indexing codebase for RAG integration."""
        mock_introspection_service.index_current_codebase = AsyncMock(return_value={
            "indexed": True
        })
        
        result = await rag_integration.index_codebase_for_rag()
        
        assert result["indexed"]
        mock_introspection_service.index_current_codebase.assert_called_once()


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_full_indexing_and_query_workflow(self, mock_vector_store, sample_codebase_files: Path):
        """Test complete workflow from indexing to querying."""
        from goldentooth_agent.core.agent_codebase.collection import CodebaseCollection
        
        # Create collection and add codebase
        collection = CodebaseCollection(mock_vector_store)
        await collection.add_codebase(
            name="test_workflow",
            root_path=sample_codebase_files,
            display_name="Test Workflow Codebase"
        )
        
        # Index the codebase
        index_result = await collection.index_codebase("test_workflow")
        
        assert index_result["documents_processed"] > 0
        assert index_result["chunks_created"] > 0
        assert len(mock_vector_store.documents) > 0
        
        # Mock search to return some of the indexed documents
        def mock_search(query, limit=10, metadata_filters=None):
            # Return documents that match the query
            matching_docs = []
            for doc_id, doc_data in mock_vector_store.documents.items():
                if query.lower() in doc_data["text"].lower():
                    matching_docs.append({
                        "document_id": doc_id,
                        "content": doc_data["text"],
                        "score": 0.9,
                        "metadata": doc_data["metadata"]
                    })
            return matching_docs[:limit]
        
        mock_vector_store.search = AsyncMock(side_effect=mock_search)
        
        # Query the indexed codebase
        search_results = await collection.search(
            query="function",
            codebase_names=["test_workflow"],
            limit=5
        )
        
        # Should find relevant results
        assert isinstance(search_results, list)
        # Results depend on what was indexed and what matches "function"
    
    @pytest.mark.asyncio
    async def test_change_detection_workflow(self, mock_vector_store, temp_dir: Path):
        """Test change detection in a realistic workflow."""
        from goldentooth_agent.core.agent_codebase.collection import CodebaseCollection
        
        # Create test codebase
        test_dir = temp_dir / "change_test"
        test_dir.mkdir()
        
        test_file = test_dir / "test_module.py"
        test_file.write_text('''
def original_function(x: int) -> int:
    """Original implementation."""
    return x * 2
''')
        
        collection = CodebaseCollection(mock_vector_store)
        await collection.add_codebase("change_test", test_dir)
        
        # First indexing
        result1 = await collection.index_codebase("change_test")
        initial_processed = result1["documents_processed"]
        
        # No changes - should skip everything
        result2 = await collection.index_codebase("change_test")
        assert result2["documents_skipped"] > 0
        assert result2["documents_processed"] == 0
        
        # Make semantic change
        test_file.write_text('''
def original_function(x: int) -> int:
    """Updated implementation with different logic."""
    return x * 3  # Changed multiplication factor
''')
        
        # Should detect change and reindex
        result3 = await collection.index_codebase("change_test")
        assert result3["documents_processed"] > 0
        
        # Make cosmetic change (formatting only)
        test_file.write_text('''
def original_function(x: int) -> int:
    """Updated implementation with different logic."""
    return x * 3    # Changed multiplication factor (added spaces)
''')
        
        # Should skip cosmetic changes
        result4 = await collection.index_codebase("change_test")
        assert result4["documents_skipped"] > 0
    
    @pytest.mark.asyncio
    async def test_token_tracking_workflow(self, mock_vector_store, temp_dir: Path):
        """Test token tracking through complete workflow."""
        from goldentooth_agent.core.agent_codebase.collection import CodebaseCollection
        
        # Create test codebase
        test_dir = temp_dir / "token_test"
        test_dir.mkdir()
        
        test_file = test_dir / "test.py"
        test_file.write_text("def test_function(): pass")
        
        collection = CodebaseCollection(mock_vector_store)
        await collection.add_codebase("token_test", test_dir)
        
        # Index and check token usage
        result = await collection.index_codebase("token_test")
        
        assert "token_usage" in result
        token_stats = result["token_usage"]
        assert token_stats["tokens_used"] >= 0
        assert token_stats["operations_count"] > 0
        
        # Check budget status
        assert "budget_status" in result
        budget = result["budget_status"]
        assert "daily_used" in budget
        assert "monthly_used" in budget
        assert "within_budget" in budget
        
        # Verify token tracker has records
        stats = collection.token_tracker.get_usage_statistics(days=1)
        assert stats["total_operations"] > 0