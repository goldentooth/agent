import gzip
import hashlib
import json
import sqlite3
import struct
import zlib
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import sqlite_vec  # type: ignore[import-untyped]
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

        # Initialize state
        self._vec_available = False

        # Initialize database and metadata
        self._init_database()
        self._init_metadata()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with sqlite-vec loaded if available."""
        conn = sqlite3.connect(self.db_path)
        conn.enable_load_extension(True)
        try:
            sqlite_vec.load(conn)
            self._vec_available = True
        except Exception:
            self._vec_available = False
        return conn

    def _init_database(self) -> None:
        """Initialize the SQLite database with sqlite-vec extension."""
        with self._get_connection() as conn:
            # Enable extension loading
            conn.enable_load_extension(True)

            # Load sqlite-vec extension
            try:
                sqlite_vec.load(conn)
                self._vec_available = True
            except Exception:
                # If extension loading fails, continue without it
                # The vec0 table creation will fail gracefully
                self._vec_available = False
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

            # Create chunks table for chunk metadata and relationships
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    parent_document_id TEXT NOT NULL,
                    parent_store_type TEXT NOT NULL,
                    chunk_type TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    size_chars INTEGER NOT NULL,
                    start_position INTEGER,
                    end_position INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (parent_store_type, parent_document_id)
                        REFERENCES documents(store_type, document_id) ON DELETE CASCADE
                )
            """
            )

            # Create chunk relationships table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunk_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_chunk_id TEXT NOT NULL,
                    target_chunk_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength REAL NOT NULL,
                    strength_category TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(source_chunk_id, target_chunk_id, relationship_type),
                    FOREIGN KEY (source_chunk_id) REFERENCES chunks(chunk_id) ON DELETE CASCADE,
                    FOREIGN KEY (target_chunk_id) REFERENCES chunks(chunk_id) ON DELETE CASCADE
                )
            """
            )

            # Create vec0 virtual table for embeddings
            # Try to create vec0 table (optimal performance)
            try:
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
                        embedding float[1536],
                        +doc_id TEXT,
                        +store_type TEXT,
                        +document_id TEXT,
                        +content_preview TEXT,
                        +chunk_id TEXT,
                        +is_chunk INTEGER DEFAULT 0
                    )
                """
                )
            except sqlite3.OperationalError as e:
                print(
                    f"Warning: vec0 extension not available ({e}), vec0 table not created"
                )

            # Always create fallback table as backup (ensures consistency)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS embeddings_fallback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT NOT NULL,
                    store_type TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    content_preview TEXT,
                    embedding BLOB,
                    chunk_id TEXT,
                    is_chunk INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """
            )

            # Migrate existing fallback table if needed
            try:
                # Check if chunk columns exist in fallback table
                cursor = conn.execute("PRAGMA table_info(embeddings_fallback)")
                columns = [row[1] for row in cursor.fetchall()]

                if "chunk_id" not in columns:
                    conn.execute(
                        "ALTER TABLE embeddings_fallback ADD COLUMN chunk_id TEXT"
                    )

                if "is_chunk" not in columns:
                    conn.execute(
                        "ALTER TABLE embeddings_fallback ADD COLUMN is_chunk INTEGER DEFAULT 0"
                    )

            except sqlite3.OperationalError:
                # Table doesn't exist yet, that's fine
                pass

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
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chunks_parent
                ON chunks(parent_store_type, parent_document_id)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chunks_type
                ON chunks(chunk_type)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_relationships_source
                ON chunk_relationships(source_chunk_id)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_relationships_target
                ON chunk_relationships(target_chunk_id)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_relationships_type
                ON chunk_relationships(relationship_type)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_relationships_strength
                ON chunk_relationships(strength)
            """
            )

            conn.commit()

    def _init_metadata(self) -> None:
        """Initialize metadata file for sidecar embedding tracking."""
        if not self.metadata_path.exists():
            default_metadata = {
                "version": "1.0",
                "model": "claude-semantic-features",
                "dimensions": 1536,
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
            checksum = metadata.get("embeddings", {}).get(doc_key, {}).get("checksum")
            return str(checksum) if checksum is not None else None
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
            return list(embedding_array.tolist())
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
                "dimensions": 1536,
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

        with self._get_connection() as conn:
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
                embedding_bytes = sqlite_vec.serialize_float32(embedding)
                conn.execute(
                    """
                    INSERT OR REPLACE INTO embeddings (
                        embedding, doc_id, store_type, document_id, content_preview
                    ) VALUES (?, ?, ?, ?, ?)
                """,
                    (embedding_bytes, doc_id, store_type, document_id, content_preview),
                )
            except sqlite3.OperationalError:
                # Fallback to regular table
                embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
                conn.execute(
                    """
                    INSERT OR REPLACE INTO embeddings_fallback (
                        doc_id, store_type, document_id, content_preview, embedding,
                        chunk_id, is_chunk, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        doc_id,
                        store_type,
                        document_id,
                        content_preview,
                        embedding_blob,
                        None,  # chunk_id for documents
                        0,  # is_chunk = False for documents
                        now,
                    ),
                )

            conn.commit()

        # Also save as sidecar file for Git storage
        self._save_sidecar_embedding(store_type, document_id, embedding)

        return doc_id

    def store_document_chunks(
        self,
        store_type: str,
        document_id: str,
        chunks: list[Any],  # DocumentChunk objects
        embeddings: list[list[float]],
        document_metadata: dict[str, Any] | None = None,
    ) -> list[str]:
        """Store document chunks and their embeddings.

        Args:
            store_type: Type of document store (e.g., "github.repos")
            document_id: ID of the parent document
            chunks: List of DocumentChunk objects
            embeddings: List of embedding vectors for each chunk
            document_metadata: Additional metadata for the parent document

        Returns:
            List of chunk IDs that were stored
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        now = datetime.now().isoformat()
        stored_chunk_ids = []

        with self._get_connection() as conn:
            # Store parent document metadata if provided
            doc_id = f"{store_type}.{document_id}"
            if document_metadata:
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
                        f"Parent document with {len(chunks)} chunks",
                        str(document_metadata),
                        now,
                        now,
                    ),
                )

            # Store each chunk
            for chunk, embedding in zip(chunks, embeddings, strict=False):
                chunk_metadata = chunk.metadata

                # Store chunk metadata
                conn.execute(
                    """
                    INSERT OR REPLACE INTO chunks (
                        chunk_id, parent_document_id, parent_store_type,
                        chunk_type, chunk_index, title, content, size_chars,
                        start_position, end_position, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        chunk.chunk_id,
                        document_id,
                        store_type,
                        chunk_metadata["chunk_type"],
                        chunk_metadata["chunk_index"],
                        chunk_metadata["title"],
                        chunk.content,
                        chunk_metadata["size_chars"],
                        chunk_metadata["start_position"],
                        chunk_metadata["end_position"],
                        now,
                        now,
                    ),
                )

                # Store chunk embedding
                content_preview = (
                    chunk.content[:200] + "..."
                    if len(chunk.content) > 200
                    else chunk.content
                )

                try:
                    # Try to use vec0 table
                    embedding_bytes = sqlite_vec.serialize_float32(embedding)
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO embeddings (
                            embedding, doc_id, store_type, document_id, content_preview,
                            chunk_id, is_chunk
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            embedding_bytes,
                            chunk.chunk_id,  # Use chunk_id as doc_id for chunks
                            store_type,
                            document_id,
                            content_preview,
                            chunk.chunk_id,
                            1,  # is_chunk = 1
                        ),
                    )
                except sqlite3.OperationalError:
                    # Fallback to regular table
                    embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO embeddings_fallback (
                            doc_id, store_type, document_id, content_preview, embedding,
                            chunk_id, is_chunk, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            chunk.chunk_id,
                            store_type,
                            document_id,
                            content_preview,
                            embedding_blob,
                            chunk.chunk_id,
                            1,  # is_chunk = 1
                            now,
                        ),
                    )

                # Also save as sidecar file for Git storage
                self._save_sidecar_embedding(store_type, chunk.chunk_id, embedding)
                stored_chunk_ids.append(chunk.chunk_id)

            conn.commit()

        return stored_chunk_ids

    def get_document_chunks(
        self, store_type: str, document_id: str
    ) -> list[dict[str, Any]]:
        """Get all chunks for a document.

        Args:
            store_type: Type of document store
            document_id: ID of the parent document

        Returns:
            List of chunk metadata dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT chunk_id, chunk_type, chunk_index, title, content,
                       size_chars, start_position, end_position, created_at, updated_at
                FROM chunks
                WHERE parent_store_type = ? AND parent_document_id = ?
                ORDER BY chunk_index
            """,
                (store_type, document_id),
            )

            chunks = []
            for row in cursor.fetchall():
                (
                    chunk_id,
                    chunk_type,
                    chunk_index,
                    title,
                    content,
                    size_chars,
                    start_pos,
                    end_pos,
                    created_at,
                    updated_at,
                ) = row
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "chunk_type": chunk_type,
                        "chunk_index": chunk_index,
                        "title": title,
                        "content": content,
                        "size_chars": size_chars,
                        "start_position": start_pos,
                        "end_position": end_pos,
                        "parent_document_id": document_id,
                        "parent_store_type": store_type,
                        "created_at": created_at,
                        "updated_at": updated_at,
                    }
                )

            return chunks

    def delete_document_chunks(self, store_type: str, document_id: str) -> int:
        """Delete all chunks for a document.

        Args:
            store_type: Type of document store
            document_id: ID of the parent document

        Returns:
            Number of chunks deleted
        """
        with self._get_connection() as conn:
            # Get chunk IDs before deleting
            cursor = conn.execute(
                """
                SELECT chunk_id FROM chunks
                WHERE parent_store_type = ? AND parent_document_id = ?
            """,
                (store_type, document_id),
            )
            chunk_ids = [row[0] for row in cursor.fetchall()]

            # Delete chunk embeddings
            deleted_embeddings = 0
            for chunk_id in chunk_ids:
                try:
                    cursor = conn.execute(
                        "DELETE FROM embeddings WHERE chunk_id = ?", (chunk_id,)
                    )
                    deleted_embeddings += cursor.rowcount
                except sqlite3.OperationalError:
                    cursor = conn.execute(
                        "DELETE FROM embeddings_fallback WHERE chunk_id = ?",
                        (chunk_id,),
                    )
                    deleted_embeddings += cursor.rowcount

            # Delete chunk metadata
            cursor = conn.execute(
                """
                DELETE FROM chunks
                WHERE parent_store_type = ? AND parent_document_id = ?
            """,
                (store_type, document_id),
            )
            deleted_chunks = cursor.rowcount

            conn.commit()

            return deleted_chunks

    def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 10,
        store_type: str | None = None,
        include_chunks: bool = True,
    ) -> list[dict[str, Any]]:
        """Search for documents similar to the query embedding.

        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            store_type: Optional filter by store type
            include_chunks: Whether to include chunks in search results

        Returns:
            List of similar documents/chunks with metadata and similarity scores
        """
        with self._get_connection() as conn:
            all_results = []

            # Try vec0 similarity search first
            try:
                query_bytes = sqlite_vec.serialize_float32(query_embedding)
                vec0_results = self._search_vec0_table(
                    conn, query_bytes, limit * 2, store_type, include_chunks
                )
                all_results.extend(vec0_results)
            except sqlite3.OperationalError:
                # vec0 not available, continue without it
                pass

            # Always search fallback table as well
            fallback_results = self._search_fallback_table(
                conn, query_embedding, limit * 2, store_type, include_chunks
            )
            all_results.extend(fallback_results)

            # Remove duplicates (same doc_id) - prefer vec0 results
            seen_doc_ids = set()
            unique_results = []
            for result in all_results:
                doc_id = result["doc_id"]
                if doc_id not in seen_doc_ids:
                    seen_doc_ids.add(doc_id)
                    unique_results.append(result)

            # Sort by similarity score and return top results
            unique_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return unique_results[:limit]

    def _search_vec0_table(
        self,
        conn: sqlite3.Connection,
        query_bytes: bytes,
        limit: int,
        store_type: str | None,
        include_chunks: bool,
    ) -> list[dict[str, Any]]:
        """Search vec0 table for similar embeddings."""
        # Build WHERE clause based on filters
        where_conditions = []
        params: list[Any] = [query_bytes]

        if store_type:
            where_conditions.append("store_type = ?")
            params.append(store_type)

        if not include_chunks:
            where_conditions.append("is_chunk = 0")

        where_clause = (
            " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        )
        params.append(limit)

        cursor = conn.execute(
            f"""
            SELECT
                doc_id, store_type, document_id, content_preview,
                chunk_id, is_chunk,
                vec_distance_cosine(embedding, ?) as distance
            FROM embeddings
            {where_clause}
            ORDER BY distance
            LIMIT ?
        """,  # nosec B608 - where_clause built from safe parameterized conditions
            params,
        )

        results = cursor.fetchall()

        # Convert to result format
        similar_docs = []
        for row in results:
            (
                doc_id,
                store_type,
                document_id,
                content_preview,
                chunk_id,
                is_chunk,
                distance,
            ) = row

            result_item = {
                "doc_id": doc_id,
                "store_type": store_type,
                "document_id": document_id,
                "content_preview": content_preview,
                "similarity_score": 1.0 - distance,  # Convert distance to similarity
                "is_chunk": bool(is_chunk),
                "chunk_id": chunk_id,
            }

            # Add metadata based on whether it's a chunk or document
            self._add_result_metadata(conn, result_item, is_chunk, chunk_id, doc_id)
            similar_docs.append(result_item)

        return similar_docs

    def _search_fallback_table(
        self,
        conn: sqlite3.Connection,
        query_embedding: list[float],
        limit: int,
        store_type: str | None,
        include_chunks: bool,
    ) -> list[dict[str, Any]]:
        """Search fallback table for similar embeddings."""
        query_vector = np.array(query_embedding, dtype=np.float32)

        # Get all embeddings
        where_conditions = []
        params = []

        if store_type:
            where_conditions.append("store_type = ?")
            params.append(store_type)

        if not include_chunks:
            where_conditions.append("is_chunk = 0")

        where_clause = (
            " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        )

        cursor = conn.execute(
            f"""
            SELECT doc_id, store_type, document_id, content_preview, embedding,
                   chunk_id, is_chunk
            FROM embeddings_fallback
            {where_clause}
        """,  # nosec B608 - where_clause built from safe parameterized conditions
            params,
        )

        similarities = []

        for row in cursor.fetchall():
            (
                doc_id,
                store_type,
                document_id,
                content_preview,
                embedding_blob,
                chunk_id,
                is_chunk,
            ) = row

            # Deserialize embedding
            embedding_vector = np.frombuffer(embedding_blob, dtype=np.float32)

            # Calculate cosine similarity
            similarity = np.dot(query_vector, embedding_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(embedding_vector)
            )

            similarities.append(
                (
                    similarity,
                    doc_id,
                    store_type,
                    document_id,
                    content_preview,
                    chunk_id,
                    is_chunk,
                )
            )

        # Sort by similarity and take top results
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_results = similarities[:limit]

        # Get full document/chunk metadata for top results
        similar_docs = []
        for (
            similarity,
            doc_id,
            store_type,
            document_id,
            content_preview,
            chunk_id,
            is_chunk,
        ) in top_results:
            result_item = {
                "doc_id": doc_id,
                "store_type": store_type,
                "document_id": document_id,
                "content_preview": content_preview,
                "similarity_score": float(similarity),
                "is_chunk": bool(is_chunk),
                "chunk_id": chunk_id,
            }

            # Add metadata based on whether it's a chunk or document
            self._add_result_metadata(conn, result_item, is_chunk, chunk_id, doc_id)
            similar_docs.append(result_item)

        return similar_docs

    def _add_result_metadata(
        self,
        conn: sqlite3.Connection,
        result_item: dict[str, Any],
        is_chunk: int | bool,
        chunk_id: str | None,
        doc_id: str,
    ) -> None:
        """Add metadata to a search result item."""
        if is_chunk and chunk_id:
            # Get chunk metadata
            chunk_cursor = conn.execute(
                """
                SELECT chunk_type, chunk_index, title, content, size_chars,
                       created_at, updated_at
                FROM chunks WHERE chunk_id = ?
            """,
                (chunk_id,),
            )
            chunk_row = chunk_cursor.fetchone()

            if chunk_row:
                (
                    chunk_type,
                    chunk_index,
                    title,
                    content,
                    size_chars,
                    created_at,
                    updated_at,
                ) = chunk_row
                result_item.update(
                    {
                        "content": content,
                        "chunk_type": chunk_type,
                        "chunk_index": chunk_index,
                        "chunk_title": title,
                        "size_chars": size_chars,
                        "created_at": created_at,
                        "updated_at": updated_at,
                    }
                )
        else:
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
                result_item.update(
                    {
                        "content": content,
                        "metadata": metadata,
                        "created_at": created_at,
                        "updated_at": updated_at,
                    }
                )

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """Get a document by its ID.

        Args:
            doc_id: Document database ID

        Returns:
            Document data or None if not found
        """
        with self._get_connection() as conn:
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
        with self._get_connection() as conn:
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
        with self._get_connection() as conn:
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
        with self._get_connection() as conn:
            # Count total documents
            cursor = conn.execute("SELECT COUNT(*) FROM documents")
            total_docs = cursor.fetchone()[0]

            # Count total chunks
            cursor = conn.execute("SELECT COUNT(*) FROM chunks")
            total_chunks = cursor.fetchone()[0]

            # Count by store type
            cursor = conn.execute(
                """
                SELECT store_type, COUNT(*)
                FROM documents
                GROUP BY store_type
            """
            )
            by_store_type = dict(cursor.fetchall())

            # Count chunks by store type
            cursor = conn.execute(
                """
                SELECT parent_store_type, COUNT(*)
                FROM chunks
                GROUP BY parent_store_type
            """
            )
            chunks_by_store_type = dict(cursor.fetchall())

            # Count chunks by type
            cursor = conn.execute(
                """
                SELECT chunk_type, COUNT(*)
                FROM chunks
                GROUP BY chunk_type
            """
            )
            chunks_by_type = dict(cursor.fetchall())

            # Check if using vec0 or fallback
            try:
                conn.execute("SELECT COUNT(*) FROM embeddings")
                embedding_engine = "sqlite-vec (vec0)"

                # Count embeddings by type
                cursor = conn.execute(
                    """
                    SELECT is_chunk, COUNT(*)
                    FROM embeddings
                    GROUP BY is_chunk
                """
                )
                embedding_counts = {
                    "documents": 0,
                    "chunks": 0,
                }
                for is_chunk, count in cursor.fetchall():
                    if is_chunk:
                        embedding_counts["chunks"] = count
                    else:
                        embedding_counts["documents"] = count

            except sqlite3.OperationalError:
                embedding_engine = "fallback (numpy)"

                # Count embeddings by type in fallback table
                cursor = conn.execute(
                    """
                    SELECT is_chunk, COUNT(*)
                    FROM embeddings_fallback
                    GROUP BY is_chunk
                """
                )
                embedding_counts = {
                    "documents": 0,
                    "chunks": 0,
                }
                for is_chunk, count in cursor.fetchall():
                    if is_chunk:
                        embedding_counts["chunks"] = count
                    else:
                        embedding_counts["documents"] = count

            return {
                "total_documents": total_docs,
                "total_chunks": total_chunks,
                "by_store_type": by_store_type,
                "chunks_by_store_type": chunks_by_store_type,
                "chunks_by_type": chunks_by_type,
                "embedding_counts": embedding_counts,
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

        with self._get_connection() as conn:
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

        with self._get_connection() as conn:
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
                    return list(row[0]) if row[0] else None
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
                return list(embedding_array.tolist())

        return None

    def get_sidecar_metadata(self) -> dict[str, Any]:
        """Get metadata about sidecar files.

        Returns:
            Metadata dictionary
        """
        try:
            return dict(json.loads(self.metadata_path.read_text()))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"embeddings": {}}

    # Chunk Relationship Methods

    def store_chunk_relationships(self, relationships: list[dict[str, Any]]) -> int:
        """Store chunk relationships in the database.

        Args:
            relationships: List of relationship dictionaries with keys:
                - source_chunk_id: ID of source chunk
                - target_chunk_id: ID of target chunk
                - relationship_type: Type of relationship
                - strength: Relationship strength (0.0-1.0)
                - strength_category: Optional category (weak/moderate/strong)
                - metadata: Optional metadata dict

        Returns:
            Number of relationships stored
        """
        stored_count = 0
        current_time = datetime.now().isoformat()

        with self._get_connection() as conn:
            for rel in relationships:
                try:
                    # Convert metadata to JSON string
                    metadata_json = json.dumps(rel.get("metadata", {}))

                    # Insert or update relationship
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO chunk_relationships
                        (source_chunk_id, target_chunk_id, relationship_type,
                         strength, strength_category, metadata, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            rel["source_chunk_id"],
                            rel["target_chunk_id"],
                            rel["relationship_type"],
                            rel["strength"],
                            rel.get("strength_category"),
                            metadata_json,
                            current_time,
                            current_time,
                        ),
                    )
                    stored_count += 1
                except sqlite3.Error as e:
                    print(f"Error storing relationship: {e}")
                    continue

            conn.commit()

        return stored_count

    def get_chunk_relationships(
        self,
        chunk_id: str | None = None,
        relationship_types: list[str] | None = None,
        min_strength: float = 0.0,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get chunk relationships from the database.

        Args:
            chunk_id: Optional chunk ID to filter relationships for
            relationship_types: Optional list of relationship types to filter
            min_strength: Minimum relationship strength to include
            limit: Optional limit on number of results

        Returns:
            List of relationship dictionaries
        """
        query = """
            SELECT source_chunk_id, target_chunk_id, relationship_type,
                   strength, strength_category, metadata, created_at, updated_at
            FROM chunk_relationships
            WHERE strength >= ?
        """
        params: list[Any] = [min_strength]

        # Add chunk ID filter
        if chunk_id:
            query += " AND (source_chunk_id = ? OR target_chunk_id = ?)"
            params.extend([chunk_id, chunk_id])

        # Add relationship type filter
        if relationship_types:
            placeholders = ",".join("?" for _ in relationship_types)
            query += f" AND relationship_type IN ({placeholders})"
            params.extend(relationship_types)

        # Add ordering and limit
        query += " ORDER BY strength DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        relationships = []

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            for row in cursor.fetchall():
                try:
                    metadata = json.loads(row[5]) if row[5] else {}
                except json.JSONDecodeError:
                    metadata = {}

                relationships.append(
                    {
                        "source_chunk_id": row[0],
                        "target_chunk_id": row[1],
                        "relationship_type": row[2],
                        "strength": row[3],
                        "strength_category": row[4],
                        "metadata": metadata,
                        "created_at": row[6],
                        "updated_at": row[7],
                    }
                )

        return relationships

    def get_related_chunks(
        self,
        chunk_id: str,
        max_related: int = 10,
        min_strength: float = 0.5,
        relationship_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get chunks related to a specific chunk.

        Args:
            chunk_id: ID of the chunk to find relationships for
            max_related: Maximum number of related chunks to return
            min_strength: Minimum relationship strength to include
            relationship_types: Optional list of relationship types to filter

        Returns:
            List of related chunks with relationship metadata
        """
        relationships = self.get_chunk_relationships(
            chunk_id=chunk_id,
            relationship_types=relationship_types,
            min_strength=min_strength,
            limit=max_related * 2,  # Get extra to filter properly
        )

        related_chunks = []
        seen_chunks = set()

        for rel in relationships:
            # Determine which chunk is the related one
            related_chunk_id = None
            if rel["source_chunk_id"] == chunk_id:
                related_chunk_id = rel["target_chunk_id"]
            elif rel["target_chunk_id"] == chunk_id:
                related_chunk_id = rel["source_chunk_id"]

            # Skip if we've already seen this chunk
            if related_chunk_id and related_chunk_id not in seen_chunks:
                seen_chunks.add(related_chunk_id)

                # Get chunk details by ID
                with self._get_connection() as conn:
                    cursor = conn.execute(
                        """
                        SELECT chunk_id, parent_document_id, parent_store_type, chunk_type,
                               chunk_index, title, content, size_chars, start_position, end_position,
                               metadata, created_at, updated_at
                        FROM chunks WHERE chunk_id = ?
                        """,
                        (related_chunk_id,),
                    )
                    chunk_row = cursor.fetchone()

                if chunk_row:
                    chunk_info = {
                        "chunk_id": chunk_row[0],
                        "parent_document_id": chunk_row[1],
                        "parent_store_type": chunk_row[2],
                        "chunk_type": chunk_row[3],
                        "chunk_index": chunk_row[4],
                        "title": chunk_row[5],
                        "content": chunk_row[6],
                        "size_chars": chunk_row[7],
                        "start_position": chunk_row[8],
                        "end_position": chunk_row[9],
                        "metadata": json.loads(chunk_row[10]) if chunk_row[10] else {},
                        "created_at": chunk_row[11],
                        "updated_at": chunk_row[12],
                    }
                    chunk_info["relationship_type"] = rel["relationship_type"]
                    chunk_info["relationship_strength"] = rel["strength"]
                    chunk_info["relationship_metadata"] = rel["metadata"]
                    related_chunks.append(chunk_info)

                # Stop if we've reached the limit
                if len(related_chunks) >= max_related:
                    break

        return related_chunks

    def delete_chunk_relationships(
        self,
        chunk_id: str | None = None,
        relationship_type: str | None = None,
    ) -> int:
        """Delete chunk relationships.

        Args:
            chunk_id: Optional chunk ID to delete relationships for
            relationship_type: Optional relationship type to delete

        Returns:
            Number of relationships deleted
        """
        if not chunk_id and not relationship_type:
            # Delete all relationships
            query = "DELETE FROM chunk_relationships"
            params: list[Any] = []
        elif chunk_id and not relationship_type:
            # Delete all relationships for a chunk
            query = "DELETE FROM chunk_relationships WHERE source_chunk_id = ? OR target_chunk_id = ?"
            params = [chunk_id, chunk_id]
        elif not chunk_id and relationship_type:
            # Delete all relationships of a specific type
            query = "DELETE FROM chunk_relationships WHERE relationship_type = ?"
            params = [relationship_type]
        else:
            # Delete specific chunk relationships of a specific type
            query = """
                DELETE FROM chunk_relationships
                WHERE (source_chunk_id = ? OR target_chunk_id = ?)
                AND relationship_type = ?
            """
            params = [chunk_id, chunk_id, relationship_type]

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            deleted_count = cursor.rowcount
            conn.commit()

        return deleted_count

    def get_relationship_stats(self) -> dict[str, Any]:
        """Get statistics about chunk relationships.

        Returns:
            Dictionary with relationship statistics
        """
        stats = {
            "total_relationships": 0,
            "relationships_by_type": {},
            "relationships_by_strength_category": {},
            "average_strength": 0.0,
            "most_connected_chunks": [],
        }

        with self._get_connection() as conn:
            # Total relationships
            cursor = conn.execute("SELECT COUNT(*) FROM chunk_relationships")
            stats["total_relationships"] = cursor.fetchone()[0]

            # Relationships by type
            cursor = conn.execute(
                """
                SELECT relationship_type, COUNT(*)
                FROM chunk_relationships
                GROUP BY relationship_type
            """
            )
            stats["relationships_by_type"] = dict(cursor.fetchall())

            # Relationships by strength category
            cursor = conn.execute(
                """
                SELECT strength_category, COUNT(*)
                FROM chunk_relationships
                WHERE strength_category IS NOT NULL
                GROUP BY strength_category
            """
            )
            stats["relationships_by_strength_category"] = dict(cursor.fetchall())

            # Average strength
            cursor = conn.execute("SELECT AVG(strength) FROM chunk_relationships")
            avg_strength = cursor.fetchone()[0]
            stats["average_strength"] = float(avg_strength) if avg_strength else 0.0

            # Most connected chunks
            cursor = conn.execute(
                """
                SELECT chunk_id, connection_count FROM (
                    SELECT source_chunk_id as chunk_id, COUNT(*) as connection_count
                    FROM chunk_relationships
                    GROUP BY source_chunk_id
                    UNION ALL
                    SELECT target_chunk_id as chunk_id, COUNT(*) as connection_count
                    FROM chunk_relationships
                    GROUP BY target_chunk_id
                )
                GROUP BY chunk_id
                ORDER BY SUM(connection_count) DESC
                LIMIT 10
            """
            )
            stats["most_connected_chunks"] = [
                {"chunk_id": row[0], "connection_count": row[1]}
                for row in cursor.fetchall()
            ]

        return stats

    def analyze_chunk_network(self) -> dict[str, Any]:
        """Analyze the chunk relationship network structure.

        Returns:
            Dictionary with network analysis results
        """
        relationships = self.get_chunk_relationships()

        if not relationships:
            return {
                "node_count": 0,
                "edge_count": 0,
                "components": 0,
                "density": 0.0,
                "clustering_coefficient": 0.0,
            }

        # Build adjacency lists
        nodes = set()
        adjacency = defaultdict(set)

        for rel in relationships:
            source = rel["source_chunk_id"]
            target = rel["target_chunk_id"]
            nodes.add(source)
            nodes.add(target)
            adjacency[source].add(target)
            adjacency[target].add(source)  # Undirected graph

        node_count = len(nodes)
        edge_count = len(relationships)

        # Calculate density
        max_edges = node_count * (node_count - 1) // 2
        density = edge_count / max_edges if max_edges > 0 else 0.0

        # Count connected components (simplified)
        visited = set()
        components = 0

        def dfs(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for neighbor in adjacency[node]:
                dfs(neighbor)

        for node in nodes:
            if node not in visited:
                dfs(node)
                components += 1

        # Simple clustering coefficient estimate
        clustering_coefficient = 0.0
        if node_count > 2:
            total_clustering = 0.0
            for node in nodes:
                neighbors = adjacency[node]
                if len(neighbors) > 1:
                    # Count triangles
                    triangles = 0
                    for n1 in neighbors:
                        for n2 in neighbors:
                            if n1 != n2 and n2 in adjacency[n1]:
                                triangles += 1
                    # Local clustering coefficient
                    possible_triangles = len(neighbors) * (len(neighbors) - 1)
                    if possible_triangles > 0:
                        total_clustering += triangles / possible_triangles

            clustering_coefficient = total_clustering / node_count

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "components": components,
            "density": density,
            "clustering_coefficient": clustering_coefficient,
            "avg_degree": (2 * edge_count) / node_count if node_count > 0 else 0.0,
        }
