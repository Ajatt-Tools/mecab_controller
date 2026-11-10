# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Convert whole-number spellings for comparisons and lookup fallbacks."""

import functools
import re
import unicodedata
from collections.abc import Sequence

from .consts import (
    ARABIC_DIGITS,
    JAPANESE_DIGITS,
    JAPANESE_NUMBER_UNITS,
    MAX_NUMERAL_VALUE,
    NUMERAL_CACHE_SIZE,
)

RE_NUMERAL = re.compile(r"[0-9零〇一二三四五六七八九十百千万億兆京]+")
KANJI_TO_DIGITS = str.maketrans(JAPANESE_DIGITS + "〇", ARABIC_DIGITS + "0")


def format_kanji_number(value: int) -> str:
    """Format a nonnegative integer below 10**20 using Japanese place-value units.

    https://en.wikipedia.org/wiki/Japanese_numerals#Numbering_in_Japanese
    """
    if not 0 <= value < MAX_NUMERAL_VALUE:
        raise ValueError("Japanese numeral is outside the supported range")
    if value < len(JAPANESE_DIGITS):
        return JAPANESE_DIGITS[value]
    for unit, symbol in JAPANESE_NUMBER_UNITS:
        if value < unit:
            continue
        quotient, remainder = divmod(value, unit)
        prefix = format_kanji_number(quotient)
        if quotient == 1 and unit < 10**4:
            prefix = ""
        suffix = ""
        if remainder:
            suffix = format_kanji_number(remainder)
        return prefix + symbol + suffix
    raise ValueError("Japanese numeral has no supported unit")


def parse_kanji_units(text: str) -> int:
    """Evaluate unit notation, raising ValueError for unrecognized digit strings."""
    for unit, symbol in JAPANESE_NUMBER_UNITS:
        if symbol not in text:
            continue
        left, right = text.split(symbol, maxsplit=1)
        multiplier = 1
        if left:
            multiplier = parse_kanji_units(left)
        remainder = 0
        if right:
            remainder = parse_kanji_units(right)
        return multiplier * unit + remainder
    return int(text.translate(KANJI_TO_DIGITS))


def parse_number(text: str) -> int | None:
    """Parse standard units or digit notation, leaving ambiguous or oversized runs unchanged."""
    if len(text) > len(format_kanji_number(MAX_NUMERAL_VALUE - 1)):
        return None
    digits = text.translate(KANJI_TO_DIGITS)
    # Keep padded identifiers such as ００１ intact instead of treating them as the number one.
    if digits.isascii() and digits.isdecimal():
        if len(digits) > 1 and digits.startswith("0"):
            return None
        if len(digits) > len(str(MAX_NUMERAL_VALUE - 1)):
            return None
        return int(digits)
    # Mixed 1万 notation and malformed units are not guessed during a frequency fallback.
    if any(char in ARABIC_DIGITS for char in text):
        return None
    try:
        value = parse_kanji_units(text)
        if format_kanji_number(value) == text:
            return value
    except ValueError:
        pass
    return None


def replace_number(match: re.Match[str], *, kanji: bool) -> str:
    """Convert a complete numeric run, preserving unsupported spellings verbatim."""
    value = parse_number(match.group())
    if value is None:
        return match.group()
    if kanji:
        return format_kanji_number(value)
    return str(value)


@functools.lru_cache(maxsize=NUMERAL_CACHE_SIZE)
def numeric_headword_variants(headword: str) -> Sequence[str]:
    """Return distinct Arabic and kanji whole-number spellings in deterministic order.

    NFKC already makes full-width digits equivalent to ASCII digits during frequency lookup.
    https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize
    """
    normalized = unicodedata.normalize("NFKC", headword)
    return tuple(
        dict.fromkeys(
            RE_NUMERAL.sub(functools.partial(replace_number, kanji=kanji), normalized) for kanji in (False, True)
        )
    )
