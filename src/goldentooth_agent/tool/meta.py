class ToolMeta(type):
  def __new__(mcs, name, bases, attrs):
    cls = super().__new__(mcs, name, bases, attrs)

    if name == "ToolBase" or attrs.get("__abstract__", False):
      return cls

    # Required attributes
    for required in ["input_schema", "output_schema", "config_class", "metadata_class"]:
      if not hasattr(cls, required):
        raise TypeError(f"{name} is missing required attribute: {required}")

    metadata = cls.metadata_class # type: ignore[attr-defined]
    try:
      _ = metadata.get_name()
      _ = metadata.get_instructions()
    except Exception as e:
      raise TypeError(f"{name} has invalid metadata_class: {e}")

    from .registry import ToolRegistry
    ToolRegistry.register(cls)

    return cls
