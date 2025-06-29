#!/usr/bin/env python3
"""
Extract the flow module into a separate package.
This demonstrates the module extraction process.
"""

import shutil
import sys
from pathlib import Path


def create_package_structure(package_name: str) -> Path:
    """Create the new package directory structure."""

    package_path = Path(f"src/goldentooth_agent/{package_name}")

    if package_path.exists():
        print(f"Package {package_name} already exists at {package_path}")
        response = input("Remove existing package? (y/N): ")
        if response.lower() == "y":
            shutil.rmtree(package_path)
        else:
            print("Aborting extraction")
            sys.exit(1)

    # Create package structure
    package_path.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    init_file = package_path / "__init__.py"
    init_content = f'''"""
{package_name.title()} package - extracted from core/{package_name.replace("_engine", "")}.

This package provides flow composition and execution capabilities
for the Goldentooth Agent system.
"""

# Re-export main components for compatibility
from .main import *  # noqa: F403,F401

__all__ = [
    # TODO: Add explicit exports
]
'''
    init_file.write_text(init_content)

    return package_path


def move_module_files(source_module: str, target_package: Path) -> list[Path]:
    """Move files from core module to new package."""

    source_path = Path(f"src/goldentooth_agent/core/{source_module}")

    if not source_path.exists():
        print(f"Source module {source_path} does not exist")
        sys.exit(1)

    moved_files = []

    # Move all Python files
    for py_file in source_path.glob("**/*.py"):
        if py_file.name == "__init__.py":
            # Rename to main.py to avoid conflicts
            target_file = target_package / "main.py"
        else:
            # Preserve relative structure
            relative_path = py_file.relative_to(source_path)
            target_file = target_package / relative_path

        # Create target directory if needed
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file (don't remove original yet)
        shutil.copy2(py_file, target_file)
        moved_files.append(target_file)
        print(f"Copied {py_file} -> {target_file}")

    # Copy README.md if it exists
    readme_source = source_path / "README.md"
    if readme_source.exists():
        readme_target = target_package / "README.md"
        shutil.copy2(readme_source, readme_target)
        moved_files.append(readme_target)
        print(f"Copied {readme_source} -> {readme_target}")

    return moved_files


def update_imports_in_file(file_path: Path, old_import: str, new_import: str):
    """Update import statements in a Python file."""

    if not file_path.suffix == ".py":
        return

    try:
        content = file_path.read_text()

        # Replace imports
        updated_content = content.replace(old_import, new_import)

        if updated_content != content:
            file_path.write_text(updated_content)
            print(f"Updated imports in {file_path}")

    except Exception as e:
        print(f"Error updating {file_path}: {e}")


def update_imports_across_codebase(old_module: str, new_package: str):
    """Update all import statements across the codebase."""

    old_import_base = f"goldentooth_agent.core.{old_module}"
    new_import_base = f"goldentooth_agent.{new_package}"

    # Find all Python files in the project
    src_path = Path("src")
    test_path = Path("tests")

    all_files = list(src_path.glob("**/*.py")) + list(test_path.glob("**/*.py"))

    import_patterns = [
        (f"from {old_import_base} import", f"from {new_import_base} import"),
        (f"from {old_import_base}.", f"from {new_import_base}."),
        (f"import {old_import_base}", f"import {new_import_base}"),
        (f"{old_import_base}.", f"{new_import_base}."),
    ]

    for file_path in all_files:
        for old_pattern, new_pattern in import_patterns:
            update_imports_in_file(file_path, old_pattern, new_pattern)


def create_compatibility_shim(old_module: str, new_package: str):
    """Create a compatibility shim in the old location."""

    old_path = Path(f"src/goldentooth_agent/core/{old_module}")

    # Create new __init__.py that re-exports from new location
    init_file = old_path / "__init__.py"

    shim_content = f'''"""
Compatibility shim for {old_module} module.

This module has been moved to goldentooth_agent.{new_package}.
This shim provides backward compatibility.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    f"goldentooth_agent.core.{old_module} is deprecated. "
    f"Use goldentooth_agent.{new_package} instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from goldentooth_agent.{new_package} import *  # noqa: F403,F401
'''

    init_file.write_text(shim_content)
    print(f"Created compatibility shim at {init_file}")


def move_tests(source_module: str, target_package: str) -> bool:
    """Move tests to match the new package structure."""

    import shutil

    old_test_path = Path(f"tests/core/{source_module}")
    new_test_path = Path(f"tests/{target_package}")

    if not old_test_path.exists():
        print(f"⚠️  No tests found at {old_test_path}")
        return True

    if new_test_path.exists():
        print(f"Test directory {new_test_path} already exists")
        response = input("Remove existing test directory? (y/N): ")
        if response.lower() == "y":
            shutil.rmtree(new_test_path)
        else:
            print("Skipping test move")
            return True

    # Copy tests to new location
    shutil.copytree(old_test_path, new_test_path)
    print(f"📋 Copied tests from {old_test_path} to {new_test_path}")

    # Update imports in test files if needed
    for test_file in new_test_path.glob("**/*.py"):
        update_imports_in_file(
            test_file,
            f"goldentooth_agent.core.{source_module}",
            f"goldentooth_agent.{target_package}",
        )

    # Remove old test directory
    shutil.rmtree(old_test_path)
    print(f"🗑️  Removed old test directory {old_test_path}")

    return True


def run_tests_for_package(package_name: str) -> bool:
    """Run tests to verify the extraction worked."""

    import subprocess

    print(f"\n🧪 Running tests for {package_name}...")

    try:
        # Check if new test location exists, otherwise fall back to old
        new_test_path = f"tests/{package_name}/"
        old_test_path = f"tests/core/{package_name.replace('_engine', '')}/"

        test_path = new_test_path if Path(new_test_path).exists() else old_test_path

        result = subprocess.run(
            ["poetry", "run", "pytest", test_path, "-v"], capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"✅ Tests pass for {package_name}")
            return True
        else:
            print(f"❌ Tests failed for {package_name}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def extract_module(source_module: str, target_package: str):
    """Extract a module into a new package."""

    print(f"🚀 Extracting {source_module} -> {target_package}")
    print("=" * 50)

    # Step 1: Create package structure
    print(f"📁 Creating package structure for {target_package}...")
    package_path = create_package_structure(target_package)

    # Step 2: Move files
    print(f"📦 Moving files from core/{source_module}...")
    moved_files = move_module_files(source_module, package_path)

    # Step 3: Update imports
    print("🔄 Updating imports across codebase...")
    update_imports_across_codebase(source_module, target_package)

    # Step 4: Create compatibility shim
    print("🔗 Creating compatibility shim...")
    create_compatibility_shim(source_module, target_package)

    # Step 5: Move tests to match new structure
    print("📋 Moving tests...")
    tests_moved = move_tests(source_module, target_package)

    # Step 6: Test the extraction
    print("🧪 Testing extraction...")
    tests_pass = run_tests_for_package(target_package)

    # Summary
    print("\n📊 EXTRACTION SUMMARY")
    print("=" * 30)
    print(f"Source: core/{source_module}")
    print(f"Target: {target_package}")
    print(f"Files moved: {len(moved_files)}")
    print(f"Tests pass: {'✅' if tests_pass else '❌'}")

    if tests_pass:
        print(f"\n🎉 Extraction of {source_module} completed successfully!")
        print(f"   New package: goldentooth_agent.{target_package}")
        print(
            f"   Compatibility: core.{source_module} still works (with deprecation warning)"
        )
    else:
        print("\n⚠️  Extraction completed but tests are failing")
        print("   You may need to fix import issues manually")

    return tests_pass


def main():
    """Extract the flow module as a demonstration."""

    if len(sys.argv) > 1:
        source_module = sys.argv[1]
        target_package = sys.argv[2] if len(sys.argv) > 2 else f"{source_module}_engine"
    else:
        source_module = "flow"
        target_package = "flow_engine"

    success = extract_module(source_module, target_package)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
