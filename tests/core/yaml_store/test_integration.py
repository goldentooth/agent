"""Integration tests for YamlStore module components.

Tests the interaction between YamlStore, YamlStoreAdapter, and YamlStoreInstaller
to ensure they work together correctly for YAML-based data persistence.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest
import yaml

from goldentooth_agent.core.yaml_store import (
    YamlStore,
    YamlStoreAdapter,
    YamlStoreInstaller,
)


class User:
    """Test data class for YAML store tests."""

    def __init__(self, name: str, age: int, email: str = ""):
        self.name = name
        self.age = age
        self.email = email

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, User):
            return False
        return (
            self.name == other.name
            and self.age == other.age
            and self.email == other.email
        )

    def __repr__(self) -> str:
        return f"User(name='{self.name}', age={self.age}, email='{self.email}')"


class UserAdapter:
    """Test adapter for User class."""

    @classmethod
    def from_dict(cls, data: dict) -> User:
        return User(name=data["name"], age=data["age"], email=data.get("email", ""))

    @classmethod
    def to_dict(cls, id: str, obj: User) -> dict:
        return {"id": id, "name": obj.name, "age": obj.age, "email": obj.email}


class Task:
    """Another test data class for YAML store tests."""

    def __init__(self, title: str, completed: bool = False, priority: int = 1):
        self.title = title
        self.completed = completed
        self.priority = priority

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Task):
            return False
        return (
            self.title == other.title
            and self.completed == other.completed
            and self.priority == other.priority
        )

    def __repr__(self) -> str:
        return f"Task(title='{self.title}', completed={self.completed}, priority={self.priority})"


class TaskAdapter:
    """Test adapter for Task class."""

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return Task(
            title=data["title"],
            completed=data.get("completed", False),
            priority=data.get("priority", 1),
        )

    @classmethod
    def to_dict(cls, id: str, obj: Task) -> dict:
        return {
            "id": id,
            "title": obj.title,
            "completed": obj.completed,
            "priority": obj.priority,
        }


class InvalidAdapter:
    """Test adapter that doesn't implement the protocol properly."""

    def from_dict(
        self, data: dict
    ) -> User:  # Missing @classmethod - this makes it invalid
        return User(data["name"], data["age"])

    # Missing to_dict method entirely - this also makes it invalid


class TestYamlStoreAdapter:
    """Test suite for YamlStoreAdapter protocol."""

    def test_adapter_protocol_implementation(self):
        """Test that UserAdapter implements YamlStoreAdapter protocol."""
        assert isinstance(UserAdapter, YamlStoreAdapter)

    def test_adapter_protocol_validation_valid_adapter(self):
        """Test that valid adapter passes protocol validation."""
        assert isinstance(TaskAdapter, YamlStoreAdapter)

    def test_adapter_protocol_validation_invalid_adapter(self):
        """Test that invalid adapter fails protocol validation."""
        assert not isinstance(InvalidAdapter, YamlStoreAdapter)

    def test_adapter_from_dict_creates_object(self):
        """Test that adapter can create object from dictionary."""
        data = {"name": "John", "age": 30, "email": "john@example.com"}
        user = UserAdapter.from_dict(data)

        assert isinstance(user, User)
        assert user.name == "John"
        assert user.age == 30
        assert user.email == "john@example.com"

    def test_adapter_to_dict_creates_dict(self):
        """Test that adapter can convert object to dictionary."""
        user = User("Jane", 25, "jane@example.com")
        data = UserAdapter.to_dict("user_1", user)

        expected = {
            "id": "user_1",
            "name": "Jane",
            "age": 25,
            "email": "jane@example.com",
        }
        assert data == expected

    def test_adapter_roundtrip_conversion(self):
        """Test that adapter can roundtrip convert object to dict and back."""
        original_user = User("Bob", 40, "bob@example.com")

        # Convert to dict and back
        data = UserAdapter.to_dict("test_user", original_user)
        restored_user = UserAdapter.from_dict(data)

        assert restored_user == original_user


