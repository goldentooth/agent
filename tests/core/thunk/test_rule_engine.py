"""Comprehensive tests for the RuleEngine class."""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from goldentooth_agent.core.thunk import Rule, RuleEngine, Thunk


# Test fixtures - context classes for testing (reused from Rule tests)
class NumberContext:
    """Simple numeric context for testing."""

    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, NumberContext) and self.value == other.value

    def __repr__(self):
        return f"NumberContext({self.value})"


class StringContext:
    """Simple string context for testing."""

    def __init__(self, text: str):
        self.text = text

    def __eq__(self, other):
        return isinstance(other, StringContext) and self.text == other.text

    def __repr__(self):
        return f"StringContext('{self.text}')"


class ComplexContext:
    """Complex context with multiple fields for testing."""

    def __init__(self, name: str, value: int, active: bool = True, tags: list = None):
        self.name = name
        self.value = value
        self.active = active
        self.tags = tags or []

    def __eq__(self, other):
        return (
            isinstance(other, ComplexContext)
            and self.name == other.name
            and self.value == other.value
            and self.active == other.active
            and self.tags == other.tags
        )

    def __repr__(self):
        return (
            f"ComplexContext('{self.name}', {self.value}, {self.active}, {self.tags})"
        )


# Test fixtures - condition functions
def is_positive(ctx: NumberContext) -> bool:
    """Check if number context value is positive."""
    return ctx.value > 0


def is_even(ctx: NumberContext) -> bool:
    """Check if number context value is even."""
    return ctx.value % 2 == 0


def is_greater_than_5(ctx: NumberContext) -> bool:
    """Check if number context value is greater than 5."""
    return ctx.value > 5


def is_greater_than_10(ctx: NumberContext) -> bool:
    """Check if number context value is greater than 10."""
    return ctx.value > 10


def value_less_than_100(ctx: NumberContext) -> bool:
    """Check if number context value is less than 100."""
    return ctx.value < 100


def is_active(ctx: ComplexContext) -> bool:
    """Check if complex context is active."""
    return ctx.active


def name_starts_with_test(ctx: ComplexContext) -> bool:
    """Check if complex context name starts with 'test'."""
    return ctx.name.startswith("test")


def has_urgent_tag(ctx: ComplexContext) -> bool:
    """Check if complex context has 'urgent' tag."""
    return "urgent" in ctx.tags


# Test fixtures - action thunks
def create_increment_action() -> Thunk[NumberContext, NumberContext]:
    """Create a thunk that increments the number context value."""

    async def increment(ctx: NumberContext) -> NumberContext:
        return NumberContext(ctx.value + 1)

    return Thunk(increment, name="increment")


def create_double_action() -> Thunk[NumberContext, NumberContext]:
    """Create a thunk that doubles the number context value."""

    async def double(ctx: NumberContext) -> NumberContext:
        return NumberContext(ctx.value * 2)

    return Thunk(double, name="double")


def create_negate_action() -> Thunk[NumberContext, NumberContext]:
    """Create a thunk that negates the number context value."""

    async def negate(ctx: NumberContext) -> NumberContext:
        return NumberContext(-ctx.value)

    return Thunk(negate, name="negate")


def create_add_5_action() -> Thunk[NumberContext, NumberContext]:
    """Create a thunk that adds 5 to the number context value."""

    async def add_5(ctx: NumberContext) -> NumberContext:
        return NumberContext(ctx.value + 5)

    return Thunk(add_5, name="add_5")


def create_multiply_by_3_action() -> Thunk[NumberContext, NumberContext]:
    """Create a thunk that multiplies the number context value by 3."""

    async def multiply_by_3(ctx: NumberContext) -> NumberContext:
        return NumberContext(ctx.value * 3)

    return Thunk(multiply_by_3, name="multiply_by_3")


