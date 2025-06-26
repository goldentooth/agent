from antidote import lazy
import os
from rich.logging import RichHandler


@lazy
def get_logger(name: str):
    """Get a rich logger."""
    from loguru import logger

    handler = RichHandler(
        level=os.environ.get("LOGLEVEL", "WARNING").upper(),
        markup=True,
        rich_tracebacks=True,
        tracebacks_suppress=[],
    )
    logger.configure(
        handlers=[
            {
                "sink": handler,
                "format": "{message}",
            },
        ]
    )
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
