"""Lib Level Manager"""
try:
    from .libshared import percentage
except (ModuleNotFoundError, ImportError):
    from libshared import percentage
from functools import lru_cache
from math import inf
from random import randint
from pprint import pprint

@lru_cache
def _debug_level_to_exp(level: int) -> int:
    if level == 0:
        return 40
    try:
        return round(round(percentage(randint(1,5) if level <= 30 else (randint(round(5), round(10)) if (level % 200) != 0 else (randint(round(20+level/300), round(30+level/300)))))(_debug_level_to_exp(level-1)))+_debug_level_to_exp(level-1))
    except Exception:
        return inf

x = [(_debug_level_to_exp(a),a) for a in range(10000)]
pprint(x)