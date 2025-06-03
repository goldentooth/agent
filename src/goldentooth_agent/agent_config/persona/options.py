from enum import Enum
from antidote import const, implements, inject, injectable, interface

class Persona(str, Enum):
  default = "default"
  straight = "straight"

DEFAULT_PERSONA = Persona.default

@injectable
class PersonaOptions:
  """Options for the persona configuration."""
  PERSONA = const.env("PERSONA", default=DEFAULT_PERSONA.value)

@interface.lazy
def get_persona() -> Persona:
  """Get the instructor client."""
  raise NotImplementedError(
    "The 'get_persona' function must be implemented."
  )

@implements.lazy(get_persona)
def get_env_persona(persona: str = inject[PersonaOptions.PERSONA]) -> Persona:
  """Get the persona from environment variables."""
  return Persona(persona) if persona else DEFAULT_PERSONA
