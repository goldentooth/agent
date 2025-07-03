"""Command-line interface for validation hooks."""

import sys

from .config import ValidationConfig
from .hook_runner import HookConfig, HookRunner


def check_file_length() -> int:
    """Check file lengths (blocking hook)."""
    config = ValidationConfig.from_environment()
    runner = HookRunner(config)
    hook_config = HookConfig(
        name="File length check", validator_type="file_length", discovery_method="files"
    )
    return runner.run_hook(hook_config, warning_mode=False)


def check_file_length_warnings() -> int:
    """Check file lengths (warning hook)."""
    config = ValidationConfig.from_environment()
    runner = HookRunner(config)
    hook_config = HookConfig(
        name="File length warnings",
        validator_type="file_length",
        discovery_method="files",
    )
    return runner.run_hook(hook_config, warning_mode=True)


def check_module_size() -> int:
    """Check module sizes (blocking hook)."""
    config = ValidationConfig.from_environment()
    runner = HookRunner(config)
    hook_config = HookConfig(
        name="Module size check",
        validator_type="module_size",
        discovery_method="modules",
    )
    return runner.run_hook(hook_config, warning_mode=False)


def check_module_size_warnings() -> int:
    """Check module sizes (warning hook)."""
    config = ValidationConfig.from_environment()
    runner = HookRunner(config)
    hook_config = HookConfig(
        name="Module size warnings",
        validator_type="module_size",
        discovery_method="modules",
    )
    return runner.run_hook(hook_config, warning_mode=True)


def check_function_length() -> int:
    """Check function lengths (blocking hook)."""
    config = ValidationConfig.from_environment()
    runner = HookRunner(config)
    hook_config = HookConfig(
        name="Function length check",
        validator_type="function_length",
        discovery_method="files",
    )
    return runner.run_hook(hook_config, warning_mode=False)


def check_function_length_warnings() -> int:
    """Check function lengths (warning hook)."""
    config = ValidationConfig.from_environment()
    runner = HookRunner(config)
    hook_config = HookConfig(
        name="Function length warnings",
        validator_type="function_length",
        discovery_method="files",
    )
    return runner.run_hook(hook_config, warning_mode=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.git_hooks.cli <hook_type>")
        print(
            "Hook types: file_length, file_length_warnings, module_size, module_size_warnings, function_length, function_length_warnings"
        )
        sys.exit(1)

    hook_type = sys.argv[1]

    if hook_type == "file_length":
        sys.exit(check_file_length())
    elif hook_type == "file_length_warnings":
        sys.exit(check_file_length_warnings())
    elif hook_type == "module_size":
        sys.exit(check_module_size())
    elif hook_type == "module_size_warnings":
        sys.exit(check_module_size_warnings())
    elif hook_type == "function_length":
        sys.exit(check_function_length())
    elif hook_type == "function_length_warnings":
        sys.exit(check_function_length_warnings())
    else:
        print(f"Unknown hook type: {hook_type}")
        sys.exit(1)
