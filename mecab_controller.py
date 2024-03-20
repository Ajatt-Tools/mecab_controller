# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import re
from collections.abc import Iterable

try:
    from .basic_types import Components, Separators, MecabParsedToken, PartOfSpeech, Inflection
    from .format import format_output
    from .kana_conv import to_hiragana, is_kana_str, to_katakana
    from .basic_mecab_controller import BasicMecabController
except ImportError:
    from basic_types import Components, Separators, MecabParsedToken, PartOfSpeech, Inflection
    from format import format_output
    from kana_conv import to_hiragana, is_kana_str, to_katakana
    from basic_mecab_controller import BasicMecabController


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
    _add_mecab_args = [
        "--node-format=" + Separators.component.join(component for component in Components) + Separators.node,
        "--unk-format=" + Components.word + Separators.node,
        "--eos-format=" + Separators.footer,
    ]

    def __init__(self, mecab_cmd: list[str] = None, mecab_args: list[str] = None, verbose: bool = False):
        super().__init__(
            mecab_cmd=mecab_cmd,
            mecab_args=(mecab_args or self._add_mecab_args),
            verbose=verbose,
        )

    def translate(self, expr: str) -> Iterable[MecabParsedToken]:
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

                if self._verbose:
                    print(word, katakana_reading, headword, part_of_speech, inflection, sep="\t")
                yield MecabParsedToken(
                    word=word,
                    headword=headword,
                    katakana_reading=(katakana_reading or None),
                    part_of_speech=PartOfSpeech(part_of_speech or None),
                    inflection_type=Inflection(inflection or None),
                )

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
        "Lorem ipsum dolor sit amet. Съешь ещё этих мягких французских булок, да выпей же чаю.",
        "粗末な家に住んでいる",
        "向けていた目",
        "軽そうに見える",
        "相合い傘",
    )
    for expr in try_expressions:
        for token in mecab.translate(expr):
            print(token)
        print(mecab.reading(expr))
        print()


if __name__ == "__main__":
    main()