def create_deactivate_action() -> Thunk[ComplexContext, ComplexContext]:
    """Create a thunk that deactivates the complex context."""

    async def deactivate(ctx: ComplexContext) -> ComplexContext:
        return ComplexContext(ctx.name, ctx.value, False, ctx.tags)

    return Thunk(deactivate, name="deactivate")


def create_add_tag_action(tag: str) -> Thunk[ComplexContext, ComplexContext]:
    """Create a thunk that adds a tag to the complex context."""

    async def add_tag(ctx: ComplexContext) -> ComplexContext:
        new_tags = ctx.tags + [tag] if tag not in ctx.tags else ctx.tags
        return ComplexContext(ctx.name, ctx.value, ctx.active, new_tags)

    return Thunk(add_tag, name=f"add_tag_{tag}")


def create_side_effect_action(
    side_effects: list,
) -> Thunk[NumberContext, NumberContext]:
    """Create a thunk that adds side effects while preserving context."""

    async def side_effect(ctx: NumberContext) -> NumberContext:
        side_effects.append(f"processed: {ctx.value}")
        return ctx

    return Thunk(side_effect, name="side_effect")


# Test fixtures - rule creation helpers
def create_increment_positive_rule(priority: int = 0) -> Rule[NumberContext]:
    """Create a rule that increments positive numbers."""
    return Rule(
        name="increment_positive",
        condition=is_positive,
        action=create_increment_action(),
        priority=priority,
        description="Increments positive numbers",
    )


def create_double_even_rule(priority: int = 0) -> Rule[NumberContext]:
    """Create a rule that doubles even numbers."""
    return Rule(
        name="double_even",
        condition=is_even,
        action=create_double_action(),
        priority=priority,
        description="Doubles even numbers",
    )


def create_negate_greater_than_10_rule(priority: int = 0) -> Rule[NumberContext]:
    """Create a rule that negates numbers greater than 10."""
    return Rule(
        name="negate_greater_than_10",
        condition=is_greater_than_10,
        action=create_negate_action(),
        priority=priority,
        description="Negates numbers greater than 10",
    )


class TestRuleEngineCreation:
    """Test cases for RuleEngine creation and basic functionality."""

    def test_rule_engine_creation_empty(self):
        """Test creating an empty rule engine."""
        engine = RuleEngine([])

        assert engine.rules == []

    def test_rule_engine_creation_single_rule(self):
        """Test creating a rule engine with a single rule."""
        rule = create_increment_positive_rule()
        engine = RuleEngine([rule])

        assert len(engine.rules) == 1
        assert engine.rules[0] is rule

    def test_rule_engine_creation_multiple_rules(self):
        """Test creating a rule engine with multiple rules."""
        rule1 = create_increment_positive_rule()
        rule2 = create_double_even_rule()
        rule3 = create_negate_greater_than_10_rule()

        engine = RuleEngine([rule1, rule2, rule3])

        assert len(engine.rules) == 3
        assert rule1 in engine.rules
        assert rule2 in engine.rules
        assert rule3 in engine.rules

    def test_rule_engine_sorts_by_priority(self):
        """Test that rule engine sorts rules by priority (highest first)."""
        rule_low = create_increment_positive_rule(priority=1)
        rule_high = create_double_even_rule(priority=10)
        rule_medium = create_negate_greater_than_10_rule(priority=5)

        engine = RuleEngine([rule_low, rule_high, rule_medium])

        # Should be sorted by priority (highest first)
        assert engine.rules[0] is rule_high  # priority 10
        assert engine.rules[1] is rule_medium  # priority 5
        assert engine.rules[2] is rule_low  # priority 1

    def test_rule_engine_handles_same_priority(self):
        """Test rule engine behavior with rules of same priority."""
        rule1 = create_increment_positive_rule(priority=5)
        rule2 = create_double_even_rule(priority=5)
        rule3 = create_negate_greater_than_10_rule(priority=10)

        engine = RuleEngine([rule1, rule2, rule3])

        # Rule3 should be first (priority 10), rule1 and rule2 order preserved
        assert engine.rules[0] is rule3  # priority 10
        assert len(engine.rules) == 3


