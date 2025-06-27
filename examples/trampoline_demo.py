"""Demonstration of Flow-based trampoline execution patterns.

This example shows how to use the new Flow trampoline system to achieve similar
functionality to the old Thunk-based trampoline, with enhanced type safety and
integration with the modern Flow architecture.
"""

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow import (
    SHOULD_BREAK_KEY,
    SHOULD_EXIT_KEY,
    SHOULD_SKIP_KEY,
    Flow,
)


def main():
    """Demonstrate Flow trampoline patterns with practical examples."""
    print("🔄 Flow Trampoline Demonstration")
    print("=" * 50)

    # Example 1: Simple Chat Bot Loop
    print("\n1. Simple Chat Bot Loop")
    print("-" * 25)

    def create_chat_bot_demo():
        """Create a simple chat bot using trampoline patterns."""

        def get_user_input(ctx: Context) -> Context:
            """Simulate getting user input."""
            new_ctx = ctx.fork()
            cycle = ctx.get("cycle", 0)

            # Simulate different user inputs
            inputs = ["hello", "help", "tell me a joke", "exit"]
            if cycle < len(inputs):
                user_input = inputs[cycle]
                print(f"  User: {user_input}")
                new_ctx["user_input"] = user_input
            else:
                new_ctx[SHOULD_EXIT_KEY.path] = True

            return new_ctx

        def process_input(ctx: Context) -> Context:
            """Process user input and generate response."""
            new_ctx = ctx.fork()
            user_input = ctx.get("user_input", "").lower()

            if user_input == "hello":
                response = "Hello! How can I help you today?"
            elif user_input == "help":
                response = "Available commands: hello, help, tell me a joke, exit"
            elif user_input == "tell me a joke":
                response = (
                    "Why don't scientists trust atoms? Because they make up everything!"
                )
            elif user_input == "exit":
                response = "Goodbye! Thanks for chatting!"
                new_ctx[SHOULD_EXIT_KEY.path] = True
            else:
                response = "I'm sorry, I don't understand that command."

            print(f"  Bot:  {response}")
            new_ctx["response"] = response
            return new_ctx

        def update_cycle(ctx: Context) -> Context:
            """Update the cycle counter."""
            new_ctx = ctx.fork()
            new_ctx["cycle"] = ctx.get("cycle", 0) + 1
            return new_ctx

        # Create flows
        input_flow = Flow.from_sync_fn(get_user_input)
        process_flow = Flow.from_sync_fn(process_input)
        cycle_flow = Flow.from_sync_fn(update_cycle)

        # Create chat loop using trampoline_chain
        chat_loop = Flow.trampoline_chain(input_flow, process_flow, cycle_flow)

        # Run the chat bot
        context = Context()
        context["cycle"] = 0
        final_context = chat_loop.run(context)

        print(f"  Chat completed after {final_context.get('cycle', 0)} interactions")

    create_chat_bot_demo()

    # Example 2: State Machine with Break/Restart
    print("\n2. State Machine with Break/Restart")
    print("-" * 35)

    def create_state_machine_demo():
        """Create a state machine that demonstrates break/restart functionality."""

        def state_machine_step(ctx: Context) -> Context:
            """Execute one step of the state machine."""
            new_ctx = ctx.fork()
            current_state = ctx.get("state", "init")
            step_count = ctx.get("steps", 0)

            print(f"  State: {current_state} (step {step_count})")
            new_ctx["steps"] = step_count + 1

            if current_state == "init":
                new_ctx["state"] = "loading"
                new_ctx["progress"] = 0

            elif current_state == "loading":
                progress = ctx.get("progress", 0) + 25
                new_ctx["progress"] = progress

                if progress >= 100:
                    new_ctx["state"] = "processing"
                    print(f"    Loading complete: {progress}%")
                else:
                    print(f"    Loading progress: {progress}%")

            elif current_state == "processing":
                attempts = ctx.get("processing_attempts", 0) + 1
                new_ctx["processing_attempts"] = attempts

                if attempts == 2:  # Simulate failure that requires restart
                    print("    Processing failed! Restarting...")
                    new_ctx[SHOULD_BREAK_KEY.path] = True
                    new_ctx["state"] = "init"  # Reset to initial state
                    new_ctx["restarts"] = ctx.get("restarts", 0) + 1
                elif attempts >= 3:  # Success after restart
                    print("    Processing successful!")
                    new_ctx["state"] = "complete"
                else:
                    print(f"    Processing attempt {attempts}...")

            elif current_state == "complete":
                print("    State machine completed successfully!")
                new_ctx[SHOULD_EXIT_KEY.path] = True

            return new_ctx

        # Create the state machine flow
        step_flow = Flow.from_sync_fn(state_machine_step)
        state_machine = Flow.trampoline(step_flow)

        # Run the state machine
        context = Context()
        context["state"] = "init"
        context["steps"] = 0
        final_context = state_machine.run(context)

        print(f"  Final state: {final_context.get('state')}")
        print(f"  Total steps: {final_context.get('steps')}")
        print(f"  Restarts: {final_context.get('restarts', 0)}")

    create_state_machine_demo()

    # Example 3: Agent with Conditional Skip
    print("\n3. Agent with Conditional Skip")
    print("-" * 30)

    def create_agent_demo():
        """Create an agent that can conditionally skip processing."""

        def receive_task(ctx: Context) -> Context:
            """Receive and categorize incoming tasks."""
            new_ctx = ctx.fork()
            task_num = ctx.get("task_count", 0)

            # Simulate different types of tasks
            tasks = [
                {"type": "data", "content": "Process user data"},
                {"type": "skip", "content": "Maintenance mode"},
                {"type": "data", "content": "Generate report"},
                {"type": "skip", "content": "System update"},
                {"type": "data", "content": "Send notifications"},
                {"type": "exit", "content": "Shutdown signal"},
            ]

            if task_num < len(tasks):
                task = tasks[task_num]
                print(f"  📥 Received: {task['content']} (type: {task['type']})")
                new_ctx["current_task"] = task
                new_ctx["task_count"] = task_num + 1
            else:
                new_ctx[SHOULD_EXIT_KEY.path] = True

            return new_ctx

        def categorize_task(ctx: Context) -> Context:
            """Categorize task and set appropriate flags."""
            new_ctx = ctx.fork()
            task = ctx.get("current_task", {})
            task_type = task.get("type", "")

            if task_type == "skip":
                print("  ⏭️  Setting skip flag - agent will be bypassed")
                new_ctx[SHOULD_SKIP_KEY.path] = True
            elif task_type == "exit":
                print("  🛑 Exit signal received")
                new_ctx[SHOULD_EXIT_KEY.path] = True

            return new_ctx

        def agent_process(ctx: Context) -> Context:
            """Main agent processing (can be skipped)."""
            new_ctx = ctx.fork()
            task = ctx.get("current_task", {})

            if task.get("type") == "data":
                result = f"✅ Processed: {task.get('content')}"
                print(f"  🤖 Agent: {result}")

                processed = ctx.get("processed_tasks", [])
                new_ctx["processed_tasks"] = processed + [result]

            # Clear skip flag for next iteration
            new_ctx[SHOULD_SKIP_KEY.path] = False
            return new_ctx

        # Create flows
        receive_flow = Flow.from_sync_fn(receive_task)
        categorize_flow = Flow.from_sync_fn(categorize_task)
        agent_flow = Flow.from_sync_fn(agent_process)

        # Create conditional agent that skips when flag is set
        skip_condition = Flow.check_should_skip()
        conditional_agent = Flow.skip_if(skip_condition, agent_flow)

        # Create the full processing loop
        agent_loop = Flow.trampoline_chain(
            receive_flow, categorize_flow, conditional_agent
        )

        # Run the agent
        context = Context()
        context["task_count"] = 0
        context["processed_tasks"] = []
        final_context = agent_loop.run(context)

        processed = final_context.get("processed_tasks", [])
        print(f"  📊 Total tasks processed: {len(processed)}")
        for i, task in enumerate(processed, 1):
            print(f"    {i}. {task}")

    create_agent_demo()

    # Example 4: Complex Flow Composition
    print("\n4. Complex Flow Composition")
    print("-" * 27)

    def create_complex_demo():
        """Show complex composition of trampoline patterns."""

        def initialization(ctx: Context) -> Context:
            """Initialize the system."""
            new_ctx = ctx.fork()
            print("  🚀 System initializing...")
            new_ctx["phase"] = "ready"
            new_ctx["errors"] = 0
            return new_ctx

        def main_operation(ctx: Context) -> Context:
            """Main operation with potential for errors."""
            new_ctx = ctx.fork()
            iteration = ctx.get("iteration", 0)
            errors = ctx.get("errors", 0)

            print(f"  ⚙️  Main operation iteration {iteration + 1}")
            new_ctx["iteration"] = iteration + 1

            # Simulate occasional errors
            if iteration == 2 or iteration == 5:
                print("  ❌ Error occurred! Breaking to error handler...")
                new_ctx["errors"] = errors + 1
                new_ctx[SHOULD_BREAK_KEY.path] = True
            elif iteration >= 8:
                print("  ✅ All operations completed successfully")
                new_ctx[SHOULD_EXIT_KEY.path] = True

            return new_ctx

        def error_handler(ctx: Context) -> Context:
            """Handle errors and decide whether to continue."""
            new_ctx = ctx.fork()
            errors = ctx.get("errors", 0)

            if errors <= 2:
                print(f"  🔧 Error {errors} handled, continuing...")
                # Continue processing
            else:
                print("  💥 Too many errors, shutting down")
                new_ctx[SHOULD_EXIT_KEY.path] = True

            return new_ctx

        # Create flows with proper error handling
        init_flow = Flow.from_sync_fn(initialization)
        main_flow = Flow.from_sync_fn(main_operation)
        error_flow = Flow.from_sync_fn(error_handler)

        # Create a complex system using exitable_chain within trampoline
        operation_chain = Flow.exitable_chain(main_flow, error_flow)
        full_system = Flow.exitable_chain(init_flow, Flow.trampoline(operation_chain))

        # Run the complex system
        context = Context()
        final_context = full_system.run(context)

        print(f"  📈 Final iteration: {final_context.get('iteration', 0)}")
        print(f"  🔢 Total errors handled: {final_context.get('errors', 0)}")

    create_complex_demo()

    print("\n✨ Trampoline Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("  • 🔄 Continuous loop execution with clean exit conditions")
    print("  • ⚡ Break/restart functionality for error recovery")
    print("  • ⏭️  Conditional skipping of operations")
    print("  • 🎯 Type-safe context key management")
    print("  • 🔗 Seamless composition with existing Flow combinators")
    print("  • 🏗️  Clean, functional architecture")

    print("\nCompared to the old Thunk-based system:")
    print("  ✅ Better type safety with ContextKey system")
    print("  ✅ Async-first design with Flow architecture")
    print("  ✅ Immutable context operations")
    print("  ✅ Composable with all existing Flow combinators")
    print("  ✅ Clear separation of concerns")
    print("  ✅ Enhanced debugging and introspection capabilities")


if __name__ == "__main__":
    main()
