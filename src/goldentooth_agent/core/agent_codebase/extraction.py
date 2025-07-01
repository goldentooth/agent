"""
Document extraction from codebase files.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from .schema import CodebaseDocument, CodebaseDocumentType


class CodebaseDocumentExtractor:
    """
    Extracts structured documents from codebase files.

    Mechanical extraction process:
    1. Walk directory tree finding relevant files
    2. Parse Python files using AST for structure
    3. Extract functions, classes, and module-level docs
    4. Read documentation files (README.md, README.bg.md)
    5. Generate structured CodebaseDocument objects
    """

    def __init__(self) -> None:
        self.excluded_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            ".pytest_cache",
            "node_modules",
            ".mypy_cache",
            ".ruff_cache",
        }

    async def extract_from_path(
        self,
        root_path: Path,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> list[CodebaseDocument]:
        """Extract all documents from a directory tree."""
        include_patterns = include_patterns or ["*.py", "*.md"]
        exclude_patterns = exclude_patterns or []

        documents = []

        for file_path in self._walk_files(
            root_path, include_patterns, exclude_patterns
        ):
            file_docs = await self._extract_from_file(file_path, root_path)
            documents.extend(file_docs)

        return documents

    def _walk_files(
        self, root_path: Path, include_patterns: list[str], exclude_patterns: list[str]
    ) -> list[Path]:
        """Walk directory tree and find matching files."""
        files = []

        for path in root_path.rglob("*"):
            if not path.is_file():
                continue

            # Skip excluded directories
            if any(excluded in path.parts for excluded in self.excluded_dirs):
                continue

            # Skip excluded patterns
            if any(path.match(pattern) for pattern in exclude_patterns):
                continue

            # Include only matching patterns
            if any(path.match(pattern) for pattern in include_patterns):
                files.append(path)

        return sorted(files)

    async def _extract_from_file(
        self, file_path: Path, root_path: Path
    ) -> list[CodebaseDocument]:
        """Extract documents from a single file."""
        try:
            if file_path.suffix == ".py":
                return await self._extract_from_python_file(file_path, root_path)
            elif file_path.suffix == ".md":
                return await self._extract_from_markdown_file(file_path, root_path)
            else:
                return []
        except Exception as e:
            # Log error but continue processing other files
            print(f"Warning: Failed to extract from {file_path}: {e}")
            return []

    async def _extract_from_python_file(
        self, file_path: Path, root_path: Path
    ) -> list[CodebaseDocument]:
        """Extract documents from Python source file."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"Warning: Syntax error in {file_path}: {e}")
            return []

        documents = []
        module_path = self._get_module_path(file_path, root_path)

        # Extract module-level docstring
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            doc_id = self._generate_doc_id(file_path, "module")
            documents.append(
                CodebaseDocument(
                    document_id=doc_id,
                    document_type=CodebaseDocumentType.MODULE_API,
                    title=f"Module: {module_path}",
                    content=content,
                    summary=module_docstring.split("\n")[0] if module_docstring else "",
                    file_path=str(file_path),
                    module_path=module_path,
                    docstring=module_docstring,
                    tags=["module", "python"],
                    dependencies=self._extract_imports(tree),
                )
            )

        # Extract functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_doc = self._extract_function_document(node, file_path, module_path)
                if func_doc:
                    documents.append(func_doc)

            elif isinstance(node, ast.ClassDef):
                class_doc = self._extract_class_document(node, file_path, module_path)
                if class_doc:
                    documents.append(class_doc)

        # Add full source code document
        source_doc_id = self._generate_doc_id(file_path, "source")
        documents.append(
            CodebaseDocument(
                document_id=source_doc_id,
                document_type=CodebaseDocumentType.SOURCE_CODE,
                title=f"Source: {file_path.name}",
                content=content,
                summary=f"Complete source code for {module_path}",
                file_path=str(file_path),
                module_path=module_path,
                tags=["source_code", "python"],
                dependencies=self._extract_imports(tree),
                complexity_score=self._calculate_complexity(tree),
            )
        )

        return documents

    def _extract_function_document(
        self, node: ast.FunctionDef, file_path: Path, module_path: str
    ) -> CodebaseDocument | None:
        """Extract document for a function definition."""
        if node.name.startswith("_") and not node.name.startswith("__"):
            # Skip private functions unless they're special methods
            return None

        func_docstring = ast.get_docstring(node)
        signature = self._get_function_signature(node)

        # Get function source code
        try:

            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            start_line = node.lineno - 1
            end_line = node.end_lineno if node.end_lineno else start_line + 1
            func_source = "".join(lines[start_line:end_line])
        except Exception:
            func_source = f"def {node.name}(...):\n    # Function definition"

        doc_id = self._generate_doc_id(file_path, f"function_{node.name}")

        return CodebaseDocument(
            document_id=doc_id,
            document_type=CodebaseDocumentType.FUNCTION_DEFINITION,
            title=f"Function: {module_path}.{node.name}",
            content=func_source,
            summary=(
                func_docstring.split("\n")[0]
                if func_docstring
                else f"Function {node.name}"
            ),
            file_path=str(file_path),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            module_path=module_path,
            signature=signature,
            docstring=func_docstring or "",
            tags=["function", "python"],
            metadata={
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "arg_count": len(node.args.args),
                "has_decorators": len(node.decorator_list) > 0,
            },
        )

    def _extract_class_document(
        self, node: ast.ClassDef, file_path: Path, module_path: str
    ) -> CodebaseDocument | None:
        """Extract document for a class definition."""
        if node.name.startswith("_"):
            # Skip private classes
            return None

        class_docstring = ast.get_docstring(node)

        # Get class source code
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            start_line = node.lineno - 1
            end_line = node.end_lineno if node.end_lineno else start_line + 1
            class_source = "".join(lines[start_line:end_line])
        except Exception:
            class_source = f"class {node.name}:\n    # Class definition"

        # Extract method names
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

        doc_id = self._generate_doc_id(file_path, f"class_{node.name}")

        return CodebaseDocument(
            document_id=doc_id,
            document_type=CodebaseDocumentType.CLASS_DEFINITION,
            title=f"Class: {module_path}.{node.name}",
            content=class_source,
            summary=(
                class_docstring.split("\n")[0]
                if class_docstring
                else f"Class {node.name}"
            ),
            file_path=str(file_path),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            module_path=module_path,
            signature=f"class {node.name}",
            docstring=class_docstring or "",
            tags=["class", "python"],
            metadata={
                "base_classes": [self._ast_to_string(base) for base in node.bases],
                "method_count": len(methods),
                "methods": methods,
                "has_decorators": len(node.decorator_list) > 0,
            },
        )

    async def _extract_from_markdown_file(
        self, file_path: Path, root_path: Path
    ) -> list[CodebaseDocument]:
        """Extract documents from Markdown file."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Determine document type based on filename
        if file_path.name == "README.bg.md":
            doc_type = CodebaseDocumentType.MODULE_BACKGROUND
            title_prefix = "Background"
        elif file_path.name == "README.md":
            doc_type = CodebaseDocumentType.MODULE_API
            title_prefix = "Documentation"
        else:
            doc_type = CodebaseDocumentType.CONFIGURATION
            title_prefix = "Documentation"

        # Extract title from first heading or filename
        title = self._extract_markdown_title(content) or file_path.name
        summary = self._extract_markdown_summary(content)

        module_path = self._get_module_path(file_path.parent, root_path)
        doc_id = self._generate_doc_id(file_path, "markdown")

        return [
            CodebaseDocument(
                document_id=doc_id,
                document_type=doc_type,
                title=f"{title_prefix}: {title}",
                content=content,
                summary=summary,
                file_path=str(file_path),
                module_path=module_path,
                tags=["documentation", "markdown"],
                metadata={
                    "file_type": file_path.suffix,
                    "word_count": len(content.split()),
                },
            )
        ]

    def _get_module_path(self, file_path: Path, root_path: Path) -> str:
        """Convert file path to Python module path."""
        try:
            rel_path = file_path.relative_to(root_path)

            # Handle special cases
            if file_path.name == "__init__.py":
                parts = rel_path.parent.parts
            else:
                parts = rel_path.with_suffix("").parts

            # Filter out non-Python directories and add prefix if needed
            python_parts = []
            for part in parts:
                if part == "src":
                    continue
                python_parts.append(part)

            return ".".join(python_parts) if python_parts else "root"

        except ValueError:
            # File is not relative to root_path
            return str(file_path.stem)

    def _generate_doc_id(self, file_path: Path, doc_type: str) -> str:
        """Generate unique document ID."""
        path_str = str(file_path)
        hash_obj = hashlib.md5(f"{path_str}:{doc_type}".encode(), usedforsecurity=False)
        return f"{file_path.stem}_{doc_type}_{hash_obj.hexdigest()[:8]}"

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements from AST."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.append(f"{node.module}.{alias.name}")

        return imports

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Generate function signature string."""
        args = []

        # Regular arguments
        for arg in node.args.args:
            args.append(arg.arg)

        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")

        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        return f"def {node.name}({', '.join(args)})"

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate rough complexity score for AST."""
        node_count = len(list(ast.walk(tree)))
        # Normalize to 0-1 scale, with 1000 nodes = 1.0
        return min(node_count / 1000.0, 1.0)

    def _ast_to_string(self, node: ast.AST) -> str:
        """Convert AST node to string representation."""
        try:
            return ast.unparse(node)
        except Exception:
            return str(type(node).__name__)

    def _extract_markdown_title(self, content: str) -> str | None:
        """Extract title from markdown content."""
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return None

    def _extract_markdown_summary(self, content: str) -> str:
        """Extract summary from markdown content."""
        lines = content.split("\n")
        summary_lines = []

        in_content = False
        for line in lines:
            line = line.strip()

            # Skip title
            if line.startswith("# "):
                in_content = True
                continue

            if in_content and line:
                summary_lines.append(line)
                # Take first paragraph
                if len(summary_lines) > 1 and not line:
                    break

        summary = " ".join(summary_lines)
        # Truncate to reasonable length
        return summary[:200] + "..." if len(summary) > 200 else summary
