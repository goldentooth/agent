"""
Smart change detection to minimize unnecessary re-embedding.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

from .schema import CodebaseDocument, CodebaseDocumentType


class ContentFingerprint(BaseModel):
    """Fingerprint for tracking content changes."""
    
    # Core identification
    document_id: str = Field(..., description="Document identifier")
    file_path: str = Field(..., description="Source file path")
    
    # Content hashes
    content_hash: str = Field(..., description="Hash of searchable content")
    structure_hash: str = Field(..., description="Hash of code structure (AST)")
    semantic_hash: str = Field(..., description="Hash of semantic content only")
    
    # Metadata
    file_mtime: float = Field(..., description="File modification time")
    line_count: int = Field(default=0, description="Number of lines")
    complexity_score: float = Field(default=0.0, description="Code complexity score")
    
    # Change tracking
    last_indexed: str = Field(..., description="Last indexing timestamp")
    embedding_id: Optional[str] = Field(default=None, description="Vector store embedding ID")
    
    def has_content_changed(self, new_fingerprint: ContentFingerprint) -> bool:
        """Check if content has meaningfully changed."""
        return self.semantic_hash != new_fingerprint.semantic_hash
    
    def has_structure_changed(self, new_fingerprint: ContentFingerprint) -> bool:
        """Check if code structure has changed."""
        return self.structure_hash != new_fingerprint.structure_hash
    
    def needs_re_embedding(self, new_fingerprint: ContentFingerprint) -> bool:
        """Determine if re-embedding is needed."""
        # Re-embed if semantic content changed
        if self.has_content_changed(new_fingerprint):
            return True
        
        # Re-embed if file is newer and structure changed significantly
        if (new_fingerprint.file_mtime > self.file_mtime and 
            self.has_structure_changed(new_fingerprint)):
            return True
        
        return False


class ChangeDetectionIndex(BaseModel):
    """Index of content fingerprints for change detection."""
    
    fingerprints: dict[str, ContentFingerprint] = Field(default_factory=dict)
    last_full_scan: str = Field(default="", description="Last full directory scan")
    
    def get_fingerprint(self, document_id: str) -> Optional[ContentFingerprint]:
        """Get fingerprint for a document."""
        return self.fingerprints.get(document_id)
    
    def update_fingerprint(self, fingerprint: ContentFingerprint) -> None:
        """Update fingerprint in index."""
        self.fingerprints[fingerprint.document_id] = fingerprint
    
    def remove_fingerprint(self, document_id: str) -> None:
        """Remove fingerprint from index."""
        self.fingerprints.pop(document_id, None)
    
    def get_stale_documents(self, current_files: set[str]) -> list[str]:
        """Get document IDs for files that no longer exist."""
        stale_docs = []
        for doc_id, fingerprint in self.fingerprints.items():
            if fingerprint.file_path not in current_files:
                stale_docs.append(doc_id)
        return stale_docs


class SmartChangeDetector:
    """
    Detects meaningful changes to minimize unnecessary re-embedding.
    
    Strategy:
    1. Generate content fingerprints based on semantic content
    2. Compare against previous fingerprints to detect changes
    3. Skip re-embedding for cosmetic changes (whitespace, comments)
    4. Re-embed only when semantic content or structure changes
    """
    
    def __init__(self, index_file_path: Path) -> None:
        self.index_file_path = index_file_path
        self.index = self._load_index()
    
    def _load_index(self) -> ChangeDetectionIndex:
        """Load change detection index from disk."""
        if self.index_file_path.exists():
            try:
                with open(self.index_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return ChangeDetectionIndex.model_validate(data)
            except Exception:
                # If index is corrupted, start fresh
                pass
        
        return ChangeDetectionIndex()
    
    def _save_index(self) -> None:
        """Save change detection index to disk."""
        self.index_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.index.model_dump(), f, indent=2)
    
    def analyze_document_changes(
        self,
        document: CodebaseDocument,
        file_path: Path
    ) -> tuple[bool, ContentFingerprint]:
        """
        Analyze if a document needs re-embedding.
        
        Returns:
            (needs_re_embedding, new_fingerprint)
        """
        new_fingerprint = self._generate_fingerprint(document, file_path)
        existing_fingerprint = self.index.get_fingerprint(document.document_id)
        
        if existing_fingerprint is None:
            # New document, needs embedding
            return True, new_fingerprint
        
        needs_re_embedding = existing_fingerprint.needs_re_embedding(new_fingerprint)
        return needs_re_embedding, new_fingerprint
    
    def _generate_fingerprint(
        self,
        document: CodebaseDocument,
        file_path: Path
    ) -> ContentFingerprint:
        """Generate content fingerprint for a document."""
        from datetime import datetime
        
        # Get file stats
        stat = file_path.stat()
        
        # Generate semantic content (what affects embeddings)
        semantic_content = self._extract_semantic_content(document)
        
        # Generate structure hash (for code documents)
        structure_content = self._extract_structure_content(document)
        
        return ContentFingerprint(
            document_id=document.document_id,
            file_path=str(file_path),
            content_hash=self._hash_content(document.get_searchable_text()),
            structure_hash=self._hash_content(structure_content),
            semantic_hash=self._hash_content(semantic_content),
            file_mtime=stat.st_mtime,
            line_count=document.line_end - document.line_start,
            complexity_score=document.complexity_score,
            last_indexed=datetime.now().isoformat()
        )
    
    def _extract_semantic_content(self, document: CodebaseDocument) -> str:
        """
        Extract only semantic content that affects search relevance.
        
        Ignores:
        - Whitespace variations
        - Comment formatting changes
        - Variable name changes that don't affect meaning
        - Import order changes
        """
        content_parts = [
            # Core semantic elements
            document.title.strip(),
            document.summary.strip(),
            self._normalize_docstring(document.docstring),
            " ".join(sorted(document.tags)),  # Sorted for consistency
            document.module_path,
        ]
        
        # For code documents, extract semantic structure
        if document.document_type in [
            CodebaseDocumentType.FUNCTION_DEFINITION,
            CodebaseDocumentType.CLASS_DEFINITION,
            CodebaseDocumentType.SOURCE_CODE
        ]:
            semantic_code = self._extract_code_semantics(document.content)
            content_parts.append(semantic_code)
        else:
            # For documentation, normalize content
            normalized_content = self._normalize_documentation(document.content)
            content_parts.append(normalized_content)
        
        return "\n".join(part for part in content_parts if part)
    
    def _extract_structure_content(self, document: CodebaseDocument) -> str:
        """Extract structural elements that indicate significant changes."""
        if document.document_type not in [
            CodebaseDocumentType.FUNCTION_DEFINITION,
            CodebaseDocumentType.CLASS_DEFINITION,
            CodebaseDocumentType.SOURCE_CODE
        ]:
            return ""
        
        try:
            # Parse AST and extract structural elements
            tree = ast.parse(document.content)
            structure_elements = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Function signature and decorator structure
                    structure_elements.append(f"function:{node.name}:{len(node.args.args)}")
                    structure_elements.extend(f"decorator:{d.id}" for d in node.decorator_list if hasattr(d, 'id'))
                
                elif isinstance(node, ast.ClassDef):
                    # Class structure and inheritance
                    structure_elements.append(f"class:{node.name}:{len(node.bases)}")
                    structure_elements.extend(f"base:{self._ast_to_string(base)}" for base in node.bases)
                
                elif isinstance(node, ast.Import):
                    # Import structure (but not order)
                    structure_elements.extend(f"import:{alias.name}" for alias in node.names)
                
                elif isinstance(node, ast.ImportFrom):
                    # From imports
                    if node.module:
                        structure_elements.extend(f"from:{node.module}.{alias.name}" for alias in node.names)
            
            return "\n".join(sorted(structure_elements))  # Sort for consistency
        
        except SyntaxError:
            # If parsing fails, use line count as rough structure indicator
            return f"lines:{len(document.content.split())}"
    
    def _extract_code_semantics(self, code: str) -> str:
        """Extract semantic elements from code, ignoring formatting."""
        try:
            tree = ast.parse(code)
            
            # Extract semantic tokens while ignoring formatting
            semantic_elements = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    semantic_elements.append(f"def {node.name}")
                    # Add simplified docstring
                    docstring = ast.get_docstring(node)
                    if docstring:
                        semantic_elements.append(self._normalize_docstring(docstring))
                
                elif isinstance(node, ast.ClassDef):
                    semantic_elements.append(f"class {node.name}")
                    docstring = ast.get_docstring(node)
                    if docstring:
                        semantic_elements.append(self._normalize_docstring(docstring))
                
                elif isinstance(node, ast.Assign):
                    # Key assignments (constants, etc.)
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            semantic_elements.append(f"const {target.id}")
            
            return " ".join(semantic_elements)
        
        except SyntaxError:
            # Fallback: normalize whitespace and comments
            lines = code.split('\n')
            normalized_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    normalized_lines.append(line)
            return " ".join(normalized_lines)
    
    def _normalize_docstring(self, docstring: str) -> str:
        """Normalize docstring by removing formatting variations."""
        if not docstring:
            return ""
        
        # Remove common docstring formatting
        lines = docstring.strip().split('\n')
        normalized_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Remove common docstring artifacts
                line = line.replace('"""', '').replace("'''", "")
                if line:
                    normalized_lines.append(line)
        
        return " ".join(normalized_lines)
    
    def _normalize_documentation(self, content: str) -> str:
        """Normalize documentation content."""
        # Remove markdown formatting variations that don't affect meaning
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Remove markdown artifacts while preserving structure
                line = line.replace('**', '').replace('*', '').replace('_', '')
                line = line.lstrip('#').strip()  # Remove heading markers
                if line:
                    normalized_lines.append(line)
        
        return " ".join(normalized_lines)
    
    def _hash_content(self, content: str) -> str:
        """Generate hash for content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def _ast_to_string(self, node: ast.AST) -> str:
        """Convert AST node to string."""
        try:
            return ast.unparse(node)
        except Exception:
            return str(type(node).__name__)
    
    def update_fingerprint(self, fingerprint: ContentFingerprint) -> None:
        """Update fingerprint and save index."""
        self.index.update_fingerprint(fingerprint)
        self._save_index()
    
    def cleanup_stale_documents(self, current_files: set[str]) -> list[str]:
        """Remove fingerprints for files that no longer exist."""
        stale_docs = self.index.get_stale_documents(current_files)
        
        for doc_id in stale_docs:
            self.index.remove_fingerprint(doc_id)
        
        if stale_docs:
            self._save_index()
        
        return stale_docs
    
    def get_indexing_stats(self) -> dict[str, Any]:
        """Get statistics about the change detection index."""
        return {
            "total_documents": len(self.index.fingerprints),
            "last_full_scan": self.index.last_full_scan,
            "avg_complexity": sum(fp.complexity_score for fp in self.index.fingerprints.values()) / len(self.index.fingerprints) if self.index.fingerprints else 0
        }