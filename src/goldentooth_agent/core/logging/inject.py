from antidote import lazy
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

if __name__ == "__main__":
  # Example usage
  from antidote import world
  logger = world[get_logger(__name__)]
  logger.debug("This is a debug message.")
  logger.info("This is an info message.")
  logger.warning("This is a warning message.")
  logger.error("This is an error message.")
  logger.critical("This is a critical message.")
