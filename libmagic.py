from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
from posixpath import exists, realpath, splitext
from typing import Any, Literal, Mapping, Union

from libpostreq import yaml_installed
from libshared import DataPath, load, parse

# Author note: Yes, i'm copy-pasting this module.


class MagicPath(DataPath, prefix='magic'):
    def read(self):
        x = splitext(self.read_path())
        if x[1] == '.yaml':
            a = load(self.read_path())
            return MagicType(a['name'], a['type'], a['speciality'])
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
            return MagicType(name, type, speciality)
        raise Exception("Unrecognized extention: %s" % x[1][1:])

    def save(self, magic: MagicType):
        x = splitext(self.read_path())
        if x[1] == '.yaml':
            a = {
                "name": magic.name,
                "type": magic.type,
                "speciality": magic.speciality
            }
            with open(self.read_path(), 'w') as f:
                return f.write(parse(a, 'yaml'))
        if x[1] == '.ini':
            a = ConfigParser({
                "name": magic.name,
                "type": magic.type,
            })
            a.add_section("speciality")
            a['speciality'].update(magic.speciality)
            with open(self.read_path(), 'w') as f:
                return f.write(parse(a, 'ini'))
        raise Exception("Unrecognized extention: %s" % x[1][1:])


@dataclass(init=True, repr=True)
class MagicType:
    name: str
    type: str
    # Resistance should be defined in speciality
    speciality: Mapping[str, Union[str, int, bool]]

    def save(self):
        a = MagicPath(
            f"magic://{self.type}/{self.name}.{'yaml' if yaml_installed is True else 'ini'}")
        a.save(self)

    @classmethod
    def load(self):
        a = MagicPath(
            f"magic://{self.type}/{self.name}.{'yaml' if yaml_installed is True else 'ini'}")
        return a.read()
