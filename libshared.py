"""Shared module for lib* module

This module is as its summary."""

from __future__ import annotations

from platform import system

__version__ = '0.0.1 [A1]'
__author__ = 'Archaent Nakasaki and RimuEirnarn'
__copyright__ = 'BSD 3-Clause'
__all__ = ['ConstCreator', 'PUID', 'make_uuid', 'RandomNamespace',
           'AssignedProtocolError', 'Protocol', "Project", 'AssetPath', 'DataPath', 'getpath']

from hashlib import sha256 as _hs_256
from io import StringIO
from os.path import exists, expanduser, realpath
from re import compile as _re_compile
from re import escape as _re_escape
from secrets import SystemRandom
from string import punctuation
from typing import (IO, Any, Callable, Dict, Iterable, List, Literal, Mapping,
                    Union)
from urllib.parse import urlsplit
from uuid import UUID as system_UUID
from uuid import uuid5

try:
    from yaml import safe_dump as yaml_parse
    from yaml import safe_load as yaml_load
except (ModuleNotFoundError, ImportError):
    yaml_load = None
    yaml_parse = None
from configparser import ConfigParser

_uuid_max_int = 340282366920938463463374607431768211455
_puid_compiled = _re_compile('['+_re_escape(punctuation)+']')


class ConstCreator:
    _objects: Dict[str, ConstCreator] = {}

    def __new__(cls, name: str, value: Any):
        if name in ConstCreator._objects:
            return ConstCreator._objects[name]
        self = super().__new__(cls)
        ConstCreator._objects[name] = self
        return self

    def __init__(self, name: str, value, /, _Repr_Mode: Literal[1, 2, 3, 4] = 2):
        self._name = name
        self._value = value
        self._reprm = _Repr_Mode
        if _Repr_Mode < 1 or _Repr_Mode > 4:
            raise ValueError("Repr mode should be either 1, 2, 3, or 4.")
        self._reprf: List[Union[Callable, None]] = [None, lambda self: f'Ref[{self._name}] -> {self._value}',
                                                    lambda self: f"{self._name}",
                                                    lambda self: f"{self._value}",
                                                    lambda self: f'Const[{self._name}]']

    def __repr__(self):
        return self._reprf[self._reprm](self)

    @staticmethod
    def define(name: str, value: Any) -> ConstCreator:
        return ConstCreator(name, value)


def make_uuid():
    return uuid5(RandomNamespace, SystemRandom().randbytes(16).decode())

# UUID is used in random ways. We, however should define our own UUID


RandomNamespace = system_UUID('urn:uuid:00000001-0000-0000-0000-000000000000')

# libshared defined of Pseudo Unique Identifiers

_chars = tuple('0123456789abcdefghijklmnopqrstuvwxyz')


def _puid_to_int(chars: str):
    return int(chars, 36)


def _int_to_spuid(n: int):
    # how we do this?
    array = []
    if n == 0:
        return '0'
    while n != 0:
        check = n % len(_chars)
        array.append(_chars[check])
        n = int(n/len(_chars))
    return ''.join(reversed(array))


class PUID:
    # Namespaces:
    # for INV, MAGIC, ITEMS, and CHARS
    # 0 - RootIdentifier (4 chars)
    # 0 - NameIdentifier (passed as name) (4 chars)

    # Namespaces for libinventory system
    # 0 - RandomIdentifier (8 chars)

    # Namespace creation:
    # 0 - Namespace name (4 chars)
    def __init__(self, name: Union[str, int, Iterable[Union[str, PUID]]], namespace: PUID = None, version: Literal[1, 2, 3, 4, 'int0', 'int1'] = 1):
        _min4 = 46656
        _max4 = 1679615
        _min8 = 221073919720733357899776
        _max8 = 7958661109946400884391935
        self._multiple_ns = None
        self._ns_root = None
        if version == 1:
            if namespace is None:
                raise TypeError(
                    f"Expecting namespace to be PUID, but got {type(namespace)}")
            self._ns_root = namespace
            _ns = _puid_compiled.sub('', name.lower())
            self._ns_body = sum(
                _hs_256((namespace.body+_ns).encode()).digest())
            _onsbd = self._ns_body
            while self._ns_body < _min4:
                self._ns_body *= 2
            while self._ns_body > _max4:
                self._ns_body -= int(_onsbd/4)
            self._ns_body = _int_to_spuid(self._ns_body)
            self._name = name
        elif version == 2:
            self._ns_root = None
            _min = 221073919720733357899776
            _max = 7958661109946400884391935
            _nran = SystemRandom((_min+_max)*500)
            nspace = _nran.randint(_min, _max)
            self._ns_body = _int_to_spuid(nspace)
        elif version == 3:
            _ns = _puid_compiled.sub('', name.lower())
            self._ns_body = sum(_hs_256((_ns).encode()).digest())
            _onsbd = self._ns_body
            self._name = name
            while self._ns_body < _min4:
                self._ns_body *= 2
            while self._ns_body > _max4:
                self._ns_body -= int(_onsbd/4)
            self._ns_body = _int_to_spuid(self._ns_body)
        elif version == 4:
            if not hasattr(name, '__iter__') and isinstance(name, str):
                raise TypeError("Iterable[PUID] is required.")
            self._ns_root: PUID = name[0]
            self._multiple_ns: Iterable[PUID] = name[:-1]
            if not isinstance(name[-1], str):
                raise TypeError("The last of PUID should be int.")
            _ns = name[-1]
            _ns = _puid_compiled.sub('', _ns.lower())
            self._ns_body = sum(_hs_256((_ns).encode()).digest())
            _onsbd = self._ns_body
            self._name = name
            while self._ns_body < _min8:
                self._ns_body *= 2
            while self._ns_body > _max8:
                self._ns_body -= int(_onsbd/4)
            self._ns_body = _int_to_spuid(self._ns_body)
            self._puid = '-'.join(a.body.upper()
                                  for a in self._multiple_ns)+'-'+self._ns_body.upper()
        elif version == 'int0':
            if not isinstance(name, int):
                raise TypeError('Version5: Name parameter should be integer.')
            name: int = name
            self._ns_body = _int_to_spuid(name)
        elif version == 'int1':
            self._ns_root: PUID = name[0]
            self._multiple_ns: Iterable[PUID] = name[:-1]
            if not isinstance(name[-1], int):
                raise TypeError("The last of PUID should be int.")
            self._ns_body = _int_to_spuid(name[-1])
            self._puid = '-'.join(a.body.upper()
                                  for a in self._multiple_ns)+'-'+self._ns_body.upper()
        else:
            raise Exception("Undefined version: %s" % version)
        if self._ns_root is None:
            self._puid = self._ns_body.upper()
            return
        self._ns_body: str = self._ns_body
        self._puid = (self._ns_root.body+'-' +
                      self._ns_body).upper() if version not in (4, 'int1') else self._puid

    @property
    def root(self):
        return self._ns_root

    @property
    def version(self):
        return self._version

    @property
    def as_int(self):
        return int(_puid_compiled.sub('', str(self).lower()), 36)

    @property
    def body(self):
        return self._ns_body

    @property
    def fields(self):
        return tuple(int()) if self._multiple_ns is not None else (int(self),)

    @classmethod
    def make_namespace(cls, name: str):
        return cls(name, version=3)

    @classmethod
    def make_random(cls):
        return cls('NONE', version=2)

    @classmethod
    def from_int(cls, data: int):
        """"Warning! This classmethod returns 1-field PUID."""
        return cls(data, version='int0')

    @classmethod
    def from_fields(cls, data: Iterable[int]):
        x = [cls(a, version='int0') for a in data[:-1]]
        x.append(data[-1])
        return cls(x, version='int1')

    def __repr__(self):
        return f"{type(self).__name__}({self._puid})"

    def __str__(self):
        return self._puid

    def __int__(self):
        return self.as_int

    def __eq__(self, other):
        if isinstance(other, PUID):
            return self._puid == other._puid
        if isinstance(other, str):
            return self._puid == other
        if isinstance(other, int):
            return int(self) == other

# Below here is mark of 'included' stuff from RimuEirnarn/GTRNv2


class AssignedProtocolError(Exception):
    """A prefix protocol is already defined"""


class Protocol:
    """Base Protocol class handler."""
    _prefix = {}

    def __init_subclass__(cls, /, prefix, final=True):
        if prefix in Protocol._prefix:
            raise AssignedProtocolError(f"{prefix} is already assigned")

        def finaliser(*args, **kwargs):
            raise NotImplementedError
        Protocol._prefix[prefix] = cls
        if final is True:
            cls.__init_subclass__ = finaliser

    def __new__(cls, url: str):
        prefix, _, path = url.partition("://")
        if prefix in cls._prefix:
            x = super().__new__(cls._prefix[prefix])
            return x
        return super().__new__(cls)

    def __init__(self, url: str):
        self._url = url
        self._splitted = urlsplit(url)
        self._path = url.partition("://")[2]

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._url}>"

    def __str__(self):
        return self._to_string()

    def _to_string(self):
        return self._url


class Project(Protocol, prefix='project', final=False):
    def read_path(self):
        path = getpath()
        if path[-1] == '/':
            return path[:-1]+self._path
        elif self._path[0] != '/':
            return path+'/'+self._path
        return path+self._path

    def __str__(self) -> str:
        return self.read_path()

    _to_string = read_path


class AssetPath(Protocol, prefix='asset', final=False):
    def __init_subclass__(cls, /, prefix, final=True):
        def read_path(self):
            path = getpath()
            if path[-1] != '/':
                path += '/'
            if self._path[0] == '/':
                self._path = self._path[1:]
            return path+prefix+'/'+self._path
        cls.read_path = read_path
        return super().__init_subclass__(prefix, final)

    def read_path(self):
        path = getpath()
        if path[-1] != '/':
            path += '/'
        if self._path[0] == '/':
            self._path = self._path[1:]
        return path+'asset/'+self._path


class DataPath(Protocol, prefix='data', final=False):
    def __init_subclass__(cls, /, prefix, final=True):
        def read_path(self):
            path = getpath()
            if path[-1] != '/':
                path += '/'
            if self._path[0] == '/':
                self._path = self._path[1:]
            return path+'data/'+prefix+'/'+self._path
        cls.read_path = read_path
        return super().__init_subclass__(prefix, final)

    def read_path(self):
        path = getpath()
        if path[-1] != '/':
            path += '/'
        if self._path[0] == '/':
            self._path = self._path[1:]
        return path+'data/'+self._path


def getpath():
    nf = 0
    file_dir = realpath(__file__+'/../')
    if system() == 'Linux':
        if not exists(expanduser("~/.config/RPGSample")):
            return file_dir
        return expanduser("~/.config/RPGSample")
    if not exists(expanduser("~/.RPGSample")):
        return file_dir
    return expanduser("~/.RPGSample")

# complete include from RimuEirnarn/GTRNv2
# Copyright (c) 2022 RimuEirnarn and Archaent Nakasaki. All rights reserved


def parse(data: Mapping[str, ConfigParser, Any], into: Literal['yaml', 'ini'] = 'ini', parse_hook=None, **kwargs):
    # Note: dr is default-readable (ini)
    indent = 2
    default_flow_style = False
    if not 'indent' in kwargs:
        kwargs['indent'] = indent
    if not 'default_flow_style' in kwargs:
        kwargs['default_flow_style'] = default_flow_style
    if into not in ('yaml', 'ini'):
        into = 'ini'

    if into == 'yaml':
        return yaml_parse(data, **kwargs)
    if into == 'ini':
        kwargs.pop('indent')
        kwargs.pop('default_flow_style')
        self: ConfigParser = data
        if not isinstance(data, ConfigParser):
            self = ConfigParser(data)
        if parse_hook is not None:
            parse_hook(self, data)
        pseudo_file = StringIO()
        self.write(pseudo_file)
        return pseudo_file.getvalue()
    return ''


def load(data: Union[str, IO], type: Literal['json', 'ini'] = 'ini', **kwargs):
    a = data
    if into not in ('yaml', 'ini'):
        into = 'ini'

    if hasattr(data, 'read'):
        # IO operation.
        a = data.read()

    if type == 'ini':
        x = ConfigParser()
        x.read_string(a)
        return x
    if type == 'yaml':
        return yaml_load(a)
