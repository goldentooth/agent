from antidote import lazy

DEFAULT_MODEL_VERSION = 'claude-3-5-sonnet-20240620'

@lazy
def get_model_version() -> str:
  """Get the model version."""
  return DEFAULT_MODEL_VERSION
