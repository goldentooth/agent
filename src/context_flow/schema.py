"""Schema system for Flow-Context integration.

This module provides base schema classes that bridge the Flow and Context systems,
enabling type-safe data exchange and validation in context-aware flow compositions.
"""

from __future__ import annotations

from typing import Any  # Only for type aliases
from typing import TypeVar, cast

from pydantic import BaseModel, ConfigDict, Field

from context import Context, ContextKey

# Type aliases for schema system
ContextData = dict[str, Any]  # Context can store arbitrary data
AnyType = type[Any]  # For type casting in generic contexts

T = TypeVar("T", bound="ContextFlowSchema")


class ContextFlowSchema(BaseModel):
    """Base schema for Flow-Context integration with bidirectional conversion.

    This class provides the foundation for type-safe data exchange between
    the Flow engine and Context system. It enables schemas to be:
    - Converted to Context entries with namespaced keys
    - Extracted from Context with proper validation
    - Used in Flow pipelines with context awareness
    """

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, arbitrary_types_allowed=True
    )

    def to_context(self, context: Context) -> Context:
        """Convert schema to context entries.

        Creates context keys for each field in the schema and stores the values.
        Keys are namespaced as 'schema.{ClassName}.{field_name}' to avoid conflicts.

        Args:
            context: The context to store schema values in

        Returns:
            Updated context with schema fields as context entries
        """
        # Get the class name to create unique context keys
        class_name = self.__class__.__name__

        # Fork context to maintain immutability
        updated_context = context.fork()

        # Iterate through all fields and create context entries
        for field_name, field_value in self.model_dump().items():
            # Create a context key for this field
            key_name = f"schema.{class_name}.{field_name}"
            field_info = self.__class__.model_fields.get(field_name)
            description = (
                field_info.description
                if field_info and field_info.description
                else f"{field_name} from {class_name}"
            )

            # Determine the type for the context key
            field_type = (  # pyright: ignore[reportUnknownVariableType]
                type(field_value) if field_value is not None else type(None)
            )

            # Create and set the context key
            # We need to cast to the expected type since ContextKey.create is generic
            context_key = ContextKey.create(  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
                key_name, cast(AnyType, field_type), description
            )
            updated_context.set(context_key.path, field_value)

        return updated_context

    @classmethod
    def from_context(cls: type[T], context: Context) -> T:
        """Extract schema from context.

        Retrieves values for all schema fields from the context using
        the same namespacing pattern as to_context().

        Args:
            context: The context to extract schema values from

        Returns:
            Schema instance populated with values from context

        Raises:
            ValueError: If required fields are missing from context
        """
        class_name = cls.__name__
        field_values = {}

        # Iterate through all fields in the schema
        for field_name, field_info in cls.model_fields.items():
            # Construct the context key name (same as in to_context)
            key_name = f"schema.{class_name}.{field_name}"

            # Try to get the value from context using the key path
            try:
                found_value = context[key_name]
                field_values[field_name] = found_value
            except KeyError as e:
                # Key not found - check if field is required
                if field_info.is_required():
                    # Required field missing - this is an error
                    raise ValueError(
                        f"Required field '{field_name}' not found in context"
                    ) from e
                else:
                    # Use default value if field is optional
                    if field_info.default is not None:
                        field_values[field_name] = field_info.default
                    elif (
                        hasattr(field_info, "default_factory")
                        and field_info.default_factory is not None
                    ):
                        try:
                            # Call the default factory without arguments
                            field_values[field_name] = field_info.default_factory()  # type: ignore[call-arg]
                        except TypeError:
                            # If default_factory needs arguments, skip it
                            pass

        return cls(**field_values)


class AgentInput(ContextFlowSchema):
    """Standard input schema for agent flows."""

    message: str = Field(..., description="Input message")
    context_data: ContextData = Field(
        default_factory=dict, description="Additional context data"
    )


class AgentOutput(ContextFlowSchema):
    """Standard output schema for agent flows."""

    response: str = Field(..., description="Agent response")
    metadata: ContextData = Field(default_factory=dict, description="Response metadata")
