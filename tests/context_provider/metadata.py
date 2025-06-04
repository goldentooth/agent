class ContextProviderMetadata:
  """Metadata for a context provider."""
  name: str

  @classmethod
  def get_name(cls) -> str:
    """Get the name of the context provider."""
    return cls.name

if __name__ == "__main__":
  # Example usage
  class ExampleContextProviderMetadata(ContextProviderMetadata):
    name = "ExampleContextProvider"

  print("Context Provider Name:", ExampleContextProviderMetadata.get_name())
  # Output: Context Provider Name: ExampleContextProvider
