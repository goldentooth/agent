"""Tests for rate limiting and DoS protection system."""

import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from goldentooth_agent.core.security.rate_limiting import (
    FixedWindowLimiter,
    MemoryRateLimitStore,
    RateLimitConfig,
    RateLimitError,
    RateLimitResult,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    check_rate_limit,
    create_rate_limiter,
    rate_limit_decorator,
)


class TestRateLimitConfig:
    """Test rate limiting configuration."""

    def test_rate_limit_config_defaults(self):
        config = RateLimitConfig()

        assert config.requests_per_minute == 100
        assert config.requests_per_hour == 1000
        assert config.burst_capacity == 10
        assert config.window_size_seconds == 60
        assert config.algorithm == "token_bucket"
        assert config.enable_per_ip_limiting is True
        assert config.enable_per_user_limiting is True

    def test_rate_limit_config_custom_values(self):
        config = RateLimitConfig(
            requests_per_minute=50, algorithm="sliding_window", burst_capacity=5
        )

        assert config.requests_per_minute == 50
        assert config.algorithm == "sliding_window"
        assert config.burst_capacity == 5


class TestRateLimitResult:
    """Test rate limit result object."""

    def test_rate_limit_result_allowed(self):
        result = RateLimitResult(
            allowed=True, remaining=5, reset_time=time.time() + 60, retry_after=None
        )

        assert result.allowed is True
        assert result.remaining == 5
        assert result.retry_after is None

    def test_rate_limit_result_denied(self):
        retry_time = time.time() + 30
        result = RateLimitResult(
            allowed=False,
            remaining=0,
            reset_time=time.time() + 60,
            retry_after=retry_time,
        )

        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after == retry_time


class TestTokenBucketLimiter:
    """Test token bucket rate limiting algorithm."""

    def test_token_bucket_initialization(self):
        config = RateLimitConfig(requests_per_minute=60, burst_capacity=10)
        limiter = TokenBucketLimiter(config)

        assert limiter.config == config
        assert limiter.bucket_capacity == 10
        assert limiter.refill_rate == 1.0  # 60 per minute = 1 per second

    @pytest.mark.asyncio
    async def test_token_bucket_allows_requests_within_limit(self):
        config = RateLimitConfig(requests_per_minute=60, burst_capacity=5)
        store = MemoryRateLimitStore()
        limiter = TokenBucketLimiter(config, store)

        key = "test_user"

        # Should allow requests up to burst capacity
        for i in range(5):
            result = await limiter.check_rate_limit(key)
            assert result.allowed is True
            assert result.remaining == 4 - i

    @pytest.mark.asyncio
    async def test_token_bucket_denies_requests_over_burst(self):
        config = RateLimitConfig(requests_per_minute=60, burst_capacity=3)
        store = MemoryRateLimitStore()
        limiter = TokenBucketLimiter(config, store)

        key = "test_user"

        # Use up all tokens
        for i in range(3):
            result = await limiter.check_rate_limit(key)
            assert result.allowed is True

        # Next request should be denied
        result = await limiter.check_rate_limit(key)
        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after is not None

    @pytest.mark.asyncio
    async def test_token_bucket_refills_over_time(self):
        config = RateLimitConfig(
            requests_per_minute=120, burst_capacity=2
        )  # 2 per second
        store = MemoryRateLimitStore()
        limiter = TokenBucketLimiter(config, store)

        key = "test_user"

        # Use up tokens
        await limiter.check_rate_limit(key)
        await limiter.check_rate_limit(key)

        # Should be denied
        result = await limiter.check_rate_limit(key)
        assert result.allowed is False

        # Wait for refill (at 2 per second, should refill 1 token in 0.5s)
        await asyncio.sleep(0.6)

        # Should allow one request
        result = await limiter.check_rate_limit(key)
        assert result.allowed is True


