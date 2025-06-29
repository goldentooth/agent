import gzip
import hashlib
import json
import sqlite3
import struct
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from antidote import inject, injectable

from ..paths import Paths


@injectable
class VectorStore:
    """Hybrid vector store supporting both SQLite and compressed sidecar files."""

    def __init__(self, paths: Paths = inject.me()) -> None:
        """Initialize the vector store.

        Args:
            paths: Paths service for data directory management
        """
        self.paths = paths
        self.db_path = paths.data() / "embeddings.db"
        self.metadata_path = paths.data() / ".embeddings" / "metadata.json"

        # Ensure directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database and metadata
        self._init_database()
        self._init_metadata()

    def _init_database(self) -> None:
        """Initialize the SQLite database with vec0 extension."""
        with sqlite3.connect(self.db_path) as conn:
            # Enable vec0 extension
            conn.enable_load_extension(True)
            try:
                # Try to load sqlite-vec extension
                conn.load_extension("vec0")
            except sqlite3.OperationalError:
                # If extension loading fails, continue without it
                # The vec0 table creation will fail gracefully
                pass

            # Create documents table for metadata
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    store_type TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(store_type, document_id)
                )
            """
            )

            # Create vec0 virtual table for embeddings
            try:
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
                        embedding float[768],
                        +doc_id TEXT,
                        +store_type TEXT,
                        +document_id TEXT,
                        +content_preview TEXT
                    )
                """
                )
            except sqlite3.OperationalError as e:
                # If vec0 is not available, create a regular table as fallback
                print(
                    f"Warning: vec0 extension not available ({e}), using fallback table"
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS embeddings_fallback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        doc_id TEXT NOT NULL,
                        store_type TEXT NOT NULL,
                        document_id TEXT NOT NULL,
                        content_preview TEXT,
                        embedding BLOB,
                        created_at TEXT NOT NULL
                    )
                """
                )

            # Create indexes
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_store_type
                ON documents(store_type)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_updated
                ON documents(updated_at)
            """
            )

            conn.commit()

    def _init_metadata(self) -> None:
        """Initialize metadata file for sidecar embedding tracking."""
        if not self.metadata_path.exists():
            default_metadata = {
                "version": "1.0",
                "model": "claude-semantic-features",
                "dimensions": 768,
                "compression": "gzip",
                "created_at": datetime.now().isoformat(),
                "embeddings": {},
            }
            self.metadata_path.write_text(
                json.dumps(default_metadata, indent=2, sort_keys=True)
            )

    def _get_sidecar_path(self, store_type: str, document_id: str) -> Path:
        """Get the path for a document's sidecar embedding file.

        Args:
            store_type: Type of document store (e.g., "github.repos")
            document_id: ID of the document

        Returns:
            Path to the .emb.gz sidecar file
        """
        # Map store types to directory structure
        if store_type.startswith("github."):
            category, subcategory = store_type.split(".", 1)
            base_dir = self.paths.data() / category / subcategory
        elif store_type.startswith("goldentooth."):
            category, subcategory = store_type.split(".", 1)
            base_dir = self.paths.data() / category / subcategory
        else:
            base_dir = self.paths.data() / store_type

        return base_dir / f"{document_id}.emb.gz"

    def _save_sidecar_embedding(
        self, store_type: str, document_id: str, embedding: list[float]
    ) -> None:
        """Save embedding as compressed sidecar file.

        Args:
            store_type: Type of document store
            document_id: ID of the document
            embedding: Embedding vector to save
        """
        sidecar_path = self._get_sidecar_path(store_type, document_id)
        sidecar_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to numpy array with deterministic format
        embedding_array = np.array(embedding, dtype=np.float32)
        raw_bytes = embedding_array.tobytes()

        # Calculate checksum of the raw embedding data
        embedding_checksum = hashlib.sha256(raw_bytes).hexdigest()

        # Check if file already exists with same checksum
        if sidecar_path.exists():
            existing_checksum = self._get_existing_checksum(store_type, document_id)
            if existing_checksum == embedding_checksum:
                # No change needed - embedding is identical
                return

        # Compress with deterministic settings (no timestamps)
        compressed_data = self._deterministic_gzip_compress(raw_bytes)
        sidecar_path.write_bytes(compressed_data)

        # Update metadata with checksum
        self._update_metadata(store_type, document_id, sidecar_path, embedding_checksum)

    def _deterministic_gzip_compress(self, data: bytes) -> bytes:
        """Compress data with deterministic gzip format (no timestamps).

        Args:
            data: Raw bytes to compress

        Returns:
            Compressed bytes with deterministic gzip headers
        """
        # Compress the data
        compressed = zlib.compress(data, level=6)

        # Create deterministic gzip header
        # Format: ID1 ID2 CM FLG MTIME XFL OS + compressed data + CRC32 + ISIZE
        header = b"\x1f\x8b"  # ID1, ID2 (gzip magic)
        header += b"\x08"  # CM (compression method: deflate)
        header += b"\x00"  # FLG (no flags)
        header += b"\x00\x00\x00\x00"  # MTIME (zero timestamp for deterministic output)
        header += b"\x00"  # XFL (no extra flags)
        header += b"\xff"  # OS (unknown)

        # Calculate CRC32 and size
        crc32 = zlib.crc32(data) & 0xFFFFFFFF
        size = len(data)

        # Create footer
        footer = struct.pack("<LL", crc32, size)

        return header + compressed + footer

    def _get_existing_checksum(self, store_type: str, document_id: str) -> str | None:
        """Get the checksum of an existing embedding file from metadata.

        Args:
            store_type: Type of document store
            document_id: ID of the document

        Returns:
            Checksum string or None if not found
        """
        try:
            metadata = json.loads(self.metadata_path.read_text())
            doc_key = f"{store_type}.{document_id}"
            return metadata.get("embeddings", {}).get(doc_key, {}).get("checksum")
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _load_sidecar_embedding(
        self, store_type: str, document_id: str
    ) -> list[float] | None:
        """Load embedding from compressed sidecar file.

        Args:
            store_type: Type of document store
            document_id: ID of the document

        Returns:
            Embedding vector or None if not found
        """
        sidecar_path = self._get_sidecar_path(store_type, document_id)
        if not sidecar_path.exists():
            return None

        try:
            with gzip.open(sidecar_path, "rb") as f:
                data = f.read()
            embedding_array = np.frombuffer(data, dtype=np.float32)
            return embedding_array.tolist()
        except Exception:
            return None

    def _update_metadata(
        self, store_type: str, document_id: str, sidecar_path: Path, checksum: str
    ) -> None:
        """Update metadata file with embedding info.

        Args:
            store_type: Type of document store
            document_id: ID of the document
            sidecar_path: Path to the sidecar file
            checksum: SHA256 checksum of the embedding data
        """
        try:
            metadata = json.loads(self.metadata_path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            metadata = {
                "version": "1.0",
                "model": "claude-semantic-features",
                "dimensions": 768,
                "compression": "gzip",
                "embeddings": {},
            }

        doc_key = f"{store_type}.{document_id}"
        existing_entry = metadata.get("embeddings", {}).get(doc_key, {})
        existing_checksum = existing_entry.get("checksum")

        # Only update timestamp if checksum changed
        if existing_checksum != checksum:
            new_entry = {
                "file": str(sidecar_path.relative_to(self.paths.data())),
                "store_type": store_type,
                "document_id": document_id,
                "checksum": checksum,
                "created_at": datetime.now().isoformat(),
                "file_size": (
                    sidecar_path.stat().st_size if sidecar_path.exists() else 0
                ),
            }
        else:
            # Keep existing entry but update file size (file may have been re-compressed)
            new_entry = existing_entry.copy()
            new_entry["file_size"] = (
                sidecar_path.stat().st_size if sidecar_path.exists() else 0
            )

        metadata["embeddings"][doc_key] = new_entry

        # Sort embeddings by key for consistent output
        metadata["embeddings"] = dict(sorted(metadata["embeddings"].items()))

        self.metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True))

    def store_document(
        self,
        store_type: str,
        document_id: str,
        content: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store a document and its embedding.

        Args:
            store_type: Type of document store (e.g., "github.repos")
            document_id: ID of the document
            content: Text content that was embedded
            embedding: Embedding vector
            metadata: Additional metadata

        Returns:
            Document database ID
        """
        doc_id = f"{store_type}.{document_id}"
        now = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Store document metadata
            conn.execute(
                """
                INSERT OR REPLACE INTO documents (
                    id, store_type, document_id, content, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    doc_id,
                    store_type,
                    document_id,
                    content,
                    str(metadata) if metadata else None,
                    now,
                    now,
                ),
            )

            # Store embedding
            content_preview = content[:200] + "..." if len(content) > 200 else content

            try:
                # Try to use vec0 table
                conn.execute(
                    """
                    INSERT OR REPLACE INTO embeddings (
                        embedding, doc_id, store_type, document_id, content_preview
                    ) VALUES (?, ?, ?, ?, ?)
                """,
                    (embedding, doc_id, store_type, document_id, content_preview),
                )
            except sqlite3.OperationalError:
                # Fallback to regular table
                embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
                conn.execute(
                    """
                    INSERT OR REPLACE INTO embeddings_fallback (
                        doc_id, store_type, document_id, content_preview, embedding, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        doc_id,
                        store_type,
                        document_id,
                        content_preview,
                        embedding_blob,
                        now,
                    ),
                )

            conn.commit()

        # Also save as sidecar file for Git storage
        self._save_sidecar_embedding(store_type, document_id, embedding)

        return doc_id

    def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 10,
        store_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for documents similar to the query embedding.

        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            store_type: Optional filter by store type

        Returns:
            List of similar documents with metadata and similarity scores
        """
        with sqlite3.connect(self.db_path) as conn:
            try:
                # Try vec0 similarity search
                if store_type:
                    cursor = conn.execute(
                        """
                        SELECT
                            doc_id, store_type, document_id, content_preview,
                            distance
                        FROM embeddings
                        WHERE store_type = ?
                        ORDER BY embedding <-> ?
                        LIMIT ?
                    """,
                        (store_type, query_embedding, limit),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT
                            doc_id, store_type, document_id, content_preview,
                            distance
                        FROM embeddings
                        ORDER BY embedding <-> ?
                        LIMIT ?
                    """,
                        (query_embedding, limit),
                    )

                results = cursor.fetchall()

                # Convert to result format
                similar_docs = []
                for row in results:
                    doc_id, store_type, document_id, content_preview, distance = row

                    # Get full document metadata
                    doc_cursor = conn.execute(
                        """
                        SELECT content, metadata, created_at, updated_at
                        FROM documents WHERE id = ?
                    """,
                        (doc_id,),
                    )
                    doc_row = doc_cursor.fetchone()

                    if doc_row:
                        content, metadata, created_at, updated_at = doc_row
                        similar_docs.append(
                            {
                                "doc_id": doc_id,
                                "store_type": store_type,
                                "document_id": document_id,
                                "content": content,
                                "content_preview": content_preview,
                                "metadata": metadata,
                                "similarity_score": 1.0
                                - distance,  # Convert distance to similarity
                                "created_at": created_at,
                                "updated_at": updated_at,
                            }
                        )

                return similar_docs

            except sqlite3.OperationalError:
                # Fallback to manual cosine similarity calculation
                return self._fallback_similarity_search(
                    query_embedding, limit, store_type, conn
                )

    def _fallback_similarity_search(
        self,
        query_embedding: list[float],
        limit: int,
        store_type: str | None,
        conn: sqlite3.Connection,
    ) -> list[dict[str, Any]]:
        """Fallback similarity search using manual cosine similarity."""
        query_vector = np.array(query_embedding, dtype=np.float32)

        # Get all embeddings
        if store_type:
            cursor = conn.execute(
                """
                SELECT doc_id, store_type, document_id, content_preview, embedding
                FROM embeddings_fallback
                WHERE store_type = ?
            """,
                (store_type,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT doc_id, store_type, document_id, content_preview, embedding
                FROM embeddings_fallback
            """
            )

        similarities = []

        for row in cursor.fetchall():
            doc_id, store_type, document_id, content_preview, embedding_blob = row

            # Deserialize embedding
            embedding_vector = np.frombuffer(embedding_blob, dtype=np.float32)

            # Calculate cosine similarity
            similarity = np.dot(query_vector, embedding_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(embedding_vector)
            )

            similarities.append(
                (similarity, doc_id, store_type, document_id, content_preview)
            )

        # Sort by similarity and take top results
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_results = similarities[:limit]

        # Get full document metadata for top results
        similar_docs = []
        for similarity, doc_id, store_type, document_id, content_preview in top_results:
            doc_cursor = conn.execute(
                """
                SELECT content, metadata, created_at, updated_at
                FROM documents WHERE id = ?
            """,
                (doc_id,),
            )
            doc_row = doc_cursor.fetchone()

            if doc_row:
                content, metadata, created_at, updated_at = doc_row
                similar_docs.append(
                    {
                        "doc_id": doc_id,
                        "store_type": store_type,
                        "document_id": document_id,
                        "content": content,
                        "content_preview": content_preview,
                        "metadata": metadata,
                        "similarity_score": float(similarity),
                        "created_at": created_at,
                        "updated_at": updated_at,
                    }
                )

        return similar_docs

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """Get a document by its ID.

        Args:
            doc_id: Document database ID

        Returns:
            Document data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT store_type, document_id, content, metadata, created_at, updated_at
                FROM documents WHERE id = ?
            """,
                (doc_id,),
            )

            row = cursor.fetchone()
            if row:
                store_type, document_id, content, metadata, created_at, updated_at = row
                return {
                    "doc_id": doc_id,
                    "store_type": store_type,
                    "document_id": document_id,
                    "content": content,
                    "metadata": metadata,
                    "created_at": created_at,
                    "updated_at": updated_at,
                }

        return None

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its embedding.

        Args:
            doc_id: Document database ID

        Returns:
            True if document was deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            # Delete from both tables
            cursor1 = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

            try:
                cursor2 = conn.execute(
                    "DELETE FROM embeddings WHERE doc_id = ?", (doc_id,)
                )
            except sqlite3.OperationalError:
                cursor2 = conn.execute(
                    "DELETE FROM embeddings_fallback WHERE doc_id = ?", (doc_id,)
                )

            conn.commit()

            return cursor1.rowcount > 0 or cursor2.rowcount > 0

    def list_documents(
        self, store_type: str | None = None, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """List all documents in the store.

        Args:
            store_type: Optional filter by store type
            limit: Optional limit on number of results

        Returns:
            List of document metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT id, store_type, document_id, created_at, updated_at FROM documents"
            params: list[str | int] = []

            if store_type:
                query += " WHERE store_type = ?"
                params.append(store_type)

            query += " ORDER BY updated_at DESC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(query, params)

            documents = []
            for row in cursor.fetchall():
                doc_id, store_type, document_id, created_at, updated_at = row
                documents.append(
                    {
                        "doc_id": doc_id,
                        "store_type": store_type,
                        "document_id": document_id,
                        "created_at": created_at,
                        "updated_at": updated_at,
                    }
                )

            return documents

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store.

        Returns:
            Dictionary with store statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            # Count total documents
            cursor = conn.execute("SELECT COUNT(*) FROM documents")
            total_docs = cursor.fetchone()[0]

            # Count by store type
            cursor = conn.execute(
                """
                SELECT store_type, COUNT(*)
                FROM documents
                GROUP BY store_type
            """
            )
            by_store_type = dict(cursor.fetchall())

            # Check if using vec0 or fallback
            try:
                conn.execute("SELECT COUNT(*) FROM embeddings")
                embedding_engine = "sqlite-vec (vec0)"
            except sqlite3.OperationalError:
                embedding_engine = "fallback (numpy)"

            return {
                "total_documents": total_docs,
                "by_store_type": by_store_type,
                "embedding_engine": embedding_engine,
                "database_path": str(self.db_path),
                "metadata_path": str(self.metadata_path),
                "sidecar_files": self.count_sidecar_files(),
            }

    def get_all_sidecar_paths(self) -> list[Path]:
        """Get paths to all sidecar embedding files.

        Returns:
            List of paths to .emb.gz files
        """
        sidecar_files = []
        data_dir = self.paths.data()

        # Search for .emb.gz files in the data directory
        for path in data_dir.rglob("*.emb.gz"):
            sidecar_files.append(path)

        return sidecar_files

    def count_sidecar_files(self) -> int:
        """Count the number of sidecar embedding files.

        Returns:
            Number of .emb.gz files
        """
        return len(self.get_all_sidecar_paths())

    def sync_sidecar_files(self) -> dict[str, Any]:
        """Sync all embeddings to sidecar files.

        Returns:
            Dictionary with sync results
        """
        created_files = []
        errors = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT store_type, document_id
                FROM documents
            """
            )

            for store_type, document_id in cursor.fetchall():
                try:
                    # Get embedding from database
                    embedding = self._get_embedding_from_db(store_type, document_id)
                    if embedding:
                        # Save as sidecar file
                        self._save_sidecar_embedding(store_type, document_id, embedding)
                        created_files.append(
                            self._get_sidecar_path(store_type, document_id)
                        )
                except Exception as e:
                    errors.append(f"{store_type}.{document_id}: {e}")

        return {
            "created_files": len(created_files),
            "errors": errors,
            "sidecar_paths": created_files,
        }

    def _get_embedding_from_db(
        self, store_type: str, document_id: str
    ) -> list[float] | None:
        """Get embedding from database.

        Args:
            store_type: Type of document store
            document_id: ID of the document

        Returns:
            Embedding vector or None if not found
        """
        doc_id = f"{store_type}.{document_id}"

        with sqlite3.connect(self.db_path) as conn:
            # Try vec0 table first
            try:
                cursor = conn.execute(
                    """
                    SELECT embedding FROM embeddings WHERE doc_id = ?
                """,
                    (doc_id,),
                )
                row = cursor.fetchone()
                if row:
                    return row[0]
            except sqlite3.OperationalError:
                pass

            # Try fallback table
            cursor = conn.execute(
                """
                SELECT embedding FROM embeddings_fallback WHERE doc_id = ?
            """,
                (doc_id,),
            )
            row = cursor.fetchone()
            if row:
                embedding_array = np.frombuffer(row[0], dtype=np.float32)
                return embedding_array.tolist()

        return None

    def get_sidecar_metadata(self) -> dict[str, Any]:
        """Get metadata about sidecar files.

        Returns:
            Metadata dictionary
        """
        try:
            return json.loads(self.metadata_path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {"embeddings": {}}
