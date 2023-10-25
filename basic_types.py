# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from types import SimpleNamespace
from typing import Optional, NamedTuple


class MecabParsedToken(NamedTuple):
    word: str
    headword: str
    katakana_reading: Optional[str]
    part_of_speech: Optional[str]
    inflection: Optional[str]


class VerySimpleNamespace(SimpleNamespace):
    def __iter__(self):
        return iter(self.__dict__.values())


Separators = SimpleNamespace(
    component="<ajt__component_separator>",
    node="<ajt__node_separator>",
    footer="<ajt__footer>",
)

Components = VerySimpleNamespace(
    word='%m',
    headword='%f[6]',
    katakana_reading='%f[7]',
    part_of_speech='%f[0]',
    inflection_type='%f[5]',
)


def main():
    for k in Components:
        print(k)


if __name__ == '__main__':
    main()
