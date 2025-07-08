"""Tests for SnapshotManager class.

This module serves as the main entry point for SnapshotManager tests.
Individual test classes have been split into separate files for better organization.

Test files:
- test_snapshot_manager_init.py: Tests for __init__ method
- test_snapshot_manager_create_snapshot.py: Tests for create_snapshot method
- test_snapshot_manager_restore_snapshot.py: Tests for restore_snapshot method
- test_snapshot_manager_list_snapshots.py: Tests for list_snapshots method
- test_snapshot_manager_delete_snapshot.py: Tests for delete_snapshot method

Run all SnapshotManager tests with:
    pytest tests/context/test_snapshot_manager*.py

Each test file includes its own MockContext class for testing purposes.
This split organization keeps files under the 1000-line limit while maintaining
comprehensive test coverage for the SnapshotManager class.
"""
