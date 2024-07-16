# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import dataclasses
import functools
import re
from collections.abc import Iterable
from typing import Optional

try:
    from .basic_mecab_controller import BasicMecabController
    from .basic_types import (
        Components,
        Inflection,
        MecabParsedToken,
        PartOfSpeech,
        Separators,
    )
    from .format import format_output
    from .kana_conv import is_kana_str, to_hiragana, to_katakana
    from .replace_mistakes import replace_mistakes
except ImportError:
    from basic_mecab_controller import BasicMecabController
    from basic_types import (
        Components,
        Inflection,
        MecabParsedToken,
        PartOfSpeech,
        Separators,
    )
    from format import format_output
    from kana_conv import is_kana_str, to_hiragana, to_katakana
    from replace_mistakes import replace_mistakes


# Mecab
##########################################################################


def escape_text(text: str) -> str:
    """Strip characters that trip up mecab."""
    text = text.replace("\n", " ")
    text = text.replace("\uff5e", "~")
    text = re.sub(r"<[^<>]+>", "", text)
    text = re.sub(r"\[sound:[^]]+]", "", text)
    text = re.sub(r"\[\[type:[^]]+]]", "", text)
    return text.strip()


class MecabController(BasicMecabController):
    _mecab_args: list[str] = [
        "--node-format=" + Separators.component.join(component for component in Components) + Separators.node,
        "--unk-format=" + Components.word + Separators.node,
        "--eos-format=" + Separators.footer,
    ]

    def __init__(
        self,
        mecab_cmd: Optional[list[str]] = None,
        mecab_args: Optional[list[str]] = None,
        verbose: bool = False,
        cache_max_size: int = 1024,
    ) -> None:
        super().__init__(
            mecab_cmd=mecab_cmd,
            mecab_args=(mecab_args or self._mecab_args),
            verbose=verbose,
        )
        self.translate = functools.lru_cache(maxsize=cache_max_size)(lambda expr: tuple(self._translate(expr)))

    def _translate(self, expr: str) -> Iterable[MecabParsedToken]:
        """Returns a parsed token for each word in expr."""
        expr = escape_text(expr)
        for section in self.run(expr).split(Separators.node):
            if section == Separators.footer:
                break
            # ignore empty sections (can be at the end of a node)
            if section:
                components = section.split(Separators.component)
                try:
                    word, headword, katakana_reading, part_of_speech, inflection = components
                except ValueError:
                    # unknown to mecab, gave the same word back
                    word, headword, katakana_reading = components * 3
                    part_of_speech, inflection = None, None

                if is_kana_str(word) or to_katakana(word) == to_katakana(katakana_reading):
                    katakana_reading = None

                token = MecabParsedToken(
                    word=word,
                    headword=headword,
                    katakana_reading=(katakana_reading or None),
                    part_of_speech=PartOfSpeech(part_of_speech or None),
                    inflection_type=Inflection(inflection or None),
                )
                for token in replace_mistakes(token):
                    if self._verbose:
                        print(*dataclasses.astuple(token), sep="\t")
                    yield token

    def reading(self, expr: str) -> str:
        """Formats furigana using Anki syntax, e.g. 野獣[やじゅう]の 様[よう]な 男[おとこ]."""
        substrings = []
        for out in self.translate(expr):
            substrings.append(
                format_output(out.word, to_hiragana(out.katakana_reading)) if out.katakana_reading else out.word
            )
        return "".join(substrings).strip()


def main():
    mecab = MecabController()

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
        "Lorem ipsum dolor sit amet. ",
        "Съешь ещё этих мягких французских булок, да выпей же чаю.",
        "粗末な家に住んでいる",
        "向けていた目",
        "軽そうに見える",
        "相合い傘",
    )
    for idx, expr in enumerate(try_expressions):
        print(f"expr  #{idx:02d}: {mecab.reading(expr)}")
        for jdx, token in enumerate(mecab.translate(expr)):
            print(f"token #{jdx:02d}: {token}")
        print("." * 20)


if __name__ == "__main__":
    main()
