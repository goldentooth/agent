"""Demonstration of Flow-Context integration with type-safe keys and expressive dependency declarations."""

from goldentooth_agent.core.context import (
    Context,
    ContextKey,
    MissingRequiredKeyError,
    context_flow,
)
from goldentooth_agent.core.flow import Flow


def main():
    """Demonstrate the power and expressiveness of Flow-Context integration."""

    # Create type-safe context keys
    user_name = ContextKey.create("user_name", str, "The user's name")
    user_age = ContextKey.create("user_age", int, "The user's age")
    greeting = ContextKey.create("greeting", str, "A personalized greeting")
    status = ContextKey.create("status", str, "Processing status")

    print("🔧 Flow-Context Integration Demo")
    print("=" * 40)

    # 1. Basic key operations
    print("\n1. Basic Context Key Operations")
    context = Context()

    # Set values using flows
    set_name_flow = Flow.set_key(user_name, "Alice")
    set_age_flow = Flow.set_key(user_age, 30)

    context = set_name_flow.run(context)
    context = set_age_flow.run(context)

    print(f"   Set name: {context['user_name']}")
    print(f"   Set age: {context['user_age']}")

    # Get values using flows
    get_name_flow = Flow.get_key(user_name)
    get_age_flow = Flow.get_key(user_age)

    name = get_name_flow.run(context)
    age = get_age_flow.run(context)

    print(f"   Retrieved name: {name}")
    print(f"   Retrieved age: {age}")

    # 2. Required vs Optional keys
    print("\n2. Required vs Optional Key Validation")

    # Optional key with default
    nickname_key = ContextKey.create("nickname", str, "User's nickname")
    optional_flow = Flow.optional_key(nickname_key, "Anonymous")
    nickname = optional_flow.run(context)
    print(f"   Nickname (with default): {nickname}")

    # Required key validation
    try:
        missing_key = ContextKey.create("missing", str, "A missing key")
        require_flow = Flow.require_key(missing_key)
        require_flow.run(context)
    except MissingRequiredKeyError as e:
        print(f"   ✓ Caught expected error: {e}")

    # 3. Context manipulation combinators
    print("\n3. Context Manipulation Combinators")

    # Copy a key
    display_name = ContextKey.create("display_name", str, "Display name")
    copy_flow = Flow.copy_key(user_name, display_name)
    context = copy_flow.run(context)
    print(f"   Copied name to display_name: {context['display_name']}")

    # Transform a key value
    upper_name = ContextKey.create("upper_name", str, "Uppercase name")
    transform_flow = Flow.transform_key(
        user_name, lambda name: name.upper(), upper_name
    )
    context = transform_flow.run(context)
    print(f"   Transformed to uppercase: {context['upper_name']}")

    # Move a key
    final_name = ContextKey.create("final_name", str, "Final name")
    move_flow = Flow.move_key(display_name, final_name)
    context = move_flow.run(context)
    print(f"   Moved display_name to final_name: {context['final_name']}")
    print(f"   display_name removed: {'display_name' not in context}")

    # 4. Declarative context-aware flows
    print("\n4. Declarative Context-Aware Flows")

    @context_flow(
        inputs=[user_name, user_age], outputs=[greeting], name="create_greeting"
    )
    def create_personalized_greeting(ctx: Context) -> Context:
        """Create a personalized greeting based on user data."""
        name = ctx["user_name"]
        age = ctx["user_age"]

        if age >= 18:
            message = f"Hello, {name}! Welcome to our adult services."
        else:
            message = f"Hi {name}! Welcome to our youth programs."

        new_ctx = ctx.fork()
        new_ctx["greeting"] = message
        return new_ctx

    context = create_personalized_greeting.run(context)
    print(f"   Created greeting: {context['greeting']}")

    # Check metadata
    print(
        f"   Flow is context-aware: {create_personalized_greeting.metadata['context_aware']}"
    )
    print(
        f"   Input dependencies: {[k.path for k in create_personalized_greeting.metadata['input_dependencies']]}"
    )
    print(
        f"   Output dependencies: {[k.path for k in create_personalized_greeting.metadata['output_dependencies']]}"
    )

    # 5. Flow composition and chaining
    print("\n5. Flow Composition and Chaining")

    # Create a processing pipeline
    def process_user_data(ctx: Context) -> Context:
        """Process user data through a multi-step pipeline."""
        # Step 1: Validate required data
        step1 = Flow.require_keys(user_name, user_age)

        # Step 2: Set processing status
        step2 = Flow.set_key(status, "processing")

        # Step 3: Create greeting (reuse our decorated flow)
        step3 = create_personalized_greeting

        # Step 4: Update status to completed
        step4 = Flow.set_key(status, "completed")

        # Compose the pipeline
        pipeline = step1.then(step2).then(step3).then(step4)

        return pipeline.run(ctx)

    fresh_context = Context()
    fresh_context["user_name"] = "Bob"
    fresh_context["user_age"] = 25

    result_context = process_user_data(fresh_context)

    print(f"   User: {result_context['user_name']}, Age: {result_context['user_age']}")
    print(f"   Status: {result_context['status']}")
    print(f"   Greeting: {result_context['greeting']}")

    # 6. Error handling and type safety
    print("\n6. Error Handling and Type Safety")

    error_context = Context()
    error_context["user_age"] = "not_a_number"  # Wrong type!

    try:
        age_flow = Flow.get_key(user_age)
        age_flow.run(error_context)
    except Exception as e:
        print(f"   ✓ Type safety enforced: {type(e).__name__}: {e}")

    print("\n✨ Demo completed! The Flow-Context integration provides:")
    print("   • Type-safe context key operations")
    print("   • Declarative dependency management")
    print("   • Expressive composition patterns")
    print("   • Functional purity and immutability")
    print("   • Rich error handling and validation")
    print("   • Clear separation of concerns")


if __name__ == "__main__":
    main()