class TestYamlStore:
    """Test suite for YamlStore class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.store_path = Path(self.temp_dir.name) / "test_store"
        self.store = YamlStore[User](self.store_path, UserAdapter)

        # Create test users
        self.user1 = User("Alice", 28, "alice@example.com")
        self.user2 = User("Charlie", 35, "charlie@example.com")
        self.user3 = User("Diana", 22)

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_store_creates_directory(self):
        """Test that YamlStore creates directory if it doesn't exist."""
        assert self.store_path.exists()
        assert self.store_path.is_dir()

    def test_store_with_existing_directory(self):
        """Test that YamlStore works with existing directory."""
        # Create another store in the same directory
        store2 = YamlStore[User](self.store_path, UserAdapter)
        assert store2.directory == self.store_path

    def test_save_creates_yaml_file(self):
        """Test that save() creates a YAML file."""
        self.store.save("user1", self.user1)

        yaml_file = self.store_path / "user1.yaml"
        assert yaml_file.exists()
        assert yaml_file.is_file()

    def test_save_creates_valid_yaml_content(self):
        """Test that save() creates valid YAML content."""
        self.store.save("user1", self.user1)

        yaml_file = self.store_path / "user1.yaml"
        with yaml_file.open() as f:
            data = yaml.safe_load(f)

        expected = {
            "id": "user1",
            "name": "Alice",
            "age": 28,
            "email": "alice@example.com",
        }
        assert data == expected

    def test_load_retrieves_saved_object(self):
        """Test that load() retrieves previously saved object."""
        self.store.save("user1", self.user1)
        loaded_user = self.store.load("user1")

        assert loaded_user == self.user1

    def test_load_nonexistent_file_raises_error(self):
        """Test that load() raises FileNotFoundError for non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.store.load("nonexistent")

    def test_exists_returns_true_for_existing_file(self):
        """Test that exists() returns True for existing file."""
        self.store.save("user1", self.user1)
        assert self.store.exists("user1") is True

    def test_exists_returns_false_for_nonexistent_file(self):
        """Test that exists() returns False for non-existent file."""
        assert self.store.exists("nonexistent") is False

    def test_delete_removes_existing_file(self):
        """Test that delete() removes existing file."""
        self.store.save("user1", self.user1)
        assert self.store.exists("user1")

        self.store.delete("user1")
        assert not self.store.exists("user1")

    def test_delete_nonexistent_file_does_not_error(self):
        """Test that delete() does not error for non-existent file."""
        # Should not raise any exception
        self.store.delete("nonexistent")

    def test_list_returns_empty_for_empty_store(self):
        """Test that list() returns empty list for empty store."""
        assert self.store.list() == []

    def test_list_returns_saved_file_names(self):
        """Test that list() returns names of saved files."""
        self.store.save("user1", self.user1)
        self.store.save("user2", self.user2)
        self.store.save("user3", self.user3)

        file_list = self.store.list()
        assert set(file_list) == {"user1", "user2", "user3"}

    def test_list_returns_sorted_names(self):
        """Test that list() returns sorted list of names."""
        # Save in non-alphabetical order
        self.store.save("charlie", self.user2)
        self.store.save("alice", self.user1)
        self.store.save("diana", self.user3)

        file_list = self.store.list()
        assert file_list == ["alice", "charlie", "diana"]

    def test_list_ignores_non_yaml_files(self):
        """Test that list() ignores non-YAML files in directory."""
        self.store.save("user1", self.user1)

        # Create non-YAML files
        (self.store_path / "not_yaml.txt").write_text("test")
        (self.store_path / "config.json").write_text("{}")
        (self.store_path / ".hidden").write_text("hidden")

        file_list = self.store.list()
        assert file_list == ["user1"]

    def test_multiple_saves_overwrites_file(self):
        """Test that multiple saves to same ID overwrites the file."""
        self.store.save("user1", self.user1)

        # Modify user and save again
        modified_user = User("Alice Modified", 29, "alice.new@example.com")
        self.store.save("user1", modified_user)

        loaded_user = self.store.load("user1")
        assert loaded_user == modified_user
        assert loaded_user != self.user1

    def test_store_with_different_types(self):
        """Test that store works with different data types."""
        task_store = YamlStore[Task](self.store_path / "tasks", TaskAdapter)

        task1 = Task("Buy groceries", False, 2)
        task2 = Task("Complete project", True, 1)

        task_store.save("task1", task1)
        task_store.save("task2", task2)

        assert task_store.exists("task1")
        assert task_store.exists("task2")

        loaded_task1 = task_store.load("task1")
        loaded_task2 = task_store.load("task2")

        assert loaded_task1 == task1
        assert loaded_task2 == task2

    def test_store_handles_special_characters_in_id(self):
        """Test that store handles special characters in ID."""
        # Test with underscores, dashes, numbers
        special_ids = ["user_1", "user-2", "user123", "user_with_long_name"]

        for i, special_id in enumerate(special_ids):
            user = User(f"User{i}", 20 + i)
            self.store.save(special_id, user)

            assert self.store.exists(special_id)
            loaded_user = self.store.load(special_id)
            assert loaded_user == user

    def test_store_preserves_data_types(self):
        """Test that store preserves different data types correctly."""
        user_with_zero_age = User("Baby", 0, "")
        self.store.save("baby", user_with_zero_age)

        loaded_user = self.store.load("baby")
        assert loaded_user.age == 0
        assert loaded_user.email == ""
        assert isinstance(loaded_user.age, int)


class TestYamlStoreInstaller:
    """Test suite for YamlStoreInstaller class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

        # Create source and destination stores
        self.source_path = self.base_path / "source"
        self.dest_path = self.base_path / "destination"

        self.source_store = YamlStore[User](self.source_path, UserAdapter)
        self.dest_store = YamlStore[User](self.dest_path, UserAdapter)

        self.installer = YamlStoreInstaller(
            self.source_store, self.dest_store, UserAdapter
        )

        # Create test users
        self.user1 = User("Alice", 28, "alice@example.com")
        self.user2 = User("Bob", 32, "bob@example.com")
        self.user3 = User("Charlie", 25, "charlie@example.com")

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_installer_with_empty_source(self):
        """Test installer with empty source store."""
        result = self.installer.install()

        assert result is False  # No files changed
        assert self.dest_store.list() == []

    def test_installer_copies_all_files_from_source(self):
        """Test that installer copies all files from source to destination."""
        # Add users to source store
        self.source_store.save("user1", self.user1)
        self.source_store.save("user2", self.user2)
        self.source_store.save("user3", self.user3)

        result = self.installer.install()

        assert result is True  # Files were changed

        # Verify all files are copied
        dest_list = self.dest_store.list()
        assert set(dest_list) == {"user1", "user2", "user3"}

        # Verify content is correct
        assert self.dest_store.load("user1") == self.user1
        assert self.dest_store.load("user2") == self.user2
        assert self.dest_store.load("user3") == self.user3

    def test_installer_does_not_overwrite_by_default(self):
        """Test that installer does not overwrite existing files by default."""
        # Add user to source
        self.source_store.save("user1", self.user1)

        # Add different user to destination with same ID
        existing_user = User("Existing Alice", 99, "existing@example.com")
        self.dest_store.save("user1", existing_user)

        result = self.installer.install(overwrite=False)

        assert result is False  # No files changed

        # Verify existing file was not overwritten
        loaded_user = self.dest_store.load("user1")
        assert loaded_user == existing_user
        assert loaded_user != self.user1

    def test_installer_overwrites_when_requested(self):
        """Test that installer overwrites existing files when overwrite=True."""
        # Add user to source
        self.source_store.save("user1", self.user1)

        # Add different user to destination with same ID
        existing_user = User("Existing Alice", 99, "existing@example.com")
        self.dest_store.save("user1", existing_user)

        result = self.installer.install(overwrite=True)

        assert result is True  # Files were changed

        # Verify file was overwritten
        loaded_user = self.dest_store.load("user1")
        assert loaded_user == self.user1
        assert loaded_user != existing_user

    def test_installer_mixed_overwrite_scenario(self):
        """Test installer with mix of new and existing files."""
        # Add users to source
        self.source_store.save("user1", self.user1)  # Will conflict
        self.source_store.save("user2", self.user2)  # New file
        self.source_store.save("user3", self.user3)  # Will conflict

        # Add some users to destination
        existing_user1 = User("Existing User1", 50)
        existing_user3 = User("Existing User3", 60)
        self.dest_store.save("user1", existing_user1)
        self.dest_store.save("user3", existing_user3)

        # Install without overwrite
        result = self.installer.install(overwrite=False)

        assert result is True  # user2 was added

        # Verify results
        assert self.dest_store.load("user1") == existing_user1  # Not overwritten
        assert self.dest_store.load("user2") == self.user2  # New file added
        assert self.dest_store.load("user3") == existing_user3  # Not overwritten

        dest_list = self.dest_store.list()
        assert set(dest_list) == {"user1", "user2", "user3"}

    def test_installer_with_overwrite_mixed_scenario(self):
        """Test installer with overwrite in mixed scenario."""
        # Add users to source
        self.source_store.save("user1", self.user1)  # Will overwrite
        self.source_store.save("user2", self.user2)  # New file

        # Add user to destination
        existing_user = User("Existing User", 50)
        self.dest_store.save("user1", existing_user)

        result = self.installer.install(overwrite=True)

        assert result is True  # Files were changed

        # Verify both files are from source
        assert self.dest_store.load("user1") == self.user1  # Overwritten
        assert self.dest_store.load("user2") == self.user2  # New file

    def test_installer_reports_false_when_no_changes(self):
        """Test that installer returns False when no changes are made."""
        # Add same users to both source and destination
        self.source_store.save("user1", self.user1)
        self.dest_store.save("user1", self.user1)

        result = self.installer.install(overwrite=False)

        assert result is False  # No changes made

    def test_installer_with_different_adapters(self):
        """Test installer works with different object types."""
        # Create task stores and installer
        task_source = YamlStore[Task](self.base_path / "task_source", TaskAdapter)
        task_dest = YamlStore[Task](self.base_path / "task_dest", TaskAdapter)
        task_installer = YamlStoreInstaller(task_source, task_dest, TaskAdapter)

        # Add tasks to source
        task1 = Task("Task 1", False, 1)
        task2 = Task("Task 2", True, 2)
        task_source.save("task1", task1)
        task_source.save("task2", task2)

        result = task_installer.install()

        assert result is True
        assert set(task_dest.list()) == {"task1", "task2"}
        assert task_dest.load("task1") == task1
        assert task_dest.load("task2") == task2