class TestRuleEngineEvaluate:
    """Test cases for RuleEngine.evaluate method."""

    @pytest.mark.asyncio
    async def test_evaluate_empty_engine(self):
        """Test evaluating with empty rule engine."""
        engine = RuleEngine([])

        ctx = NumberContext(5)
        result = await engine.evaluate(ctx)

        assert result.value == 5  # Unchanged

    @pytest.mark.asyncio
    async def test_evaluate_single_rule_applies(self):
        """Test evaluating with single rule that applies."""
        rule = create_increment_positive_rule()
        engine = RuleEngine([rule])

        ctx = NumberContext(3)
        result = await engine.evaluate(ctx)

        assert result.value == 4  # 3 + 1

    @pytest.mark.asyncio
    async def test_evaluate_single_rule_does_not_apply(self):
        """Test evaluating with single rule that doesn't apply."""
        rule = create_increment_positive_rule()
        engine = RuleEngine([rule])

        ctx = NumberContext(-3)
        result = await engine.evaluate(ctx)

        assert result.value == -3  # Unchanged

    @pytest.mark.asyncio
    async def test_evaluate_multiple_rules_sequential(self):
        """Test evaluating with multiple rules applied sequentially."""
        rule1 = create_increment_positive_rule(priority=2)
        rule2 = create_double_even_rule(priority=1)

        engine = RuleEngine([rule1, rule2])

        ctx = NumberContext(3)  # Positive and odd
        result = await engine.evaluate(ctx)

        # Rule1 first (higher priority): 3 -> 4 (increment)
        # Rule2 second: 4 -> 8 (double, because 4 is even)
        assert result.value == 8

    @pytest.mark.asyncio
    async def test_evaluate_rules_priority_order(self):
        """Test that rules are evaluated in priority order."""
        # Create rules with different outcomes based on order
        add_5_rule = Rule(
            name="add_5",
            condition=is_positive,
            action=create_add_5_action(),
            priority=10,
        )

        multiply_by_3_rule = Rule(
            name="multiply_by_3",
            condition=is_positive,
            action=create_multiply_by_3_action(),
            priority=5,
        )

        engine = RuleEngine(
            [multiply_by_3_rule, add_5_rule]
        )  # Added in reverse priority order

        ctx = NumberContext(2)
        result = await engine.evaluate(ctx)

        # Should execute add_5 first (priority 10): 2 -> 7
        # Then multiply_by_3 (priority 5): 7 -> 21
        assert result.value == 21

    @pytest.mark.asyncio
    async def test_evaluate_complex_rule_chain(self):
        """Test evaluating complex chain of rules."""
        rule1 = create_increment_positive_rule(priority=3)
        rule2 = create_double_even_rule(priority=2)
        rule3 = create_negate_greater_than_10_rule(priority=1)

        engine = RuleEngine([rule1, rule2, rule3])

        ctx = NumberContext(5)  # Positive and odd
        result = await engine.evaluate(ctx)

        # Rule1: 5 -> 6 (increment because positive)
        # Rule2: 6 -> 12 (double because even)
        # Rule3: 12 -> -12 (negate because > 10)
        assert result.value == -12

    @pytest.mark.asyncio
    async def test_evaluate_with_complex_context(self):
        """Test evaluating with complex context type."""
        deactivate_rule = Rule(
            name="deactivate_test",
            condition=name_starts_with_test,
            action=create_deactivate_action(),
            priority=2,
        )

        add_processed_tag_rule = Rule(
            name="add_processed_tag",
            condition=is_active,
            action=create_add_tag_action("processed"),
            priority=1,
        )

        engine = RuleEngine([deactivate_rule, add_processed_tag_rule])

        ctx = ComplexContext("test_item", 42, True, ["initial"])
        result = await engine.evaluate(ctx)

        # First (priority 2): deactivate because name starts with "test"
        # Second (priority 1): doesn't apply because no longer active
        assert result.active is False
        assert result.tags == ["initial"]  # No "processed" tag added

    @pytest.mark.asyncio
    async def test_evaluate_some_rules_apply(self):
        """Test evaluating where only some rules apply."""
        increment_rule = create_increment_positive_rule(priority=3)
        double_even_rule = create_double_even_rule(priority=2)
        negate_rule = create_negate_greater_than_10_rule(priority=1)

        engine = RuleEngine([increment_rule, double_even_rule, negate_rule])

        ctx = NumberContext(2)  # Positive and even, but not > 10
        result = await engine.evaluate(ctx)

        # Rule1: 2 -> 3 (increment because positive)
        # Rule2: 3 unchanged (not even anymore)
        # Rule3: 3 unchanged (not > 10)
        assert result.value == 3


