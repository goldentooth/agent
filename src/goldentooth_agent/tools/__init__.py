import importlib
import pkgutil
import sys

def import_all_tools():
  package = sys.modules[__name__]
  for _, modname, ispkg in pkgutil.iter_modules(package.__path__):
    if not ispkg:
      importlib.import_module(f"{package.__name__}.{modname}")

import_all_tools()