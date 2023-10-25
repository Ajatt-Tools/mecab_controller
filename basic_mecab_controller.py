# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import subprocess
import sys

IS_MAC = sys.platform.startswith("darwin")
IS_WIN = sys.platform.startswith("win32")
SUPPORT_DIR = os.path.join(os.path.dirname(__file__), "support")

if not os.path.isfile(mecabrc := os.path.join(SUPPORT_DIR, "mecabrc")):
    with open(mecabrc, 'w') as f:
        # create mecabrc if it doesn't exist
        f.write("")

if IS_WIN:
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    si = None


def find_best_dic_dir():
    """
    If the user has mecab-ipadic-neologd (or mecab-ipadic) installed, pick its system dictionary.
    """
    possible_locations = (
        '/usr/lib/mecab/dic/mecab-ipadic-neologd',
        '/usr/lib/mecab/dic/ipadic',
        '/usr/local/lib/mecab/dic/ipadic'  # for `brew install mecab-ipadic`
    )
    for directory in possible_locations:
        if os.path.isdir(directory):
            return directory
    return SUPPORT_DIR


def find_executable(name: str) -> str:
    """
    If possible, use the executable installed in the system.
    Otherwise, use the executable provided in the support directory.
    """
    from distutils.spawn import find_executable as find
    if cmd := find(name):
        return cmd
    else:
        cmd = os.path.join(SUPPORT_DIR, name)
        if IS_WIN:
            cmd += '.exe'
        elif IS_MAC:
            cmd += '.mac'
        else:
            cmd += '.lin'
        if not IS_WIN:
            os.chmod(cmd, 0o755)
        return cmd


def normalize_for_platform(popen: list[str]) -> list[str]:
    if IS_WIN:
        popen = [os.path.normpath(x) for x in popen]
    return popen


class BasicMecabController:
    _mecab_cmd = [
        find_executable('mecab'),
        '--dicdir='
        + find_best_dic_dir(),
        '--rcfile='
        + os.path.join(SUPPORT_DIR, "mecabrc"),
        '--userdic='
        + os.path.join(SUPPORT_DIR, "user_dic.dic"),
    ]

    def __init__(self, mecab_cmd: list[str] = None, mecab_args: list[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mecab_cmd = normalize_for_platform((mecab_cmd or self._mecab_cmd) + (mecab_args or []))
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


def main():
    mecab = BasicMecabController()

    try_expressions = (
        "カリン、自分でまいた種は自分で刈り取れ",
        "昨日、林檎を2個買った。",
        "真莉、大好きだよん＾＾",
        "彼２０００万も使った。",
        "彼二千三百六十円も使った。",
        "千葉",
        "昨日すき焼きを食べました",
        "二人の美人",
        "詳細はお気軽にお問い合わせ下さい。",
        "Lorem ipsum dolor sit amet. Съешь ещё этих мягких французских булок, да выпей же чаю.",
    )

    for expr in try_expressions:
        print(mecab.run(expr))


if __name__ == '__main__':
    main()
