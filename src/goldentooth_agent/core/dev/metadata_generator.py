"""Automated generation and maintenance of README.meta.yaml files."""

import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from antidote import injectable


@dataclass
class MetadataUpdateResult:
    """Result of a metadata update operation."""

    module_path: Path
    updated: bool = False
    would_update: bool = False
    changes: list[str] = None
    errors: list[str] = None

    def __post_init__(self) -> None:
        if self.changes is None:
            self.changes = []
        if self.errors is None:
            self.errors = []


@dataclass
class SymbolInfo:
    """Information about a symbol (class, function, constant)."""

    name: str
    docstring: str = ""
    signature: str = ""
    methods: list[str] = None
    public: bool = True

    def __post_init__(self) -> None:
        if self.methods is None:
            self.methods = []


@dataclass
class ModuleAnalysis:
    """Analysis result for a Python module."""

    module_name: str
    description: str
    file_count: int
    loc: int
    class_count: int
    function_count: int
    symbols: list[str]
    exports: list[str]
    internal_dependencies: list[str]
    external_dependencies: list[str]
    complexity: str  # "Low", "Medium", "High", "Critical"

    # Enhanced symbol information
    classes: list[SymbolInfo] = None
    functions: list[SymbolInfo] = None
    constants: list[SymbolInfo] = None

    def __post_init__(self) -> None:
        if self.classes is None:
            self.classes = []
        if self.functions is None:
            self.functions = []
        if self.constants is None:
            self.constants = []


