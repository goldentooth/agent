"""
Token usage tracking and cost analysis for embedding operations.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class TokenUsageRecord(BaseModel):
    """Record of token usage for an embedding operation."""

    # Operation details
    operation_id: str = Field(..., description="Unique operation identifier")
    operation_type: str = Field(
        ..., description="Type of operation (embed, re_embed, skip)"
    )
    timestamp: str = Field(..., description="Operation timestamp")

    # Content details
    content_hash: str = Field(..., description="Hash of content being embedded")
    content_length: int = Field(..., description="Character length of content")
    token_count: int = Field(..., description="Number of tokens used")

    # Model details
    model_name: str = Field(..., description="Embedding model used")
    model_version: str = Field(default="", description="Model version if available")

    # Cost analysis
    estimated_cost_usd: float = Field(default=0.0, description="Estimated cost in USD")

    # Context
    document_type: str = Field(default="", description="Type of document embedded")
    module_path: str = Field(default="", description="Module path if applicable")
    codebase_name: str = Field(default="", description="Codebase name")

    # Change detection context
    was_cached: bool = Field(default=False, description="Whether embedding was cached")
    change_reason: str = Field(default="", description="Reason for re-embedding")


class TokenBudget(BaseModel):
    """Token budget configuration and tracking."""

    daily_limit: int = Field(default=100000, description="Daily token limit")
    monthly_limit: int = Field(default=2000000, description="Monthly token limit")
    warning_threshold: float = Field(
        default=0.8, description="Warning at 80% of budget"
    )

    # Current usage
    daily_used: int = Field(default=0, description="Tokens used today")
    monthly_used: int = Field(default=0, description="Tokens used this month")
    last_reset_date: str = Field(default="", description="Last budget reset date")


class TokenTracker:
    """
    Tracks token usage and provides cost analysis for embedding operations.

    Features:
    1. Precise token counting using tiktoken
    2. Cost estimation based on model pricing
    3. Usage statistics and trends
    4. Budget monitoring and alerts
    5. Savings analysis from change detection
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.budget = TokenBudget()
        self._init_database()
        self._load_budget()

    def _init_database(self) -> None:
        """Initialize SQLite database for token tracking."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Token usage records
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS token_usage (
                    operation_id TEXT PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    content_length INTEGER NOT NULL,
                    token_count INTEGER NOT NULL,
                    model_name TEXT NOT NULL,
                    model_version TEXT DEFAULT '',
                    estimated_cost_usd REAL DEFAULT 0.0,
                    document_type TEXT DEFAULT '',
                    module_path TEXT DEFAULT '',
                    codebase_name TEXT DEFAULT '',
                    was_cached BOOLEAN DEFAULT FALSE,
                    change_reason TEXT DEFAULT ''
                )
            """
            )

            # Budget tracking
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS token_budget (
                    id INTEGER PRIMARY KEY,
                    daily_limit INTEGER NOT NULL,
                    monthly_limit INTEGER NOT NULL,
                    warning_threshold REAL NOT NULL,
                    daily_used INTEGER DEFAULT 0,
                    monthly_used INTEGER DEFAULT 0,
                    last_reset_date TEXT NOT NULL
                )
            """
            )

            # Indexes for efficient queries
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON token_usage(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_operation_type ON token_usage(operation_type)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_model_name ON token_usage(model_name)"
            )

            conn.commit()

    def count_tokens(
        self, text: str, model_name: str = "text-embedding-ada-002"
    ) -> int:
        """
        Count tokens in text using tiktoken.

        This gives us precise token counts for cost calculation.
        """
        try:
            import tiktoken  # type: ignore[import-not-found]

            # Map model names to tiktoken encodings
            encoding_map = {
                "text-embedding-ada-002": "cl100k_base",
                "text-embedding-3-small": "cl100k_base",
                "text-embedding-3-large": "cl100k_base",
                "text-davinci-003": "p50k_base",
                "gpt-3.5-turbo": "cl100k_base",
                "gpt-4": "cl100k_base",
            }

            encoding_name = encoding_map.get(model_name, "cl100k_base")
            encoding = tiktoken.get_encoding(encoding_name)

            return len(encoding.encode(text))

        except ImportError:
            # Fallback estimation if tiktoken not available
            # Rough estimate: ~4 characters per token for English text
            return max(1, len(text) // 4)

    def record_embedding_operation(
        self,
        content: str,
        content_hash: str,
        model_name: str,
        operation_type: str = "embed",
        document_type: str = "",
        module_path: str = "",
        codebase_name: str = "",
        was_cached: bool = False,
        change_reason: str = "",
    ) -> TokenUsageRecord:
        """Record token usage for an embedding operation."""
        import uuid

        token_count = self.count_tokens(content, model_name) if not was_cached else 0
        estimated_cost = self._calculate_cost(token_count, model_name)

        record = TokenUsageRecord(
            operation_id=str(uuid.uuid4()),
            operation_type=operation_type,
            timestamp=datetime.now().isoformat(),
            content_hash=content_hash,
            content_length=len(content),
            token_count=token_count,
            model_name=model_name,
            estimated_cost_usd=estimated_cost,
            document_type=document_type,
            module_path=module_path,
            codebase_name=codebase_name,
            was_cached=was_cached,
            change_reason=change_reason,
        )

        self._store_record(record)
        self._update_budget(token_count)

        return record

    def _calculate_cost(self, token_count: int, model_name: str) -> float:
        """Calculate estimated cost based on current pricing."""
        # Current OpenAI pricing (as of 2024) - update as needed
        pricing_per_1k_tokens = {
            "text-embedding-ada-002": 0.0001,
            "text-embedding-3-small": 0.00002,
            "text-embedding-3-large": 0.00013,
            # Add other models as needed
        }

        rate = pricing_per_1k_tokens.get(
            model_name, 0.0001
        )  # Default to ada-002 pricing
        return (token_count / 1000.0) * rate

    def _store_record(self, record: TokenUsageRecord) -> None:
        """Store usage record in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO token_usage
                (operation_id, operation_type, timestamp, content_hash, content_length,
                 token_count, model_name, model_version, estimated_cost_usd,
                 document_type, module_path, codebase_name, was_cached, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    record.operation_id,
                    record.operation_type,
                    record.timestamp,
                    record.content_hash,
                    record.content_length,
                    record.token_count,
                    record.model_name,
                    record.model_version,
                    record.estimated_cost_usd,
                    record.document_type,
                    record.module_path,
                    record.codebase_name,
                    record.was_cached,
                    record.change_reason,
                ),
            )
            conn.commit()

    def _update_budget(self, tokens_used: int) -> None:
        """Update budget usage."""
        now = datetime.now()
        today = now.date().isoformat()

        # Reset daily/monthly counters if needed
        if self.budget.last_reset_date != today:
            last_reset = (
                datetime.fromisoformat(self.budget.last_reset_date)
                if self.budget.last_reset_date
                else now
            )

            # Reset daily counter
            self.budget.daily_used = 0

            # Reset monthly counter if new month
            if now.month != last_reset.month or now.year != last_reset.year:
                self.budget.monthly_used = 0

            self.budget.last_reset_date = today

        # Update usage
        self.budget.daily_used += tokens_used
        self.budget.monthly_used += tokens_used

        self._save_budget()

    def _load_budget(self) -> None:
        """Load budget from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM token_budget ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()

            if row:
                self.budget = TokenBudget(
                    daily_limit=row[1],
                    monthly_limit=row[2],
                    warning_threshold=row[3],
                    daily_used=row[4],
                    monthly_used=row[5],
                    last_reset_date=row[6],
                )

    def _save_budget(self) -> None:
        """Save budget to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO token_budget
                (id, daily_limit, monthly_limit, warning_threshold,
                 daily_used, monthly_used, last_reset_date)
                VALUES (1, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.budget.daily_limit,
                    self.budget.monthly_limit,
                    self.budget.warning_threshold,
                    self.budget.daily_used,
                    self.budget.monthly_used,
                    self.budget.last_reset_date,
                ),
            )
            conn.commit()

    def check_budget_status(self) -> dict[str, Any]:
        """Check current budget status and warnings."""
        daily_usage_pct = (
            self.budget.daily_used / self.budget.daily_limit
            if self.budget.daily_limit > 0
            else 0
        )
        monthly_usage_pct = (
            self.budget.monthly_used / self.budget.monthly_limit
            if self.budget.monthly_limit > 0
            else 0
        )

        warnings = []
        if daily_usage_pct >= self.budget.warning_threshold:
            warnings.append(f"Daily usage at {daily_usage_pct:.1%} of limit")
        if monthly_usage_pct >= self.budget.warning_threshold:
            warnings.append(f"Monthly usage at {monthly_usage_pct:.1%} of limit")

        return {
            "daily_used": self.budget.daily_used,
            "daily_limit": self.budget.daily_limit,
            "daily_usage_pct": daily_usage_pct,
            "monthly_used": self.budget.monthly_used,
            "monthly_limit": self.budget.monthly_limit,
            "monthly_usage_pct": monthly_usage_pct,
            "warnings": warnings,
            "within_budget": daily_usage_pct < 1.0 and monthly_usage_pct < 1.0,
        }

    def get_usage_statistics(self, days: int = 30) -> dict[str, Any]:
        """Get comprehensive usage statistics."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total usage
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total_operations,
                    SUM(token_count) as total_tokens,
                    SUM(estimated_cost_usd) as total_cost,
                    SUM(CASE WHEN was_cached THEN 1 ELSE 0 END) as cached_operations
                FROM token_usage
                WHERE timestamp >= ?
            """,
                (cutoff_date,),
            )

            totals = cursor.fetchone()

            # By operation type
            cursor.execute(
                """
                SELECT operation_type, COUNT(*), SUM(token_count), SUM(estimated_cost_usd)
                FROM token_usage
                WHERE timestamp >= ?
                GROUP BY operation_type
            """,
                (cutoff_date,),
            )

            by_operation = {
                row[0]: (row[1], row[2], row[3]) for row in cursor.fetchall()
            }

            # By model
            cursor.execute(
                """
                SELECT model_name, COUNT(*), SUM(token_count), SUM(estimated_cost_usd)
                FROM token_usage
                WHERE timestamp >= ?
                GROUP BY model_name
            """,
                (cutoff_date,),
            )

            by_model = {row[0]: (row[1], row[2], row[3]) for row in cursor.fetchall()}

            # By document type
            cursor.execute(
                """
                SELECT document_type, COUNT(*), SUM(token_count)
                FROM token_usage
                WHERE timestamp >= ? AND document_type != ''
                GROUP BY document_type
            """,
                (cutoff_date,),
            )

            by_doc_type = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

            # Change detection savings
            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN operation_type = 'skip' THEN 1 ELSE 0 END) as skipped_ops,
                    AVG(CASE WHEN operation_type != 'skip' THEN token_count ELSE NULL END) as avg_tokens_per_op
                FROM token_usage
                WHERE timestamp >= ?
            """,
                (cutoff_date,),
            )

            savings_data = cursor.fetchone()

        # Calculate savings from change detection
        skipped_ops = savings_data[0] or 0
        avg_tokens = savings_data[1] or 0
        estimated_tokens_saved = skipped_ops * avg_tokens
        estimated_cost_saved = estimated_tokens_saved * 0.0001 / 1000  # Rough estimate

        return {
            "period_days": days,
            "total_operations": totals[0] or 0,
            "total_tokens": totals[1] or 0,
            "total_cost_usd": totals[2] or 0.0,
            "cached_operations": totals[3] or 0,
            "cache_hit_rate": (totals[3] or 0) / max(1, totals[0] or 1),
            "by_operation_type": by_operation,
            "by_model": by_model,
            "by_document_type": by_doc_type,
            "change_detection_savings": {
                "operations_skipped": skipped_ops,
                "estimated_tokens_saved": estimated_tokens_saved,
                "estimated_cost_saved_usd": estimated_cost_saved,
            },
            "budget_status": self.check_budget_status(),
        }

    def get_cost_breakdown(
        self, group_by: str = "day", days: int = 30
    ) -> dict[str, Any]:
        """Get cost breakdown over time."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # SQL date formatting based on grouping
        date_format = {"day": "%Y-%m-%d", "week": "%Y-W%W", "month": "%Y-%m"}.get(
            group_by, "%Y-%m-%d"
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT
                    strftime('{date_format}', timestamp) as period,
                    COUNT(*) as operations,
                    SUM(token_count) as tokens,
                    SUM(estimated_cost_usd) as cost
                FROM token_usage
                WHERE timestamp >= ?
                GROUP BY period
                ORDER BY period
            """,
                (cutoff_date,),
            )

            results = cursor.fetchall()

        return {
            "group_by": group_by,
            "breakdown": [
                {
                    "period": row[0],
                    "operations": row[1],
                    "tokens": row[2],
                    "cost_usd": row[3],
                }
                for row in results
            ],
        }

    def export_usage_data(self, output_path: Path, format: str = "json") -> None:
        """Export usage data for analysis."""
        stats = self.get_usage_statistics(days=365)  # Full year
        breakdown = self.get_cost_breakdown(days=365)

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "usage_statistics": stats,
            "cost_breakdown": breakdown,
            "budget_configuration": self.budget.model_dump(),
        }

        if format == "json":
            with open(output_path, "w") as f:
                json.dump(export_data, f, indent=2)
        elif format == "csv":
            # Could implement CSV export if needed
            pass
