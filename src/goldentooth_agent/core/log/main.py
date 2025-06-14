import anthropic
import atomic_agents
from antidote import lazy
import httpcore
import instructor
import logging
from logging import Logger
import os
from rich.logging import RichHandler

@lazy
def get_logger(name: str) -> Logger:
  """Get a rich logger."""
  FORMAT = "%(message)s"
  logging.basicConfig(
    level=os.environ.get('LOGLEVEL', 'WARNING').upper(),
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
      RichHandler(
        markup=True,
        rich_tracebacks=True,
        tracebacks_suppress=[],
      ),
    ],
  )
  logger = logging.getLogger(name)
  return logger
