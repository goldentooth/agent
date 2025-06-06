from antidote import injectable

@injectable
class StraightnessOptions:
  """Options for the straightness configuration."""
  enabled: bool = False
