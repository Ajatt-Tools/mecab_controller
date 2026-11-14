# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

try:
    from .kana_conv import is_kana_str
    from .kana_conv import to_katakana as _
except ImportError:
    from kana_conv import is_kana_str
    from kana_conv import to_katakana as _


def adjust_reading(source_word: str, source_reading: str, target_word: str) -> str:  # 死ん  # シン  # 死ぬ  # → シヌ
    """
    Adjusts the word's reading to match its conjugated form.
    E.g., if raw_word is 食べた and the reading is たべる, it should output たべた.
    """
    if _(source_word) == _(source_reading):
        # or maybe return headword_reading
        return target_word
    if _(source_word) == _(target_word):
        return source_reading
    if is_kana_str(target_word):
        return target_word

    # Analyze the headword.
    # Go from the last to the first character
    # and skip the characters that are identical between the headword and the reading.
    # In the end, the reading of a common `stem` should be found, e.g. "ひざまず" for "跪かなかった"
    idx_headword, idx_reading = len(source_word), len(source_reading)
    while _(source_word[idx_headword - 1]) == _(source_reading[idx_reading - 1]):
        idx_headword -= 1
        idx_reading -= 1
    stem_reading = source_reading[:idx_reading]
    inflected_reading = target_word[idx_headword:]

    if _(stem_reading) == _(source_reading):
        return source_reading
    return stem_reading + inflected_reading


assert _(adjust_reading("食べる", "たべる", "食べた")) == "たべた"
assert _(adjust_reading("死ん", "シン", "死ぬ")) == "シヌ"
assert _(adjust_reading("死ぬ", "シヌ", "死ん")) == "シン"
