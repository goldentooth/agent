"""Comprehensive tests for the Rule class."""

import asyncio
import pytest
from goldentooth_agent.core.rules import Rule
from goldentooth_agent.core.flow import Flow


# Test fixtures - context classes for testing
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

    def __init__(self, name: str, value: int, active: bool = True):
        self.name = name
        self.value = value
        self.active = active

    def __eq__(self, other):
        return (
            isinstance(other, ComplexContext)
            and self.name == other.name
            and self.value == other.value
            and self.active == other.active
        )

    def __repr__(self):
        return f"ComplexContext('{self.name}', {self.value}, {self.active})"


# Test fixtures - condition functions
def is_positive(ctx: NumberContext) -> bool:
    """Check if number context value is positive."""
    return ctx.value > 0


def is_even(ctx: NumberContext) -> bool:
    """Check if number context value is even."""
    return ctx.value % 2 == 0


def value_greater_than_10(ctx: NumberContext) -> bool:
    """Check if number context value is greater than 10."""
    return ctx.value > 10


def is_active(ctx: ComplexContext) -> bool:
    """Check if complex context is active."""
    return ctx.active


def name_starts_with_test(ctx: ComplexContext) -> bool:
    """Check if complex context name starts with 'test'."""
    return ctx.name.startswith("test")


def text_contains_hello(ctx: StringContext) -> bool:
    """Check if string context contains 'hello'."""
    return "hello" in ctx.text.lower()


# Test fixtures - action flows
def create_increment_action() -> Flow[NumberContext, NumberContext]:
    """Create a flow that increments the number context value."""

    async def increment_stream(stream):
        async for ctx in stream:
            yield NumberContext(ctx.value + 1)

    return Flow(increment_stream, name="increment")


def create_double_action() -> Flow[NumberContext, NumberContext]:
    """Create a flow that doubles the number context value."""

    async def double_stream(stream):
        async for ctx in stream:
            yield NumberContext(ctx.value * 2)

    return Flow(double_stream, name="double")


def create_negate_action() -> Flow[NumberContext, NumberContext]:
    """Create a flow that negates the number context value."""

    async def negate_stream(stream):
        async for ctx in stream:
            yield NumberContext(-ctx.value)

    return Flow(negate_stream, name="negate")


def create_activate_action() -> Flow[ComplexContext, ComplexContext]:
    """Create a flow that activates the complex context."""

    async def activate_stream(stream):
        async for ctx in stream:
            yield ComplexContext(ctx.name, ctx.value, True)

    return Flow(activate_stream, name="activate")


def create_uppercase_action() -> Flow[StringContext, StringContext]:
    """Create a flow that uppercases the string context."""

    async def uppercase_stream(stream):
        async for ctx in stream:
            yield StringContext(ctx.text.upper())

    return Flow(uppercase_stream, name="uppercase")


def create_side_effect_action(
    side_effects: list,
) -> Flow[NumberContext, NumberContext]:
    """Create a flow that adds side effects while preserving context."""

    async def side_effect_stream(stream):
        async for ctx in stream:
            side_effects.append(f"processed: {ctx.value}")
            yield ctx

    return Flow(side_effect_stream, name="side_effect")


class TestRuleCreation:
    """Test cases for Rule creation and basic functionality."""

    def test_rule_creation_basic(self):
        """Test creating a basic rule."""
        action = create_increment_action()
        rule = Rule(name="increment_positive", condition=is_positive, action=action)

        assert rule.name == "increment_positive"
        assert rule.condition is is_positive
        assert rule.action is action
        assert rule.priority == 0  # Default priority
        assert rule.description is None  # Default description

    def test_rule_creation_with_priority(self):
        """Test creating a rule with custom priority."""
        action = create_increment_action()
        rule = Rule(
            name="high_priority_rule", condition=is_positive, action=action, priority=10
        )

        assert rule.priority == 10

    def test_rule_creation_with_description(self):
        """Test creating a rule with description."""
        action = create_increment_action()
        rule = Rule(
            name="documented_rule",
            condition=is_positive,
            action=action,
            description="This rule increments positive numbers",
        )

        assert rule.description == "This rule increments positive numbers"

    def test_rule_creation_with_all_parameters(self):
        """Test creating a rule with all parameters."""
        action = create_double_action()
        rule = Rule(
            name="complete_rule",
            condition=is_even,
            action=action,
            priority=5,
            description="Doubles even numbers",
        )

        assert rule.name == "complete_rule"
        assert rule.condition is is_even
        assert rule.action is action
        assert rule.priority == 5
        assert rule.description == "Doubles even numbers"


