# Compatibility shim — all consumers keep working unchanged.
# Real definitions live in game/constants.py and game/ai_tables.py.
import pygame  # kept so existing `import initvar; pygame...` patterns still work
from game.constants import *
from game.ai_tables import *