class TestRuleEngineCall:
    """Test cases for RuleEngine.__call__ method."""

    @pytest.mark.asyncio
    async def test_call_delegates_to_evaluate(self):
        """Test that __call__ delegates to evaluate method."""
        rule = create_increment_positive_rule()
        engine = RuleEngine([rule])

        ctx = NumberContext(5)
        result_call = await engine(ctx)
        result_evaluate = await engine.evaluate(ctx)

        assert result_call.value == result_evaluate.value == 6


class TestRuleEngineAddRule:
    """Test cases for RuleEngine.add_rule method."""

    @pytest.mark.asyncio
    async def test_add_rule_to_empty_engine(self):
        """Test adding rule to empty engine."""
        engine = RuleEngine([])
        rule = create_increment_positive_rule()

        engine.add_rule(rule)

        assert len(engine.rules) == 1
        assert engine.rules[0] is rule

    @pytest.mark.asyncio
    async def test_add_rule_maintains_priority_order(self):
        """Test that adding rule maintains priority order."""
        rule1 = create_increment_positive_rule(priority=5)
        rule2 = create_double_even_rule(priority=10)
        engine = RuleEngine([rule1])

        engine.add_rule(rule2)

        assert len(engine.rules) == 2
        assert engine.rules[0] is rule2  # Higher priority first
        assert engine.rules[1] is rule1

    @pytest.mark.asyncio
    async def test_add_rule_and_evaluate(self):
        """Test adding rule and then evaluating."""
        rule1 = create_increment_positive_rule(priority=2)
        engine = RuleEngine([rule1])

        # Add second rule
        rule2 = create_double_even_rule(priority=1)
        engine.add_rule(rule2)

        ctx = NumberContext(3)
        result = await engine.evaluate(ctx)

        # Rule1: 3 -> 4 (increment)
        # Rule2: 4 -> 8 (double)
        assert result.value == 8

    @pytest.mark.asyncio
    async def test_add_multiple_rules_sequentially(self):
        """Test adding multiple rules sequentially."""
        engine = RuleEngine([])

        rule1 = create_increment_positive_rule(priority=1)
        rule2 = create_double_even_rule(priority=3)
        rule3 = create_negate_greater_than_10_rule(priority=2)

        engine.add_rule(rule1)
        engine.add_rule(rule2)
        engine.add_rule(rule3)

        # Should be sorted by priority
        assert engine.rules[0] is rule2  # priority 3
        assert engine.rules[1] is rule3  # priority 2
        assert engine.rules[2] is rule1  # priority 1


