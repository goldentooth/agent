from .registry import ContextProviderRegistry

class ContextProviderMeta(type):
  def __new__(mcs, name, bases, attrs):
    cls = super().__new__(mcs, name, bases, attrs)

    if name == "ContextProviderBase" or attrs.get("__abstract__", False):
      return cls

    for required in ["metadata_class"]:
      if not hasattr(cls, required):
        raise TypeError(f"{name} is missing required attribute: {required}")

    metadata = cls.metadata_class # type: ignore[attr-defined]
    try:
      _ = metadata.get_name()
    except Exception as e:
      raise TypeError(f"{name} has invalid metadata_class: {e}")

    ContextProviderRegistry.register(cls)

    return cls

if __name__ == "__main__":
  # This block is for testing the metaclass functionality
  class ExampleContextProvider(metaclass=ContextProviderMeta):
    class metadata_class:
      @staticmethod
      def get_name():
        return "ExampleContextProvider"

  print("ExampleContextProvider registered successfully.")
  print("Registered context providers:", ContextProviderRegistry.keys())
