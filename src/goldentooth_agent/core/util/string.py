import re

def camel_to_snake(camel_case_string):
  """Converts a camel case string to snake case."""
  s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', camel_case_string)
  return re.sub(r'([A-Z]+)([A-Z][a-z]*)', r'\1_\2', s1).lower()