class TestRuleEngineAsThunk:
    """Test cases for RuleEngine.as_thunk method."""

    @pytest.mark.asyncio
    async def test_as_thunk_basic(self):
        """Test converting rule engine to thunk."""
        rule1 = create_increment_positive_rule()
        rule2 = create_double_even_rule()
        engine = RuleEngine([rule1, rule2])

        thunk = engine.as_thunk()

        assert thunk.name == "RuleEngine"
        assert isinstance(thunk, Thunk)

        # Test thunk functionality
        ctx = NumberContext(3)
        result = await thunk(ctx)

        # Should behave same as engine.evaluate
        expected = await engine.evaluate(NumberContext(3))
        assert result.value == expected.value

    def test_as_thunk_metadata(self):
        """Test that as_thunk includes metadata."""
        rule1 = create_increment_positive_rule()
        rule2 = create_double_even_rule()
        rule3 = create_negate_greater_than_10_rule()
        engine = RuleEngine([rule1, rule2, rule3])

        thunk = engine.as_thunk()

        assert thunk.metadata["rules"] == [
            "increment_positive",
            "double_even",
            "negate_greater_than_10",
        ]
        assert thunk.metadata["count"] == 3

    def test_as_thunk_empty_engine_metadata(self):
        """Test as_thunk metadata for empty engine."""
        engine = RuleEngine([])
        thunk = engine.as_thunk()

        assert thunk.metadata["rules"] == []
        assert thunk.metadata["count"] == 0

    @pytest.mark.asyncio
    async def test_as_thunk_integration_with_other_thunks(self):
        """Test that rule engine thunk integrates with other thunks."""
        rule = create_double_even_rule()
        engine = RuleEngine([rule])
        engine_thunk = engine.as_thunk()

        # Chain with another thunk
        increment_thunk = create_increment_action()
        chained = engine_thunk.chain(increment_thunk)

        ctx = NumberContext(4)  # Even number
        result = await chained(ctx)

        # Engine: 4 -> 8 (double even)
        # Increment: 8 -> 9
        assert result.value == 9


class TestRuleEngineSideEffects:
    """Test cases for side effects and logging in RuleEngine."""

    @pytest.mark.asyncio
    async def test_rule_engine_with_side_effects(self):
        """Test rule engine with rules that have side effects."""
        side_effects = []

        side_effect_rule = Rule(
            name="side_effect_rule",
            condition=is_positive,
            action=create_side_effect_action(side_effects),
            priority=2,
        )

        increment_rule = create_increment_positive_rule(priority=1)

        engine = RuleEngine([side_effect_rule, increment_rule])

        ctx = NumberContext(5)
        result = await engine.evaluate(ctx)

        assert result.value == 6  # 5 + 1
        assert side_effects == ["processed: 5"]

    @pytest.mark.asyncio
    async def test_rule_engine_multiple_side_effects(self):
        """Test rule engine with multiple side effect rules."""
        side_effects1 = []
        side_effects2 = []

        side_effect_rule1 = Rule(
            name="side_effect_1",
            condition=is_positive,
            action=create_side_effect_action(side_effects1),
            priority=3,
        )

        side_effect_rule2 = Rule(
            name="side_effect_2",
            condition=lambda ctx: ctx.value > 5,
            action=create_side_effect_action(side_effects2),
            priority=1,
        )

        increment_rule = create_increment_positive_rule(priority=2)

        engine = RuleEngine([side_effect_rule1, increment_rule, side_effect_rule2])

        ctx = NumberContext(7)
        result = await engine.evaluate(ctx)

        assert result.value == 8  # 7 + 1
        assert side_effects1 == ["processed: 7"]
        assert side_effects2 == ["processed: 8"]  # After increment


