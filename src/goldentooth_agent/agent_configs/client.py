from antidote import const, implements, inject, interface, lazy
import anthropic
import instructor

AGENT_PROVIDER = const.env(default='anthropic')
AGENT_SYNC_MODE = const.env(default='async')

@inject
def using_provider(name: str, current: str = inject[AGENT_PROVIDER]) -> bool:
  return name == current

@inject
def using_sync_mode(mode: str, current: str = inject[AGENT_SYNC_MODE]) -> bool:
  return mode == current

@interface
def get_client() -> instructor.Instructor | instructor.AsyncInstructor:
  """Get the instructor client."""
  raise NotImplementedError(
    "The 'get_client' function must be implemented by the client provider."
  )

@lazy
@implements(get_client).when(using_provider('anthropic'), using_sync_mode('async'))
def get_async_anthropic_client() -> instructor.AsyncInstructor:
  """Get the asynchronous Anthropic instructor client."""
  return instructor.from_anthropic(anthropic.AsyncAnthropic())

@lazy
@implements(get_client).when(using_provider('anthropic'), using_sync_mode('sync'))
def get_sync_anthropic_client() -> instructor.Instructor:
  """Get the synchronous Anthropic instructor client."""
  return instructor.from_anthropic(anthropic.Anthropic())
