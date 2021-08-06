# -*- coding: utf-8 -*-

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
from typing import List, Optional, Container

from .compound_furigana import break_compound_furigana
from .kana_conv import to_hiragana

isMac = sys.platform.startswith("darwin")
isWin = sys.platform.startswith("win32")

SUPPORT_DIR = os.path.join(os.path.dirname(__file__), "support")

if not os.path.isfile(mecabrc := os.path.join(SUPPORT_DIR, "mecabrc")):
    with open(mecabrc, 'w') as f:
        # create mecabrc if doesn't exist
        f.write("")

if isWin:
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    si = None


def strip_some_html(s: str) -> str:
    # strip html, but keep newlines and <b></b> tags to let Targeted Sentence Cards formatting through
    return re.sub(r'<(?!br|b|/b)[^<>]*?>', '', s)


def escape_text(text: str) -> str:
    # strip characters that trip up mecab
    text = text.replace("\n", " ")
    text = text.replace(u'\uff5e', "～")
    text = strip_some_html(text)
    return text


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

class BasicMecabController(object):
    def __init__(self, mecab_cmd: List[str]):
        self._mecab_cmd = normalize_for_platform(mecab_cmd)
        os.environ['DYLD_LIBRARY_PATH'] = SUPPORT_DIR
        os.environ['LD_LIBRARY_PATH'] = SUPPORT_DIR
        print('mecab cmd:', self._mecab_cmd)

    def run(self, expr: str) -> str:
        expr = escape_text(expr).encode('utf-8', "ignore") + b'\n'

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

        return outs.rstrip(b'\r\n').decode('utf-8', "replace")


class MecabController(BasicMecabController):
    _mecab_cmd = [
        find_executable('mecab'),
        '--node-format=%m[%f[7]] ',
        '--unk-format=%m[] ',
        '--eos-format=\n',
        '-d', SUPPORT_DIR,
        '-r', os.path.join(SUPPORT_DIR, "mecabrc"),
        '-u', os.path.join(SUPPORT_DIR, "user_dic.dic")
    ]

    def __init__(self):
        super().__init__(self._mecab_cmd)

    def reading(self, expr: str, skip_words: Optional[Container[str]]) -> str:
        expr = self.run(expr)
        out = []

        for node in expr.split():
            try:
                (kanji, reading) = re.match(r'(.+)\[(.*)]', node).groups()
            except AttributeError:
                sys.stderr.write(
                    "Unexpected output from mecab.\n"
                    "Perhaps your Windows username contains non-Latin text?: %s\n" % repr(expr)
                )
                return ""

            # couldn't generate or no kanji
            if not reading or kanji == reading or kanji == to_hiragana(reading):
                out.append(kanji)
                continue

            # convert reading to hiragana
            reading = to_hiragana(reading)

            # ended up the same
            if reading == kanji:
                out.append(kanji)
                continue

            # skip expressions
            if skip_words and kanji in skip_words:
                out.append(kanji)
                continue

            # strip matching characters and beginning and end of reading and kanji
            # reading should always be at least as long as the kanji
            place_l = 0
            place_r = 0
            for i in range(1, len(kanji)):
                if kanji[-i] != reading[-i]:
                    break
                place_r = i
            for i in range(0, len(kanji) - 1):
                if kanji[i] != reading[i]:
                    break
                place_l = i + 1
            if place_l == 0:
                if place_r == 0:
                    out_expr = " %s[%s]" % (kanji, reading)
                else:
                    out_expr = " %s[%s]%s" % (kanji[:-place_r], reading[:-place_r], reading[-place_r:])

                out_expr = break_compound_furigana(out_expr)
            else:
                if place_r == 0:
                    out_expr = "%s %s[%s]" % (reading[:place_l], kanji[place_l:], reading[place_l:])
                else:
                    out_expr = "%s %s[%s]%s" % (
                        reading[:place_l], kanji[place_l:-place_r],
                        reading[place_l:-place_r], reading[-place_r:],
                    )

            out.append(out_expr)

        return ''.join(out).strip().replace("< br>", "<br>")