@injectable
class ModuleMetadataGenerator:
    """Generates and maintains README.meta.yaml files for Python modules."""

    def __init__(self) -> None:
        self.project_patterns = {
            "goldentooth_agent.core.",
            "goldentooth_agent.cli.",
            "goldentooth_agent.flow_engine.",
        }
        self._git_available = self._check_git_available()

    def update_module_metadata(
        self, module_path: Path, force: bool = False, dry_run: bool = False
    ) -> MetadataUpdateResult:
        """Update README.meta.yaml for a single module."""
        result = MetadataUpdateResult(module_path=module_path)

        try:
            # Check if this is a Python module directory
            if not self._is_python_module(module_path):
                result.errors.append("Not a Python module directory")
                return result

            # Analyze the module
            analysis = self._analyze_module(module_path)

            # Load existing metadata if it exists
            meta_file = module_path / "README.meta.yaml"
            existing_metadata = {}
            if meta_file.exists():
                with open(meta_file) as f:
                    existing_metadata = yaml.safe_load(f) or {}

            # Generate new metadata
            new_metadata = self._generate_metadata(analysis, existing_metadata)

            # Check if update is needed
            if (
                not force
                and existing_metadata
                and not self._metadata_changed(existing_metadata, new_metadata)
            ):
                return result

            # Track changes
            changes = self._detect_changes(existing_metadata, new_metadata)
            result.changes.extend(changes)

            if dry_run:
                result.would_update = bool(changes)
                return result

            # Write new metadata
            self._write_metadata(meta_file, new_metadata)
            result.updated = True

        except Exception as e:
            result.errors.append(str(e))

        return result

    def update_all_modules(
        self, project_root: Path, force: bool = False, dry_run: bool = False
    ) -> list[MetadataUpdateResult]:
        """Update README.meta.yaml for all modules in the project."""
        results = []

        # Find all Python module directories
        module_dirs = self._find_module_directories(project_root)

        for module_dir in module_dirs:
            result = self.update_module_metadata(
                module_dir, force=force, dry_run=dry_run
            )
            results.append(result)

        return results

    def validate_module_metadata(self, module_path: Path) -> list[str]:
        """Validate README.meta.yaml against actual module content."""
        errors = []

        meta_file = module_path / "README.meta.yaml"
        if not meta_file.exists():
            errors.append("Missing README.meta.yaml file")
            return errors

        try:
            with open(meta_file) as f:
                metadata = yaml.safe_load(f)

            if not metadata:
                errors.append("Empty metadata file")
                return errors

            # Analyze current module state
            analysis = self._analyze_module(module_path)

            # Validate file count
            declared_files = metadata.get("file_count", 0)
            if abs(analysis.file_count - declared_files) > 1:
                errors.append(
                    f"File count mismatch: declared {declared_files}, "
                    f"actual {analysis.file_count}"
                )

            # Validate symbols
            declared_symbols = set(metadata.get("symbols", []))
            actual_symbols = set(analysis.symbols)

            missing_symbols = actual_symbols - declared_symbols
            if missing_symbols:
                errors.append(f"Missing symbols in metadata: {sorted(missing_symbols)}")

            extra_symbols = declared_symbols - actual_symbols
            if extra_symbols:
                errors.append(f"Extra symbols in metadata: {sorted(extra_symbols)}")

            # Validate exports
            declared_exports = set(metadata.get("exports", []))
            actual_exports = set(analysis.exports)

            if declared_exports != actual_exports:
                errors.append(
                    f"Exports mismatch - declared: {sorted(declared_exports)}, "
                    f"actual: {sorted(actual_exports)}"
                )

            # Validate dependencies
            declared_internal = set(metadata.get("internal_dependencies", []))
            actual_internal = set(analysis.internal_dependencies)

            missing_deps = actual_internal - declared_internal
            if missing_deps:
                errors.append(f"Missing internal dependencies: {sorted(missing_deps)}")

            # Check complexity assessment
            if analysis.file_count > 10 or analysis.loc > 3000:
                if metadata.get("complexity") not in ["High", "Critical"]:
                    errors.append("Module complexity should be High or Critical")

        except Exception as e:
            errors.append(f"Error reading metadata file: {e}")

        return errors

    def validate_all_metadata(self, project_root: Path) -> dict[Path, list[str]]:
        """Validate all README.meta.yaml files in the project."""
        all_errors = {}

        module_dirs = self._find_module_directories(project_root)

        for module_dir in module_dirs:
            errors = self.validate_module_metadata(module_dir)
            if errors:
                all_errors[module_dir] = errors

        return all_errors

    def update_changed_modules(
        self,
        project_root: Path,
        since_commit: str = "HEAD",
        force: bool = False,
        dry_run: bool = False,
    ) -> list[MetadataUpdateResult]:
        """Update README.meta.yaml for modules that have changed since the specified commit."""
        results = []

        # Get modules that have changed
        changed_modules = self._get_changed_python_modules(project_root, since_commit)

        if not changed_modules:
            return results

        # Update metadata for each changed module
        for module_dir in changed_modules:
            result = self.update_module_metadata(
                module_dir, force=force, dry_run=dry_run
            )
            results.append(result)

        return results

    def update_for_pre_commit(self, project_root: Path) -> list[MetadataUpdateResult]:
        """Update metadata for modules with staged changes (optimized for pre-commit)."""
        results = []

        # Get modules with staged changes
        staged_modules = self._get_staged_python_modules(project_root)

        if not staged_modules:
            return results

        # Update metadata for each staged module
        for module_dir in staged_modules:
            result = self.update_module_metadata(module_dir, force=True, dry_run=False)
            if result.updated:
                # Stage the updated metadata file
                self._stage_metadata_file(module_dir / "README.meta.yaml")
            results.append(result)

        return results

    def validate_for_commit(self, project_root: Path) -> list[str]:
        """Validate metadata for modules that will be committed."""
        all_errors = []

        # Get modules with staged changes
        staged_modules = self._get_staged_python_modules(project_root)

        if not staged_modules:
            # No staged Python modules, no validation needed
            return all_errors

        # Validate each staged module
        for module_dir in staged_modules:
            # Check if README.meta.yaml exists
            meta_file = module_dir / "README.meta.yaml"
            if not meta_file.exists():
                all_errors.append(f"{module_dir.name}: Missing README.meta.yaml file")
                continue

            # Validate the metadata
            errors = self.validate_module_metadata(module_dir)
            if errors:
                all_errors.extend([f"{module_dir.name}: {error}" for error in errors])

        return all_errors

    def check_metadata_freshness(self, project_root: Path) -> list[str]:
        """Check that README.meta.yaml files are newer than their corresponding Python files."""
        stale_modules = []

        # Find all Python module directories
        module_dirs = self._find_module_directories(project_root)

        for module_dir in module_dirs:
            staleness_info = self._check_module_metadata_freshness(module_dir)
            if staleness_info:
                stale_modules.append(staleness_info)

        return stale_modules

    def check_staged_metadata_freshness(self, project_root: Path) -> list[str]:
        """Check metadata freshness only for modules with staged changes."""
        stale_modules = []

        # Get modules with staged changes
        staged_modules = self._get_staged_python_modules(project_root)

        for module_dir in staged_modules:
            staleness_info = self._check_module_metadata_freshness(module_dir)
            if staleness_info:
                stale_modules.append(staleness_info)

        return stale_modules

    def _check_module_metadata_freshness(self, module_path: Path) -> str | None:
        """Check if a module's README.meta.yaml is fresh relative to its Python files."""
        meta_file = module_path / "README.meta.yaml"

        # If no metadata file exists, it's definitely stale
        if not meta_file.exists():
            return f"{module_path.name}: Missing README.meta.yaml file"

        try:
            meta_mtime = meta_file.stat().st_mtime

            # Check all Python files in the module
            py_files = list(module_path.glob("*.py"))
            if not py_files:
                # No Python files, metadata shouldn't exist or is unnecessary
                return None

            # Find the newest Python file
            newest_py_mtime = max(py_file.stat().st_mtime for py_file in py_files)
            newest_py_file = max(py_files, key=lambda f: f.stat().st_mtime)

            # Allow a small tolerance (1 second) for filesystem timestamp precision
            if newest_py_mtime > meta_mtime + 1:
                from datetime import datetime

                meta_time = datetime.fromtimestamp(meta_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                py_time = datetime.fromtimestamp(newest_py_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                return (
                    f"{module_path.name}: README.meta.yaml ({meta_time}) is older than "
                    f"{newest_py_file.name} ({py_time})"
                )

            return None

        except OSError as e:
            return f"{module_path.name}: Error checking file timestamps: {e}"

    def generate_commit_message_info(self, project_root: Path) -> str | None:
        """Generate information about metadata changes for commit messages."""
        if not self._git_available:
            return None

        try:
            # Check if any README.meta.yaml files are staged
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--", "**/README.meta.yaml"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            staged_meta_files = [
                line.strip() for line in result.stdout.splitlines() if line.strip()
            ]

            if not staged_meta_files:
                return None

            # Generate summary of metadata changes
            module_count = len(staged_meta_files)

            if module_count == 1:
                module_name = Path(staged_meta_files[0]).parent.name
                return f"Update metadata for {module_name} module"
            else:
                return f"Update metadata for {module_count} modules"

        except subprocess.CalledProcessError:
            return None

    def _check_git_available(self) -> bool:
        """Check if git is available and we're in a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_changed_python_modules(
        self, project_root: Path, since_commit: str = "HEAD"
    ) -> list[Path]:
        """Get Python modules that have changed since the specified commit."""
        if not self._git_available:
            # Fall back to all modules if git is not available
            return self._find_module_directories(project_root)

        changed_modules = set()

        try:
            # Get list of changed Python files
            result = subprocess.run(
                ["git", "diff", "--name-only", since_commit, "--", "*.py"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            changed_files = [
                project_root / line.strip()
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            # Group files by their module directory
            for file_path in changed_files:
                if file_path.exists() and file_path.suffix == ".py":
                    module_dir = self._find_module_directory_for_file(file_path)
                    if module_dir:
                        changed_modules.add(module_dir)

        except subprocess.CalledProcessError:
            # Fall back to all modules if git command fails
            return self._find_module_directories(project_root)

        return sorted(changed_modules)

    def _get_staged_python_modules(self, project_root: Path) -> list[Path]:
        """Get Python modules with staged changes."""
        if not self._git_available:
            return []

        staged_modules = set()

        try:
            # Get list of staged Python files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--", "*.py"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            staged_files = [
                project_root / line.strip()
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            # Group files by their module directory
            for file_path in staged_files:
                if file_path.exists() and file_path.suffix == ".py":
                    module_dir = self._find_module_directory_for_file(file_path)
                    if module_dir:
                        staged_modules.add(module_dir)

        except subprocess.CalledProcessError:
            return []

        return sorted(staged_modules)

    def _find_module_directory_for_file(self, file_path: Path) -> Path | None:
        """Find the most specific module directory that contains the given Python file."""
        # Define exclusion patterns (same as in _find_module_directories)
        excluded_dirs = ["old", "tests", "examples", "scripts"]
        
        # Start from the file's directory and walk up to find all module directories
        current_dir = file_path.parent
        most_specific_module = None

        while current_dir != current_dir.parent:  # Stop at filesystem root
            # Check if this directory should be excluded
            if any(f"/{dirname}/" in str(current_dir) or str(current_dir).endswith(f"/{dirname}") for dirname in excluded_dirs):
                current_dir = current_dir.parent
                continue
                
            # Check if this directory is a Python module
            if self._is_python_module(current_dir):
                # This is a module directory - keep track of the most specific one
                if most_specific_module is None:
                    most_specific_module = current_dir

            current_dir = current_dir.parent

        return most_specific_module

    def _stage_file(self, file_path: Path) -> None:
        """Stage a file for commit."""
        if not self._git_available or not file_path.exists():
            return

        try:
            subprocess.run(
                ["git", "add", str(file_path)], cwd=file_path.parent, check=True
            )
        except subprocess.CalledProcessError:
            # Ignore errors if staging fails
            pass

    def _stage_metadata_file(self, metadata_file: Path) -> None:
        """Stage a metadata file for commit (legacy alias)."""
        self._stage_file(metadata_file)

    def _is_python_module(self, path: Path) -> bool:
        """Check if a directory is a Python module."""
        if not path.is_dir():
            return False

        # Must contain at least one .py file
        py_files = list(path.glob("*.py"))
        return len(py_files) > 0

    def _find_module_directories(self, project_root: Path) -> list[Path]:
        """Find all Python module directories in the project."""
        module_dirs = []

        # Look in src/ directory primarily
        src_dir = project_root / "src"
        if src_dir.exists():
            for path in src_dir.rglob("*"):
                if path.is_dir() and self._is_python_module(path):
                    # Skip __pycache__ and other special directories
                    if path.name.startswith("__") and path.name.endswith("__"):
                        continue
                    # Skip excluded directories
                    excluded_dirs = ["old", "tests", "examples", "scripts"]
                    if any(f"/{dirname}/" in str(path) or str(path).endswith(f"/{dirname}") for dirname in excluded_dirs):
                        continue
                    module_dirs.append(path)

        # Also check for modules in project root
        for path in project_root.rglob("*"):
            if (
                path.is_dir()
                and self._is_python_module(path)
                and not any(part.startswith(".") for part in path.parts)
                and path not in module_dirs
                and not any(f"/{dirname}/" in str(path) or str(path).endswith(f"/{dirname}") for dirname in ["old", "tests", "examples", "scripts"])  # Skip excluded directories
            ):
                module_dirs.append(path)

        return sorted(module_dirs)

    def _analyze_module(self, module_path: Path) -> ModuleAnalysis:
        """Analyze a Python module directory."""
        py_files = list(module_path.glob("*.py"))

        # Basic metrics
        file_count = len(py_files)
        total_loc = 0

        # Use sets to prevent duplicates across files
        all_defined_symbols = set()
        all_classes = set()
        all_functions = set()  # Module-level functions only
        all_total_functions = set()  # All functions including methods
        all_constants = set()
        all_type_aliases = set()
        internal_deps = set()
        external_deps = set()

        # Collect detailed symbol information
        all_detailed_classes: list[SymbolInfo] = []
        all_detailed_functions: list[SymbolInfo] = []
        all_detailed_constants: list[SymbolInfo] = []

        # Analyze each Python file
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                # Count non-empty lines
                total_loc += len(
                    [line for line in content.splitlines() if line.strip()]
                )

                # Parse AST for detailed analysis
                tree = ast.parse(content)
                file_analysis = self._analyze_ast(tree, py_file)

                # Aggregate symbols (only actual definitions, not re-exports)
                all_defined_symbols.update(file_analysis["symbols"])
                all_classes.update(file_analysis["classes"])
                all_functions.update(file_analysis["functions"])  # Module-level only
                all_total_functions.update(
                    file_analysis["total_functions"]
                )  # All functions
                all_constants.update(file_analysis["constants"])
                all_type_aliases.update(file_analysis["type_aliases"])

                # Aggregate dependencies
                internal_deps.update(file_analysis["internal_deps"])
                external_deps.update(file_analysis["external_deps"])

                # Aggregate detailed symbol information
                all_detailed_classes.extend(file_analysis["detailed_classes"])
                all_detailed_functions.extend(file_analysis["detailed_functions"])
                all_detailed_constants.extend(file_analysis["detailed_constants"])

            except Exception:
                # Skip files that can't be parsed, but log the issue
                continue

        # Determine exports from __init__.py (these may include re-exports)
        exports = self._get_exports(module_path)

        # Clean up dependencies - remove duplicates and sort
        cleaned_internal_deps = sorted(internal_deps)
        cleaned_external_deps = sorted(external_deps)

        # Assess complexity based on actual metrics
        complexity = self._assess_complexity(
            file_count, total_loc, len(all_classes), len(all_functions)
        )

        # Generate module name from path
        module_name = self._generate_module_name(module_path)

        # Combine all defined symbols for the final list
        final_symbols = (
            all_defined_symbols
            | all_classes
            | all_functions
            | all_constants
            | all_type_aliases
        )

        # Generate module description (we'll enhance this later)
        module_description = f"{module_name} module"

        return ModuleAnalysis(
            module_name=module_name,
            description=module_description,
            file_count=file_count,
            loc=total_loc,
            class_count=len(all_classes),
            function_count=len(
                all_total_functions
            ),  # Use total function count including methods
            symbols=sorted(final_symbols),
            exports=sorted(set(exports)),  # Deduplicate exports too
            internal_dependencies=cleaned_internal_deps,
            external_dependencies=cleaned_external_deps,
            complexity=complexity,
            classes=all_detailed_classes,
            functions=all_detailed_functions,
            constants=all_detailed_constants,
        )

    def _analyze_ast(
        self, tree: ast.AST, module_path: Path | None = None
    ) -> dict[str, Any]:
        """Analyze an AST for symbols and dependencies."""
        # Use sets throughout to prevent duplicates
        defined_symbols = set()  # Actually defined in this module
        classes = set()
        functions = set()
        constants = set()
        type_aliases = set()
        internal_deps = set()
        external_deps = set()
        # Note: re-exported symbols tracking removed as unused

        # Enhanced symbol information
        detailed_classes: list[SymbolInfo] = []
        detailed_functions: list[SymbolInfo] = []
        detailed_constants: list[SymbolInfo] = []

        # First pass: collect all module-level definitions and imports
        module_level_nodes = list(tree.body)
        imported_names = set()  # Track what we import for re-export detection

        for node in module_level_nodes:
            # Actual definitions (not nested)
            if isinstance(node, ast.ClassDef):
                defined_symbols.add(node.name)
                classes.add(node.name)

                # Collect detailed class information
                detailed_classes.append(
                    SymbolInfo(
                        name=node.name,
                        docstring=self._extract_docstring(node),
                        signature="",  # Classes don't have signatures like functions
                        methods=self._get_class_methods(node),
                        public=not node.name.startswith("_"),
                    )
                )

                # Also count methods within classes as functions
                for class_node in node.body:
                    if isinstance(class_node, ast.FunctionDef | ast.AsyncFunctionDef):
                        # Don't add to defined_symbols as these aren't module-level
                        # but do count them as functions for metrics
                        functions.add(f"{node.name}.{class_node.name}")

            elif isinstance(node, ast.FunctionDef):
                defined_symbols.add(node.name)
                functions.add(node.name)

                # Collect detailed function information
                detailed_functions.append(
                    SymbolInfo(
                        name=node.name,
                        docstring=self._extract_docstring(node),
                        signature=self._get_function_signature(node),
                        public=not node.name.startswith("_"),
                    )
                )

            elif isinstance(node, ast.AsyncFunctionDef):
                defined_symbols.add(node.name)
                functions.add(node.name)

                # Collect detailed function information
                detailed_functions.append(
                    SymbolInfo(
                        name=node.name,
                        docstring=self._extract_docstring(node),
                        signature=self._get_function_signature(node),
                        public=not node.name.startswith("_"),
                    )
                )

            # Module-level assignments (constants, type aliases, etc.)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        symbol_name = target.id
                        defined_symbols.add(symbol_name)

                        # Categorize the assignment
                        if symbol_name.isupper():
                            constants.add(symbol_name)

                            # Collect detailed constant information
                            constant_value = ""
                            try:
                                if isinstance(node.value, ast.Constant):
                                    constant_value = repr(node.value.value)
                                elif isinstance(node.value, ast.Str):  # Python < 3.8
                                    constant_value = repr(node.value.s)
                                elif isinstance(node.value, ast.Num):  # Python < 3.8
                                    constant_value = repr(node.value.n)
                            except Exception:
                                constant_value = (
                                    ast.unparse(node.value)
                                    if hasattr(ast, "unparse")
                                    else ""
                                )

                            detailed_constants.append(
                                SymbolInfo(
                                    name=symbol_name,
                                    docstring="",  # Constants typically don't have docstrings
                                    signature=constant_value,  # Use signature field for value
                                    public=not symbol_name.startswith("_"),
                                )
                            )
                        elif self._is_type_alias_assignment(node):
                            type_aliases.add(symbol_name)

            # Type aliases with new syntax (Python 3.12+)
            elif isinstance(node, ast.TypeAlias):
                if isinstance(node.name, ast.Name):
                    symbol_name = node.name.id
                    defined_symbols.add(symbol_name)
                    type_aliases.add(symbol_name)

            # Direct imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imported_name = alias.asname or alias.name.split(".")[-1]
                    imported_names.add(imported_name)

                    # Track dependencies
                    module_name = alias.name.split(".")[0]
                    if self._is_internal_dependency(alias.name):
                        internal_deps.add(alias.name)
                    else:
                        external_deps.add(module_name)

            # From imports
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Track the module dependency
                    if self._is_internal_dependency(node.module):
                        internal_deps.add(node.module)
                    else:
                        module_name = node.module.split(".")[0]
                        external_deps.add(module_name)

                    # Track imported names for re-export detection
                    for alias in node.names:
                        if alias.name != "*":  # Skip star imports
                            imported_name = alias.asname or alias.name
                            imported_names.add(imported_name)

        # All symbols that exist in this module (defined or imported)
        all_symbols = defined_symbols | imported_names

        # Count all functions (including methods) for metrics
        total_function_count = len(
            [f for f in functions if "." not in f]
        )  # Module-level functions
        total_function_count += len([f for f in functions if "." in f])  # Methods

        # But only include module-level functions in symbols
        module_level_functions = {f for f in functions if "." not in f}

        return {
            "symbols": defined_symbols,  # Only actual module-level definitions
            "all_symbols": all_symbols,  # Definitions + imports
            "classes": classes,
            "functions": module_level_functions,  # Only module-level functions for symbols
            "total_functions": functions,  # All functions including methods for counting
            "constants": constants,
            "type_aliases": type_aliases,
            "internal_deps": internal_deps,
            "external_deps": external_deps,
            "imported_names": imported_names,
            # Enhanced symbol information
            "detailed_classes": detailed_classes,
            "detailed_functions": detailed_functions,
            "detailed_constants": detailed_constants,
        }

    def _is_type_alias_assignment(self, node: ast.Assign) -> bool:
        """Check if an assignment is likely a type alias."""
        if not isinstance(
            node.value, ast.Name | ast.Subscript | ast.Attribute | ast.Constant
        ):
            return False

        # Check if the target name suggests it's a type (PascalCase)
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                if name[0].isupper() and not name.isupper():  # PascalCase, not CONSTANT
                    return True

        return False

    def _extract_docstring(self, node: ast.AST) -> str:
        """Extract docstring from an AST node."""
        if (
            isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            return node.body[0].value.value.strip()
        return ""

    def _get_function_signature(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> str:
        """Generate function signature from AST node."""
        args = []

        # Regular arguments
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        # *args
        if node.args.vararg:
            vararg_str = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                vararg_str += f": {ast.unparse(node.args.vararg.annotation)}"
            args.append(vararg_str)

        # **kwargs
        if node.args.kwarg:
            kwarg_str = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                kwarg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
            args.append(kwarg_str)

        # Return type
        return_type = ""
        if node.returns:
            return_type = f" -> {ast.unparse(node.returns)}"

        async_prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        return f"{async_prefix}def {node.name}({', '.join(args)}){return_type}"

    def _get_class_methods(self, node: ast.ClassDef) -> list[str]:
        """Get list of public methods from a class definition."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if not item.name.startswith("_"):  # Only public methods
                    methods.append(item.name)
        return methods

    def _is_internal_dependency(self, module_name: str) -> bool:
        """Check if a module is an internal project dependency."""
        return any(module_name.startswith(pattern) for pattern in self.project_patterns)

    def _get_exports(self, module_path: Path) -> list[str]:
        """Get exported symbols from __init__.py."""
        init_file = module_path / "__init__.py"
        if not init_file.exists():
            return []

        exports = set()  # Use set to prevent duplicates

        try:
            content = init_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Only look at module-level nodes
            for node in tree.body:
                # Look for __all__ assignment (explicit exports)
                if (
                    isinstance(node, ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "__all__"
                ):

                    if isinstance(node.value, ast.List):
                        for item in node.value.elts:
                            if isinstance(item, ast.Str):
                                exports.add(item.s)
                            elif isinstance(item, ast.Constant) and isinstance(
                                item.value, str
                            ):
                                exports.add(item.value)

                    # If we found __all__, that's the authoritative export list
                    return sorted(exports)

                # If no __all__, look for direct imports that make symbols available
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            if alias.name != "*":  # Skip star imports
                                export_name = alias.asname or alias.name
                                exports.add(export_name)

                # Direct imports that create new names in the module
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        export_name = alias.asname or alias.name.split(".")[-1]
                        exports.add(export_name)

                # Module-level definitions are also implicit exports
                elif isinstance(
                    node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
                ):
                    if not node.name.startswith("_"):  # Don't include private symbols
                        exports.add(node.name)

                # Module-level assignments (constants, etc.)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith(
                            "_"
                        ):
                            exports.add(target.id)

        except Exception:
            # If we can't parse __init__.py, return empty list
            return []

        return sorted(exports)

    def _assess_complexity(
        self, file_count: int, loc: int, class_count: int, func_count: int
    ) -> str:
        """Assess module complexity."""
        if file_count > 10 or loc > 3000 or class_count > 15:
            return "Critical"
        elif file_count > 5 or loc > 1500 or class_count > 8:
            return "High"
        elif file_count > 2 or loc > 500 or class_count > 3:
            return "Medium"
        else:
            return "Low"

    def _generate_module_name(self, module_path: Path) -> str:
        """Generate a human-readable module name from path."""
        # Take the last directory name and make it readable
        name = module_path.name

        # Convert snake_case to Title Case
        words = name.replace("_", " ").split()
        return " ".join(word.capitalize() for word in words)

    def _generate_metadata(
        self, analysis: ModuleAnalysis, existing: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate metadata dictionary from analysis."""
        metadata = {
            "module_name": analysis.module_name,
            "description": analysis.description,
            "complexity": analysis.complexity,
            "file_count": analysis.file_count,
            "loc": f"~{analysis.loc}",
            "test_coverage": existing.get(
                "test_coverage", "Medium"
            ),  # Preserve manual setting
            "class_count": analysis.class_count,
            "function_count": analysis.function_count,
            "coverage_target": existing.get(
                "coverage_target", "90%+"
            ),  # Preserve manual setting
            "test_perf": existing.get(
                "test_perf", "All tests <200ms"
            ),  # Preserve manual setting
        }

        # Dependencies
        if analysis.internal_dependencies:
            metadata["internal_dependencies"] = analysis.internal_dependencies
        else:
            metadata["internal_dependencies"] = []

        if analysis.external_dependencies:
            metadata["external_dependencies"] = analysis.external_dependencies
        else:
            metadata["external_dependencies"] = []

        # Symbols and exports
        metadata["symbols"] = analysis.symbols
        metadata["exports"] = analysis.exports

        # Enhanced symbol information
        if analysis.classes:
            metadata["classes"] = [
                {
                    "name": cls.name,
                    "docstring": cls.docstring,
                    "methods": cls.methods,
                    "public": cls.public,
                }
                for cls in analysis.classes
                if cls.public  # Only include public classes
            ]

        if analysis.functions:
            metadata["functions"] = [
                {
                    "name": func.name,
                    "signature": func.signature,
                    "docstring": func.docstring,
                    "public": func.public,
                }
                for func in analysis.functions
                if func.public  # Only include public functions
            ]

        if analysis.constants:
            metadata["constants"] = [
                {
                    "name": const.name,
                    "value": const.signature,  # We stored the value in signature field
                    "public": const.public,
                }
                for const in analysis.constants
                if const.public  # Only include public constants
            ]

        return metadata

    def _metadata_changed(self, old: dict[str, Any], new: dict[str, Any]) -> bool:
        """Check if metadata has meaningfully changed."""
        # Compare key fields that are auto-generated
        key_fields = [
            "file_count",
            "loc",
            "class_count",
            "function_count",
            "symbols",
            "exports",
            "internal_dependencies",
            "external_dependencies",
        ]

        for field in key_fields:
            if old.get(field) != new.get(field):
                return True

        return False

    def _detect_changes(self, old: dict[str, Any], new: dict[str, Any]) -> list[str]:
        """Detect specific changes between metadata versions."""
        changes = []

        # Check numeric fields
        for field in ["file_count", "class_count", "function_count"]:
            old_val = old.get(field, 0)
            new_val = new.get(field, 0)
            if old_val != new_val:
                changes.append(f"{field}: {old_val} → {new_val}")

        # Check LOC (handle ~ prefix)
        old_loc = str(old.get("loc", "~0")).replace("~", "")
        new_loc = str(new.get("loc", "~0")).replace("~", "")
        if old_loc != new_loc:
            changes.append(f"loc: ~{old_loc} → ~{new_loc}")

        # Check list fields
        for field in [
            "symbols",
            "exports",
            "internal_dependencies",
            "external_dependencies",
        ]:
            old_set = set(old.get(field, []))
            new_set = set(new.get(field, []))

            added = new_set - old_set
            removed = old_set - new_set

            if added:
                changes.append(f"{field}: added {sorted(added)}")
            if removed:
                changes.append(f"{field}: removed {sorted(removed)}")

        # Check complexity
        old_complexity = old.get("complexity", "Low")
        new_complexity = new.get("complexity", "Low")
        if old_complexity != new_complexity:
            changes.append(f"complexity: {old_complexity} → {new_complexity}")

        return changes

    def _write_metadata(self, meta_file: Path, metadata: dict[str, Any]) -> None:
        """Write metadata to YAML file with proper formatting."""
        with open(meta_file, "w") as f:
            # Write with clean formatting
            yaml.dump(
                metadata,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=80,
            )

    def generate_readme_from_metadata(self, module_path: Path) -> str:
        """Generate README.md content from README.meta.yaml."""
        meta_file = module_path / "README.meta.yaml"
        if not meta_file.exists():
            raise FileNotFoundError(f"No README.meta.yaml found in {module_path}")

        with open(meta_file) as f:
            metadata = yaml.safe_load(f)

        if not metadata:
            raise ValueError(f"Empty metadata in {meta_file}")

        return self._generate_readme_content(metadata)

    def _generate_readme_content(self, metadata: dict[str, Any]) -> str:
        """Generate README.md content from metadata dictionary."""
        sections = []

        # Title and description
        module_name = metadata.get("module_name", "Module")
        description = metadata.get("description", f"{module_name} module")

        sections.append(f"# {module_name}")
        sections.append("")
        sections.append(description)
        sections.append("")

        # Overview section
        sections.append("## Overview")
        sections.append("")
        complexity = metadata.get("complexity", "Unknown")
        file_count = metadata.get("file_count", 0)
        loc = metadata.get("loc", "~0")
        class_count = metadata.get("class_count", 0)
        function_count = metadata.get("function_count", 0)

        sections.append(f"- **Complexity**: {complexity}")
        sections.append(f"- **Files**: {file_count} Python files")
        sections.append(f"- **Lines of Code**: {loc}")
        sections.append(f"- **Classes**: {class_count}")
        sections.append(f"- **Functions**: {function_count}")
        sections.append("")

        # API Reference
        sections.append("## API Reference")
        sections.append("")

        # Classes
        classes = metadata.get("classes", [])
        if classes:
            sections.append("### Classes")
            sections.append("")
            for cls in classes:
                if not cls.get("public", True):
                    continue

                name = cls.get("name", "")
                docstring = cls.get("docstring", "")
                methods = cls.get("methods", [])

                sections.append(f"#### {name}")
                if docstring:
                    sections.append(f"{docstring}")
                else:
                    sections.append(f"Class for {name.lower()} functionality.")

                if methods:
                    sections.append("")
                    sections.append("**Public Methods:**")
                    for method in methods:
                        sections.append(f"- `{method}()`")

                sections.append("")

        # Functions
        functions = metadata.get("functions", [])
        if functions:
            sections.append("### Functions")
            sections.append("")
            for func in functions:
                if not func.get("public", True):
                    continue

                name = func.get("name", "")
                signature = func.get("signature", "")
                docstring = func.get("docstring", "")

                sections.append(f"#### `{signature}`")
                if docstring:
                    sections.append(f"{docstring}")
                else:
                    sections.append(f"Function {name}.")
                sections.append("")

        # Constants
        constants = metadata.get("constants", [])
        if constants:
            sections.append("### Constants")
            sections.append("")
            for const in constants:
                if not const.get("public", True):
                    continue

                name = const.get("name", "")
                value = const.get("value", "")

                sections.append(f"#### `{name}`")
                if value:
                    sections.append(f"Value: `{value}`")
                sections.append("")

        # Dependencies
        internal_deps = metadata.get("internal_dependencies", [])
        external_deps = metadata.get("external_dependencies", [])

        if internal_deps or external_deps:
            sections.append("## Dependencies")
            sections.append("")

            if internal_deps:
                sections.append("### Internal Dependencies")
                for dep in internal_deps:
                    sections.append(f"- `{dep}`")
                sections.append("")

            if external_deps:
                sections.append("### External Dependencies")
                for dep in external_deps:
                    sections.append(f"- `{dep}`")
                sections.append("")

        # Exports
        exports = metadata.get("exports", [])
        if exports:
            sections.append("## Exports")
            sections.append("")
            sections.append("This module exports the following symbols:")
            sections.append("")
            for export in exports:
                sections.append(f"- `{export}`")
            sections.append("")

        # Testing and Quality
        sections.append("## Quality Metrics")
        sections.append("")
        test_coverage = metadata.get("test_coverage", "Unknown")
        coverage_target = metadata.get("coverage_target", "90%+")
        test_perf = metadata.get("test_perf", "All tests <200ms")

        sections.append(f"- **Test Coverage**: {test_coverage}")
        sections.append(f"- **Coverage Target**: {coverage_target}")
        sections.append(f"- **Performance**: {test_perf}")
        sections.append("")

        return "\n".join(sections)

    def write_readme_from_metadata(self, module_path: Path) -> bool:
        """Generate and write README.md from README.meta.yaml."""
        try:
            readme_content = self.generate_readme_from_metadata(module_path)
            readme_file = module_path / "README.md"

            with open(readme_file, "w") as f:
                f.write(readme_content)

            return True
        except Exception:
            return False

    def update_all_readmes(self, project_root: Path) -> list[Path]:
        """Generate README.md files for all modules that have metadata."""
        updated_readmes = []

        # Find all README.meta.yaml files
        for meta_file in project_root.rglob("README.meta.yaml"):
            # Skip excluded directories
            if any(
                excluded in str(meta_file)
                for excluded in ["/old/", "/examples/", "/tests/"]
            ):
                continue

            module_dir = meta_file.parent
            if self.write_readme_from_metadata(module_dir):
                updated_readmes.append(module_dir / "README.md")

        return updated_readmes

    def check_readme_freshness(self, project_root: Path) -> list[str]:
        """Check that README.md files are newer than their corresponding README.meta.yaml files."""
        stale_readmes = []

        # Find all README.meta.yaml files
        for meta_file in project_root.rglob("README.meta.yaml"):
            # Skip excluded directories
            if any(
                excluded in str(meta_file)
                for excluded in ["/old/", "/examples/", "/tests/"]
            ):
                continue

            module_dir = meta_file.parent
            staleness_info = self._check_readme_freshness(module_dir)
            if staleness_info:
                stale_readmes.append(staleness_info)

        return stale_readmes

    def check_staged_readme_freshness(self, project_root: Path) -> list[str]:
        """Check README freshness only for modules with staged changes."""
        stale_readmes = []

        # Get modules with staged changes
        staged_modules = self._get_staged_python_modules(project_root)

        for module_dir in staged_modules:
            staleness_info = self._check_readme_freshness(module_dir)
            if staleness_info:
                stale_readmes.append(staleness_info)

        return stale_readmes

    def _check_readme_freshness(self, module_path: Path) -> str | None:
        """Check if a module's README.md is fresh relative to its README.meta.yaml."""
        meta_file = module_path / "README.meta.yaml"
        readme_file = module_path / "README.md"

        # If no metadata file exists, no README is expected
        if not meta_file.exists():
            return None

        # If metadata exists but no README, it's stale
        if not readme_file.exists():
            return (
                f"{module_path.name}: Missing README.md file (README.meta.yaml exists)"
            )

        try:
            meta_mtime = meta_file.stat().st_mtime
            readme_mtime = readme_file.stat().st_mtime

            # Allow a small tolerance (1 second) for filesystem timestamp precision
            if meta_mtime > readme_mtime + 1:
                from datetime import datetime

                meta_time = datetime.fromtimestamp(meta_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                readme_time = datetime.fromtimestamp(readme_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                return (
                    f"{module_path.name}: README.md ({readme_time}) is older than "
                    f"README.meta.yaml ({meta_time})"
                )

            return None

        except OSError as e:
            return f"{module_path.name}: Error checking file timestamps: {e}"
