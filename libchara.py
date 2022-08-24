from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
from posixpath import exists, realpath, splitext
from typing import Any, Literal, Mapping, Union
from libshared import DataPath, parse_data, load_data
from libsavestate import DataUnpickler


class CharaPath(DataPath, prefix="chara"):
    """Character Protocol Handler. Loader/Saver for Character object. Use it like in _main()
    or
    Save:
    >>> chara = Character(...)
    >>> a = CharaPath("chara://_debug.chr?compiled=true")
    >>> # You can use true for compiled
    >>> a.save(chara)

    Load:
    >>> a = CharaPath("chara://_debug.chr")
    >>> a"""
    # TODO: Due to Issue #1 (Local git instance), problem to save character/other in non-compiled way is persist.
    #     : So, use YAML or .conf-like?

    def save(self, obj: Character):
        """save Character to destined path"""
        if self.IsCompiled is True:
            with open(self.read_path(), 'wb') as f:
                return f.write(DataUnpickler.dumps(obj))

    def load(self) -> Character:
        """load Character from path"""
        if self.IsCompiled is True:
            with open(self.read_path(), 'rb') as f:
                return DataUnpickler.unload(f.read())


@dataclass(init=True)
class Character:
    """Character"""
    name: str
    gender: str
    race: str
    age: int

    def __repr__(self):
        return f"{type(self).__name__}({self.name})"


def _main():
    chara = Character("Debug", "None", 'None', 0)
    a = CharaPath("chara://_debug.chr?compiled=true")
    a.save(chara)
    n = a.load()
    repr(chara)
    assert n.age == chara.age