class TestRuleEngineEdgeCases:
    """Test edge cases and error conditions for RuleEngine."""

    @pytest.mark.asyncio
    async def test_rule_engine_with_zero_priority_rules(self):
        """Test rule engine with all zero priority rules."""
        rule1 = create_increment_positive_rule(priority=0)
        rule2 = create_double_even_rule(priority=0)
        rule3 = create_negate_greater_than_10_rule(priority=0)

        engine = RuleEngine([rule1, rule2, rule3])

        ctx = NumberContext(5)
        result = await engine.evaluate(ctx)

        # All have same priority, so order of addition is preserved
        # Rule1: 5 -> 6, Rule2: 6 -> 12, Rule3: 12 -> -12
        assert result.value == -12

    @pytest.mark.asyncio
    async def test_rule_engine_with_negative_priorities(self):
        """Test rule engine with negative priority rules."""
        rule1 = create_increment_positive_rule(priority=-1)
        rule2 = create_double_even_rule(priority=-5)
        rule3 = create_negate_greater_than_10_rule(priority=0)

        engine = RuleEngine([rule1, rule2, rule3])

        # Should be sorted: rule3 (0), rule1 (-1), rule2 (-5)
        assert engine.rules[0].priority == 0
        assert engine.rules[1].priority == -1
        assert engine.rules[2].priority == -5

    @pytest.mark.asyncio
    async def test_rule_engine_exception_handling(self):
        """Test rule engine behavior when a rule raises exception."""

        def failing_condition(ctx: NumberContext) -> bool:
            if ctx.value == 99:
                raise ValueError("Special condition failure")
            return ctx.value > 0

        failing_rule = Rule(
            name="failing_rule",
            condition=failing_condition,
            action=create_increment_action(),
            priority=2,
        )

        normal_rule = create_double_even_rule(priority=1)
        engine = RuleEngine([failing_rule, normal_rule])

        # Normal case should work
        ctx_normal = NumberContext(4)
        result_normal = await engine.evaluate(ctx_normal)
        assert (
            result_normal.value == 5
        )  # 4 + 1 (failing_rule applies), then 4 is no longer even so double_rule doesn't apply

        # Exception case should propagate
        ctx_exception = NumberContext(99)
        with pytest.raises(ValueError, match="Special condition failure"):
            await engine.evaluate(ctx_exception)

    @pytest.mark.asyncio
    async def test_rule_engine_action_exception(self):
        """Test rule engine behavior when a rule action raises exception."""

        async def failing_action(ctx: NumberContext) -> NumberContext:
            raise RuntimeError("Action failed")

        failing_rule = Rule(
            name="failing_action_rule",
            condition=is_positive,
            action=Thunk(failing_action, name="failing_action"),
            priority=2,
        )

        normal_rule = create_increment_positive_rule(priority=1)
        engine = RuleEngine([failing_rule, normal_rule])

        ctx = NumberContext(5)
        with pytest.raises(RuntimeError, match="Action failed"):
            await engine.evaluate(ctx)

    @pytest.mark.asyncio
    async def test_rule_engine_with_large_number_of_rules(self):
        """Test rule engine performance with many rules."""
        rules = []
        for i in range(50):
            rule = Rule(
                name=f"rule_{i}",
                condition=lambda ctx, threshold=i: ctx.value > threshold,
                action=create_increment_action(),
                priority=i,
            )
            rules.append(rule)

        engine = RuleEngine(rules)

        ctx = NumberContext(25)
        result = await engine.evaluate(ctx)

        # Rules with priority 49 down to 26 will apply (conditions: value > 49 down to value > 26 won't apply)
        # Rules with priority 25 down to 0 will apply (conditions: value > 25 down to value > 0)
        # That's 25 rules that will increment (value starts at 25, so rules 0-24 apply)
        assert result.value == 25 + 25  # 50


