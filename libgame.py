"""Lib game"""


# The basic of this is implementing basic functionality of ALL defined lib* resources.
#
# There are Items, Magics, and Inventory.
# Then there'll be many helper classes everywhere.
#
# Concluding into one, connector of everything. In this module.
#
# Base of RPGSample.
#
# Things that are need to be implemented:
#
# 1. Battle system
# 2. Logics
# 3. Game-to-system cookbooks.
# 4. Ticks.

from __future__ import annotations

from libchara import Character
from libitems import ItemType
from libmagic import MagicType
from libinventory import Inventory
from libshared import Project
from libsavestate import DataUnpickler

class ProfilePath(Project, prefix='profile'):
    """Profile/save path"""
    def read(self) -> Profile:
        with open(self.read_path(), 'rb') as f:
            return DataUnpickler.unload(f.read())

    def save(self, profile: Profile):
        with open(self.read_path(), 'wb') as f:
            return f.write(DataUnpickler.dumps(profile))

class Profile:
    """Profile/Save object"""
    def __init__(self, character: Character, inventory: Inventory):
        self._chara = character
        self._inventory = inventory
        self._state = dict(
            level=0,
            exp=0,
            wd=(0,0)
        )

    def set_character(self, character: Character):
        self._chara = character
    
    @property
    def inventory(self):
        """Inventory"""
        return self._inventory
    
    def __repr__(self):
        return f"{self._chara.name}[{self._state['level']}]"

def _main():
    x = ProfilePath("profile://default.profile")
    y = Profile(Character('None', 'None', 'None', 0), Inventory('Main', 20))
    print(repr(y))
    if not x.exists():
        x.save(y)
    else:
        y = x.read()
    print(repr(y))

if __name__ == '__main__':
    _main()