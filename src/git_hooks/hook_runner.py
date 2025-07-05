"""Generic hook runner to eliminate CLI duplication."""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

# Import validators to trigger registration
from . import (  # noqa: F401  # type: ignore[reportUnusedImport]
    file_validator,
    function_validator,
    module_validator,
)
from .config import ValidationConfig
from .core import ValidationResult, ValidationSeverity, Validator
from .utils import (
    DEFAULT_EXCLUDE_PATTERNS,
    get_all_files,
    get_modules,
    get_staged_files,
    print_results,
)
from .validator_registry import ValidatorRegistry


@dataclass
class HookConfig:
    """Configuration for a specific hook."""

    name: str
    validator_type: str
    discovery_method: str  # "files" or "modules"


def is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    return (
        subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True
        ).returncode
        == 0
    )


def create_validator(validator_type: str, config: ValidationConfig) -> Validator:
    """Create a validator instance from configuration using registry."""
    validator_config = config.get_validator_config(validator_type)

    # Add default exclude patterns to config
    validator_config = {
        **validator_config,
        "exclude_patterns": DEFAULT_EXCLUDE_PATTERNS,
    }

    return ValidatorRegistry.create(validator_type, validator_config)


class HookRunner:
    """Generic hook runner that eliminates CLI duplication."""

    def __init__(self, config: ValidationConfig) -> None:
        super().__init__()
        self.config = config

    def run_hook(
        self,
        hook_config: HookConfig,
        warning_mode: bool = False,
        target_files: Optional[List[Path]] = None,
        verbose: bool = False,
    ) -> int:
        """Run a validation hook with the specified configuration."""
        validator = create_validator(hook_config.validator_type, self.config)

        # Use provided target files or discover them
        if target_files is not None:
            targets = target_files
        else:
            targets = self._discover_targets(hook_config)

        if not targets:
            print(f"✅ {hook_config.name}: No files to check")
            return 0

        results = self._validate_targets(validator, targets, warning_mode, verbose)
        return self._process_results(results, hook_config.name, warning_mode)

    def _discover_targets(self, hook_config: HookConfig) -> List[Path]:
        """Discover targets to validate based on discovery method."""
        if hook_config.discovery_method == "files":
            return get_staged_files() if is_git_repo() else get_all_files()
        elif hook_config.discovery_method == "modules":
            return get_modules()
        else:
            raise ValueError(
                f"Unknown discovery method: {hook_config.discovery_method}"
            )

    def _validate_targets(
        self,
        validator: Validator,
        targets: List[Path],
        warning_mode: bool,
        verbose: bool = False,
    ) -> List[ValidationResult]:
        """Validate all targets and collect results."""
        results: List[ValidationResult] = []
        for target in targets:
            if verbose:
                print(f"Checking {target}...")
                # Show detailed function info for function length validator
                if hasattr(validator, "get_all_function_statements"):
                    function_info = getattr(validator, "get_all_function_statements")(
                        target
                    )
                    if function_info:
                        print(f"  Functions found:")
                        for (
                            func_name,
                            start_line,
                            end_line,
                            line_count,
                            stmt_count,
                        ) in function_info:
                            status = (
                                "❌"
                                if stmt_count > 15
                                else "⚠️" if stmt_count > 12 else "✅"
                            )
                            print(
                                f"    {func_name}: {stmt_count} statements, {line_count} lines (lines {start_line}-{end_line}) {status}"
                            )
                    else:
                        print(f"  No functions found")
                elif hasattr(validator, "get_all_function_info"):
                    function_info = getattr(validator, "get_all_function_info")(target)
                    if function_info:
                        print(f"  Functions found:")
                        for (
                            func_name,
                            start_line,
                            end_line,
                            line_count,
                        ) in function_info:
                            status = (
                                "❌"
                                if line_count > 15
                                else "⚠️" if line_count > 12 else "✅"
                            )
                            print(
                                f"    {func_name}: {line_count} lines (lines {start_line}-{end_line}) {status}"
                            )
                    else:
                        print(f"  No functions found")

            result = validator.validate(target)
            if result and self._should_include_result(result, warning_mode):
                results.append(result)
                if verbose:
                    print(f"  📋 Validation result: {result.message}")
            elif verbose and result is None:
                print(f"  ✅ No validation issues found")
        return results

    def _should_include_result(
        self, result: ValidationResult, warning_mode: bool
    ) -> bool:
        """Determine if result should be included based on mode."""
        if warning_mode:
            return True  # Include all results in warning mode
        else:
            return (
                result.severity == ValidationSeverity.ERROR
            )  # Only errors in blocking mode

    def _process_results(
        self, results: List[ValidationResult], hook_name: str, warning_mode: bool
    ) -> int:
        """Process results and determine exit code."""
        print_results(results, hook_name)
        return 0 if warning_mode else (1 if results else 0)
