from antidote import const, implements, inject, injectable, interface

DEFAULT_MODEL_VERSION = 'claude-3-5-sonnet-20240620'

@injectable
class ModelOptions:
  """Options for the model configuration."""
  VERSION = const.env("MODEL_VERSION", default=DEFAULT_MODEL_VERSION)

@interface.lazy
def get_model_version() -> str:
  """Get the instructor client."""
  raise NotImplementedError(
    "The 'get_model_version' function must be implemented."
  )

@implements.lazy(get_model_version)
def get_env_model_version(model_version: str = inject[ModelOptions.VERSION]) -> str:
  """Get the model version from environment variables."""
  return model_version
