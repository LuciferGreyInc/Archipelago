import Utils
from Utils import read_snes_rom
from worlds.AutoWorld import World
from worlds.Files import APDeltaPatch
from .Levels import level_list, level_dict

USHASH = '120abf304f0c40fe059f6a192ed4f947'
ROM_PLAYER_LIMIT = 65535

import hashlib
import os
import math
