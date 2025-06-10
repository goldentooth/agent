from antidote import inject
from rich.console import Console
import typer
from typing import Protocol, runtime_checkable
from goldentooth_agent.core.pipeline import Middleware, NextMiddleware, middleware
from goldentooth_agent.core.thunk import Thunk
from .console import get_console, get_error_console

def console_print_mw(message: str, style: str = "") -> Middleware:
  """Generator for middleware to print a message to the console."""
  @middleware
  @inject
  async def _middleware(context: object, next: NextMiddleware, console: Console = inject[get_console()]):
    """Middleware to print a message to the console with optional styling."""
    console.print(f"[{style}]{message}[/{style}]" if style else message)
    await next()
  return _middleware

def console_print_th(message: str, style: str = "") -> Thunk[Console, None]:
  """Generator for thunk to print a message to the console."""
  @inject
  async def _thunk(_nil, console: Console = inject[get_console()]) -> None:
    """Thunk to print a message to the console with optional styling."""
    console.print(f"[{style}]{message}[/{style}]" if style else message)
  return Thunk(_thunk)

def console_print_error_mw(message: str, style: str) -> Middleware:
  """Generator for middleware to print an error message to the console."""
  @middleware
  @inject
  async def _middleware(context: object, next: NextMiddleware, console: Console = inject[get_error_console()]):
    """Middleware to print an error message to the console with optional styling."""
    console.print(f"[{style}]{message}[/{style}]" if style else message)
    await next()
  return _middleware

def console_print_error_th(message: str, style: str) -> Thunk[Console, None]:
  """Generator for thunk to print an error message to the console."""
  @inject
  async def _thunk(_nil, console: Console = inject[get_error_console()]) -> None:
    """Thunk to print an error message to the console with optional styling."""
    console.print(f"[{style}]{message}[/{style}]" if style else message)
  return Thunk(_thunk)

@runtime_checkable
class HasUserInput(Protocol):
  """Protocol for a context that has user input."""
  user_input: str

def console_input_mw(prompt: str = "You:", style: str = "bold blue") -> Middleware[HasUserInput]:
  """Generator for middleware to prompt the user for input and return it."""
  @middleware
  @inject
  async def _middleware(context: HasUserInput, next: NextMiddleware, console: Console = inject[get_console()]):
    """Middleware to prompt the user for input with a styled prompt."""
    user_input = console.input(f"\n[{style}]{prompt}[/{style}] " if style else f"\n{prompt} ")
    context.user_input = user_input
    await next()
  return _middleware

def exit_on_input_mw() -> Middleware[HasUserInput]:
  """Generator for middleware to prompt the user for input and return it."""
  @middleware
  async def _middleware(context: HasUserInput, next: NextMiddleware):
    """Middleware to exit the application if the user inputs /exit or /quit."""
    if context.user_input.strip().lower() in ["/exit", "/quit"]:
      typer.Exit()
    await next()
  return _middleware

def console_input_th(prompt: str = "You:", style: str = "bold blue") -> Thunk[Console, str]:
  """Generator for thunk to prompt the user for input and return it."""
  @inject
  async def _thunk(_nil, console: Console = inject[get_console()]) -> str:
    """Thunk to prompt the user for input."""
    return console.input(f"\n[{style}]{prompt}[/{style}] " if style else f"\n{prompt} ")
  return Thunk(_thunk)

def exit_on_input_th() -> Thunk[str, str]:
  """Thunk to exit the application if the user inputs /exit or /quit."""
  @inject
  async def _thunk(user_input: str, console: Console = inject[get_console()]) -> str:
    """Thunk to exit the application."""
    if user_input.strip().lower() in ["/exit", "/quit"]:
      console.print("Exiting the application. Goodbye!", style="bold red")
      typer.Exit()
    return user_input
  return Thunk(_thunk)
