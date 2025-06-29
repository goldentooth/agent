"""
Compatibility shim for flow module.

This module has been moved to goldentooth_agent.flow_engine.
This shim provides backward compatibility.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "goldentooth_agent.core.flow is deprecated. "
    "Use goldentooth_agent.flow_engine instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from new location
from goldentooth_agent.flow_engine import *  # noqa: F403
