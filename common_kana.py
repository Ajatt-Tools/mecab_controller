# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import typing

try:
    from .kana_conv import is_kana_str
    from .kana_conv import to_katakana as _
except ImportError:
    from kana_conv import is_kana_str
    from kana_conv import to_katakana as _


def find_common_suffix_length(string1: str, string2: str) -> int:
    suffix_length = 0
    for word_char, reading_char in zip(reversed(string1), reversed(string2)):
        if _(word_char) != _(reading_char):
            break
        suffix_length += 1
    return suffix_length


class SourceWord(typing.NamedTuple):
    word: str
    reading: str


def extend_stem_reading(source: SourceWord, target_word: str) -> str:
    """Append kana added after an unchanged spelling, or retain the source reading when unsupported."""
    # 見[ミ] → 見る and 出来[デキ] → 出来る have no source kana ending for the replacement loop to strip.
    if target_word.startswith(source.word):  # Example: 出来る starts with 出来
        ending = target_word[len(source.word) :]  # 出来る → る
        if ending and is_kana_str(ending):
            return source.reading + ending  # でき＋る
    # target word without kana ending: "場合"
    # or the target does not start with the source: "軽そう".startswith("軽装")
    return source.reading


assert extend_stem_reading(SourceWord("見", "み"), target_word="見る") == "みる"
assert extend_stem_reading(SourceWord("場", "ば"), target_word="場合") == "ば"


def adjust_kuru_reading(source: SourceWord, target_word: str) -> str:
    """Recover the 来る stem in either kana script without mistaking 出来る for a 来る compound."""
    stem = target_word[:-1]  # Here stem is any string ending with 来.R
    if not source.word.startswith(stem):
        return ""
    ending = source.word[len(stem) :]
    if not ending:
        stem_reading = source.reading
    elif not (is_kana_str(ending) and _(source.reading).endswith(_(ending))):
        return ""
    else:
        stem_reading = source.reading[: -len(ending)]

    # 来[き]/来[こ] and やって来[やってき] need a stem change, not just suffix replacement.
    # IPADIC has no headword-reading field: https://taku910.github.io/mecab/format.html
    if stem_reading.endswith(("き", "こ", "く")):
        return stem_reading[:-1] + "くる"
    if _(stem_reading).endswith(("キ", "コ", "ク")):
        return stem_reading[:-1] + "クル"
    return ""


assert adjust_kuru_reading(SourceWord("来", "き"), target_word="来る") == "くる"
assert adjust_kuru_reading(SourceWord("やって来", "やってこ"), target_word="やって来る") == "やってくる"
assert adjust_kuru_reading(SourceWord("来", "らい"), target_word="来る") == ""


def adjust_reading_ending(source: SourceWord, target_word: str) -> str:
    """Reuse suffix adjustment in either direction after handling unchanged words and irregular stems."""
    # Analyze the headword.
    # Go from the last to the first character
    # and skip the characters that are identical between the headword and the reading.
    # In the end, the reading of a common `stem` should be found, e.g. "ひざまず" for "跪かなかった"
    common_suffix_length = find_common_suffix_length(*source)
    # Example: stem (kanji) reading for 食べた is た, inflected reading (suffix) is べた.
    stem_reading = source.reading[: len(source.reading) - common_suffix_length]
    inflected_reading = target_word[len(source.word) - common_suffix_length :]

    if _(stem_reading) == _(source.reading):
        # Example: 寝[ね], stem_reading=ね; 出来[デキ], stem_reading=デキ
        return extend_stem_reading(source, target_word=target_word)
    return stem_reading + inflected_reading


assert adjust_reading_ending(SourceWord("死ん", "しん"), target_word="死ぬ") == "しぬ"
assert adjust_reading_ending(SourceWord("死ぬ", "しぬ"), target_word="死ん") == "しん"
assert adjust_reading_ending(SourceWord("寝", "ね"), target_word="寝る") == "ねる"


def is_kuru_headword(word: str) -> bool:
    """Return whether the spelling identifies 来る or a compound, excluding 出来る."""
    # 来る changes its kanji's reading to キ or コ, unlike the ichidan verb 出来る.
    # Include the older 來 spelling without treating 出來る as a 来る compound.
    return word.endswith(("来る", "來る")) and not word.endswith(("出来る", "出來る"))


assert is_kuru_headword("来る")
assert is_kuru_headword("やって來る")
assert not is_kuru_headword("出来る")


def adjust_reading(source: SourceWord, target_word: str) -> str:
    """
    Adjust the source reading to the target spelling's inflected or dictionary form.
    For example, 食べる[たべる] → 食べた gives たべた, and 死ん[しん] → 死ぬ gives しぬ.
    Unsupported spelling changes retain the source reading.
    """
    if not (source.word and source.reading and target_word):
        return ""
    if _(source.word) == _(source.reading):
        # or maybe return headword_reading
        return target_word
    if _(source.word) == _(target_word):
        return source.reading
    if is_kana_str(target_word):
        return target_word
    if is_kuru_headword(target_word):
        return adjust_kuru_reading(source, target_word=target_word)
    return adjust_reading_ending(source, target_word=target_word)


assert adjust_reading(SourceWord("食べる", "たべる"), "食べた") == "たべた"
assert adjust_reading(SourceWord("死ん", "しん"), "死ぬ") == "しぬ"
assert adjust_reading(SourceWord("死ぬ", "しぬ"), "死ん") == "しん"
