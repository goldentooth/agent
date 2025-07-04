"""Command-line interface for validation hooks."""

import sys

from .config import ValidationConfig
from .hook_runner import HookConfig, HookRunner


def run_hook_with_config(config: HookConfig, warning_mode: bool = False) -> int:
    """Run a hook with the given configuration."""
    validation_config = ValidationConfig.from_environment()
    runner = HookRunner(validation_config)
    return runner.run_hook(config, warning_mode=warning_mode)


def check_file_length() -> int:
    """Check file lengths (blocking hook)."""
    config = HookConfig(
        name="File length check", validator_type="file_length", discovery_method="files"
    )
    return run_hook_with_config(config, warning_mode=False)


def check_file_length_warnings() -> int:
    """Check file lengths (warning hook)."""
    config = HookConfig(
        name="File length warnings",
        validator_type="file_length",
        discovery_method="files",
    )
    return run_hook_with_config(config, warning_mode=True)


def check_module_size() -> int:
    """Check module sizes (blocking hook)."""
    config = HookConfig(
        name="Module size check",
        validator_type="module_size",
        discovery_method="modules",
    )
    return run_hook_with_config(config, warning_mode=False)


def check_module_size_warnings() -> int:
    """Check module sizes (warning hook)."""
    config = HookConfig(
        name="Module size warnings",
        validator_type="module_size",
        discovery_method="modules",
    )
    return run_hook_with_config(config, warning_mode=True)


def check_function_length() -> int:
    """Check function lengths (blocking hook)."""
    config = HookConfig(
        name="Function length check",
        validator_type="function_length",
        discovery_method="files",
    )
    return run_hook_with_config(config, warning_mode=False)


def check_function_length_warnings() -> int:
    """Check function lengths (warning hook)."""
    config = HookConfig(
        name="Function length warnings",
        validator_type="function_length",
        discovery_method="files",
    )
    return run_hook_with_config(config, warning_mode=True)


HOOK_DISPATCH = {
    "file_length": check_file_length,
    "file_length_warnings": check_file_length_warnings,
    "module_size": check_module_size,
    "module_size_warnings": check_module_size_warnings,
    "function_length": check_function_length,
    "function_length_warnings": check_function_length_warnings,
}


def print_usage() -> None:
    """Print usage information and exit."""
    print("Usage: python -m src.git_hooks.cli <hook_type>")
    print(f"Hook types: {', '.join(HOOK_DISPATCH.keys())}")
    sys.exit(1)


def main() -> None:
    """Main entry point for CLI."""
    if len(sys.argv) != 2:
        print_usage()

    hook_type = sys.argv[1]
    hook_func = HOOK_DISPATCH.get(hook_type)

    if hook_func is None:
        print(f"Unknown hook type: {hook_type}")
        sys.exit(1)

    sys.exit(hook_func())


if __name__ == "__main__":
    main()
