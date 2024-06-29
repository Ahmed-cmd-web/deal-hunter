import os

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"


if DEVELOPMENT_MODE:
    from .settingsConfig.development import *
else:
    from .settingsConfig.production import *

