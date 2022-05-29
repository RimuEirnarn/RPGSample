from configparser import ConfigParser
from dataclasses import dataclass
from posixpath import exists, realpath, splitext
from typing import Any, Literal, Mapping, Union

from libpostreq import yaml_installed
from libshared import Project, load, parse


@dataclass(init=True)
class Character:
    name: str
    gender: str
    race: str
    age: int

    def __repr__(self):
        return f"{type(self).__name__}({self.name})"
