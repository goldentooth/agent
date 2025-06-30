"""Development utilities for the Goldentooth Agent project.

This module provides automated README.meta.yaml generation and maintenance.
Includes pre-commit hook integration for seamless workflow.
"""

from .metadata_generator import MetadataUpdateResult, ModuleMetadataGenerator

__all__ = ["ModuleMetadataGenerator", "MetadataUpdateResult"]