class TestSlidingWindowLimiter:
    """Test sliding window rate limiting algorithm."""

    @pytest.mark.asyncio
    async def test_sliding_window_allows_requests_within_window(self):
        config = RateLimitConfig(
            requests_per_minute=10, window_size_seconds=60, algorithm="sliding_window"
        )
        store = MemoryRateLimitStore()
        limiter = SlidingWindowLimiter(config, store)

        key = "test_user"

        # Should allow requests up to limit
        for i in range(10):
            result = await limiter.check_rate_limit(key)
            assert result.allowed is True
            assert result.remaining == 9 - i

    @pytest.mark.asyncio
    async def test_sliding_window_denies_requests_over_limit(self):
        config = RateLimitConfig(
            requests_per_minute=5, window_size_seconds=60, algorithm="sliding_window"
        )
        store = MemoryRateLimitStore()
        limiter = SlidingWindowLimiter(config, store)

        key = "test_user"

        # Use up limit
        for i in range(5):
            result = await limiter.check_rate_limit(key)
            assert result.allowed is True

        # Next request should be denied
        result = await limiter.check_rate_limit(key)
        assert result.allowed is False
        assert result.remaining == 0

    @pytest.mark.asyncio
    async def test_sliding_window_rolls_over_time(self):
        config = RateLimitConfig(
            requests_per_minute=2,
            window_size_seconds=1,  # 1 second window for fast testing
            algorithm="sliding_window",
        )
        store = MemoryRateLimitStore()
        limiter = SlidingWindowLimiter(config, store)

        key = "test_user"

        # Use up limit
        await limiter.check_rate_limit(key)
        await limiter.check_rate_limit(key)

        # Should be denied
        result = await limiter.check_rate_limit(key)
        assert result.allowed is False

        # Wait for window to slide
        await asyncio.sleep(1.1)

        # Should allow requests again
        result = await limiter.check_rate_limit(key)
        assert result.allowed is True


class TestFixedWindowLimiter:
    """Test fixed window rate limiting algorithm."""

    @pytest.mark.asyncio
    async def test_fixed_window_allows_requests_within_window(self):
        config = RateLimitConfig(
            requests_per_minute=5, window_size_seconds=60, algorithm="fixed_window"
        )
        store = MemoryRateLimitStore()
        limiter = FixedWindowLimiter(config, store)

        key = "test_user"

        # Should allow requests up to limit
        for i in range(5):
            result = await limiter.check_rate_limit(key)
            assert result.allowed is True
            assert result.remaining == 4 - i

    @pytest.mark.asyncio
    async def test_fixed_window_resets_at_window_boundary(self):
        config = RateLimitConfig(
            requests_per_minute=2,
            window_size_seconds=1,  # 1 second window
            algorithm="fixed_window",
        )
        store = MemoryRateLimitStore()
        limiter = FixedWindowLimiter(config, store)

        key = "test_user"

        # Use up limit
        await limiter.check_rate_limit(key)
        await limiter.check_rate_limit(key)

        # Should be denied
        result = await limiter.check_rate_limit(key)
        assert result.allowed is False

        # Wait for next window
        await asyncio.sleep(1.1)

        # Should allow requests in new window
        result = await limiter.check_rate_limit(key)
        assert result.allowed is True


class TestMemoryRateLimitStore:
    """Test in-memory rate limit store."""

    @pytest.mark.asyncio
    async def test_memory_store_get_set(self):
        store = MemoryRateLimitStore()

        key = "test_key"
        data = {"tokens": 5, "last_refill": time.time()}

        # Should return None for non-existent key
        result = await store.get(key)
        assert result is None

        # Set and retrieve data
        await store.set(key, data, ttl=60)
        result = await store.get(key)
        assert result == data

    @pytest.mark.asyncio
    async def test_memory_store_increment(self):
        store = MemoryRateLimitStore()

        key = "counter_key"

        # Increment non-existent key
        result = await store.increment(key, ttl=60)
        assert result == 1

        # Increment existing key
        result = await store.increment(key)
        assert result == 2

        result = await store.increment(key)
        assert result == 3

    @pytest.mark.asyncio
    async def test_memory_store_ttl_expiration(self):
        store = MemoryRateLimitStore()

        key = "expire_key"
        data = {"test": "value"}

        # Set with very short TTL
        await store.set(key, data, ttl=0.1)

        # Should exist immediately
        result = await store.get(key)
        assert result == data

        # Wait for expiration
        await asyncio.sleep(0.2)

        # Should be expired
        result = await store.get(key)
        assert result is None

    @pytest.mark.asyncio
    async def test_memory_store_delete(self):
        store = MemoryRateLimitStore()

        key = "delete_key"
        data = {"test": "value"}

        await store.set(key, data)
        assert await store.get(key) == data

        await store.delete(key)
        assert await store.get(key) is None


