"""Command-line interface for validation hooks."""

import sys
from pathlib import Path
from typing import Annotated, List, Optional

import typer

from .config import ValidationConfig
from .hook_runner import HookConfig, HookRunner
from .utils import get_all_files, get_staged_files


def is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    import subprocess

    return (
        subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True
        ).returncode
        == 0
    )


def get_files_by_glob(pattern: str, all_files: bool = False) -> List[Path]:
    """Get files matching a glob pattern."""
    import glob
    from pathlib import Path

    # If pattern doesn't contain wildcards, try direct path match first
    if "*" not in pattern and "?" not in pattern:
        direct_path = Path(pattern)
        if direct_path.exists() and direct_path.is_file():
            return [direct_path]

    # Use glob to find matching files
    glob_matches = glob.glob(pattern, recursive=True)
    matching_files = [Path(f) for f in glob_matches if Path(f).is_file()]

    # If using git context and not all_files, filter to only include tracked files
    if not all_files and is_git_repo():
        if get_staged_files():
            # If there are staged files, limit to staged files
            staged_files = set(get_staged_files())
            matching_files = [f for f in matching_files if f in staged_files]

    return matching_files


app = typer.Typer(
    help="Git hooks validation CLI",
    rich_markup_mode="rich",
)


def run_hook_with_config(
    hook_config: HookConfig,
    warning_mode: bool = False,
    target_files: Optional[List[Path]] = None,
    verbose: bool = False,
) -> int:
    """Run a hook with the given configuration."""
    validation_config = ValidationConfig.from_environment()
    runner = HookRunner(validation_config)
    return runner.run_hook(
        hook_config,
        warning_mode=warning_mode,
        target_files=target_files,
        verbose=verbose,
    )


def create_hook_config(hook_type: str) -> HookConfig:
    """Create HookConfig based on hook type."""
    if hook_type.startswith("file_length"):
        return HookConfig(
            name=(
                "File length check"
                if not hook_type.endswith("_warnings")
                else "File length warnings"
            ),
            validator_type="file_length",
            discovery_method="files",
        )
    elif hook_type.startswith("module_size"):
        return HookConfig(
            name=(
                "Module size check"
                if not hook_type.endswith("_warnings")
                else "Module size warnings"
            ),
            validator_type="module_size",
            discovery_method="modules",
        )
    elif hook_type.startswith("function_length"):
        return HookConfig(
            name=(
                "Function length check"
                if not hook_type.endswith("_warnings")
                else "Function length warnings"
            ),
            validator_type="function_length",
            discovery_method="files",
        )
    else:
        raise ValueError(f"Unknown hook type: {hook_type}")


@app.command()
def file_length(
    warnings: Annotated[
        bool, typer.Option(help="Show warnings instead of errors only")
    ] = False,
    all_files: Annotated[
        bool, typer.Option(help="Check all files instead of just staged files")
    ] = False,
    files: Annotated[
        Optional[str],
        typer.Option(help="Check files matching the specified glob pattern"),
    ] = None,
    verbose: Annotated[bool, typer.Option(help="Show detailed output")] = False,
) -> None:
    """Check file lengths."""
    hook_type = "file_length_warnings" if warnings else "file_length"
    _run_validation(hook_type, all_files, files, verbose)


@app.command()
def module_size(
    warnings: Annotated[
        bool, typer.Option(help="Show warnings instead of errors only")
    ] = False,
    all_files: Annotated[
        bool, typer.Option(help="Check all files instead of just staged files")
    ] = False,
    files: Annotated[
        Optional[str],
        typer.Option(help="Check files matching the specified glob pattern"),
    ] = None,
    verbose: Annotated[bool, typer.Option(help="Show detailed output")] = False,
) -> None:
    """Check module sizes."""
    hook_type = "module_size_warnings" if warnings else "module_size"
    _run_validation(hook_type, all_files, files, verbose)


