from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GoldentoothNode(BaseModel):
    """Represents a node in the Goldentooth cluster."""

    id: str = Field(..., description="Node identifier")
    name: str = Field(..., description="Human-readable node name")
    hostname: str = Field(..., description="Network hostname")
    ip_address: str | None = Field(None, description="IP address")

    # Hardware info
    architecture: str | None = Field(
        None, description="CPU architecture (e.g. arm64, x86_64)"
    )
    cpu_cores: int | None = Field(None, description="Number of CPU cores")
    memory_gb: float | None = Field(None, description="RAM in GB")
    storage_gb: float | None = Field(None, description="Storage capacity in GB")

    # Status
    status: str = Field(
        "unknown", description="Node status: online, offline, maintenance, unknown"
    )
    role: str = Field("worker", description="Node role: master, worker, storage, edge")

    # Location and environment
    datacenter: str | None = Field(None, description="Datacenter or location")
    environment: str = Field(
        "production", description="Environment: production, staging, dev"
    )

    # Services and capabilities
    services: list[str] = Field(
        default_factory=list, description="Services running on this node"
    )
    capabilities: list[str] = Field(
        default_factory=list, description="Node capabilities/labels"
    )

    # Monitoring
    last_seen: datetime | None = Field(
        None, description="When node was last seen alive"
    )
    uptime_hours: float | None = Field(None, description="Current uptime in hours")

    # Metadata
    created_at: datetime | None = Field(
        None, description="When node was added to cluster"
    )
    updated_at: datetime | None = Field(
        None, description="When node info was last updated"
    )

    # RAG metadata
    last_synced: datetime | None = Field(
        None, description="When this data was last synced"
    )
    rag_include: bool = Field(True, description="Whether to include in RAG indexing")


class GoldentoothNodeAdapter:
    """Adapter for GoldentoothNode YAML serialization."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoldentoothNode:
        """Create a GoldentoothNode from dictionary data."""
        # Handle datetime strings
        for date_field in ["last_seen", "created_at", "updated_at", "last_synced"]:
            if data.get(date_field) and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(
                    data[date_field].replace("Z", "+00:00")
                )

        return GoldentoothNode(**data)

    @classmethod
    def to_dict(cls, id: str, obj: GoldentoothNode) -> dict[str, Any]:
        """Convert GoldentoothNode to dictionary for YAML serialization."""
        data = obj.model_dump()

        # Convert datetime objects to ISO strings
        for date_field in ["last_seen", "created_at", "updated_at", "last_synced"]:
            if data.get(date_field):
                data[date_field] = data[date_field].isoformat()

        return data


class GoldentoothService(BaseModel):
    """Represents a service in the Goldentooth ecosystem."""

    id: str = Field(..., description="Service identifier")
    name: str = Field(..., description="Human-readable service name")
    description: str | None = Field(None, description="Service description")

    # Service details
    service_type: str = Field(
        ..., description="Type of service: web, api, database, cache, etc."
    )
    version: str | None = Field(None, description="Service version")

    # Network configuration
    port: int | None = Field(None, description="Primary service port")
    ports: list[int] = Field(default_factory=list, description="All exposed ports")
    endpoints: list[str] = Field(
        default_factory=list, description="Service endpoints/URLs"
    )

    # Deployment
    nodes: list[str] = Field(
        default_factory=list, description="Nodes where service runs"
    )
    replicas: int = Field(1, description="Number of service replicas")

    # Status and health
    status: str = Field(
        "unknown", description="Service status: running, stopped, degraded, unknown"
    )
    health_check_url: str | None = Field(None, description="Health check endpoint")

    # Dependencies
    depends_on: list[str] = Field(
        default_factory=list, description="Services this depends on"
    )
    used_by: list[str] = Field(
        default_factory=list, description="Services that depend on this"
    )

    # Configuration
    config: dict[str, Any] = Field(
        default_factory=dict, description="Service configuration"
    )
    environment_vars: dict[str, str] = Field(
        default_factory=dict, description="Environment variables"
    )

    # Monitoring and metrics
    metrics_endpoint: str | None = Field(
        None, description="Prometheus metrics endpoint"
    )
    log_level: str = Field("info", description="Log level")

    # Timestamps
    created_at: datetime | None = Field(None, description="When service was deployed")
    updated_at: datetime | None = Field(
        None, description="When service was last updated"
    )

    # RAG metadata
    last_synced: datetime | None = Field(
        None, description="When this data was last synced"
    )
    rag_include: bool = Field(True, description="Whether to include in RAG indexing")
    priority: str = Field("medium", description="RAG priority: low, medium, high")


class GoldentoothServiceAdapter:
    """Adapter for GoldentoothService YAML serialization."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoldentoothService:
        """Create a GoldentoothService from dictionary data."""
        # Handle datetime strings
        for date_field in ["created_at", "updated_at", "last_synced"]:
            if data.get(date_field) and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(
                    data[date_field].replace("Z", "+00:00")
                )

        return GoldentoothService(**data)

    @classmethod
    def to_dict(cls, id: str, obj: GoldentoothService) -> dict[str, Any]:
        """Convert GoldentoothService to dictionary for YAML serialization."""
        data = obj.model_dump()

        # Convert datetime objects to ISO strings
        for date_field in ["created_at", "updated_at", "last_synced"]:
            if data.get(date_field):
                data[date_field] = data[date_field].isoformat()

        return data
