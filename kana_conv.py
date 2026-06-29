# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import re

# Define characters
HIRAGANA = "ぁあぃいぅうぇえぉおかがか゚きぎき゚くぐく゚けげけ゚こごこ゚さざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"
KATAKANA = "ァアィイゥウェエォオカガカ゚キギキ゚クグク゚ケゲケ゚コゴコ゚サザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"

# Translation tables
KATAKANA_TO_HIRAGANA = str.maketrans(KATAKANA, HIRAGANA)
HIRAGANA_TO_KATAKANA = str.maketrans(HIRAGANA, KATAKANA)

RE_ONE_MORA = re.compile(r".゚?[ァィゥェォャュョぁぃぅぇぉゃゅょ]?")


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
    if not word:
        raise ValueError("string can't be empty")
    return all(map(is_kana_char, word))


def main() -> None:
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
