"""Document chunking system for intelligent content splitting."""

import re
from dataclasses import dataclass
from typing import Any

from antidote import injectable


@dataclass
class DocumentChunk:
    """Represents a chunk of a document with metadata."""

    chunk_id: str
    parent_doc_id: str
    store_type: str
    document_id: str
    chunk_type: str
    content: str
    metadata: dict[str, Any]
    sequence: int  # Order within parent document


@injectable
class DocumentChunker:
    """Intelligently splits documents into meaningful chunks for better RAG retrieval."""

    def chunk_document(
        self, store_type: str, document_id: str, document_data: dict[str, Any]
    ) -> list[DocumentChunk]:
        """Split a document into logical chunks based on its type and content.

        Args:
            store_type: Type of document store (e.g., "github.repos", "notes")
            document_id: Unique identifier for the document
            document_data: Document content dictionary

        Returns:
            List of document chunks
        """
        if store_type == "github.repos":
            return self._chunk_github_repo(store_type, document_id, document_data)
        elif store_type == "github.orgs":
            return self._chunk_github_org(store_type, document_id, document_data)
        elif store_type == "notes":
            return self._chunk_note(store_type, document_id, document_data)
        else:
            # Default: treat as single chunk for unknown types
            return self._chunk_generic(store_type, document_id, document_data)

    def _chunk_github_repo(
        self, store_type: str, document_id: str, document_data: dict[str, Any]
    ) -> list[DocumentChunk]:
        """Chunk a GitHub repository document into logical sections."""
        chunks = []
        parent_doc_id = f"{store_type}.{document_id}"

        # Chunk 1: Core metadata and description
        core_content = self._build_repo_core_content(document_data)
        chunks.append(
            DocumentChunk(
                chunk_id=f"{parent_doc_id}.core",
                parent_doc_id=parent_doc_id,
                store_type=store_type,
                document_id=document_id,
                chunk_type="repo_core",
                content=core_content,
                metadata={
                    "chunk_type": "repo_core",
                    "chunk_index": 1,
                    "parent_document_id": parent_doc_id,
                    "parent_store_type": store_type,
                    "title": f"{document_data.get('name', document_id)} - Core Info",
                    "size_chars": len(core_content),
                    "start_position": 0,
                    "end_position": len(core_content),
                    "language": document_data.get("language"),
                    "size_kb": document_data.get("size_kb"),
                    "stars": document_data.get("stars"),
                    "is_archived": document_data.get("is_archived", False),
                },
                sequence=1,
            )
        )

        # Chunk 2: Technical details (languages, topics, technical metadata)
        tech_content = self._build_repo_tech_content(document_data)
        if tech_content.strip():
            start_pos = len(core_content)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{parent_doc_id}.technical",
                    parent_doc_id=parent_doc_id,
                    store_type=store_type,
                    document_id=document_id,
                    chunk_type="repo_technical",
                    content=tech_content,
                    metadata={
                        "chunk_type": "repo_technical",
                        "chunk_index": 2,
                        "parent_document_id": parent_doc_id,
                        "parent_store_type": store_type,
                        "title": f"{document_data.get('name', document_id)} - Technical Details",
                        "size_chars": len(tech_content),
                        "start_position": start_pos,
                        "end_position": start_pos + len(tech_content),
                        "languages": document_data.get("languages", []),
                        "topics": document_data.get("topics", []),
                        "default_branch": document_data.get("default_branch"),
                    },
                    sequence=2,
                )
            )

        # Chunk 3: Activity and status information
        activity_content = self._build_repo_activity_content(document_data)
        if activity_content.strip():
            start_pos = len(core_content) + len(tech_content)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{parent_doc_id}.activity",
                    parent_doc_id=parent_doc_id,
                    store_type=store_type,
                    document_id=document_id,
                    chunk_type="repo_activity",
                    content=activity_content,
                    metadata={
                        "chunk_type": "repo_activity",
                        "chunk_index": 3,
                        "parent_document_id": parent_doc_id,
                        "parent_store_type": store_type,
                        "title": f"{document_data.get('name', document_id)} - Activity Status",
                        "size_chars": len(activity_content),
                        "start_position": start_pos,
                        "end_position": start_pos + len(activity_content),
                        "updated_at": document_data.get("updated_at"),
                        "pushed_at": document_data.get("pushed_at"),
                        "open_issues": document_data.get("open_issues"),
                        "forks": document_data.get("forks"),
                    },
                    sequence=3,
                )
            )

        return chunks

    def _chunk_github_org(
        self, store_type: str, document_id: str, document_data: dict[str, Any]
    ) -> list[DocumentChunk]:
        """Chunk a GitHub organization document."""
        # Organizations are typically small, keep as single chunk
        parent_doc_id = f"{store_type}.{document_id}"
        content = self._build_org_content(document_data)

        return [
            DocumentChunk(
                chunk_id=f"{parent_doc_id}.main",
                parent_doc_id=parent_doc_id,
                store_type=store_type,
                document_id=document_id,
                chunk_type="org_main",
                content=content,
                metadata={
                    "public_repos": document_data.get("public_repos"),
                    "updated_at": document_data.get("updated_at"),
                },
                sequence=1,
            )
        ]

    def _chunk_note(
        self, store_type: str, document_id: str, document_data: dict[str, Any]
    ) -> list[DocumentChunk]:
        """Chunk a note document by markdown sections."""
        chunks = []
        parent_doc_id = f"{store_type}.{document_id}"
        content = document_data.get("content", "")

        if not content.strip():
            # Empty content, create minimal chunk
            return self._chunk_generic(store_type, document_id, document_data)

        # Split by markdown headers
        sections = self._split_markdown_sections(content)

        if len(sections) <= 1:
            # No clear sections, treat as single chunk
            return self._chunk_generic(store_type, document_id, document_data)

        # Create chunks for each section
        position = 0
        for i, (header, section_content) in enumerate(sections, 1):
            chunk_content = f"{header}\n{section_content}".strip()
            if chunk_content:
                # Add document metadata to first chunk
                if i == 1:
                    metadata_text = self._build_note_metadata(document_data)
                    chunk_content = f"{metadata_text}\n\n{chunk_content}"

                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{parent_doc_id}.section{i}",
                        parent_doc_id=parent_doc_id,
                        store_type=store_type,
                        document_id=document_id,
                        chunk_type="note_section",
                        content=chunk_content,
                        metadata={
                            "chunk_type": "note_section",
                            "chunk_index": i,
                            "parent_document_id": parent_doc_id,
                            "parent_store_type": store_type,
                            "title": header.strip("# ") if header else f"Section {i}",
                            "size_chars": len(chunk_content),
                            "start_position": position,
                            "end_position": position + len(chunk_content),
                            "header": header.strip("# "),
                            "category": document_data.get("category"),
                            "tags": document_data.get("tags", []),
                            "keywords": document_data.get("keywords", []),
                        },
                        sequence=i,
                    )
                )
                position += len(chunk_content)

        return chunks

    def _chunk_generic(
        self, store_type: str, document_id: str, document_data: dict[str, Any]
    ) -> list[DocumentChunk]:
        """Create a single chunk for unknown document types."""
        parent_doc_id = f"{store_type}.{document_id}"

        # Extract all text content
        text_parts = []
        text_fields = [
            "name",
            "title",
            "description",
            "content",
            "summary",
            "keywords",
            "tags",
            "topics",
        ]

        for field in text_fields:
            value = document_data.get(field)
            if value:
                if isinstance(value, str):
                    text_parts.append(f"{field.title()}: {value}")
                elif isinstance(value, list):
                    text_parts.append(
                        f"{field.title()}: {', '.join(str(item) for item in value)}"
                    )

        content = "\n".join(text_parts)

        return [
            DocumentChunk(
                chunk_id=f"{parent_doc_id}.main",
                parent_doc_id=parent_doc_id,
                store_type=store_type,
                document_id=document_id,
                chunk_type="generic",
                content=content,
                metadata={"original_fields": list(document_data.keys())},
                sequence=1,
            )
        ]

    def _build_repo_core_content(self, document_data: dict[str, Any]) -> str:
        """Build core content for a repository chunk."""
        parts = []

        name = document_data.get("name", "")
        description = document_data.get("description", "")

        if name:
            parts.append(f"Repository: {name}")
        if description:
            parts.append(f"Description: {description}")

        # Add basic metadata
        language = document_data.get("language")
        if language:
            parts.append(f"Primary Language: {language}")

        size_kb = document_data.get("size_kb")
        if size_kb:
            parts.append(f"Size: {size_kb} KB")

        priority = document_data.get("priority")
        if priority:
            parts.append(f"Priority: {priority}")

        return "\n".join(parts)

    def _build_repo_tech_content(self, document_data: dict[str, Any]) -> str:
        """Build technical content for a repository chunk."""
        parts = []

        languages = document_data.get("languages", [])
        if languages:
            parts.append(f"Languages: {', '.join(languages)}")

        topics = document_data.get("topics", [])
        if topics:
            parts.append(f"Topics: {', '.join(topics)}")

        default_branch = document_data.get("default_branch")
        if default_branch:
            parts.append(f"Default Branch: {default_branch}")

        return "\n".join(parts)

    def _build_repo_activity_content(self, document_data: dict[str, Any]) -> str:
        """Build activity content for a repository chunk."""
        parts = []

        stars = document_data.get("stars", 0)
        forks = document_data.get("forks", 0)
        open_issues = document_data.get("open_issues", 0)

        if stars or forks or open_issues:
            parts.append(
                f"Activity: {stars} stars, {forks} forks, {open_issues} open issues"
            )

        updated_at = document_data.get("updated_at")
        if updated_at:
            parts.append(f"Last Updated: {updated_at}")

        pushed_at = document_data.get("pushed_at")
        if pushed_at:
            parts.append(f"Last Push: {pushed_at}")

        is_archived = document_data.get("is_archived", False)
        if is_archived:
            parts.append("Status: Archived")

        return "\n".join(parts)

    def _build_org_content(self, document_data: dict[str, Any]) -> str:
        """Build content for an organization chunk."""
        parts = []

        name = document_data.get("name", "")
        description = document_data.get("description", "")

        if name:
            parts.append(f"Organization: {name}")
        if description:
            parts.append(f"Description: {description}")

        public_repos = document_data.get("public_repos", 0)
        if public_repos:
            parts.append(f"Public Repositories: {public_repos}")

        return "\n".join(parts)

    def _build_note_metadata(self, document_data: dict[str, Any]) -> str:
        """Build metadata content for a note chunk."""
        parts = []

        title = document_data.get("title", "")
        if title:
            parts.append(f"Title: {title}")

        category = document_data.get("category", "")
        if category:
            parts.append(f"Category: {category}")

        tags = document_data.get("tags", [])
        if tags:
            parts.append(f"Tags: {', '.join(tags)}")

        keywords = document_data.get("keywords", [])
        if keywords:
            parts.append(f"Keywords: {', '.join(keywords)}")

        return "\n".join(parts)

    def _split_markdown_sections(self, content: str) -> list[tuple[str, str]]:
        """Split markdown content by headers.

        Returns:
            List of (header, content) tuples
        """
        # Split by markdown headers (# ## ### etc.)
        header_pattern = r"^(#{1,6}\s+.+)$"
        lines = content.split("\n")

        sections = []
        current_header = ""
        current_content = []

        for line in lines:
            if re.match(header_pattern, line):
                # Save previous section
                if current_header or current_content:
                    sections.append((current_header, "\n".join(current_content)))

                # Start new section
                current_header = line
                current_content = []
            else:
                current_content.append(line)

        # Save final section
        if current_header or current_content:
            sections.append((current_header, "\n".join(current_content)))

        return sections

    def get_chunk_summary(self, chunks: list[DocumentChunk]) -> dict[str, Any]:
        """Generate a summary of chunks for a document.

        Args:
            chunks: List of document chunks

        Returns:
            Dictionary with chunk summary information
        """
        if not chunks:
            return {"total_chunks": 0, "chunk_types": [], "total_content_length": 0}

        chunk_types = [chunk.chunk_type for chunk in chunks]
        chunk_type_counts = {}
        for chunk_type in chunk_types:
            chunk_type_counts[chunk_type] = chunk_type_counts.get(chunk_type, 0) + 1

        total_content_length = sum(len(chunk.content) for chunk in chunks)

        return {
            "total_chunks": len(chunks),
            "chunk_types": list(chunk_type_counts.keys()),
            "chunk_type_counts": chunk_type_counts,
            "total_content_length": total_content_length,
            "avg_chunk_length": total_content_length // len(chunks) if chunks else 0,
            "sequences": [chunk.sequence for chunk in chunks],
        }
