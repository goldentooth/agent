from antidote import inject
from rich.console import Console
import typer
from typing import Protocol, runtime_checkable
from goldentooth_agent.core.pipeline import Middleware, NextMiddleware, middleware
from goldentooth_agent.core.thunk import Thunk
from .store import StaticContextProviderStore

