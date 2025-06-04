import importlib
import pkgutil
import sys
from .agent_output import AgentOutputSchema
from .user_input import UserInputSchema

def import_all_schemata():
  package = sys.modules[__name__]
  for _, modname, ispkg in pkgutil.iter_modules(package.__path__):
    if not ispkg:
      importlib.import_module(f"{package.__name__}.{modname}")

import_all_schemata()

__all__ = [
  "AgentOutputSchema",
  "UserInputSchema",
]