@app.command()
def function_length(
    warnings: Annotated[
        bool, typer.Option(help="Show warnings instead of errors only")
    ] = False,
    all_files: Annotated[
        bool, typer.Option(help="Check all files instead of just staged files")
    ] = False,
    files: Annotated[
        Optional[str],
        typer.Option(help="Check files matching the specified glob pattern"),
    ] = None,
    verbose: Annotated[bool, typer.Option(help="Show detailed output")] = False,
) -> None:
    """Check function lengths."""
    hook_type = "function_length_warnings" if warnings else "function_length"
    _run_validation(hook_type, all_files, files, verbose)


def _run_validation(
    hook_type: str, all_files: bool, files: Optional[str], verbose: bool
) -> None:
    """Run validation with the specified parameters."""
    # Create hook config first
    hook_config = create_hook_config(hook_type)

    # Determine target files based on arguments
    target_files: Optional[List[Path]] = None
    if files:
        target_files = get_files_by_glob(files, all_files)
        if not target_files:
            typer.echo(f"No files found matching pattern: {files}")
            raise typer.Exit(0)
    elif all_files:
        # For module validation, don't pass target_files when using --all-files
        # Let the hook runner discover modules properly using get_modules()
        if hook_config.discovery_method == "modules":
            target_files = None  # Let hook runner use get_modules()
        else:
            target_files = get_all_files()

    # Run validation
    warning_mode = hook_type.endswith("_warnings")
    exit_code = run_hook_with_config(
        hook_config,
        warning_mode=warning_mode,
        target_files=target_files,
        verbose=verbose,
    )
    raise typer.Exit(exit_code)


# Legacy functions for backward compatibility with existing pre-commit hooks
def check_file_length() -> int:
    """Check file lengths (blocking hook)."""
    hook_config = HookConfig(
        name="File length check", validator_type="file_length", discovery_method="files"
    )
    return run_hook_with_config(hook_config, warning_mode=False)


def check_file_length_warnings() -> int:
    """Check file lengths (warning hook)."""
    hook_config = HookConfig(
        name="File length warnings",
        validator_type="file_length",
        discovery_method="files",
    )
    return run_hook_with_config(hook_config, warning_mode=True)


def check_module_size() -> int:
    """Check module sizes (blocking hook)."""
    hook_config = HookConfig(
        name="Module size check",
        validator_type="module_size",
        discovery_method="modules",
    )
    return run_hook_with_config(hook_config, warning_mode=False)


def check_module_size_warnings() -> int:
    """Check module sizes (warning hook)."""
    hook_config = HookConfig(
        name="Module size warnings",
        validator_type="module_size",
        discovery_method="modules",
    )
    return run_hook_with_config(hook_config, warning_mode=True)


def check_function_length() -> int:
    """Check function lengths (blocking hook)."""
    hook_config = HookConfig(
        name="Function length check",
        validator_type="function_length",
        discovery_method="files",
    )
    return run_hook_with_config(hook_config, warning_mode=False)


def check_function_length_warnings() -> int:
    """Check function lengths (warning hook)."""
    hook_config = HookConfig(
        name="Function length warnings",
        validator_type="function_length",
        discovery_method="files",
    )
    return run_hook_with_config(hook_config, warning_mode=True)


HOOK_DISPATCH = {
    "file_length": check_file_length,
    "file_length_warnings": check_file_length_warnings,
    "module_size": check_module_size,
    "module_size_warnings": check_module_size_warnings,
    "function_length": check_function_length,
    "function_length_warnings": check_function_length_warnings,
}


def main() -> None:
    """Legacy main entry point for backward compatibility."""
    if len(sys.argv) == 2 and sys.argv[1] in HOOK_DISPATCH:
        # Legacy mode: python -m src.git_hooks.cli function_length
        hook_func = HOOK_DISPATCH[sys.argv[1]]
        sys.exit(hook_func())
    else:
        # New Typer mode
        app()


if __name__ == "__main__":
    main()
