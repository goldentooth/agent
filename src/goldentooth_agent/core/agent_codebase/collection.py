"""
Codebase collection management for multiple repositories.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from goldentooth_agent.core.embeddings import VectorStore

from .change_detection import SmartChangeDetector
from .extraction import CodebaseDocumentExtractor
from .schema import CodebaseDocument, CodebaseDocumentType
from .source import DocumentSource
from .token_tracking import TokenTracker


class CodebaseInfo(BaseModel):
    """Information about a codebase in the collection."""

    name: str = Field(..., description="Codebase identifier")
    display_name: str = Field(..., description="Human-readable name")
    root_path: Path = Field(..., description="Root directory path")
    description: str = Field(default="", description="Brief description")
    version: str = Field(default="", description="Version or commit hash")

    # Analysis metadata
    last_indexed: str = Field(default="", description="Last indexing timestamp")
    document_count: int = Field(default=0, description="Number of documents")
    total_lines: int = Field(default=0, description="Total lines of code")

    # Configuration
    include_patterns: list[str] = Field(
        default_factory=lambda: ["*.py"], description="File patterns to include"
    )
    exclude_patterns: list[str] = Field(
        default_factory=lambda: ["__pycache__", "*.pyc", ".git"],
        description="Patterns to exclude",
    )


class CodebaseCollection:
    """
    Manages multiple codebases for introspection and comparison.

    Mechanically, this works by:
    1. Extracting documents from source files using AST parsing
    2. Chunking documents based on their type and content structure
    3. Embedding chunks using the existing vector store infrastructure
    4. Indexing for semantic and keyword search
    5. Providing query interfaces for introspection
    """

    def __init__(
        self, vector_store: VectorStore, collection_name: str = "agent_codebase"
    ) -> None:
        self.vector_store = vector_store
        self.collection_name = collection_name
        self.codebases: dict[str, CodebaseInfo] = {}
        self.extractor = CodebaseDocumentExtractor()

        # Initialize change detector and token tracker with files in data directory
        from goldentooth_agent.core.paths import Paths

        data_dir = Paths().data()
        index_path = data_dir / f"{collection_name}_change_index.json"
        token_db_path = data_dir / f"{collection_name}_tokens.db"

        self.change_detector = SmartChangeDetector(index_path)
        self.token_tracker = TokenTracker(token_db_path)

    async def add_codebase(
        self,
        name: str,
        root_path: Path,
        display_name: str | None = None,
        description: str = "",
        **kwargs: Any,
    ) -> None:
        """Add a codebase to the collection."""
        codebase_info = CodebaseInfo(
            name=name,
            display_name=display_name or name,
            root_path=root_path,
            description=description,
            **kwargs,
        )
        self.codebases[name] = codebase_info

    async def index_codebase(
        self, codebase_name: str, force_full_reindex: bool = False
    ) -> dict[str, Any]:
        """
        Index a codebase by extracting and embedding all documents.

        Enhanced with smart change detection:
        1. Extract documents from source files (AST parsing)
        2. Check for meaningful changes using content fingerprinting
        3. Skip re-embedding for cosmetic changes (whitespace, comments)
        4. Re-embed only when semantic content changes
        5. Update change detection index
        """
        if codebase_name not in self.codebases:
            raise ValueError(f"Codebase '{codebase_name}' not found")

        codebase_info = self.codebases[codebase_name]

        # Extract all documents from the codebase
        documents = await self.extractor.extract_from_path(
            codebase_info.root_path,
            include_patterns=codebase_info.include_patterns,
            exclude_patterns=codebase_info.exclude_patterns,
        )

        # Track current files for cleanup
        current_files = {doc.file_path for doc in documents}

        # Clean up stale documents from change index
        stale_docs = self.change_detector.cleanup_stale_documents(current_files)
        if stale_docs:
            # TODO: Remove stale documents from vector store
            pass

        # Create document source for the codebase
        source = DocumentSource(
            name=f"{self.collection_name}_{codebase_name}",
            display_name=codebase_info.display_name,
            description=f"Codebase introspection for {codebase_info.display_name}",
            metadata={
                "codebase_name": codebase_name,
                "root_path": str(codebase_info.root_path),
                "collection_type": "agent_codebase",
            },
        )

        # Process documents with change detection
        total_chunks = 0
        total_lines = 0
        documents_processed = 0
        documents_skipped = 0

        for document in documents:
            file_path = Path(document.file_path)

            # Check if document needs re-embedding
            needs_embedding, new_fingerprint = (
                self.change_detector.analyze_document_changes(document, file_path)
            )

            if force_full_reindex or needs_embedding:
                # Chunk the document based on its type
                chunks = self._chunk_document(document)

                # Remove old chunks if they exist
                old_fingerprint = self.change_detector.index.get_fingerprint(
                    document.document_id
                )
                if old_fingerprint and old_fingerprint.embedding_id:
                    # TODO: Remove old chunks from vector store
                    pass

                chunk_ids = []
                for i, chunk in enumerate(chunks):
                    # Create unique document ID
                    doc_id = f"{codebase_name}:{document.document_id}:chunk_{i}"

                    # Track token usage for this chunk
                    content_hash = f"{document.document_id}_chunk_{i}"
                    change_reason = (
                        new_fingerprint.document_id
                        if not force_full_reindex
                        else "force_reindex"
                    )

                    token_record = self.token_tracker.record_embedding_operation(
                        content=chunk,
                        content_hash=content_hash,
                        model_name="text-embedding-ada-002",  # Default, could be configurable
                        operation_type=(
                            "embed" if old_fingerprint is None else "re_embed"
                        ),
                        document_type=document.document_type.value,
                        module_path=document.module_path,
                        codebase_name=codebase_name,
                        was_cached=False,
                        change_reason=change_reason,
                    )

                    # Add to vector store
                    doc_id = self.vector_store.store_document(
                        store_type=self.collection_name,
                        document_id=doc_id,
                        content=chunk,
                        embedding=[],  # Empty embedding - will be filled by vector store
                        metadata={
                            "title": document.title,
                            "document_type": document.document_type.value,
                            "module_path": document.module_path,
                            "file_path": document.file_path,
                            "line_start": document.line_start,
                            "line_end": document.line_end,
                            "tags": document.tags,
                            "signature": document.signature,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "token_count": token_record.token_count,
                            "estimated_cost_usd": token_record.estimated_cost_usd,
                            "source_display_name": source.display_name,
                            "source_description": source.description,
                            **document.metadata,
                        },
                    )

                    chunk_ids.append(doc_id)
                    total_chunks += 1

                # Update fingerprint with embedding reference
                new_fingerprint.embedding_id = ",".join(chunk_ids)
                documents_processed += 1
            else:
                # Document unchanged, skip re-embedding
                # Still record this as a "skip" operation for metrics
                self.token_tracker.record_embedding_operation(
                    content=document.get_searchable_text(),
                    content_hash=new_fingerprint.content_hash,
                    model_name="text-embedding-ada-002",
                    operation_type="skip",
                    document_type=document.document_type.value,
                    module_path=document.module_path,
                    codebase_name=codebase_name,
                    was_cached=True,
                    change_reason="no_semantic_changes",
                )
                documents_skipped += 1

            # Update fingerprint in change detector
            self.change_detector.update_fingerprint(new_fingerprint)
            total_lines += document.line_end - document.line_start

        # Update codebase stats
        from datetime import datetime

        codebase_info.last_indexed = datetime.now().isoformat()
        codebase_info.document_count = len(documents)
        codebase_info.total_lines = total_lines

        # Get token usage statistics for this indexing run
        token_stats = self.token_tracker.get_usage_statistics(days=1)  # Today's usage
        budget_status = self.token_tracker.check_budget_status()

        return {
            "codebase_name": codebase_name,
            "documents_total": len(documents),
            "documents_processed": documents_processed,
            "documents_skipped": documents_skipped,
            "chunks_created": total_chunks,
            "total_lines": total_lines,
            "stale_documents_removed": len(stale_docs),
            "change_detection_stats": self.change_detector.get_indexing_stats(),
            "token_usage": {
                "tokens_used": token_stats["total_tokens"],
                "estimated_cost_usd": token_stats["total_cost_usd"],
                "operations_count": token_stats["total_operations"],
                "cache_hit_rate": token_stats["cache_hit_rate"],
                "tokens_saved": token_stats["change_detection_savings"][
                    "estimated_tokens_saved"
                ],
                "cost_saved_usd": token_stats["change_detection_savings"][
                    "estimated_cost_saved_usd"
                ],
            },
            "budget_status": budget_status,
        }

    def _chunk_document(self, document: CodebaseDocument) -> list[str]:
        """
        Chunk a document based on its type and content.

        Mechanical chunking strategy:
        - Function/class definitions: Keep as single chunks (usually small)
        - Module documentation: Split on sections, preserve structure
        - Source code: Split on logical boundaries (functions, classes)
        - Background docs: Split on sections, maintain context
        """
        content = document.get_searchable_text()
        chunk_size = document.get_chunk_size_hint()

        # For small documents, return as single chunk
        if len(content) <= chunk_size:
            return [content]

        # Type-specific chunking strategies
        if document.document_type in [
            CodebaseDocumentType.FUNCTION_DEFINITION,
            CodebaseDocumentType.CLASS_DEFINITION,
        ]:
            # Keep function/class definitions intact
            return [content]

        elif document.document_type == CodebaseDocumentType.MODULE_BACKGROUND:
            # Split on section headers but preserve structure
            return self._chunk_markdown_sections(content, chunk_size)

        elif document.document_type == CodebaseDocumentType.SOURCE_CODE:
            # Split on logical code boundaries
            return self._chunk_source_code(content, chunk_size)

        else:
            # Default: simple paragraph-based chunking
            return self._chunk_by_paragraphs(content, chunk_size)

    def _chunk_markdown_sections(self, content: str, chunk_size: int) -> list[str]:
        """Chunk markdown content by sections."""
        lines = content.split("\n")
        chunks = []
        current_chunk: list[str] = []
        current_size = 0
        min_chunk_size = chunk_size // 4  # Minimum size before considering split

        for line in lines:
            line_size = len(line) + 1  # +1 for newline

            # Start new chunk on major headers, but avoid very small chunks
            if (
                line.startswith("# ")
                and current_chunk  # Don't split on very first line
                and current_size > min_chunk_size
            ):  # Ensure minimum chunk size
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_size = 0

            # Check if adding this line would make chunk too large
            if current_chunk and current_size + line_size > chunk_size * 1.15:
                # Force split before adding the line
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_size = 0

            # Handle extremely long individual lines by splitting them
            if line_size > chunk_size * 1.15:
                # If we have existing content, flush it first
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_size = 0

                # Split the long line into smaller pieces
                words = line.split()
                temp_line = ""
                for word in words:
                    if len(temp_line + " " + word) > chunk_size:
                        if temp_line:  # Add the current line chunk
                            chunks.append(temp_line.strip())
                        temp_line = word
                    else:
                        if temp_line:
                            temp_line += " " + word
                        else:
                            temp_line = word

                # Add any remaining content as the start of next chunk
                if temp_line:
                    current_chunk = [temp_line.strip()]
                    current_size = len(temp_line.strip()) + 1
            else:
                current_chunk.append(line)
                current_size += line_size

            # Split if chunk is too large at good break points
            if current_size > chunk_size:
                # Prefer empty lines for clean breaks
                if line.strip() == "":
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_size = 0

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _chunk_source_code(self, content: str, chunk_size: int) -> list[str]:
        """Chunk source code on logical boundaries."""
        lines = content.split("\n")
        chunks = []
        current_chunk: list[str] = []
        current_size = 0

        for line in lines:
            line_size = len(line) + 1

            # Start new chunk on function/class definitions if chunk is substantial
            if (
                line.strip().startswith(("def ", "class ", "async def "))
                and current_size > chunk_size // 3
            ):
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_size = 0

            current_chunk.append(line)
            current_size += line_size

            # Split if chunk is too large and we're at a good boundary
            if current_size > chunk_size and line.strip() == "":
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_size = 0

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _chunk_by_paragraphs(self, content: str, chunk_size: int) -> list[str]:
        """Simple paragraph-based chunking."""
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk: list[str] = []
        current_size = 0

        for paragraph in paragraphs:
            para_size = len(paragraph) + 2  # +2 for double newline

            if current_size + para_size > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_size = 0

            current_chunk.append(paragraph)
            current_size += para_size

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    async def search(
        self,
        query: str,
        codebase_names: list[str] | None = None,
        document_types: list[CodebaseDocumentType] | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search across codebases with filtering.

        Mechanical query process:
        1. Generate query embedding
        2. Perform vector similarity search
        3. Filter by codebase and document type
        4. Rank results by relevance score
        5. Return structured results with metadata
        """
        # Build filter criteria
        filters = {}

        if codebase_names:
            # Filter by codebase name (embedded in document ID)
            filters["codebase_filter"] = codebase_names

        if document_types:
            filters["document_type"] = [dt.value for dt in document_types]

        # First, convert query text to embedding
        # TODO: This requires an embeddings service - for now return empty results
        # In production, we'd use: query_embedding = await embeddings_service.create_embedding(query)
        return []  # Temporary until embedding service is properly integrated

    def get_codebase_info(self, codebase_name: str) -> CodebaseInfo | None:
        """Get information about a specific codebase."""
        return self.codebases.get(codebase_name)

    def list_codebases(self) -> list[CodebaseInfo]:
        """List all codebases in the collection."""
        return list(self.codebases.values())
