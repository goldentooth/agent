from instructor import Instructor, Mode, Provider
from typing import Generator

class NoOpInstructor(Instructor):
  """A no-operation instructor that returns a default response."""

  def __init__(self, default_response: str = "NoOp Response"):
    """Initialize the NoOpInstructor with a default response."""
    self._default_response = default_response
    super().__init__(
      client=None,
      create=self.create_fn,
      mode=Mode.TOOLS,
      provider=Provider.OPENAI,
    )

  def create_fn(self, *, response_model=None, messages=None, **kwargs):
    """Create a response using the default response."""
    if response_model:
      return response_model(chat_message=self._default_response)
    return {"chat_message": self._default_response}

  def create_partial(self, *args, **kwargs) -> Generator:
    """Create a partial response generator."""
    yield self.create_fn(**kwargs)

  def create_iterable(self, *args, **kwargs) -> Generator:
    """Create an iterable response generator."""
    yield self.create_fn(**kwargs)

  def create_with_completion(self, *args, **kwargs):
    """Create a response with a mock completion."""
    result = self.create_fn(**kwargs)
    return result, {"mock": "completion"}
