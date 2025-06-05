from antidote import implements, inject, injectable, interface

DEFAULT_MODEL_VERSION = 'claude-3-5-sonnet-20240620'

@injectable
class ModelOptions:
  """Options for the model configuration."""
  version: str = DEFAULT_MODEL_VERSION

@interface.lazy
def get_model_version() -> str:
  """Get the instructor client."""
  raise NotImplementedError(
    "The 'get_model_version' function must be implemented."
  )

@implements.lazy(get_model_version)
def get_current_model_version(options: ModelOptions = inject[ModelOptions]) -> str:
  """Get the model version from environment variables."""
  return options.version
