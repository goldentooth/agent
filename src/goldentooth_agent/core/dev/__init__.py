"""Development utilities for the Goldentooth Agent project.

This module provides automated README.meta.yaml generation and maintenance.
"""

from .metadata_generator import MetadataUpdateResult, ModuleMetadataGenerator

__all__ = ["ModuleMetadataGenerator", "MetadataUpdateResult"]
