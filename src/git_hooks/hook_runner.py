"""Generic hook runner to eliminate CLI duplication."""

import subprocess
from dataclasses import dataclass
from typing import List

from .config import ValidationConfig
from .core import ValidationResult, ValidationSeverity, Validator
from .file_validator import FileLengthValidator
from .function_validator import FunctionLengthValidator
from .module_validator import ModuleSizeValidator
from .utils import (
    DEFAULT_EXCLUDE_PATTERNS,
    get_all_files,
    get_modules,
    get_staged_files,
    print_results,
)


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
    """Create a validator instance from configuration."""
    validator_config = config.get_validator_config(validator_type)

    if validator_type == "file_length":
        return FileLengthValidator(
            limit=validator_config["limit"],
            warn_threshold=validator_config["warn_threshold"],
            urgent_threshold=validator_config["urgent_threshold"],
            exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
        )
    elif validator_type == "module_size":
        return ModuleSizeValidator(
            limit=validator_config["limit"],
            warn_threshold=validator_config["warn_threshold"],
            urgent_threshold=validator_config["urgent_threshold"],
            exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
        )
    elif validator_type == "function_length":
        return FunctionLengthValidator(
            limit=validator_config["limit"],
            warn_threshold=validator_config["warn_threshold"],
            urgent_threshold=validator_config["urgent_threshold"],
            exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
        )
    else:
        raise ValueError(f"Unknown validator type: {validator_type}")


class HookRunner:
    """Generic hook runner that eliminates CLI duplication."""

    def __init__(self, config: ValidationConfig) -> None:
        super().__init__()
        self.config = config

    def run_hook(self, hook_config: HookConfig, warning_mode: bool = False) -> int:
        """Run a validation hook with the specified configuration."""
        validator = create_validator(hook_config.validator_type, self.config)

        # Discover targets to validate
        if hook_config.discovery_method == "files":
            targets = get_staged_files() if is_git_repo() else get_all_files()
        elif hook_config.discovery_method == "modules":
            targets = get_modules()
        else:
            raise ValueError(
                f"Unknown discovery method: {hook_config.discovery_method}"
            )

        if not targets:
            print(f"✅ {hook_config.name}: No files to check")
            return 0

        # Validate all targets
        results: List[ValidationResult] = []
        for target in targets:
            result = validator.validate(target)
            if result:
                if warning_mode:
                    # In warning mode, include all results
                    results.append(result)
                else:
                    # In blocking mode, only include errors
                    if result.severity == ValidationSeverity.ERROR:
                        results.append(result)

        # Print results and determine exit code
        print_results(results, hook_config.name)

        if warning_mode:
            return 0  # Always succeed in warning mode
        else:
            return 1 if results else 0  # Fail if there are errors in blocking mode
