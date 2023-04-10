# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

__all__ = ['to_katakana', 'to_hiragana', 'is_kana_str', 'is_inflected']

from typing import Optional

# Define characters
HIRAGANA = "ぁあぃいぅうぇえぉおかがか゚きぎき゚くぐく゚けげけ゚こごこ゚さざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"
KATAKANA = "ァアィイゥウェエォオカガカ゚キギキ゚クグク゚ケゲケ゚コゴコ゚サザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"

# Translation tables
KATAKANA_TO_HIRAGANA = str.maketrans(KATAKANA, HIRAGANA)
HIRAGANA_TO_KATAKANA = str.maketrans(HIRAGANA, KATAKANA)


def to_hiragana(kana):
    return kana.translate(KATAKANA_TO_HIRAGANA)


def to_katakana(kana):
    return kana.translate(HIRAGANA_TO_KATAKANA)


def is_kana_char(char: str) -> bool:
    return (
            char in HIRAGANA
            or char in KATAKANA
            or char == 'ー'
    )


def is_kana_str(word: str) -> bool:
    return all(map(is_kana_char, word))


def longest_kana_suffix(word: str) -> Optional[str]:
    for i in range(len(word)):
        if is_kana_str(substr := word[i:]):
            return substr


def is_inflected(headword: str, reading: str) -> bool:
    """
    Test if a reading of a verb/adjective is inflected, e.g. 臭くて, 臭かった.
    A reading is inflected if the word's kana ending isn't equal to the reading's ending.
    """
    return bool(
        (kana_suffix := longest_kana_suffix(headword))
        and to_katakana(kana_suffix) != to_katakana(reading[-len(kana_suffix):])
    )


def main():
    assert to_hiragana('<div>オープンソース形態素解析エンジンです。Test 😀') == '<div>おーぷんそーす形態素解析えんじんです。Test 😀'
    assert to_katakana('お前はもう死んでいる。') == 'オ前ハモウ死ンデイル。'
    assert is_kana_str('ひらがなカタカナ') is True
    assert is_kana_str('ニュース') is True
    assert is_kana_str('故郷は') is False
    assert longest_kana_suffix("分かる") == "かる"
    assert longest_kana_suffix("綺麗") is None
    assert is_inflected("分かる", "わかる") is False
    assert is_inflected("臭い", "くさい") is False
    assert is_inflected("分かる", "わかった") is True
    assert is_inflected("綺麗", "きれい") is False
    print("Ok.")


if __name__ == '__main__':
    main()