class TestRuleApply:
    """Test cases for Rule.apply method."""

    @pytest.mark.asyncio
    async def test_apply_condition_true(self):
        """Test applying rule when condition is true."""
        action = create_increment_action()
        rule = Rule(name="increment_positive", condition=is_positive, action=action)

        ctx = NumberContext(5)
        result = await rule.apply(ctx)

        assert result.value == 6  # 5 + 1

    @pytest.mark.asyncio
    async def test_apply_condition_false(self):
        """Test applying rule when condition is false."""
        action = create_increment_action()
        rule = Rule(name="increment_positive", condition=is_positive, action=action)

        ctx = NumberContext(-5)
        result = await rule.apply(ctx)

        assert result.value == -5  # Unchanged because condition is false

    @pytest.mark.asyncio
    async def test_apply_with_even_condition(self):
        """Test applying rule with even number condition."""
        action = create_double_action()
        rule = Rule(name="double_even", condition=is_even, action=action)

        # Test with even number
        ctx_even = NumberContext(4)
        result_even = await rule.apply(ctx_even)
        assert result_even.value == 8  # 4 * 2

        # Test with odd number
        ctx_odd = NumberContext(3)
        result_odd = await rule.apply(ctx_odd)
        assert result_odd.value == 3  # Unchanged

    @pytest.mark.asyncio
    async def test_apply_with_complex_context(self):
        """Test applying rule with complex context."""
        action = create_activate_action()
        rule = Rule(
            name="activate_test_items", condition=name_starts_with_test, action=action
        )

        # Test with matching name
        ctx_match = ComplexContext("test_item", 42, False)
        result_match = await rule.apply(ctx_match)
        assert result_match.active is True

        # Test with non-matching name
        ctx_no_match = ComplexContext("production_item", 42, False)
        result_no_match = await rule.apply(ctx_no_match)
        assert result_no_match.active is False  # Unchanged

    @pytest.mark.asyncio
    async def test_apply_with_string_context(self):
        """Test applying rule with string context."""
        action = create_uppercase_action()
        rule = Rule(
            name="uppercase_hello", condition=text_contains_hello, action=action
        )

        # Test with matching text
        ctx_match = StringContext("Hello World")
        result_match = await rule.apply(ctx_match)
        assert result_match.text == "HELLO WORLD"

        # Test with non-matching text
        ctx_no_match = StringContext("Goodbye World")
        result_no_match = await rule.apply(ctx_no_match)
        assert result_no_match.text == "Goodbye World"  # Unchanged


class TestRuleCall:
    """Test cases for Rule.__call__ method."""

    @pytest.mark.asyncio
    async def test_call_delegates_to_apply(self):
        """Test that __call__ delegates to apply method."""
        action = create_increment_action()
        rule = Rule(name="increment_positive", condition=is_positive, action=action)

        ctx = NumberContext(3)
        result_call = await rule(ctx)
        result_apply = await rule.apply(ctx)

        assert result_call.value == result_apply.value == 4


