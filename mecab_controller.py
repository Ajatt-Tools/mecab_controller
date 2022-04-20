# Japanese support add-on for Anki 2.1
# Copyright (C) 2021  Ren Tatsumoto. <tatsu at autistici.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Parts of this file were based on Japanese Support:
# https://github.com/ankitects/anki-addons/blob/main/code/japanese/reading.py
#
# Any modifications to this file must keep this entire header intact.

import os
import re
import subprocess
import sys
from typing import List, Optional, NamedTuple, Iterable

from .format import format_output
from .kana_conv import to_hiragana, is_kana_word, to_katakana

isMac = sys.platform.startswith("darwin")
isWin = sys.platform.startswith("win32")

SUPPORT_DIR = os.path.join(os.path.dirname(__file__), "support")

if not os.path.isfile(mecabrc := os.path.join(SUPPORT_DIR, "mecabrc")):
    with open(mecabrc, 'w') as f:
        # create mecabrc if it doesn't exist
        f.write("")

if isWin:
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    si = None


def normalize_for_platform(popen: List[str]) -> List[str]:
    if isWin:
        popen = [os.path.normpath(x) for x in popen]
    return popen


def find_executable(name: str) -> str:
    from distutils.spawn import find_executable as find
    if cmd := find(name):
        return cmd
    else:
        cmd = os.path.join(SUPPORT_DIR, name)
        if isWin:
            cmd += '.exe'
        elif isMac:
            cmd += '.mac'
        else:
            cmd += '.lin'
        if not isWin:
            os.chmod(cmd, 0o755)
        return cmd


# Mecab
##########################################################################

class ParsedToken(NamedTuple):
    word: str
    headword: str
    katakana_reading: Optional[str]
    part_of_speech: Optional[str]
    inflection: Optional[str]

    @property
    def hiragana_reading(self) -> str:
        return to_hiragana(self.katakana_reading)


class BasicMecabController:
    __mecab_cmd = [
        find_executable('mecab'),
        '-d', SUPPORT_DIR,
        '-r', os.path.join(SUPPORT_DIR, "mecabrc"),
        '-u', os.path.join(SUPPORT_DIR, "user_dic.dic"),
    ]

    def __init__(self, mecab_cmd: List[str] = None, mecab_args: List[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mecab_cmd = mecab_cmd if mecab_cmd else self.__mecab_cmd
        mecab_args = mecab_args if mecab_args else []
        self._mecab_cmd = normalize_for_platform(mecab_cmd + mecab_args)

        os.environ['DYLD_LIBRARY_PATH'] = SUPPORT_DIR
        os.environ['LD_LIBRARY_PATH'] = SUPPORT_DIR
        print('mecab cmd:', self._mecab_cmd)

    def run(self, expr: str) -> str:
        expr = expr.encode('utf-8', 'ignore') + b'\n'
        try:
            proc = subprocess.Popen(
                self._mecab_cmd,
                bufsize=-1,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=si,
            )
        except OSError:
            raise Exception("Please ensure your Linux system has 64 bit binary support.")

        try:
            outs, errs = proc.communicate(expr, timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()

        return outs.rstrip(b'\r\n').decode('utf-8', 'replace')


class MecabController(BasicMecabController):
    _add_mecab_args = [
        # Format: word,headword,katakana reading,part of speech,inflection
        '--node-format=%m,%f[6],%f[7],%f[0],%f[5]\t',
        '--unk-format=%m\t',
        '--eos-format=\n',
    ]

    def __init__(self, verbose: bool = False, *args, **kwargs):
        super().__init__(mecab_args=self._add_mecab_args, *args, **kwargs)
        self._verbose = verbose

    @staticmethod
    def escape_text(text: str) -> str:
        """Strip characters that trip up mecab."""
        text = text.replace("\n", " ")
        text = text.replace('\uff5e', "~")
        text = re.sub(r'<[^<>]+>', '', text)
        text = re.sub(r"\[sound:[^]]+]", "", text)
        text = re.sub(r"\[\[type:[^]]+]]", "", text)
        return text.strip()

    def translate(self, expr: str) -> Iterable[ParsedToken]:
        """ Returns a parsed token for each word in expr. """
        expr = self.escape_text(expr)

        for section in self.run(expr).split('\t'):
            if section:
                try:
                    word, headword, katakana_reading, part_of_speech, inflection = section.split(',')
                except ValueError:
                    word, headword, katakana_reading = (section,) * 3
                    part_of_speech, inflection = None, None

                if is_kana_word(word) or to_katakana(word) == to_katakana(katakana_reading):
                    katakana_reading = None

                if self._verbose:
                    print(word, katakana_reading, headword, part_of_speech, inflection, sep='\t')
                yield ParsedToken(
                    word=word,
                    headword=headword,
                    katakana_reading=katakana_reading,
                    part_of_speech=part_of_speech,
                    inflection=inflection
                )

    def reading(self, expr: str) -> str:
        substrings = []
        for out in self.translate(expr):
            substrings.append(
                format_output(out.word, to_hiragana(out.katakana_reading))
                if out.katakana_reading
                else out.word
            )
        return ''.join(substrings).strip()
