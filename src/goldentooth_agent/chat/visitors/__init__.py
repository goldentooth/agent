import importlib
import pkgutil
import sys
from .greeter import GreeterVisitor

def import_all_visitors():
  package = sys.modules[__name__]
  for _, modname, ispkg in pkgutil.iter_modules(package.__path__):
    if not ispkg:
      importlib.import_module(f"{package.__name__}.{modname}")

import_all_visitors()

__all__ = [
  "GreeterVisitor",
]