class TestRuleEngineIntegration:
    """Integration tests for RuleEngine with different scenarios."""

    @pytest.mark.asyncio
    async def test_rule_engine_complex_business_logic(self):
        """Test rule engine with complex business logic scenario."""
        # Business rules for processing items

        # High priority: Security rules
        security_rule = Rule(
            name="security_check",
            condition=lambda ctx: "sensitive" in ctx.tags,
            action=create_add_tag_action("secured"),
            priority=100,
        )

        # Medium priority: Processing rules
        urgent_rule = Rule(
            name="urgent_processing",
            condition=has_urgent_tag,
            action=create_add_tag_action("fast_track"),
            priority=50,
        )

        # Low priority: Cleanup rules
        deactivate_rule = Rule(
            name="deactivate_test",
            condition=name_starts_with_test,
            action=create_deactivate_action(),
            priority=10,
        )

        engine = RuleEngine([security_rule, urgent_rule, deactivate_rule])

        ctx = ComplexContext("test_document", 42, True, ["urgent", "sensitive"])
        result = await engine.evaluate(ctx)

        # Security rule: adds "secured" tag
        # Urgent rule: adds "fast_track" tag
        # Deactivate rule: deactivates the context
        assert "secured" in result.tags
        assert "fast_track" in result.tags
        assert result.active is False

    @pytest.mark.asyncio
    async def test_rule_engine_mathematical_processing(self):
        """Test rule engine for mathematical processing pipeline."""
        # Rules for mathematical transformations

        # If negative, make positive
        abs_rule = Rule(
            name="absolute_value",
            condition=lambda ctx: ctx.value < 0,
            action=create_negate_action(),
            priority=10,
        )

        # If even, double it
        double_even_rule = create_double_even_rule(priority=5)

        # If result > 20, divide by 2 (approximate with multiply by 0.5)
        divide_large_rule = Rule(
            name="divide_large",
            condition=lambda ctx: ctx.value > 20,
            action=Thunk(lambda ctx: NumberContext(ctx.value // 2), name="divide_by_2"),
            priority=1,
        )

        engine = RuleEngine([abs_rule, double_even_rule, divide_large_rule])

        ctx = NumberContext(-6)
        result = await engine.evaluate(ctx)

        # abs: -6 -> 6
        # double_even: 6 -> 12
        # divide_large: 12 -> 6 (12 is not > 20)
        assert result.value == 12

    @pytest.mark.asyncio
    async def test_rule_engine_nested_with_thunk_operations(self):
        """Test rule engine integration with thunk operations."""
        rule1 = create_increment_positive_rule()
        rule2 = create_double_even_rule()
        engine = RuleEngine([rule1, rule2])

        engine_thunk = engine.as_thunk()

        # Create a complex thunk chain
        final_thunk = engine_thunk.map(
            lambda ctx: NumberContext(ctx.value + 10)
        ).filter(lambda ctx: ctx.value > 15)

        ctx = NumberContext(3)
        result = await final_thunk(ctx)

        # Engine: 3 -> 4 -> 8 (increment then double)
        # Map: 8 -> 18
        # Filter: 18 > 15, so passes through
        assert result.value == 18

    def test_rule_engine_repr(self):
        """Test string representation of RuleEngine."""
        rule1 = create_increment_positive_rule()
        rule2 = create_double_even_rule()
        engine = RuleEngine([rule1, rule2])

        # RuleEngine should have a meaningful representation
        repr_str = repr(engine)
        assert "RuleEngine" in repr_str


class TestRuleEnginePerformance:
    """Performance tests for RuleEngine."""

    @pytest.mark.asyncio
    async def test_rule_engine_performance_many_evaluations(self):
        """Test rule engine performance with many evaluations."""
        rule = create_increment_positive_rule()
        engine = RuleEngine([rule])

        ctx = NumberContext(1)
        for _ in range(100):
            ctx = await engine.evaluate(ctx)

        assert ctx.value == 101

    @pytest.mark.asyncio
    async def test_rule_engine_performance_concurrent_evaluations(self):
        """Test rule engine with concurrent evaluations."""
        rule1 = create_increment_positive_rule(
            priority=1
        )  # Lower priority, applied second
        rule2 = create_double_even_rule(priority=2)  # Higher priority, applied first
        engine = RuleEngine([rule1, rule2])

        # Run multiple evaluations concurrently
        contexts = [NumberContext(i) for i in range(1, 11)]

        tasks = [engine.evaluate(ctx) for ctx in contexts]
        results = await asyncio.gather(*tasks)

        # Verify results
        for i, result in enumerate(results, 1):
            if (
                i % 2 == 1
            ):  # Odd numbers: double_even doesn't apply, then increment applies
                expected = i + 1  # Just incremented
            else:  # Even numbers: double_even applies first, then increment applies to the result
                expected = (i * 2) + 1  # Doubled then incremented
            assert result.value == expected
