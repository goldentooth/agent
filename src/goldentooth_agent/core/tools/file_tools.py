"""File-based tools for I/O operations, document processing, and data transformation."""

from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from typing import Any, Literal

import aiofiles
from pydantic import Field

from ..flow_agent import FlowIOSchema, FlowTool


# File Read Tool
class FileReadInput(FlowIOSchema):
    """Input schema for file read tool."""

    file_path: str = Field(..., description="Path to file to read")
    encoding: str = Field(default="utf-8", description="File encoding")
    max_size: int = Field(
        default=10_000_000, description="Maximum file size to read (10MB)"
    )
    binary_mode: bool = Field(default=False, description="Read file in binary mode")


class FileReadOutput(FlowIOSchema):
    """Output schema for file read tool."""

    file_path: str = Field(..., description="Path to file that was read")
    content: str = Field(..., description="File content (base64 encoded if binary)")
    encoding: str = Field(..., description="File encoding used")
    size_bytes: int = Field(..., description="File size in bytes")
    mime_type: str | None = Field(default=None, description="Detected MIME type")
    is_binary: bool = Field(..., description="Whether file was read in binary mode")
    success: bool = Field(..., description="Whether read was successful")
    error: str | None = Field(default=None, description="Error message if failed")


async def file_read_implementation(input_data: FileReadInput) -> FileReadOutput:
    """Read file content with encoding and size limits."""
    import base64

    try:
        file_path = Path(input_data.file_path)

        # Check if file exists
        if not file_path.exists():
            return FileReadOutput(
                file_path=input_data.file_path,
                content="",
                encoding=input_data.encoding,
                size_bytes=0,
                is_binary=input_data.binary_mode,
                success=False,
                error="File not found",
            )

        # Check file size
        size_bytes = file_path.stat().st_size
        if size_bytes > input_data.max_size:
            return FileReadOutput(
                file_path=input_data.file_path,
                content="",
                encoding=input_data.encoding,
                size_bytes=size_bytes,
                is_binary=input_data.binary_mode,
                success=False,
                error=f"File too large: {size_bytes} bytes > {input_data.max_size} bytes",
            )

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))

        # Read file content
        if input_data.binary_mode:
            async with aiofiles.open(file_path, "rb") as f:
                content_bytes = await f.read()
                content = base64.b64encode(content_bytes).decode("ascii")
        else:
            async with aiofiles.open(file_path, encoding=input_data.encoding) as f:
                content = await f.read()

        return FileReadOutput(
            file_path=input_data.file_path,
            content=content,
            encoding=input_data.encoding,
            size_bytes=size_bytes,
            mime_type=mime_type,
            is_binary=input_data.binary_mode,
            success=True,
            error=None,
        )

    except UnicodeDecodeError as e:
        return FileReadOutput(
            file_path=input_data.file_path,
            content="",
            encoding=input_data.encoding,
            size_bytes=0,
            is_binary=input_data.binary_mode,
            success=False,
            error=f"Encoding error: {str(e)}. Try binary mode.",
        )
    except Exception as e:
        return FileReadOutput(
            file_path=input_data.file_path,
            content="",
            encoding=input_data.encoding,
            size_bytes=0,
            is_binary=input_data.binary_mode,
            success=False,
            error=str(e),
        )


# File Write Tool
class FileWriteInput(FlowIOSchema):
    """Input schema for file write tool."""

    file_path: str = Field(..., description="Path to file to write")
    content: str = Field(..., description="Content to write (base64 for binary)")
    encoding: str = Field(default="utf-8", description="File encoding")
    binary_mode: bool = Field(default=False, description="Write file in binary mode")
    create_dirs: bool = Field(
        default=True, description="Create parent directories if needed"
    )
    append_mode: bool = Field(
        default=False, description="Append to file instead of overwriting"
    )