class TestIntegration:
    """Integration tests for the complete yaml_store system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_complete_workflow(self):
        """Test complete workflow: create, save, load, install."""
        # Create stores
        templates_store = YamlStore[User](self.base_path / "templates", UserAdapter)
        user_store = YamlStore[User](self.base_path / "users", UserAdapter)

        # Add template users
        template_admin = User("Admin Template", 0, "admin@template.com")
        template_user = User("User Template", 0, "user@template.com")

        templates_store.save("admin", template_admin)
        templates_store.save("user", template_user)

        # Install templates to user store
        installer = YamlStoreInstaller(templates_store, user_store, UserAdapter)
        result = installer.install()

        assert result is True

        # Verify installation
        assert set(user_store.list()) == {"admin", "user"}

        # Modify and save a user
        admin_user = user_store.load("admin")
        admin_user.name = "Real Admin"
        admin_user.age = 35
        admin_user.email = "admin@company.com"
        user_store.save("admin", admin_user)

        # Add a new user
        new_user = User("John Doe", 28, "john@company.com")
        user_store.save("john", new_user)

        # Verify final state
        final_list = user_store.list()
        assert set(final_list) == {"admin", "user", "john"}

        loaded_admin = user_store.load("admin")
        assert loaded_admin.name == "Real Admin"
        assert loaded_admin.age == 35

        loaded_john = user_store.load("john")
        assert loaded_john == new_user

    def test_file_system_integration(self):
        """Test that files are actually created on the file system."""
        store = YamlStore[User](self.base_path / "fs_test", UserAdapter)

        user = User("FS Test", 30, "fs@test.com")
        store.save("fs_user", user)

        # Verify file exists on disk
        yaml_file = self.base_path / "fs_test" / "fs_user.yaml"
        assert yaml_file.exists()

        # Verify file content directly
        with yaml_file.open() as f:
            content = f.read()

        assert "name: FS Test" in content
        assert "age: 30" in content
        assert "email: fs@test.com" in content

        # Verify we can manually load the YAML
        with yaml_file.open() as f:
            data = yaml.safe_load(f)

        manual_user = UserAdapter.from_dict(data)
        assert manual_user == user

    def test_concurrent_store_access(self):
        """Test that multiple stores can access the same directory safely."""
        store_path = self.base_path / "shared"

        # Create multiple store instances
        store1 = YamlStore[User](store_path, UserAdapter)
        store2 = YamlStore[User](store_path, UserAdapter)

        # Save from first store
        user1 = User("User1", 25)
        store1.save("user1", user1)

        # Read from second store
        assert store2.exists("user1")
        loaded_user = store2.load("user1")
        assert loaded_user == user1

        # Save from second store
        user2 = User("User2", 30)
        store2.save("user2", user2)

        # Verify both stores see both files
        assert set(store1.list()) == {"user1", "user2"}
        assert set(store2.list()) == {"user1", "user2"}

    def test_error_handling_with_corrupted_yaml(self):
        """Test error handling when YAML file is corrupted."""
        store = YamlStore[User](self.base_path / "error_test", UserAdapter)

        # Create a corrupted YAML file manually
        yaml_file = store.directory / "corrupted.yaml"
        yaml_file.write_text("invalid: yaml: content: [unclosed")

        # Verify the file exists in listing but loading fails gracefully
        file_list = store.list()
        assert "corrupted" in file_list

        with pytest.raises(yaml.YAMLError):
            store.load("corrupted")

    def test_adapter_validation_in_store(self):
        """Test that store validates adapter at runtime."""
        # This test verifies that the protocol checking works in practice
        assert isinstance(UserAdapter, YamlStoreAdapter)

        # Create store with valid adapter
        store = YamlStore[User](self.base_path / "validation_test", UserAdapter)
        user = User("Valid", 25)

        # This should work fine
        store.save("valid", user)
        loaded = store.load("valid")
        assert loaded == user
