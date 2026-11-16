# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import re

# Define characters
HIRAGANA = "ぁあぃいぅうぇえぉおかがか゚きぎき゚くぐく゚けげけ゚こごこ゚さざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"
KATAKANA = "ァアィイゥウェエォオカガカ゚キギキ゚クグク゚ケゲケ゚コゴコ゚サザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"

# Translation tables
KATAKANA_TO_HIRAGANA = str.maketrans(KATAKANA, HIRAGANA)
HIRAGANA_TO_KATAKANA = str.maketrans(HIRAGANA, KATAKANA)

RE_ONE_MORA = re.compile(r".゚?[ァィゥェォャュョぁぃぅぇぉゃゅょ]?")
# Reuse the exact character lists, including ゚, rather than accepting whole Unicode blocks.
# A compiled match avoids per-character Python calls without retaining words in a cache.
RE_KANA_STR = re.compile(f"[{re.escape(HIRAGANA + KATAKANA + 'ー')}]+")


def kana_to_moras(kana: str) -> list[str]:
    return re.findall(RE_ONE_MORA, kana)


def to_hiragana(kana: str) -> str:
    return kana.translate(KATAKANA_TO_HIRAGANA)


def to_katakana(kana: str) -> str:
    return kana.translate(HIRAGANA_TO_KATAKANA)


def is_hiragana_char(char: str) -> bool:
    if len(char) != 1:
        raise ValueError("string must contain one character")
    return char in HIRAGANA or char == "ー"


def is_katakana_char(char: str) -> bool:
    if len(char) != 1:
        raise ValueError("string must contain one character")
    return char in KATAKANA or char == "ー"


def is_kana_char(char: str) -> bool:
    if len(char) != 1:
        raise ValueError("string must contain one character")
    return char in HIRAGANA or char in KATAKANA or char == "ー"


def is_hiragana_str(word: str) -> bool:
    if not word:
        raise ValueError("string can't be empty")
    return all(map(is_hiragana_char, word))


def is_katakana_str(word: str) -> bool:
    if not word:
        raise ValueError("string can't be empty")
    return all(map(is_katakana_char, word))


def is_kana_str(word: str) -> bool:
    """Return whether a nonempty word contains only supported kana, raising ValueError for empty input."""
    if not word:
        raise ValueError("string can't be empty")
    # fullmatch() also rejects trailing newlines, unlike a pattern ending with $.
    # https://docs.python.org/3/library/re.html#re.Pattern.fullmatch
    return RE_KANA_STR.fullmatch(word) is not None


def main() -> None:
    """Verify sample kana conversions and character classification results."""
    assert (
        to_hiragana("<div>オープンソース形態素解析エンジンです。Test 😀")
        == "<div>おーぷんそーす形態素解析えんじんです。Test 😀"
    )
    assert to_katakana("お前はもう死んでいる。") == "オ前ハモウ死ンデイル。"
    assert to_katakana("いまり") == "イマリ"
    assert to_katakana(HIRAGANA) == KATAKANA
    assert is_kana_str("ひらがなカタカナ") is True
    assert is_kana_str("ニュース") is True
    assert is_kana_str("故郷は") is False
    print("Ok.")


if __name__ == "__main__":
    main()