class FileWriteOutput(FlowIOSchema):
    """Output schema for file write tool."""

    file_path: str = Field(..., description="Path to file that was written")
    bytes_written: int = Field(..., description="Number of bytes written")
    encoding: str = Field(..., description="File encoding used")
    is_binary: bool = Field(..., description="Whether file was written in binary mode")
    was_appended: bool = Field(..., description="Whether content was appended")
    success: bool = Field(..., description="Whether write was successful")
    error: str | None = Field(default=None, description="Error message if failed")


async def file_write_implementation(input_data: FileWriteInput) -> FileWriteOutput:
    """Write content to file with directory creation and mode handling."""
    import base64

    try:
        file_path = Path(input_data.file_path)

        # Create parent directories if needed
        if input_data.create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine file mode
        mode: Literal["ab", "a", "wb", "w"]
        if input_data.append_mode and input_data.binary_mode:
            mode = "ab"
        elif input_data.append_mode:
            mode = "a"
        elif input_data.binary_mode:
            mode = "wb"
        else:
            mode = "w"

        # Write content
        bytes_written = 0
        if input_data.binary_mode:
            # Decode base64 content
            try:
                content_bytes = base64.b64decode(input_data.content)
            except Exception as e:
                return FileWriteOutput(
                    file_path=input_data.file_path,
                    bytes_written=0,
                    encoding=input_data.encoding,
                    is_binary=input_data.binary_mode,
                    was_appended=input_data.append_mode,
                    success=False,
                    error=f"Invalid base64 content: {str(e)}",
                )

            async with aiofiles.open(str(file_path), mode) as f:
                await f.write(content_bytes)
                bytes_written = len(content_bytes)
        else:
            async with aiofiles.open(
                str(file_path), mode, encoding=input_data.encoding
            ) as f:
                await f.write(input_data.content)
                bytes_written = len(input_data.content.encode(input_data.encoding))

        return FileWriteOutput(
            file_path=input_data.file_path,
            bytes_written=bytes_written,
            encoding=input_data.encoding,
            is_binary=input_data.binary_mode,
            was_appended=input_data.append_mode,
            success=True,
            error=None,
        )

    except Exception as e:
        return FileWriteOutput(
            file_path=input_data.file_path,
            bytes_written=0,
            encoding=input_data.encoding,
            is_binary=input_data.binary_mode,
            was_appended=input_data.append_mode,
            success=False,
            error=str(e),
        )


# JSON Processing Tool
class JsonProcessInput(FlowIOSchema):
    """Input schema for JSON processing tool."""

    operation: str = Field(
        ..., description="Operation: parse, stringify, validate, extract, transform"
    )
    json_data: str | None = Field(default=None, description="JSON string to process")
    data_object: dict[str, Any] | None = Field(
        default=None, description="Python object to process"
    )
    json_path: str | None = Field(
        default=None, description="JSONPath expression for extraction"
    )
    transform_rules: dict[str, Any] | None = Field(
        default=None, description="Transformation rules"
    )
    pretty_print: bool = Field(default=True, description="Pretty print JSON output")
    sort_keys: bool = Field(default=False, description="Sort keys in JSON output")


class JsonProcessOutput(FlowIOSchema):
    """Output schema for JSON processing tool."""

    operation: str = Field(..., description="Operation that was performed")
    result_json: str | None = Field(default=None, description="JSON string result")
    result_data: dict[str, Any] | None = Field(
        default=None, description="Python object result"
    )
    extracted_values: list[Any] = Field(
        default_factory=list, description="Extracted values from JSONPath"
    )
    validation_errors: list[str] = Field(
        default_factory=list, description="JSON validation errors"
    )
    success: bool = Field(..., description="Whether operation was successful")
    error: str | None = Field(default=None, description="Error message if failed")