class TestRuleAsFlow:
    """Test cases for Rule.as_flow method."""

    @pytest.mark.asyncio
    async def test_as_flow_basic(self):
        """Test converting rule to flow."""
        action = create_double_action()
        rule = Rule(
            name="double_positive",
            condition=is_positive,
            action=action,
            priority=5,
            description="Doubles positive numbers",
        )

        flow = rule.as_flow()

        assert flow.name == "double_positive"
        assert isinstance(flow, Flow)

        # Test flow functionality
        async def test_stream():
            yield NumberContext(3)
            yield NumberContext(-3)

        results = []
        async for result in flow(test_stream()):
            results.append(result)

        assert len(results) == 2
        assert results[0].value == 6  # 3 * 2
        assert results[1].value == -3  # Unchanged

    def test_as_flow_metadata(self):
        """Test that as_flow preserves metadata."""
        action = create_increment_action()
        rule = Rule(
            name="increment_even",
            condition=is_even,
            action=action,
            priority=10,
            description="Increments even numbers",
        )

        flow = rule.as_flow()

        assert flow.metadata["condition"] == "is_even"
        assert flow.metadata["action"] == "increment"
        assert flow.metadata["priority"] == 10
        assert flow.metadata["description"] == "Increments even numbers"

    def test_as_flow_metadata_with_lambda(self):
        """Test as_flow metadata with lambda condition."""
        action = create_increment_action()
        rule = Rule(name="lambda_rule", condition=lambda x: x.value > 5, action=action)

        flow = rule.as_flow()

        assert flow.metadata["condition"] == "<lambda>"
        assert flow.metadata["action"] == "increment"


class TestRuleChaining:
    """Test cases for chaining rules and complex scenarios."""

    @pytest.mark.asyncio
    async def test_multiple_rules_sequence(self):
        """Test applying multiple rules in sequence."""
        increment_action = create_increment_action()
        double_action = create_double_action()

        # Rule 1: Increment if positive
        rule1 = Rule(
            name="increment_positive", condition=is_positive, action=increment_action
        )

        # Rule 2: Double if even
        rule2 = Rule(name="double_even", condition=is_even, action=double_action)

        ctx = NumberContext(3)  # Positive and odd

        # Apply rule 1: 3 -> 4 (incremented)
        ctx = await rule1.apply(ctx)
        assert ctx.value == 4

        # Apply rule 2: 4 -> 8 (doubled because now even)
        ctx = await rule2.apply(ctx)
        assert ctx.value == 8

    @pytest.mark.asyncio
    async def test_rule_with_side_effects(self):
        """Test rule that produces side effects."""
        side_effects = []
        action = create_side_effect_action(side_effects)

        rule = Rule(name="side_effect_rule", condition=is_positive, action=action)

        ctx_positive = NumberContext(5)
        result_positive = await rule.apply(ctx_positive)

        assert result_positive.value == 5  # Unchanged
        assert side_effects == ["processed: 5"]

        ctx_negative = NumberContext(-5)
        result_negative = await rule.apply(ctx_negative)

        assert result_negative.value == -5  # Unchanged
        assert side_effects == ["processed: 5"]  # No new side effect


