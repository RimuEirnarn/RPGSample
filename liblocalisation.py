"""Lib localisation

This is an abstraction of locale or i18n.

We don't use them as we're defining ourself."""

from __future__ import annotations
from typing import Dict, Union

from os.path import exists as p_exists
from libshared import DataPath, ConstCreator
from shlex import split

_locales: Dict[str, Dict[Union[str, int], str]] = {}  # Caching readed-localisation. We don't want to read everything again.
_current_locale = 'en'
undefined = ConstCreator('Undefined', [5])

def _locale_reader(name, data: str) -> dict:
    """ Read locale, returns dict because of #"""
    r = data.split('\n')
    obj = {}
    for i, a in enumerate(r):
        if len(a) == 0:
            continue
        if a[0] != '@':
            continue
        b = a.split(' ')
        if len(b) <= 2:
            raise Exception(
                f"The required is 3 words. Got {len(b)} at line {i+1}")
        namespace = b[0][1:]
        nm = b[0]
        if nm[0] != '@':
            continue
        if namespace not in obj:
            obj[namespace] = {}
        idname = b[1][1:]
        idn = b[1]
        values = ''.join(b[2:])  # Used in # and $ if # only 1 word.
        if idn[0] not in ("#", '$'):
            continue
        if idn[0] == '#':
            obj[namespace][idname] = values
        if idn[0] == '$':
            if not idname.isnumeric():
                raise Exception(
                    f"Not an integer while using $ (line {i+1} char {a.find('$')})")
            idname = int(idname)
            obj[namespace][idname] = values
    _locales[name] = obj
    return obj


class LocalisationError(Exception):
    """A localisation file is not found"""
    pass


class LCPath(DataPath, prefix='locale', compilable=False, default=1):
    """Localisation Protocol Handlers."""
    def read_path(self):
        return super().read_path()+'.locale'

    def touch(self):
        with open(self.read_path(), 'w') as f:
            f.write("""To write a localisation, first. We need to know the syntax. It's quite simple.
@namespace $0 Locale string, no need to put \" or \'.
OR
@namespace #Window The window name, yes.

Explanation:
    Because anything started except with @ is marked as comments.
    Namespace is namespace. Place to put the identifier and text.
    And then, $ -- $ used to recognise certain text is numerical and will be used as identifier.
    That's the reason why there's no \" or \'
    # is used as string identifier. If you don't want to use $.
    But remember, 1 word only.

Then, let's give it a shot!

`@main $0 RPGSample
`@main #Confirmation Konfirmasi
`@main #OK Oke
`@main #Cancel Batal""")

    def read(self) -> Localisation:
        with open(self.read_path()) as f:
            data = f.read()
        return _locale_reader(self._path, data)

    def exists(self) -> bool:
        return p_exists(self.read_path())


class Localisation:
    """Localisation object"""

    def __init__(self, name: str, obj: Dict[str, Dict[Union[str, int], str]]):
        self._current_locale_name = name
        self._current_locale = obj

    @staticmethod
    def set_locale(name: str):
        global _current_locale
        if Localisation.is_this_exists(name) is False:
            raise LocalisationError(
                f"Locale {name} does not exists in locale path.")
        _current_locale = name

    def get_text(self, namespace: str, referer: Union[str, int]) -> Union[str, ConstCreator]:
        return _locales.get(_current_locale, self._current_locale).get(namespace, {}).get(referer, undefined)

    # Do not define set_text()

    @staticmethod
    def make_locale(name: str):
        x = LCPath(f"locale://{name}")
        x.touch()

    @staticmethod
    def load_locale(name: str) -> Localisation:
        LCPath(f"locale://{name}").read()
        return Localisation(name, _locales[name])

    @staticmethod
    def is_this_exists(name: str):
        return LCPath(f"locale://{name}").exists()

def get_text(namespace: str, referer: Union[str, int]) -> Union[str, ConstCreator]:
    return _locales[_current_locale].get(namespace, {}).get(referer, undefined)

def _main():
    pass
