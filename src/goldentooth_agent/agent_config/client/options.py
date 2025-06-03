import anthropic
import instructor
from antidote import const, implements, inject, injectable, interface

@injectable
class ClientOptions:
  """Options for the client configuration."""
  PROVIDER = const.env("CLIENT_PROVIDER", default='anthropic')
  SYNC_MODE = const.env("CLIENT_SYNC_MODE", default='async')

@inject
def using_provider(name: str, current: str = inject[ClientOptions.PROVIDER]) -> bool:
  return name == current

@inject
def using_sync_mode(mode: str, current: str = inject[ClientOptions.SYNC_MODE]) -> bool:
  return mode == current

@interface.lazy
def get_client() -> instructor.Instructor | instructor.AsyncInstructor:
  """Get the instructor client."""
  raise NotImplementedError(
    "The 'get_client' function must be implemented by the client provider."
  )

@implements.lazy(get_client).when(using_provider('anthropic'), using_sync_mode('async'))
def get_async_anthropic_client() -> instructor.AsyncInstructor:
  """Get the asynchronous Anthropic instructor client."""
  return instructor.from_anthropic(anthropic.AsyncAnthropic())

@implements.lazy(get_client).when(using_provider('anthropic'), using_sync_mode('sync'))
def get_sync_anthropic_client() -> instructor.Instructor:
  """Get the synchronous Anthropic instructor client."""
  return instructor.from_anthropic(anthropic.Anthropic())