class TestRateLimiterFactory:
    """Test rate limiter factory functions."""

    def test_create_rate_limiter_token_bucket(self):
        config = RateLimitConfig(algorithm="token_bucket")
        limiter = create_rate_limiter(config)

        assert isinstance(limiter, TokenBucketLimiter)
        assert limiter.config == config

    def test_create_rate_limiter_sliding_window(self):
        config = RateLimitConfig(algorithm="sliding_window")
        limiter = create_rate_limiter(config)

        assert isinstance(limiter, SlidingWindowLimiter)

    def test_create_rate_limiter_fixed_window(self):
        config = RateLimitConfig(algorithm="fixed_window")
        limiter = create_rate_limiter(config)

        assert isinstance(limiter, FixedWindowLimiter)

    def test_create_rate_limiter_invalid_algorithm(self):
        config = RateLimitConfig(algorithm="invalid_algorithm")

        with pytest.raises(ValueError, match="Unknown rate limiting algorithm"):
            create_rate_limiter(config)


class TestRateLimitDecorator:
    """Test rate limiting decorator."""

    @pytest.mark.asyncio
    async def test_rate_limit_decorator_allows_calls(self):
        config = RateLimitConfig(requests_per_minute=10)

        @rate_limit_decorator(config)
        async def test_function(user_id: str):
            return f"Success for {user_id}"

        # Should allow calls
        result = await test_function("user1")
        assert result == "Success for user1"

        result = await test_function("user2")
        assert result == "Success for user2"

    @pytest.mark.asyncio
    async def test_rate_limit_decorator_blocks_calls(self):
        config = RateLimitConfig(requests_per_minute=1, burst_capacity=1)

        @rate_limit_decorator(config, key_func=lambda user_id: user_id)
        async def test_function(user_id: str):
            return f"Success for {user_id}"

        # First call should succeed
        result = await test_function("user1")
        assert result == "Success for user1"

        # Second call should be rate limited
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            await test_function("user1")

        # Different user should still work
        result = await test_function("user2")
        assert result == "Success for user2"

    @pytest.mark.asyncio
    async def test_rate_limit_decorator_custom_key_function(self):
        config = RateLimitConfig(requests_per_minute=2, burst_capacity=1)

        # Custom key function that ignores user_id
        @rate_limit_decorator(config, key_func=lambda *args, **kwargs: "global")
        async def test_function(user_id: str):
            return f"Success for {user_id}"

        # First call should succeed
        await test_function("user1")

        # Second call with different user should still be rate limited
        # because they share the same key ("global")
        with pytest.raises(RateLimitError):
            await test_function("user2")


class TestGlobalRateLimiter:
    """Test global rate limiter functionality."""

    @pytest.mark.asyncio
    async def test_global_rate_limiter_check(self):
        # Use global rate limiter
        result = await check_rate_limit("test_global_user")
        assert isinstance(result, RateLimitResult)
        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_global_rate_limiter_shared_state(self):
        # Multiple calls to global rate limiter should share state
        key = "shared_state_user"

        # Make several requests
        for i in range(5):
            result = await check_rate_limit(key)
            assert result.allowed is True

        # Remaining count should decrease
        assert result.remaining < 100  # Default config allows 100 per minute


