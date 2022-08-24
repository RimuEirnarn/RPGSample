"""Lib Save State"""

# This module MUST be a standalone module and must not imports any lib* or any files in here.
# Yes, avoid circular import. Because fixing them is a hell.
# Avoid problems is better than solving problems.

from pickle import Unpickler, UnpicklingError, dumps
from typing import Any, Union
from io import BytesIO


class PickleFileError(Exception):
    @classmethod
    def zero_or_other(cls, length: int) -> str:
        if length == 0:
            return str(cls()).format(this=0, deconstant="so... It's not filled! Try to fill it again.")
        return str(cls()).format(this=length, deconstant="so... It's unpicklable. Are you really sure this aint a pickle object?")

    def __str__(self):
        return "Either the file is not filled or is not a pickled file. We get {this} amount, {deconstant}"


class ReturnState(Unpickler):

    @classmethod
    def unload(cls, data: Union[str, bytes]):
        if isinstance(data, str):
            data = data.decode()
        if data == b'':
            raise PickleFileError(PickleFileError.zero_or_other(0))
        return cls(BytesIO(data)).load()


class DataUnpickler(ReturnState):

    def find_class(self, module: str, name: str) -> Any:  # Too many UNIONS!!
        try:
            return super().find_class(module, name)
        except UnpicklingError:
            if module not in ("libchara", 'libgame', 'libinventory', 'liblocalisation', 'libmagic', 'libshared'):
                raise
            if name not in ("ConstCreator", "PUID", 'percentage', 'Protocol', 'Project', 'AssetPath', 'DataPath', 'Character', 'Profile', 'Inventory', "ItemType", "MagicType"):
                raise
            return super().find_class(module, name)

    @staticmethod
    def dumps(data: Any) -> bytes:
        return dumps(data)

def compile_data():
    from libshared import Protocol
    # XXX: On certain classes. A URL Scheme with query of ?type=compiled
    #      Should move the read_path value to some other things.
    #      data-source on default then
    #      data on compiled
    #      Loading on data-source should be forbidden.
    #      Aside that, on global install; data-source will be hidden.
    #      That means, it must be some sort of flags of global install.
    #      Or, we shouldn't just do that.
    pass

def _main():
    from pickle import dumps
    from libshared import PUID

    x = dumps(PUID(None, version=2))
    y = DataUnpickler.unload(x)
