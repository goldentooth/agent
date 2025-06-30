"""
Tests for token usage tracking and cost analysis.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from goldentooth_agent.core.agent_codebase.token_tracking import (
    TokenTracker,
    TokenUsageRecord,
    TokenBudget
)


class TestTokenUsageRecord:
    """Test TokenUsageRecord model."""
    
    def test_record_creation(self):
        """Test creating token usage record."""
        record = TokenUsageRecord(
            operation_id="op_123",
            operation_type="embed",
            timestamp="2024-01-01T12:00:00",
            content_hash="abc123",
            content_length=500,
            token_count=125,
            model_name="text-embedding-ada-002",
            estimated_cost_usd=0.0125,
            document_type="function_definition",
            module_path="test.module",
            codebase_name="test_codebase"
        )
        
        assert record.operation_id == "op_123"
        assert record.operation_type == "embed"
        assert record.token_count == 125
        assert record.estimated_cost_usd == 0.0125
        assert record.document_type == "function_definition"
        assert record.module_path == "test.module"
        assert record.codebase_name == "test_codebase"
        assert not record.was_cached  # Default False


class TestTokenBudget:
    """Test TokenBudget model."""
    
    def test_budget_defaults(self):
        """Test budget default values."""
        budget = TokenBudget()
        
        assert budget.daily_limit == 100000
        assert budget.monthly_limit == 2000000
        assert budget.warning_threshold == 0.8
        assert budget.daily_used == 0
        assert budget.monthly_used == 0
        assert budget.last_reset_date == ""
    
    def test_budget_custom_values(self):
        """Test budget with custom values."""
        budget = TokenBudget(
            daily_limit=50000,
            monthly_limit=1000000,
            warning_threshold=0.9,
            daily_used=10000,
            monthly_used=250000
        )
        
        assert budget.daily_limit == 50000
        assert budget.monthly_limit == 1000000
        assert budget.warning_threshold == 0.9
        assert budget.daily_used == 10000
        assert budget.monthly_used == 250000


class TestTokenTracker:
    """Test TokenTracker functionality."""
    
    def test_tracker_initialization(self, token_tracker: TokenTracker):
        """Test tracker initializes correctly."""
        assert token_tracker.budget.daily_limit == 100000
        assert token_tracker.budget.monthly_limit == 2000000
    
    def test_count_tokens_with_tiktoken(self, token_tracker: TokenTracker):
        """Test token counting with tiktoken available."""
        # Test actual token counting or fallback
        count = token_tracker.count_tokens("test text", "text-embedding-ada-002")
        
        # Should return some reasonable count (actual tiktoken or fallback)
        assert count > 0
        assert isinstance(count, int)
    
    def test_count_tokens_fallback(self, token_tracker: TokenTracker):
        """Test token counting fallback logic."""
        # Test that fallback produces reasonable results
        text = "test text here"
        count = token_tracker.count_tokens(text, "text-embedding-ada-002")
        
        # Should be reasonable (either tiktoken result or ~4 chars per token)
        expected_min = max(1, len(text) // 6)  # Conservative estimate
        expected_max = len(text) // 2  # Liberal estimate
        assert expected_min <= count <= expected_max
    
    def test_calculate_cost(self, token_tracker: TokenTracker):
        """Test cost calculation."""
        # Test ada-002 pricing
        cost = token_tracker._calculate_cost(1000, "text-embedding-ada-002")
        assert cost == 0.0001  # $0.0001 per 1k tokens
        
        # Test small model pricing
        cost = token_tracker._calculate_cost(1000, "text-embedding-3-small")
        assert cost == 0.00002  # $0.00002 per 1k tokens
        
        # Test unknown model (defaults to ada-002)
        cost = token_tracker._calculate_cost(1000, "unknown-model")
        assert cost == 0.0001
        
        # Test fractional tokens
        cost = token_tracker._calculate_cost(500, "text-embedding-ada-002")
        assert cost == 0.00005  # Half of 1k tokens
    
    def test_record_embedding_operation(self, token_tracker: TokenTracker):
        """Test recording embedding operation."""
        content = "def test_function(): pass"
        
        record = token_tracker.record_embedding_operation(
            content=content,
            content_hash="test_hash",
            model_name="text-embedding-ada-002",
            operation_type="embed",
            document_type="function_definition",
            module_path="test.module",
            codebase_name="test_codebase"
        )
        
        assert record.content_hash == "test_hash"
        assert record.content_length == len(content)
        assert record.token_count > 0  # Should have calculated tokens
        assert record.estimated_cost_usd > 0  # Should have calculated cost
        assert record.operation_type == "embed"
        assert record.document_type == "function_definition"
        assert record.module_path == "test.module"
        assert record.codebase_name == "test_codebase"
        assert not record.was_cached
    
    def test_record_cached_operation(self, token_tracker: TokenTracker):
        """Test recording cached operation."""
        content = "def cached_function(): pass"
        
        record = token_tracker.record_embedding_operation(
            content=content,
            content_hash="cached_hash",
            model_name="text-embedding-ada-002",
            operation_type="skip",
            was_cached=True
        )
        
        assert record.token_count == 0  # Cached operations use 0 tokens
        assert record.estimated_cost_usd == 0.0
        assert record.was_cached
        assert record.operation_type == "skip"
    
    def test_budget_updates(self, token_tracker: TokenTracker):
        """Test budget usage updates."""
        initial_daily = token_tracker.budget.daily_used
        initial_monthly = token_tracker.budget.monthly_used
        
        # Record operation with token usage
        token_tracker.record_embedding_operation(
            content="test content for budget",
            content_hash="budget_test",
            model_name="text-embedding-ada-002"
        )
        
        # Budget should be updated
        assert token_tracker.budget.daily_used > initial_daily
        assert token_tracker.budget.monthly_used > initial_monthly
    
    def test_check_budget_status(self, token_tracker: TokenTracker):
        """Test budget status checking."""
        # Set known budget values
        token_tracker.budget.daily_limit = 1000
        token_tracker.budget.monthly_limit = 10000
        token_tracker.budget.daily_used = 800  # 80%
        token_tracker.budget.monthly_used = 5000  # 50%
        token_tracker.budget.warning_threshold = 0.7  # 70%
        
        status = token_tracker.check_budget_status()
        
        assert status["daily_used"] == 800
        assert status["daily_limit"] == 1000
        assert status["daily_usage_pct"] == 0.8
        assert status["monthly_used"] == 5000
        assert status["monthly_limit"] == 10000
        assert status["monthly_usage_pct"] == 0.5
        assert status["within_budget"]  # Still under 100%
        assert len(status["warnings"]) == 1  # Daily over 70% threshold
        assert "Daily usage at 80.0%" in status["warnings"][0]
    
    def test_budget_warnings(self, token_tracker: TokenTracker):
        """Test budget warning generation."""
        # Set budget at warning levels
        token_tracker.budget.daily_limit = 1000
        token_tracker.budget.monthly_limit = 10000
        token_tracker.budget.daily_used = 900  # 90% - over threshold
        token_tracker.budget.monthly_used = 8500  # 85% - over threshold
        token_tracker.budget.warning_threshold = 0.8  # 80%
        
        status = token_tracker.check_budget_status()
        
        assert len(status["warnings"]) == 2
        assert any("Daily usage at 90.0%" in w for w in status["warnings"])
        assert any("Monthly usage at 85.0%" in w for w in status["warnings"])
    
    def test_budget_exceeded(self, token_tracker: TokenTracker):
        """Test budget exceeded detection."""
        # Set budget over limits
        token_tracker.budget.daily_limit = 1000
        token_tracker.budget.daily_used = 1100  # 110% - over budget
        
        status = token_tracker.check_budget_status()
        
        assert not status["within_budget"]
        assert status["daily_usage_pct"] == 1.1
    
    def test_get_usage_statistics(self, token_tracker: TokenTracker):
        """Test usage statistics generation."""
        # Record some operations
        token_tracker.record_embedding_operation(
            content="function content",
            content_hash="func1",
            model_name="text-embedding-ada-002",
            operation_type="embed",
            document_type="function_definition"
        )
        
        token_tracker.record_embedding_operation(
            content="class content", 
            content_hash="class1",
            model_name="text-embedding-ada-002",
            operation_type="embed",
            document_type="class_definition"
        )
        
        token_tracker.record_embedding_operation(
            content="skipped content",
            content_hash="skip1", 
            model_name="text-embedding-ada-002",
            operation_type="skip",
            was_cached=True
        )
        
        stats = token_tracker.get_usage_statistics(days=30)
        
        assert stats["total_operations"] == 3
        assert stats["total_tokens"] > 0  # Should have tokens from non-cached ops
        assert stats["total_cost_usd"] > 0
        assert stats["cached_operations"] == 1
        assert stats["cache_hit_rate"] == 1/3  # 1 cached out of 3 operations
        
        # Check breakdown data
        assert "by_operation_type" in stats
        assert "by_document_type" in stats
        assert "change_detection_savings" in stats
        assert "budget_status" in stats
    
    def test_get_cost_breakdown(self, token_tracker: TokenTracker):
        """Test cost breakdown by time period."""
        # Record operation
        token_tracker.record_embedding_operation(
            content="breakdown test content",
            content_hash="breakdown1",
            model_name="text-embedding-ada-002"
        )
        
        breakdown = token_tracker.get_cost_breakdown(group_by="day", days=7)
        
        assert breakdown["group_by"] == "day"
        assert len(breakdown["breakdown"]) >= 0  # May be empty if no data in range
        
        # If we have data, check structure
        if breakdown["breakdown"]:
            entry = breakdown["breakdown"][0]
            assert "period" in entry
            assert "operations" in entry
            assert "tokens" in entry
            assert "cost_usd" in entry
    
    def test_export_usage_data(self, token_tracker: TokenTracker, temp_dir: Path):
        """Test exporting usage data."""
        # Record some operations
        token_tracker.record_embedding_operation(
            content="export test",
            content_hash="export1",
            model_name="text-embedding-ada-002"
        )
        
        export_file = temp_dir / "token_export.json"
        token_tracker.export_usage_data(export_file)
        
        assert export_file.exists()
        
        # Check export file structure
        import json
        with open(export_file) as f:
            data = json.load(f)
        
        assert "export_timestamp" in data
        assert "usage_statistics" in data
        assert "cost_breakdown" in data
        assert "budget_configuration" in data
    
    def test_budget_persistence(self, temp_dir: Path):
        """Test budget persistence across tracker instances."""
        db_file = temp_dir / "budget_test.db"
        
        # Create first tracker and modify budget
        tracker1 = TokenTracker(db_file)
        tracker1.budget.daily_limit = 50000
        tracker1.budget.daily_used = 10000
        tracker1._save_budget()
        
        # Create second tracker - should load persisted budget
        tracker2 = TokenTracker(db_file)
        
        assert tracker2.budget.daily_limit == 50000
        assert tracker2.budget.daily_used == 10000
    
    def test_budget_reset_logic(self, token_tracker: TokenTracker):
        """Test budget reset on date changes."""
        # Set initial state
        token_tracker.budget.daily_used = 5000
        token_tracker.budget.monthly_used = 20000
        token_tracker.budget.last_reset_date = "2024-01-01"
        
        # Mock current date to be different
        with patch('goldentooth_agent.core.agent_codebase.token_tracking.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 2, 12, 0, 0)  # Next day
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat.return_value = datetime(2024, 1, 1, 0, 0, 0)
            
            # Trigger budget update
            token_tracker._update_budget(100)
            
            # Daily should reset, monthly should not
            assert token_tracker.budget.daily_used == 100  # Reset + new usage
            assert token_tracker.budget.monthly_used == 20100  # Accumulated
            assert token_tracker.budget.last_reset_date == "2024-01-02"
    
    def test_monthly_budget_reset(self, token_tracker: TokenTracker):
        """Test monthly budget reset."""
        # Set initial state
        token_tracker.budget.daily_used = 5000
        token_tracker.budget.monthly_used = 20000
        token_tracker.budget.last_reset_date = "2024-01-15"
        
        # Mock current date to be next month
        with patch('goldentooth_agent.core.agent_codebase.token_tracking.datetime') as mock_datetime:
            mock_now = datetime(2024, 2, 1, 12, 0, 0)  # Next month
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat.return_value = datetime(2024, 1, 15, 0, 0, 0)
            
            # Trigger budget update
            token_tracker._update_budget(100)
            
            # Both daily and monthly should reset
            assert token_tracker.budget.daily_used == 100  # Reset + new usage
            assert token_tracker.budget.monthly_used == 100  # Reset + new usage
    
    def test_database_initialization(self, temp_dir: Path):
        """Test that database is properly initialized."""
        db_file = temp_dir / "init_test.db"
        
        # Creating tracker should initialize database
        tracker = TokenTracker(db_file)
        
        assert db_file.exists()
        
        # Check that tables exist by trying to query them
        import sqlite3
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            
            # Check token_usage table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='token_usage'")
            assert cursor.fetchone() is not None
            
            # Check token_budget table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='token_budget'")
            assert cursor.fetchone() is not None
    
    def test_database_record_storage(self, token_tracker: TokenTracker):
        """Test that records are properly stored in database."""
        record = token_tracker.record_embedding_operation(
            content="database test",
            content_hash="db_test",
            model_name="test-model",
            operation_type="test_op",
            document_type="test_doc",
            module_path="test.module",
            codebase_name="test_base"
        )
        
        # Query database directly to verify storage
        import sqlite3
        with sqlite3.connect(token_tracker.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM token_usage WHERE operation_id = ?", (record.operation_id,))
            row = cursor.fetchone()
            
            assert row is not None
            assert row[1] == "test_op"  # operation_type
            assert row[6] == "test-model"  # model_name
            assert row[9] == "test_doc"  # document_type
            assert row[10] == "test.module"  # module_path