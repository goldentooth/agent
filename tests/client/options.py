import anthropic
import instructor
from antidote import implements, inject, injectable, interface

@injectable
class ClientOptions:
  """Options for the client configuration."""
  provider: str = 'anthropic'
  sync_mode: str = 'sync'

  @inject.method
  def using_provider(self, name: str) -> bool:
    return self.provider == name

  @inject.method
  def using_sync_mode(self, mode: str) -> bool:
    return self.sync_mode == mode

@interface.lazy
def get_client() -> instructor.Instructor | instructor.AsyncInstructor:
  """Get the instructor client."""
  raise NotImplementedError(
    "The 'get_client' function must be implemented by the client provider."
  )

@implements.lazy(get_client).when(ClientOptions.using_provider('anthropic'), ClientOptions.using_sync_mode('async'))
def get_async_anthropic_client() -> instructor.AsyncInstructor:
  """Get the asynchronous Anthropic instructor client."""
  return instructor.from_anthropic(anthropic.AsyncAnthropic())

@implements.lazy(get_client).when(ClientOptions.using_provider('anthropic'), ClientOptions.using_sync_mode('sync'))
def get_sync_anthropic_client() -> instructor.Instructor:
  """Get the synchronous Anthropic instructor client."""
  return instructor.from_anthropic(anthropic.Anthropic())
