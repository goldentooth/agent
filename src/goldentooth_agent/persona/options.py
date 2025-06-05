from enum import Enum
from antidote import implements, inject, injectable, interface

class Persona(str, Enum):
  default = "default"
  straight = "straight"

@injectable
class PersonaOptions:
  """Options for the persona configuration."""
  persona: Persona = Persona.default

@interface.lazy
def get_persona() -> Persona:
  """Get the instructor client."""
  raise NotImplementedError(
    "The 'get_persona' function must be implemented."
  )

@implements.lazy(get_persona)
def get_current_persona(options: PersonaOptions = inject[PersonaOptions]) -> Persona:
  """Get the current persona."""
  return options.persona
