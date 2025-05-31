from typing import Type
from .meta import ToolMeta
from .metadata import ToolMetadata
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig, BaseIOSchema

class ToolBase(BaseTool, metaclass=ToolMeta):
  """Abstract base class for all tools."""
  __abstract__ = True

  config_class: Type[BaseToolConfig]
  metadata_class: Type[ToolMetadata]

  def __init__(self, config):
    self.config = config

  def run(self, params: BaseIOSchema) -> BaseIOSchema: # type: ignore[override]
    raise NotImplementedError
