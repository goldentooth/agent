from importlib.resources import files
import yaml
from goldentooth_agent.data import personae  # Import the *module*, not the path

def load_persona_yaml(name: str):
  """Load a persona YAML file by name."""
  path = files(personae).joinpath(f"{name}.yaml")
  with path.open('r', encoding='utf-8') as f:
    return yaml.safe_load(f)

def get_persona_names():
  """Get a list of all available persona names."""
  return [f.stem for f in files(personae).iterdir() if f.suffix == '.yaml'] # type: ignore

def load_all_personae():
  """Load all persona YAML files and return a dictionary of their contents."""
  all_personae = {}
  for name in get_persona_names():
    all_personae[name] = load_persona_yaml(name)
  return all_personae
