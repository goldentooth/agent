"""Integration tests for the context module."""

from __future__ import annotations

from typing import Any

from goldentooth_agent.core.context import ContextKey, Symbol, context_key


class TestContextIntegration:
    """Integration tests demonstrating real-world usage of context components."""

    def test_complete_workflow(self) -> None:
        """Test a complete workflow using all context components."""
        # Create context keys using different methods
        user_name_key = context_key("user.name", str, "User's display name")
        user_age_key: ContextKey[int] = ContextKey(
            "user.age", int, "User's age in years"
        )
        session_data_key: ContextKey[dict[str, Any]] = ContextKey.create(
            "session.data", dict, "Session information"
        )

        # Create context storage
        context: dict[ContextKey[Any], Any] = {}

        # Store values
        context[user_name_key] = "Alice Smith"
        context[user_age_key] = 30
        context[session_data_key] = {
            "session_id": "abc123",
            "started_at": "2024-01-01T10:00:00Z",
            "messages": ["Hello", "How are you?"],
        }

        # Retrieve values
        assert context[user_name_key] == "Alice Smith"
        assert context[user_age_key] == 30
        assert context[session_data_key]["session_id"] == "abc123"

        # Test symbol functionality
        user_symbol = user_name_key.symbol
        assert isinstance(user_symbol, Symbol)
        assert user_symbol == "user.name"
        assert user_symbol.parts() == ["user", "name"]

        # Test that keys with same path are equivalent
        duplicate_key: ContextKey[str] = ContextKey(
            "user.name", str, "Different description"
        )
        assert context[duplicate_key] == "Alice Smith"

        # Test string representation
        assert str(user_name_key) == "user.name"
        assert repr(user_age_key) == "ContextKey(user.age<int>)"

    def test_nested_context_navigation(self) -> None:
        """Test working with nested context paths."""
        # Create hierarchical context keys
        intent_key = context_key("agent.intent", str, "Current agent intent")
        confidence_key = context_key("agent.confidence", float, "Confidence level")
        preferences_key = context_key(
            "agent.context.user.preferences", dict, "User preferences"
        )
        history_key = context_key(
            "agent.context.session.history", list, "Session history"
        )

        # Store keys for potential future use
        # agent_keys = [intent_key, confidence_key, preferences_key, history_key]

        # Verify symbol parts for hierarchical navigation
        intent_parts = intent_key.symbol.parts()
        assert intent_parts == ["agent", "intent"]

        preferences_parts = preferences_key.symbol.parts()
        assert preferences_parts == ["agent", "context", "user", "preferences"]

        history_parts = history_key.symbol.parts()
        assert history_parts == ["agent", "context", "session", "history"]

        # Create context with hierarchical data
        context: dict[ContextKey[Any], Any] = {
            intent_key: "greeting",
            confidence_key: 0.85,
            preferences_key: {"theme": "dark", "language": "en"},
            history_key: ["msg1", "msg2", "msg3"],
        }

        # Verify data access
        assert context[intent_key] == "greeting"
        assert context[confidence_key] == 0.85
        prefs_dict = context[preferences_key]
        assert prefs_dict["theme"] == "dark"
        history_list = context[history_key]
        assert len(history_list) == 3

    def test_context_key_collections(self) -> None:
        """Test using context keys in various collection types."""
        # Create various context keys
        keys = [
            context_key("system.version", str),
            context_key("system.uptime", int),
            context_key("user.authenticated", bool),
            context_key("user.permissions", list[str]),
        ]

        # Test in list
        key_list = list(keys)
        assert len(key_list) == 4
        assert keys[0] in key_list

        # Test in set (should handle duplicates correctly)
        duplicate_key: ContextKey[str] = ContextKey(
            "system.version", str, "Different description"
        )
        key_set = set(keys + [duplicate_key])
        assert len(key_set) == 4  # No duplicate because same path

        # Test as dictionary keys
        context = {key: f"value_{i}" for i, key in enumerate(keys)}
        assert context[keys[0]] == "value_0"
        assert context[duplicate_key] == "value_0"  # Same value due to same path

        # Test sorting (should work due to string inheritance of Symbol)
        sorted_keys = sorted(keys, key=lambda k: str(k))
        expected_order = [
            "system.uptime",
            "system.version",
            "user.authenticated",
            "user.permissions",
        ]
        assert [str(k) for k in sorted_keys] == expected_order

    def test_symbol_operations_with_context_keys(self) -> None:
        """Test Symbol operations in context of ContextKey usage."""
        key = context_key("application.modules.auth.settings", dict)
        symbol = key.symbol

        # Test symbol string operations
        assert symbol.startswith("application")
        assert symbol.endswith("settings")
        assert "modules" in symbol
        assert len(symbol) == len("application.modules.auth.settings")

        # Test parts for navigation
        parts = symbol.parts()
        assert parts == ["application", "modules", "auth", "settings"]

        # Test building new symbols from parts
        parent_path = ".".join(parts[:-1])  # Remove last part
        parent_symbol = Symbol(parent_path)
        assert parent_symbol == "application.modules.auth"
        assert parent_symbol.parts() == ["application", "modules", "auth"]

        # Test symbol comparison and sorting
        related_symbols = [
            Symbol("application.modules.auth.settings"),
            Symbol("application.modules.auth.users"),
            Symbol("application.modules.core.config"),
            Symbol("application.settings"),
        ]

        sorted_symbols = sorted(related_symbols)
        expected = [
            "application.modules.auth.settings",
            "application.modules.auth.users",
            "application.modules.core.config",
            "application.settings",
        ]
        assert [str(s) for s in sorted_symbols] == expected

    def test_type_safety_demonstration(self) -> None:
        """Demonstrate type safety features of ContextKey."""
        # Create typed context keys
        str_key: ContextKey[str] = context_key("config.name", str)
        int_key: ContextKey[int] = context_key("config.port", int)
        dict_key: ContextKey[dict[str, str]] = context_key("config.env", dict[str, str])

        # The type information is preserved for static analysis
        # (though not enforced at runtime in Python)
        assert str_key.type_ is str
        assert int_key.type_ is int
        assert dict_key.type_ == dict[str, str]

        # Create context
        context: dict[ContextKey[Any], Any] = {
            str_key: "MyApp",
            int_key: 8080,
            dict_key: {"ENV": "production", "DEBUG": "false"},
        }

        # Access with type hints for IDE support
        app_name = context[str_key]
        port = context[int_key]
        env_vars = context[dict_key]

        assert app_name == "MyApp"
        assert port == 8080
        assert env_vars["ENV"] == "production"

    def test_real_world_agent_context(self) -> None:
        """Test a realistic agent context scenario."""
        # Define context schema for an AI agent
        user_id_key = context_key("user.id", str, "Unique user identifier")
        user_name_key = context_key("user.name", str, "User's display name")
        user_preferences_key = context_key("user.preferences", dict, "User preferences")
        session_id_key = context_key("session.id", str, "Session identifier")
        session_messages_key = context_key(
            "session.messages", list, "Conversation history"
        )
        agent_intent_key = context_key(
            "agent.current_intent", str, "Current agent intent"
        )
        agent_confidence_key = context_key(
            "agent.confidence", float, "Intent confidence"
        )
        agent_context_key = context_key("agent.context", dict, "Agent working memory")

        # Schema mapping for reference
        # context_schema = {
        #     "user_id": user_id_key,
        #     "user_name": user_name_key,
        #     "user_preferences": user_preferences_key,
        #     "session_id": session_id_key,
        #     "session_messages": session_messages_key,
        #     "agent_intent": agent_intent_key,
        #     "agent_confidence": agent_confidence_key,
        #     "agent_context": agent_context_key,
        # }

        # Initialize context
        agent_context: dict[ContextKey[Any], Any] = {
            user_id_key: "user_12345",
            user_name_key: "John Doe",
            user_preferences_key: {"language": "en", "timezone": "UTC"},
            session_id_key: "session_67890",
            session_messages_key: [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help you?"},
            ],
            agent_intent_key: "greeting",
            agent_confidence_key: 0.95,
            agent_context_key: {"last_topic": "introduction"},
        }

        # Verify context access
        assert agent_context[user_name_key] == "John Doe"
        assert agent_context[agent_confidence_key] == 0.95
        session_messages = agent_context[session_messages_key]
        assert len(session_messages) == 2

        # Test context key properties
        assert user_preferences_key.symbol.parts() == ["user", "preferences"]
        assert str(user_preferences_key) == "user.preferences"
        assert user_preferences_key.type_ is dict

        # Test that context can be queried by path patterns
        all_keys = [
            user_id_key,
            user_name_key,
            user_preferences_key,
            session_id_key,
            session_messages_key,
            agent_intent_key,
            agent_confidence_key,
            agent_context_key,
        ]
        user_keys = [k for k in all_keys if str(k).startswith("user.")]
        agent_keys = [k for k in all_keys if str(k).startswith("agent.")]

        assert len(user_keys) == 3
        assert len(agent_keys) == 3

        # Verify all user data is accessible
        user_data = {str(k): agent_context[k] for k in user_keys}  # type: ignore
        expected_user_data = {
            "user.id": "user_12345",
            "user.name": "John Doe",
            "user.preferences": {"language": "en", "timezone": "UTC"},
        }
        assert user_data == expected_user_data
