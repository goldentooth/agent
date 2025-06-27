"""Schema system for Flow-based agents with context integration."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from ..context import Context, ContextKey

T = TypeVar("T", bound="FlowIOSchema")


class FlowIOSchema(BaseModel):
    """Base schema for all Flow-based agent interactions with context integration."""

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, arbitrary_types_allowed=True
    )

    def to_context(self, context: Context) -> Context:
        """Convert schema to context entries.

        Creates context keys for each field in the schema and stores the values.
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
            field_type = type(field_value) if field_value is not None else Any

            # Create and set the context key
            context_key = ContextKey.create(key_name, field_type, description)
            updated_context.set(context_key.path, field_value)

        return updated_context

    @classmethod
    def from_context(cls: type[T], context: Context) -> T:
        """Extract schema from context.

        Retrieves values for all schema fields from the context.
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
                    elif hasattr(field_info, "default_factory") and callable(
                        field_info.default_factory
                    ):
                        try:
                            field_values[field_name] = field_info.default_factory()  # type: ignore[call-arg]
                        except TypeError:
                            # If default_factory needs arguments, skip it
                            pass

        return cls(**field_values)


class AgentInput(FlowIOSchema):
    """Standard input for agent flows."""

    message: str = Field(..., description="Input message")
    context_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional context data"
    )


class AgentOutput(FlowIOSchema):
    """Standard output for agent flows."""

    response: str = Field(..., description="Agent response")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )
