"""Shared module for lib* module

This module is as its summary."""

from __future__ import annotations

__version__ = '0.0.1 [A1]'
__author__ = 'Archaent Nakasaki and RimuEirnarn'
__copyright__ = 'BSD 3-Clause'
__all__ = ['ConstCreator', 'PUID', 'make_uuid', 'RandomNamespace',
           'AssignedProtocolError', 'Protocol', "Project", 'AssetPath', 'DataPath', 'getpath']

from hashlib import sha256 as _hs_256
from io import StringIO
from os.path import exists, expanduser, realpath
from re import compile as _re_compile, escape as _re_escape
from secrets import SystemRandom
from string import punctuation
from typing import (IO, Any, Callable, Dict, Iterable, List, Literal, Mapping,
                    Union)
from urllib.parse import urlsplit, parse_qs
from uuid import UUID as system_UUID
from uuid import uuid5
from inspect import currentframe as _icf, getframeinfo as _igfi
from ast import parse as _astparse
from platform import system
from random import Random
from json import loads as json_loads
from warnings import warn
from configparser import ConfigParser

_uuid_max_int = 340282366920938463463374607431768211455
_puid_compiled = _re_compile('['+_re_escape(punctuation)+']')

# =================================================================

#                       Custom Exception

# =================================================================


class OperationFailed(Exception):
    """An error occured when executing certain function."""


class FallbackOperation(UserWarning):
    """A certain operation failed, use fallback instead."""

# ================================================================


def _cast(data: str):
    if data == 'yes' or data == 'on':
        return True
    if data == 'no' or data == 'off':
        return False
    if data == 'none':
        return None
    try:
        return json_loads(data)
    except Exception:
        return data


class ConstCreator:
    """Constant Creator"""
    _objects: Dict[str, ConstCreator] = {}

    def __new__(cls, name: str = None, value: Any = None):
        if name in ConstCreator._objects:
            return ConstCreator._objects[name]
        self = super().__new__(cls)
        ConstCreator._objects[name] = self
        return self

    def __init__(self, name: str = None, value=None, /, _Repr_Mode: Literal[1, 2, 3, 4] = 2):
        if name is None and value is None:
            caller = _igfi(_icf().f_back)  # Don't edit this part.
            if caller.code_context is not None:
                code = _astparse(caller.code_context[caller.index])
                name = code.body[0].targets[0].id
                value = f"Ref[{caller.function}.{name}]"
            else:
                code = None
                name = f'Constant-{len(self._objects)}'
                value = f"Ref[{name}]"
                # Black magic is done!
            del caller, code
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

    @property
    def value(self):
        """Value of constant"""
        return self._value

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__dict__['_reprf'] = [None, lambda self: f'Ref[{self._name}] -> {self._value}',
                                   lambda self: f"{self._name}",
                                   lambda self: f"{self._value}",
                                   lambda self: f'Const[{self._name}]']

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['_reprf']
        return d


_MISSING = ConstCreator()


class RODictProxy:
    """Read only dict object proxy"""
    def __init_subclass__(cls) -> None:
        raise Exception("Cannot subclass Readonly Dict Proxy object")

    def __init__(self, object: dict):
        self.__object = object

    def __getitem__(self, key):
        try:
            return self.__object[key]
        except KeyError:
            raise KeyError(key) from None

    def get(self, key, default=_MISSING):
        return self.__object.get(key, default)

    def items(self):
        return self.__object.items()

    def copy(self):
        return self.__object.copy()

    def __repr__(self):
        return repr(self.__object)


class percentage:
    """Percentage class.
    Doing self+VALUE will adjust self's value.
    So, do different thing."""

    def __init__(self, of: Union[int, float]):
        self._param = of
        self._hotparam = of/100

    def __call__(self, other: Union[int, float]) -> float:
        if not isinstance(other, (int, float)):
            raise TypeError("Expected integer or float (got %s)" %
                            type(other).__name__)
        return other * self._hotparam  # Fixing on live-calculate

    def __rshift__(self, other: Union[int, float]) -> float:
        return self(other)

    def __add__(self, other: Union[int, float, percentage]) -> percentage:
        if not isinstance(other, (int, float)):
            raise TypeError("Expected integer or float (got %s)" %
                            type(other).__name__)
        if isinstance(other, percentage):
            self._param += other._param
            self._hotparam = self._param/100
            return self
        self._param += other
        return self

    def __sub__(self, other: Union[int, float, percentage]) -> percentage:
        if not isinstance(other, (int, float)):
            raise TypeError("Expected integer or float (got %s)" %
                            type(other).__name__)
        if isinstance(other, percentage):
            self._param -= other._param
            self._hotparam = self._param/100
            return self
        self._param -= other
        return self

    def __radd__(self, other: Union[int, float]) -> Union[int, float]:
        return other + self(other)

    def __rsub__(self, other: Union[int, float]) -> Union[int, float]:
        return other - self(other)

    def __abs__(self):
        self._param = abs(self._param)
        self._hotparam = self._param/100
        return self

    def __neg__(self):
        self._param = -self._param
        self._hotparam = self._param/100
        return self

    def __repr__(self):
        return f"{self._param:.2f}%"


def make_uuid():
    return uuid5(RandomNamespace, ''.join(Random().choice(tuple('ABCDEEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrtuvwxyz')*5)))

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
    """To be deprecated"""
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
            self._puid = '-'.join((a.body.upper()
                                  for a in self._multiple_ns))+'-'+self._ns_body.upper()
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
# Also, edited in order to keep things good.


class AssignedProtocolError(Exception):
    """A prefix protocol is already defined"""


class Protocol:
    """Base Protocol class handler.
    You can use it like this:
    <protocol>://<path>?query=value#fragment
    Just, be aware that some protocol handlers may not accept query or fragment."""
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
        self._config = {a: (_cast(b[0].lower()) if len(b) == 1 else [_cast(
            c.lower()) for c in b]) for a, b in parse_qs(self._splitted.query).items()}
        self._roconfig = RODictProxy(self._config)
        # /path/to/dir?encoding=UTF-8 is a literal that not /path/to/dir and leaving query as config.
        self._path = url.partition(
            "://")[2].replace(self._splitted.fragment, '').replace('?'+self._splitted.query, '')

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._url}>"

    def __str__(self):
        return self._to_string()

    def _to_string(self):
        return self._url

    @property
    def config(self):
        """Config/query"""
        return self._roconfig


class Project(Protocol, prefix='project', final=False):
    """Project is project protocol handler."""
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
        if path[-1] == '/':
            return path[:-1]+self._path
        elif self._path[0] != '/':
            return path+'/'+self._path
        return path+self._path

    def __str__(self) -> str:
        return self.read_path()

    def exists(self) -> bool:
        return exists(self.read_path())

    _to_string = read_path


class AssetPath(Protocol, prefix='asset', final=False):
    """AssetPath is Asset protocol handler. You can get certain project's related stuff in asset directory."""
    def __init_subclass__(cls, /, prefix, final=True):
        def read_path(self):
            path = getpath()
            if path[-1] != '/':
                path += '/'
            if self._path[0] == '/':
                self._path = self._path[1:]
            return path+'asset/'+prefix+'/'+self._path
        cls.read_path = read_path
        return super().__init_subclass__(prefix, final)

    def read_path(self):
        path = getpath()
        if path[-1] != '/':
            path += '/'
        if self._path[0] == '/':
            self._path = self._path[1:]
        return path+'asset/'+self._path

    def exists(self) -> bool:
        return exists(self.read_path())


class DataPath(Protocol, prefix='data', final=False):
    """DataPath is the data protocol handler, contains items, etc.
    You can use like this:
    >>> DataPath("data://items/idk.cmp")"""
    def __init_subclass__(cls, /, prefix, compilable=True, default=0, final=True):
        if compilable is True:
            def read_path(self):
                path = getpath()
                _p = "data-source/"
                if self._config.get("compiled", False) is True:
                    _p = "data/"
                if path[-1] != '/':
                    path += '/'
                if self._path[0] == '/':
                    self._path = self._path[1:]
                return path+_p+prefix+'/'+self._path
        else:
            def read_path(self):
                path = getpath()
                _p = "data-source" if default == 0 else "data/"
                if path[-1] != '/':
                    path += '/'
                if self._path[0] == '/':
                    self._path = self._path[1:]
                return path+_p+prefix+'/'+self._path
        cls.read_path = read_path
        return super().__init_subclass__(prefix, final)

    def read_path(self):
        path = getpath()
        _p = 'data-source/'
        if self._config.get("compiled", False) is True:
            _p = 'data/'
        if path[-1] != '/':
            path += '/'
        if self._path[0] == '/':
            self._path = self._path[1:]
        return path+_p+self._path

    def exists(self) -> bool:
        return exists(self.read_path())

    @property
    def IsCompiled(self) -> bool:
        return self._config("compiled", False)


def getpath():
    """Return the App configuration/saved path (not in where this program is found... unless...)"""
    nf = 0
    file_dir = realpath(__file__+'/../')
    if system() == 'Linux':
        if not exists(expanduser("~/.config/RPGSample")):
            return file_dir
        return expanduser("~/.config/RPGSample")
    if not exists(expanduser("~/.RPGSample")):
        return file_dir
    return expanduser("~/.RPGSample")

# complete include from RimuEirnarn/GTRNv2 (It may not exists in public)
# Copyright (c) 2022 RimuEirnarn and Archaent Nakasaki. All rights reserved


def parse_data(obj: Mapping[str, Mapping[str, Any]], stream: IO = None, *args, **kwargs):
    data = StringIO()
    self = ConfigParser()
    self.read_dict(obj)
    self.write(data, True)
    if stream is None:
        return data.getvalue()
    if hasattr(stream, 'writable'):
        if stream.writable() is False:
            raise OperationFailed("The stream is not writable")
        try:
            return stream.write(data)
        except TypeError:
            warn("The stream only support bytes. Attempting to switch.",
                 FallbackOperation)
            return stream.write(data.encode())
    raise OperationFailed("The stream is not writable")


def load_data(obj: Union[str, bytes], **kwargs):
    if isinstance(obj, bytes):
        obj = obj.decode()
    if not kwargs.get('dict_type', None):
        del kwargs['dict_type']
    if not kwargs.get('defaults', None):
        del kwargs['defaults']

    self = ConfigParser(**kwargs)
    self.read_string(obj)
    a = {}
    for i in self.sections:
        a[i] = self[i]
    return a.copy()


def _main():
    const0 = ConstCreator("CONST", 10)
    p0 = percentage(50)
    uuid0 = make_uuid()
    _p0 = _puid_to_int('55H32F')
    _p1 = _int_to_spuid(_p0)
    _p2 = (_p0 == _puid_to_int(_p1))
    _p3 = PUID('Debug', None, 2)
    proto0 = Protocol("project://main.py")
    proto1 = Protocol("asset://image/main.png")
    proto2 = Protocol("data://items")
    path = getpath()
    return 0

# Will there be anything else?
