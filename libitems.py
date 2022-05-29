"""Lib items"""

from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
from posixpath import exists, realpath, splitext
from typing import Any, Literal, Mapping, Union

from libpostreq import yaml_installed
from libshared import DataPath, load, parse


class ItemPath(DataPath, prefix='items'):
    def read(self):
        x = splitext(self.read_path())
        if x[1] == '.yaml':
            a = load(self.read_path())
            return ItemType(a['name'], a['type'], a['speciality'])
        if x[1] == '.ini':
            a = load(self.read_path())
            fs = 0
            c = [False]*3
            if 'speciality' not in a:
                fs = 1
            for i, b in enumerate(('name', 'type', 'speciality')):
                if b in a['DEFAULTS']:
                    c[i] = True
            if fs == 1 and c[2] is False:
                raise Exception(
                    "Expecting speciality in outer section or in default section.")
            c[2] = True
            if sum(c) <= 2:
                raise Exception("The expected arguments are minimal")
            name = a['DEFAULTS']['name']
            type = a['DEFAULTS']['type']
            speciality = a['DEFAULTS']['speciality'] if fs == 0 else a['speciality']
            return ItemType(name, type, speciality)
        raise Exception("Unrecognized extention: %s" % x[1][1:])

    def save(self, item: ItemType):
        x = splitext(self.read_path())
        if x[1] == '.yaml':
            a = {
                "name": item.name,
                "type": item.type,
                "speciality": item.speciality
            }
            with open(self.read_path(), 'w') as f:
                return f.write(parse(a, 'yaml'))
        if x[1] == '.ini':
            a = ConfigParser({
                "name": item.name,
                "type": item.type,
            })
            a.add_section("speciality")
            a['speciality'].update(item.speciality)
            with open(self.read_path(), 'w') as f:
                return f.write(parse(a, 'ini'))
        raise Exception("Unrecognized extention: %s" % x[1][1:])


@dataclass(init=True, repr=True)
class ItemType:
    name: str
    type: str
    speciality: Mapping[str, Union[str, int, bool]]

    def save(self):
        a = ItemPath(
            f"items://{self.type}/{self.name}.{'yaml' if yaml_installed is True else 'ini'}")
        a.save(self)

    @classmethod
    def load(self):
        a = ItemPath(
            f"items://{self.type}/{self.name}.{'yaml' if yaml_installed is True else 'ini'}")
        return a.read()