class TestRateLimitingIntegration:
    """Test rate limiting integration scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_same_user(self):
        config = RateLimitConfig(requests_per_minute=5, burst_capacity=3)
        store = MemoryRateLimitStore()
        limiter = TokenBucketLimiter(config, store)

        key = "concurrent_user"

        # Send concurrent requests
        tasks = [limiter.check_rate_limit(key) for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # Some should be allowed, some denied
        allowed_count = sum(1 for result in results if result.allowed)
        denied_count = sum(1 for result in results if not result.allowed)

        assert allowed_count <= 3  # Burst capacity
        assert denied_count >= 2  # Excess requests

    @pytest.mark.asyncio
    async def test_different_users_isolated_limits(self):
        config = RateLimitConfig(requests_per_minute=2, burst_capacity=1)
        store = MemoryRateLimitStore()
        limiter = TokenBucketLimiter(config, store)

        # Exhaust limit for user1
        result = await limiter.check_rate_limit("user1")
        assert result.allowed is True

        result = await limiter.check_rate_limit("user1")
        assert result.allowed is False

        # user2 should still have their own limit
        result = await limiter.check_rate_limit("user2")
        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_rate_limit_with_ip_and_user_keys(self):
        config = RateLimitConfig(requests_per_minute=3, burst_capacity=2)
        store = MemoryRateLimitStore()
        limiter = TokenBucketLimiter(config, store)

        # Test different key formats
        ip_key = "ip:192.168.1.1"
        user_key = "user:john_doe"
        combined_key = "ip:192.168.1.1:user:john_doe"

        # Each should have independent limits
        for key in [ip_key, user_key, combined_key]:
            result = await limiter.check_rate_limit(key)
            assert result.allowed is True

            result = await limiter.check_rate_limit(key)
            assert result.allowed is True

            # Third request should be denied
            result = await limiter.check_rate_limit(key)
            assert result.allowed is False


class TestRateLimitErrorHandling:
    """Test error handling in rate limiting."""

    @pytest.mark.asyncio
    async def test_store_error_handling(self):
        # Mock a store that raises exceptions
        store = AsyncMock()
        store.get.side_effect = Exception("Store connection failed")

        config = RateLimitConfig()
        limiter = TokenBucketLimiter(config, store)

        # Should handle store errors gracefully
        with pytest.raises(RateLimitError, match="Rate limiting error"):
            await limiter.check_rate_limit("test_key")

    def test_rate_limit_error_attributes(self):
        error = RateLimitError(
            "Rate limit exceeded",
            retry_after=30,
            remaining=0,
            reset_time=time.time() + 60,
        )

        assert "Rate limit exceeded" in str(error)
        assert error.retry_after == 30
        assert error.remaining == 0
        assert error.reset_time is not None


class TestRateLimitPerformance:
    """Test rate limiting performance characteristics."""

    @pytest.mark.asyncio
    async def test_high_throughput_rate_limiting(self):
        config = RateLimitConfig(requests_per_minute=1000, burst_capacity=100)
        store = MemoryRateLimitStore()
        limiter = TokenBucketLimiter(config, store)

        # Test many concurrent requests
        start_time = time.time()

        tasks = []
        for i in range(100):
            tasks.append(limiter.check_rate_limit(f"user_{i % 10}"))

        results = await asyncio.gather(*tasks)

        execution_time = time.time() - start_time

        # Should complete quickly
        assert execution_time < 1.0

        # Most requests should be allowed
        allowed_count = sum(1 for result in results if result.allowed)
        assert allowed_count >= 50  # At least half should be allowed

    @pytest.mark.asyncio
    async def test_memory_store_cleanup_performance(self):
        store = MemoryRateLimitStore(cleanup_interval=0.1)

        # Add many entries with short TTL
        for i in range(100):
            await store.set(f"key_{i}", {"data": i}, ttl=0.05)

        # Wait for cleanup
        await asyncio.sleep(0.2)
        
        # Force cleanup of expired entries
        await store.force_cleanup()

        # Store should have cleaned up expired entries
        # This is implementation-dependent, but we can check it doesn't grow unbounded
        assert len(store._data) < 100


class TestRateLimitCompliance:
    """Test rate limiting compliance with standards."""

    @pytest.mark.asyncio
    async def test_http_headers_information(self):
        config = RateLimitConfig(requests_per_minute=10)
        store = MemoryRateLimitStore()
        limiter = TokenBucketLimiter(config, store)

        result = await limiter.check_rate_limit("test_user")

        # Should provide information for HTTP headers
        assert result.remaining is not None
        assert result.reset_time is not None

        if not result.allowed:
            assert result.retry_after is not None

    @pytest.mark.asyncio
    async def test_rate_limit_precision(self):
        config = RateLimitConfig(
            requests_per_minute=60, burst_capacity=1
        )  # 1 per second
        store = MemoryRateLimitStore()
        limiter = TokenBucketLimiter(config, store)

        key = "precision_test"

        # First request should succeed
        result = await limiter.check_rate_limit(key)
        assert result.allowed is True

        # Immediate second request should fail
        result = await limiter.check_rate_limit(key)
        assert result.allowed is False

        # Wait almost 1 second
        await asyncio.sleep(0.9)
        result = await limiter.check_rate_limit(key)
        assert result.allowed is False  # Still too early

        # Wait full second
        await asyncio.sleep(0.2)  # Total 1.1 seconds
        result = await limiter.check_rate_limit(key)
        assert result.allowed is True  # Should be allowed now
