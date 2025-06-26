"""Rules module for flow-based rule engines and conditional logic.

This module provides Flow-based rule systems for implementing conditional logic
and business rules processing. Rules are pure Flow-based and don't depend on Thunk.
"""

from .rule import Rule
from .rule_engine import RuleEngine

__all__ = ["Rule", "RuleEngine"]