class TestRuleEdgeCases:
    """Test edge cases and error conditions for Rule."""

    @pytest.mark.asyncio
    async def test_rule_with_zero_value(self):
        """Test rule behavior with zero value."""
        action = create_increment_action()
        rule = Rule(name="increment_positive", condition=is_positive, action=action)

        ctx = NumberContext(0)
        result = await rule.apply(ctx)

        assert result.value == 0  # Zero is not positive, so no change

    @pytest.mark.asyncio
    async def test_rule_with_large_numbers(self):
        """Test rule behavior with large numbers."""
        action = create_double_action()
        rule = Rule(name="double_large", condition=value_greater_than_10, action=action)

        ctx = NumberContext(1000000)
        result = await rule.apply(ctx)

        assert result.value == 2000000

    @pytest.mark.asyncio
    async def test_rule_with_negative_priority(self):
        """Test rule with negative priority."""
        action = create_increment_action()
        rule = Rule(
            name="negative_priority", condition=is_positive, action=action, priority=-5
        )

        assert rule.priority == -5

        ctx = NumberContext(3)
        result = await rule.apply(ctx)
        assert result.value == 4  # Still works normally

    @pytest.mark.asyncio
    async def test_rule_condition_exception(self):
        """Test rule behavior when condition raises exception."""

        def failing_condition(ctx: NumberContext) -> bool:
            if ctx.value == 99:
                raise ValueError("Special value not allowed")
            return ctx.value > 0

        action = create_increment_action()
        rule = Rule(
            name="failing_condition_rule", condition=failing_condition, action=action
        )

        # Normal case should work
        ctx_normal = NumberContext(5)
        result_normal = await rule.apply(ctx_normal)
        assert result_normal.value == 6

        # Exception case should propagate
        ctx_exception = NumberContext(99)
        with pytest.raises(ValueError, match="Special value not allowed"):
            await rule.apply(ctx_exception)

    @pytest.mark.asyncio
    async def test_rule_action_exception(self):
        """Test rule behavior when action raises exception."""

        @Flow.from_value_fn
        async def failing_action(ctx: NumberContext) -> NumberContext:
            if ctx.value == 99:
                raise RuntimeError("Action failed")
            return NumberContext(ctx.value + 1)

        action = failing_action
        rule = Rule(name="failing_action_rule", condition=is_positive, action=action)

        # Normal case should work
        ctx_normal = NumberContext(5)
        result_normal = await rule.apply(ctx_normal)
        assert result_normal.value == 6

        # Exception case should propagate
        ctx_exception = NumberContext(99)
        with pytest.raises(RuntimeError, match="Action failed"):
            await rule.apply(ctx_exception)


class TestRuleIntegration:
    """Integration tests for Rule with different flow types."""

    @pytest.mark.asyncio
    async def test_rule_with_complex_flow_chain(self):
        """Test rule with complex flow action chain."""
        # Create a complex action that increments then doubles using flow composition
        increment_flow = create_increment_action()
        double_flow = create_double_action()
        complex_action = increment_flow >> double_flow

        rule = Rule(
            name="increment_then_double", condition=is_positive, action=complex_action
        )

        ctx = NumberContext(3)
        result = await rule.apply(ctx)

        assert result.value == 8  # (3 + 1) * 2

    @pytest.mark.asyncio
    async def test_rule_flow_integration(self):
        """Test that rule as flow integrates well with flow operations."""
        action = create_double_action()
        rule = Rule(name="double_positive", condition=is_positive, action=action)

        rule_flow = rule.as_flow()

        # Compose the rule flow with another flow
        increment_flow = create_increment_action()
        composed = rule_flow >> increment_flow

        async def test_stream():
            yield NumberContext(3)

        results = []
        async for result in composed(test_stream()):
            results.append(result)

        assert len(results) == 1
        assert results[0].value == 7  # (3 * 2) + 1

    def test_rule_repr(self):
        """Test string representation of Rule."""
        action = create_increment_action()
        rule = Rule(
            name="test_rule",
            condition=is_positive,
            action=action,
            priority=5,
            description="Test rule",
        )

        # Rule uses dataclass representation
        repr_str = repr(rule)
        assert "Rule" in repr_str
        assert "test_rule" in repr_str
        assert "5" in repr_str  # priority


class TestRulePerformance:
    """Performance and stress tests for Rule."""

    @pytest.mark.asyncio
    async def test_rule_performance_many_applications(self):
        """Test rule performance with many applications."""
        action = create_increment_action()
        rule = Rule(name="performance_rule", condition=is_positive, action=action)

        # Apply rule many times
        ctx = NumberContext(1)
        for _ in range(100):
            ctx = await rule.apply(ctx)

        assert ctx.value == 101  # Started at 1, incremented 100 times

    @pytest.mark.asyncio
    async def test_rule_with_async_heavy_action(self):
        """Test rule with async action that has delays."""

        @Flow.from_value_fn
        async def slow_action(ctx: NumberContext) -> NumberContext:
            await asyncio.sleep(0.001)  # Small delay
            return NumberContext(ctx.value * 2)

        action = slow_action
        rule = Rule(name="slow_rule", condition=is_positive, action=action)

        ctx = NumberContext(3)
        result = await rule.apply(ctx)

        assert result.value == 6