async def json_process_implementation(
    input_data: JsonProcessInput,
) -> JsonProcessOutput:
    """Process JSON data with various operations."""
    try:
        operation = input_data.operation.lower()

        if operation == "parse":
            # Parse JSON string to object
            if not input_data.json_data:
                return JsonProcessOutput(
                    operation=operation,
                    success=False,
                    error="No JSON data provided for parsing",
                )

            try:
                result_data = json.loads(input_data.json_data)
                return JsonProcessOutput(
                    operation=operation, result_data=result_data, success=True
                )
            except json.JSONDecodeError as e:
                return JsonProcessOutput(
                    operation=operation,
                    success=False,
                    error=f"JSON parsing error: {str(e)}",
                )

        elif operation == "stringify":
            # Convert object to JSON string
            if input_data.data_object is None:
                return JsonProcessOutput(
                    operation=operation,
                    success=False,
                    error="No data object provided for stringification",
                )

            result_json = json.dumps(
                input_data.data_object,
                indent=2 if input_data.pretty_print else None,
                sort_keys=input_data.sort_keys,
                ensure_ascii=False,
            )

            return JsonProcessOutput(
                operation=operation, result_json=result_json, success=True
            )

        elif operation == "validate":
            # Validate JSON syntax
            if not input_data.json_data:
                return JsonProcessOutput(
                    operation=operation,
                    success=False,
                    error="No JSON data provided for validation",
                )

            validation_errors: list[str] = []
            try:
                json.loads(input_data.json_data)
                return JsonProcessOutput(
                    operation=operation,
                    validation_errors=validation_errors,
                    success=True,
                )
            except json.JSONDecodeError as e:
                validation_errors.append(str(e))
                return JsonProcessOutput(
                    operation=operation,
                    validation_errors=validation_errors,
                    success=False,
                    error="JSON validation failed",
                )

        elif operation == "extract":
            # Extract values using JSONPath (simplified implementation)
            if not input_data.json_path:
                return JsonProcessOutput(
                    operation=operation,
                    success=False,
                    error="No JSONPath provided for extraction",
                )

            # This is a simplified JSONPath implementation
            # For full JSONPath support, would need jsonpath-ng library
            data = None
            if input_data.json_data:
                data = json.loads(input_data.json_data)
            elif input_data.data_object:
                data = input_data.data_object
            else:
                return JsonProcessOutput(
                    operation=operation,
                    success=False,
                    error="No data provided for extraction",
                )

            # Simple path extraction (e.g., "$.key", "$.items[0].name")
            path = input_data.json_path.lstrip("$.")
            extracted_values: list[Any] = []

            try:
                # Basic path traversal
                current = data
                for part in path.split("."):
                    if "[" in part and "]" in part:
                        # Handle array indexing
                        key, index_part = part.split("[", 1)
                        index = int(index_part.rstrip("]"))
                        if key:
                            current = current[key]
                        current = current[index]  # type: ignore[index]
                    else:
                        current = current[part]

                extracted_values = (
                    [current] if not isinstance(current, list) else current
                )

                return JsonProcessOutput(
                    operation=operation, extracted_values=extracted_values, success=True
                )
            except (KeyError, IndexError, ValueError) as e:
                return JsonProcessOutput(
                    operation=operation,
                    success=False,
                    error=f"JSONPath extraction error: {str(e)}",
                )

        else:
            return JsonProcessOutput(
                operation=operation,
                success=False,
                error=f"Unknown operation: {operation}",
            )

    except Exception as e:
        return JsonProcessOutput(
            operation=input_data.operation, success=False, error=str(e)
        )


# Tool instances
FileReadTool = FlowTool(
    name="file_read",
    input_schema=FileReadInput,
    output_schema=FileReadOutput,
    implementation=file_read_implementation,  # type: ignore[arg-type]
    description="Read file content with encoding detection, size limits, and binary support",
)

FileWriteTool = FlowTool(
    name="file_write",
    input_schema=FileWriteInput,
    output_schema=FileWriteOutput,
    implementation=file_write_implementation,  # type: ignore[arg-type]
    description="Write content to files with directory creation and append support",
)

JsonProcessTool = FlowTool(
    name="json_process",
    input_schema=JsonProcessInput,
    output_schema=JsonProcessOutput,
    implementation=json_process_implementation,  # type: ignore[arg-type]
    description="Process JSON data with parsing, validation, extraction, and transformation",
)
