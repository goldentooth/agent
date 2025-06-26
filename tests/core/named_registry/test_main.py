from __future__ import annotations

import pytest
from unittest.mock import Mock, patch
from typing import Protocol

from goldentooth_agent.core.named_registry.main import (
    NamedRegistry,
    Creatable,
    RegisterCallable,
    make_register_fn,
)


class RegistryItem:
    """Test class for registry tests."""

    def __init__(self, value: str = "test"):
        self.value = value


class CreatableRegistryItem:
    """Test class that implements Creatable protocol."""

    def __init__(self, value: str = "created"):
        self.value = value

    @classmethod
    def create(cls) -> CreatableRegistryItem:
        return cls("created_instance")


class TestNamedRegistry:
    """Test suite for NamedRegistry class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = NamedRegistry[RegistryItem]()
        self.test_obj = RegistryItem("test_value")

    def test_init_creates_empty_registry(self):
        """Test that registry initializes with empty dictionary."""
        registry = NamedRegistry[str]()
        assert registry._registry == {}

    def test_set_stores_object(self):
        """Test that set() stores an object with given ID."""
        self.registry.set("test_id", self.test_obj)
        assert self.registry._registry["test_id"] is self.test_obj

    def test_get_retrieves_object(self):
        """Test that get() retrieves stored object."""
        self.registry.set("test_id", self.test_obj)
        retrieved = self.registry.get("test_id")
        assert retrieved is self.test_obj

    def test_get_raises_keyerror_for_missing_id(self):
        """Test that get() raises KeyError for unregistered ID."""
        with pytest.raises(KeyError) as exc_info:
            self.registry.get("missing_id")

        error_message = str(exc_info.value)
        assert "missing_id" in error_message
        assert "is not registered" in error_message
        assert "available IDs" in error_message

    def test_get_keyerror_shows_available_ids(self):
        """Test that KeyError message shows available IDs."""
        self.registry.set("id1", RegistryItem("1"))
        self.registry.set("id2", RegistryItem("2"))

        with pytest.raises(KeyError) as exc_info:
            self.registry.get("missing")

        error_message = str(exc_info.value)
        assert "['id1', 'id2']" in error_message

    def test_remove_deletes_object(self):
        """Test that remove() deletes object from registry."""
        self.registry.set("test_id", self.test_obj)
        self.registry.remove("test_id")
        assert "test_id" not in self.registry._registry

    def test_remove_nonexistent_id_does_not_error(self):
        """Test that remove() does not error for non-existent ID."""
        # Should not raise any exception
        self.registry.remove("nonexistent")

    def test_has_returns_true_for_existing_id(self):
        """Test that has() returns True for registered ID."""
        self.registry.set("test_id", self.test_obj)
        assert self.registry.has("test_id") is True

    def test_has_returns_false_for_missing_id(self):
        """Test that has() returns False for unregistered ID."""
        assert self.registry.has("missing_id") is False

    def test_list_returns_sorted_ids(self):
        """Test that list() returns sorted list of IDs."""
        self.registry.set("c", RegistryItem())
        self.registry.set("a", RegistryItem())
        self.registry.set("b", RegistryItem())

        ids = self.registry.list()
        assert ids == ["a", "b", "c"]

    def test_list_returns_empty_for_empty_registry(self):
        """Test that list() returns empty list for empty registry."""
        assert self.registry.list() == []

    def test_all_returns_all_objects(self):
        """Test that all() returns all registered objects."""
        obj1 = RegistryItem("1")
        obj2 = RegistryItem("2")

        self.registry.set("id1", obj1)
        self.registry.set("id2", obj2)

        all_objects = self.registry.all()
        assert len(all_objects) == 2
        assert obj1 in all_objects
        assert obj2 in all_objects

    def test_all_returns_empty_for_empty_registry(self):
        """Test that all() returns empty list for empty registry."""
        assert self.registry.all() == []

    def test_items_returns_name_object_pairs(self):
        """Test that items() returns (name, object) pairs."""
        obj1 = RegistryItem("1")
        obj2 = RegistryItem("2")

        self.registry.set("id1", obj1)
        self.registry.set("id2", obj2)

        items = self.registry.items()
        assert len(items) == 2
        assert ("id1", obj1) in items
        assert ("id2", obj2) in items

    def test_items_returns_empty_for_empty_registry(self):
        """Test that items() returns empty list for empty registry."""
        assert self.registry.items() == []

    def test_clear_removes_all_entries(self):
        """Test that clear() removes all registry entries."""
        self.registry.set("id1", RegistryItem("1"))
        self.registry.set("id2", RegistryItem("2"))

        self.registry.clear()

        assert self.registry._registry == {}
        assert self.registry.list() == []

    def test_generic_typing_with_different_types(self):
        """Test that generic typing works with different types."""
        str_registry = NamedRegistry[str]()

        str_registry.set("key", "value")
        assert str_registry.get("key") == "value"

        int_registry = NamedRegistry[int]()

        int_registry.set("number", 42)
        assert int_registry.get("number") == 42


class TestCreatableProtocol:
    """Test suite for Creatable protocol."""

    def test_creatable_class_implements_protocol(self):
        """Test that CreatableRegistryItem implements Creatable protocol."""
        assert isinstance(CreatableRegistryItem, Creatable)

    def test_non_creatable_class_does_not_implement_protocol(self):
        """Test that regular class does not implement Creatable protocol."""
        assert not isinstance(RegistryItem, Creatable)

    def test_creatable_create_method_works(self):
        """Test that create() method works on Creatable class."""
        instance = CreatableRegistryItem.create()
        assert isinstance(instance, CreatableRegistryItem)
        assert instance.value == "created_instance"


class TestRegisterCallableProtocol:
    """Test suite for RegisterCallable protocol."""

    def test_protocol_structure(self):
        """Test that RegisterCallable protocol has correct structure."""
        # This is mainly a structural test to ensure the protocol is defined correctly
        assert hasattr(RegisterCallable, '__call__')


class TestMakeRegisterFn:
    """Test suite for make_register_fn factory function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = NamedRegistry[RegistryItem]()

    @patch('antidote.world')
    def test_register_with_class_and_id(self, mock_world):
        """Test registering a class with explicit ID."""
        mock_world.__getitem__.return_value = self.registry

        # Create instance function to mock object creation
        test_obj = RegistryItem("test_value")
        get_instance_fn = lambda: test_obj

        register_fn = make_register_fn(
            NamedRegistry[RegistryItem],
            get_instance_fn=get_instance_fn
        )

        # Register with class and ID
        result = register_fn(RegistryItem, id="test_id")

        assert result is RegistryItem
        assert self.registry.has("test_id")
        # Should register the instance from get_instance_fn
        registered_obj = self.registry.get("test_id")
        assert registered_obj is test_obj

    @patch('antidote.world')
    def test_register_with_object_and_id(self, mock_world):
        """Test registering an object with explicit ID."""
        mock_world.__getitem__.return_value = self.registry

        register_fn = make_register_fn(NamedRegistry[RegistryItem])
        test_obj = RegistryItem("test_value")

        result = register_fn(obj=test_obj, id="test_id")

        assert result is RegistryItem  # Returns the type
        assert self.registry.has("test_id")
        assert self.registry.get("test_id") is test_obj

    @patch('antidote.world')
    def test_register_with_creatable_class(self, mock_world):
        """Test registering a Creatable class."""
        registry = NamedRegistry[CreatableRegistryItem]()
        mock_world.__getitem__.return_value = registry

        register_fn = make_register_fn(NamedRegistry[CreatableRegistryItem])

        result = register_fn(CreatableRegistryItem, id="creatable_id")

        assert result is CreatableRegistryItem
        assert registry.has("creatable_id")
        registered_obj = registry.get("creatable_id")
        assert isinstance(registered_obj, CreatableRegistryItem)
        assert registered_obj.value == "created_instance"

    @patch('antidote.world')
    def test_register_with_get_instance_fn(self, mock_world):
        """Test registering with custom get_instance_fn."""
        mock_world.__getitem__.return_value = self.registry

        custom_obj = RegistryItem("custom")
        get_instance_fn = lambda: custom_obj

        register_fn = make_register_fn(
            NamedRegistry[RegistryItem],
            get_instance_fn=get_instance_fn
        )

        result = register_fn(RegistryItem, id="custom_id")

        assert result is RegistryItem
        assert self.registry.has("custom_id")
        assert self.registry.get("custom_id") is custom_obj

    @patch('antidote.world')
    def test_register_with_default_id_fn(self, mock_world):
        """Test registering with custom default_id_fn."""
        mock_world.__getitem__.return_value = self.registry

        def default_id_fn(obj: RegistryItem) -> str:
            return f"auto_{obj.value}"

        register_fn = make_register_fn(
            NamedRegistry[RegistryItem],
            default_id_fn=default_id_fn
        )

        test_obj = RegistryItem("unique")
        result = register_fn(obj=test_obj)

        assert result is RegistryItem
        assert self.registry.has("auto_unique")
        assert self.registry.get("auto_unique") is test_obj

    @patch('antidote.world')
    def test_register_raises_error_without_object_or_creatable(self, mock_world):
        """Test that registration raises error without object or Creatable class."""
        mock_world.__getitem__.return_value = self.registry

        register_fn = make_register_fn(NamedRegistry[RegistryItem])

        with pytest.raises(ValueError, match="An object must be provided or creatable"):
            register_fn(id="test_id")

    @patch('antidote.world')
    def test_register_raises_error_without_id(self, mock_world):
        """Test that registration raises error without ID."""
        mock_world.__getitem__.return_value = self.registry

        register_fn = make_register_fn(NamedRegistry[RegistryItem])
        test_obj = RegistryItem("test")

        with pytest.raises(ValueError, match="An ID must be provided or derivable"):
            register_fn(obj=test_obj)

    @patch('antidote.world')
    def test_register_can_derive_id_from_default_id_fn(self, mock_world):
        """Test that registration can derive ID from default_id_fn."""
        mock_world.__getitem__.return_value = self.registry

        def default_id_fn(obj: RegistryItem) -> str:
            return f"derived_{obj.value}"

        register_fn = make_register_fn(
            NamedRegistry[RegistryItem],
            default_id_fn=default_id_fn
        )

        test_obj = RegistryItem("test_value")
        result = register_fn(obj=test_obj)

        assert result is RegistryItem
        assert self.registry.has("derived_test_value")
        assert self.registry.get("derived_test_value") is test_obj


class TestIntegration:
    """Integration tests for the complete named registry system."""

    @patch('antidote.world')
    def test_full_registration_workflow(self, mock_world):
        """Test a complete registration and retrieval workflow."""
        registry = NamedRegistry[RegistryItem]()
        mock_world.__getitem__.return_value = registry

        # Create register function
        register = make_register_fn(
            NamedRegistry[RegistryItem],
            default_id_fn=lambda obj: f"obj_{obj.value}"
        )

        # Register some objects
        obj1 = RegistryItem("first")
        obj2 = RegistryItem("second")

        register(obj=obj1)
        register(obj=obj2, id="custom_second")

        # Verify registration
        assert registry.has("obj_first")
        assert registry.has("custom_second")
        assert registry.get("obj_first") is obj1
        assert registry.get("custom_second") is obj2

        # Test listing
        assert sorted(registry.list()) == ["custom_second", "obj_first"]

        # Test items
        items = registry.items()
        assert len(items) == 2
        assert ("obj_first", obj1) in items
        assert ("custom_second", obj2) in items

