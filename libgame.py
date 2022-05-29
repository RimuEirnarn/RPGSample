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


from libchara import Character
from libitems import ItemPath
from libmagic import MagicPath
from libinventory import Inventory
from libshared import Project


class Profile(Project, prefix='profile'):
    pass
