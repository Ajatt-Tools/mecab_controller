# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import enum
import functools
import re
import unicodedata

from .consts import (
    ARAB_TO_FULL_WIDTH_DIGITS,
    ARABIC_DIGITS,
    JAPANESE_DIGITS,
    JAPANESE_NUMBER_UNITS,
    KANJI_TO_DIGITS,
    MAX_NUMERAL_VALUE,
    NUMERAL_CACHE_SIZE,
    RE_NUMERAL,
)
from .kana_conv import to_katakana


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
    # Do not guess the value of mixed 1万 notation or malformed units.
    if any(char in ARABIC_DIGITS for char in text):
        return None
    try:
        value = parse_kanji_units(text)
        if format_kanji_number(value) == text:
            return value
    except ValueError:
        pass
    return None


class NumeralSpelling(enum.Enum):
    """Select kanji, ASCII Arabic digits, or full-width Arabic digits for numeric conversion."""

    kanji = enum.auto()
    arabic = enum.auto()  # Arabic means ASCII numbers.
    full_width = enum.auto()


def replace_number(match: re.Match[str], *, spelling: NumeralSpelling) -> str:
    """Normalize matched digits and convert supported numeral values."""
    # Normalize only the matched numeral so unrelated full-width letters and kana stay unchanged.
    # https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize
    normalized_number = unicodedata.normalize("NFKC", match.group())
    value = parse_number(normalized_number)
    arabic = normalized_number
    if value is not None:
        arabic = str(value)
    match spelling:
        case NumeralSpelling.full_width:
            return arabic.translate(ARAB_TO_FULL_WIDTH_DIGITS)
        case NumeralSpelling.arabic:
            return arabic
        case NumeralSpelling.kanji:
            if value is None:
                # Padded identifiers still need digit-width conversion: ００１ becomes 001, not 1.
                return normalized_number
            return format_kanji_number(value)
    raise ValueError("unreachable")


@functools.lru_cache(maxsize=NUMERAL_CACHE_SIZE)
def convert_numbers(text: str, *, spelling: NumeralSpelling) -> str:
    """Convert numbers to the requested spelling while preserving surrounding text."""
    return RE_NUMERAL.sub(functools.partial(replace_number, spelling=spelling), text)


def to_arabic_numbers(text: str) -> str:
    """
    Convert numbers to ASCII digits without changing the surrounding text.
    Examples: "二人三脚" -> "2人3脚", "Ａ一号" -> "Ａ1号", "ｶﾀｶﾅ二" -> "ｶﾀｶﾅ2", "００１号" -> "001号", "１万回" -> "1万回".
    Padded identifiers keep their leading zeros.
    Mixed digit/unit notation and malformed or oversized numbers are not evaluated, but their digits become ASCII.
    """
    # Do not normalize text here. replace_number() applies NFKC only to each RE_NUMERAL match.
    # Normalizing the whole string would also change Ａ to A and ｶﾀｶﾅ to カタカナ.
    return convert_numbers(text, spelling=NumeralSpelling.arabic)


def normalize_headword(headword: str) -> str:
    """Normalize compatibility characters, kana, and whole-number spellings for indexing.

    https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize
    """
    # Normalize first because characters like ゟ expand to hiragana that must then become katakana.
    return to_arabic_numbers(to_katakana(unicodedata.normalize("NFKC", headword)))
