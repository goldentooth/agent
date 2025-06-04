from __future__ import annotations
from typing import Type, TYPE_CHECKING
from atomic_agents.lib.base.base_tool import BaseTool
from .meta import ToolMeta

if TYPE_CHECKING:
  from .metadata import ToolMetadata
  from atomic_agents.agents.base_agent import BaseIOSchema
  from atomic_agents.lib.base.base_tool import BaseToolConfig

class ToolBase(BaseTool, metaclass=ToolMeta):
  """Abstract base class for all tools."""
  __abstract__ = True

  config_class: Type[BaseToolConfig]
  metadata_class: Type[ToolMetadata]

  def __init__(self, config):
    self.config = config

  def run(self, params: BaseIOSchema) -> BaseIOSchema: # type: ignore[override]
    raise NotImplementedError
