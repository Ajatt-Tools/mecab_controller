# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import dataclasses
import re
from collections.abc import Iterable, Sequence

try:
    from .basic_types import Inflection, MecabParsedToken, PartOfSpeech
    from .consts import (
        NATIVE_TSU_READINGS,
        NUMERAL_READINGS,
        P_COUNTER_ENDINGS,
        SHORT_COUNTER_ENDINGS,
        VOICED_COUNTER_ENDINGS,
    )
    from .word_conv import to_arabic_numbers
except ImportError:
    from basic_types import Inflection, MecabParsedToken, PartOfSpeech
    from consts import (
        NATIVE_TSU_READINGS,
        NUMERAL_READINGS,
        P_COUNTER_ENDINGS,
        SHORT_COUNTER_ENDINGS,
        VOICED_COUNTER_ENDINGS,
    )
    from word_conv import to_arabic_numbers


RE_NUMERAL_WORD = re.compile(r"[〇零一二三四五六七八九十百千万億兆０-９0-9]+")
RE_COUNTER_WORD = re.compile(r"ヶ月|人称|人前|[つ月日筋隻丁品番枚時回円万歳限人]")
RE_SHORT_COUNTER_COUNT = re.compile(r"(?P<number>[1-9][0-9]?)(?P<counter>[人個枚本台匹冊階歳回杯分つ])")


@dataclasses.dataclass
class WrappedToken:
    """Track whether an ordered correction has already consumed a token."""

    token: MecabParsedToken
    skip: bool = False


def replace_mistakes(tokens: Iterable[MecabParsedToken]) -> Iterable[MecabParsedToken]:
    consumed = tuple(WrappedToken(token) for token in tokens)
    for idx, wrapped in enumerate(consumed):
        if wrapped.skip:
            continue
        yield from replace_mistake(wrapped.token, consumed, idx)


def slice_headwords(context: Sequence[WrappedToken], start: int, end: int) -> Sequence[str]:
    """Return headwords in a context window, or an empty sequence if it is incomplete.
    E.g., ["十一", "人"].
    """
    try:
        return tuple(context[idx].token.headword for idx in range(start, end))
    except IndexError:
        return ()


def slice_context(context: Sequence[WrappedToken], start: int, end: int) -> str:
    """Join token surfaces in a context window, or return an empty string if it is incomplete.
    E.g., ["十一", "人"]  → "十一人"
    """
    try:
        return "".join(context[idx].token.word for idx in range(start, end))
    except IndexError:
        return ""


def take_headword(context: Sequence[WrappedToken], pos: int) -> str:
    """Return a context token's headword, or an empty string when its position is unavailable."""
    try:
        return context[pos].token.headword
    except IndexError:
        return ""


def skip_context(context: Sequence[WrappedToken], start: int, end: int | None = None) -> None:
    """Mark tokens as consumed, defaulting to the single token at start."""
    if end is None:
        end = start + 1
    for idx in range(start, end):
        context[idx].skip = True


def merge_context(
    context: Sequence[WrappedToken], *, pos: int, end: int, new_katakana_reading: str = ""
) -> MecabParsedToken:
    """Concatenate token words, headwords, and readings, optionally replacing the combined reading."""
    # Keep token-boundary matching in the ordered rules, not in a second parser.
    # https://docs.python.org/3/library/dataclasses.html#dataclasses.replace
    skip_context(context, pos + 1, end)
    tokens = tuple(wrapped.token for wrapped in context[pos:end])
    return dataclasses.replace(
        tokens[0],
        word="".join(token.word for token in tokens),
        headword="".join(token.headword for token in tokens),
        # ９[キュウ] + 円[エン] → ９円[キュウエン]. Empty readings add no characters.
        katakana_reading=new_katakana_reading or "".join(token.katakana_reading for token in tokens),
    )


def is_numeral_string(string: str | None) -> bool:
    """Recognize complete numeral strings in kanji, ASCII, or full-width digits."""
    return RE_NUMERAL_WORD.fullmatch(string or "") is not None


assert is_numeral_string("２１") is True


def is_counter_string(string: str | None) -> bool:
    """Recognize whole counter words without matching prefixes of longer words."""
    return RE_COUNTER_WORD.fullmatch(string or "") is not None


assert is_counter_string("人称") is True


def token_comes_after_number(context: Sequence[WrappedToken], pos: int) -> bool:
    """Check whether the preceding token consists entirely of number characters."""
    # Example: In ["十一", "人", "前"] "人" comes after a number.
    # 十一人 is じゅういちにん, not じゅうひとり.
    return pos > 0 and is_numeral_string(context[pos - 1].token.word)


def token_comes_before_regular_person_counter_suffix(context: Sequence[WrappedToken], pos: int) -> bool:
    """Check for a following 称, 前, or whole 三脚 token, which needs a regular person-counter reading."""
    # Example: In ["十一", "人", "前"] "人" comes before the counter suffix "前"
    # 一人称, 一人前, and 二人三脚 also use the regular counter.
    return take_headword(context, pos + 1) in ("称", "前", "三脚")


def token_comes_before_split_sankyaku(context: Sequence[WrappedToken], pos: int) -> bool:
    """Check whether the following two token surfaces spell 三脚 in an expression such as 二人三脚."""
    # Example: In ["二人", "三", "脚"] tokens ["三", "脚"] spell "三脚".
    return slice_context(context, pos + 1, pos + 3) == "三脚"


def needs_regular_person_counter_reading(context: Sequence[WrappedToken], pos: int) -> bool:
    """Check the surrounding tokens for a regular rather than native one/two-person counter reading."""
    # Example: In ["十一", "人", "前"] "人" needs the にん reading.
    # 十一人 is じゅういちにん, not じゅうひとり.
    # 一人称 and 二人三脚 also use the regular counter.
    return (
        token_comes_after_number(context, pos)  # 一人 after number: 十一人
        or token_comes_before_regular_person_counter_suffix(context, pos)  # 一人 before 称: 一人称
        or token_comes_before_split_sankyaku(context, pos)  # 二人 before 三 and 脚: 二人三脚
    )


def short_number_reading(number: int) -> str:
    """Read the regular tens and ones of a matched number from one through 99.
    27 → ニジュウナナ
    """
    tens, units = divmod(number, 10)
    reading = ""
    if tens > 1:
        reading = NUMERAL_READINGS[tens]
    if tens:
        reading += "ジュウ"
    return reading + NUMERAL_READINGS[units]


assert short_number_reading(27) == "ニジュウナナ"


def short_person_count_reading(number: int) -> str:
    """Apply native one/two-person readings and the ヨニン ending to short person counts.
    14 → ジュウヨニン
    """
    if number == 1:
        return "ヒトリ"
    if number == 2:
        return "フタリ"
    reading = short_number_reading(number)
    if number % 10 == 4:
        reading = reading[:-1]
    return reading + "ニン"


assert short_person_count_reading(14) == "ジュウヨニン"


def correct_person_counter_reading(token: MecabParsedToken) -> MecabParsedToken:
    """Correct short person counts while leaving padded identifiers and larger counts unchanged."""
    # Example: ２人[ニニン] gets corrected to ２人[フタリ]
    # Unknown digit tokens such as 11 have no numeral reading in bundled IPADIC.
    match = RE_SHORT_COUNTER_COUNT.fullmatch(to_arabic_numbers(token.headword))
    if match and match["counter"] == "人":
        return dataclasses.replace(token, katakana_reading=short_person_count_reading(int(match["number"])))
    return token


def counter_has_gemination(number: int, counter: str) -> bool:
    """Select counters whose final numeral consonant doubles, without applying 六個's change to 六冊 or 六歳.
    6個 → True (ろっこ), 2回 → False (にかい)
    """
    if counter in ("冊", "歳"):
        return number % 10 in (0, 1, 8)
    return counter in ("個", "本", "匹", "階", "回", "杯", "分") and number % 10 in (0, 1, 6, 8)


assert counter_has_gemination(6, "個") is True  # ろっこ
assert counter_has_gemination(2, "回") is False  # にかい


def short_counter_ending(number: int, counter: str) -> str:
    """Resolve counter voicing and handakuten separately from changes to the numeral.
    Example: 7+分=>ふん
    """
    if number % 10 == 3 and counter in VOICED_COUNTER_ENDINGS:
        return VOICED_COUNTER_ENDINGS[counter]
    if counter == "分" and number % 10 in (3, 4):
        return "プン"  # otherwise, ふん is used.
    if counter_has_gemination(number, counter):
        return P_COUNTER_ENDINGS.get(counter, SHORT_COUNTER_ENDINGS[counter])
    return SHORT_COUNTER_ENDINGS[counter]


assert short_counter_ending(7, "分") == "フン"


def short_counter_reading(number: int, counter: str) -> str:
    """Read a supported short counter, returning an empty string for unsupported native つ counts."""
    if counter == "人":
        return short_person_count_reading(number)
    elif counter == "つ":
        if 1 <= number <= len(NATIVE_TSU_READINGS):
            return NATIVE_TSU_READINGS[number - 1]
        return ""
    elif counter == "歳" and number == 20:
        return "ハタチ"
    reading = short_number_reading(number)
    # 一個, 六個, 八個, and multiples of 十 use イッコ, ロッコ, ハッコ, and ジュッコ endings.
    if counter_has_gemination(number, counter):
        reading = reading[:-1] + "ッ"
    return reading + short_counter_ending(number, counter)


assert short_counter_reading(20, "歳") == "ハタチ"
assert short_counter_reading(6, "本") == "ロッポン"


def correct_short_counter_reading(token: MecabParsedToken) -> MecabParsedToken:
    """Supply a merged count's numeral reading while retaining its spelling and headword for dictionary lookup."""
    # Example: 四十本 receives the ヨンジュッポン reading.
    if match := RE_SHORT_COUNTER_COUNT.fullmatch(to_arabic_numbers(token.headword)):
        # 三 + 十二分 must read サンジュウニフン, not retain a lexical 十二分 suffix reading.
        # The ordered rules leave an already-unified 十二分 untouched unless its context identifies a counter.
        if reading := short_counter_reading(int(match["number"]), match["counter"]):
            return dataclasses.replace(token, katakana_reading=reading)
    return token


def is_short_counter(context: Sequence[WrappedToken], start: int, end: int) -> bool:
    """Check whether the complete context span is a supported short counter."""
    # Example: In ["十一", "人", "前"] "十一"+"人" is a short counter.
    # fullmatch returns a Match object for ２ + １ + 人, not the Boolean 'True'.
    return RE_SHORT_COUNTER_COUNT.fullmatch(to_arabic_numbers(slice_context(context, start, end))) is not None


def replace_mistake(token: MecabParsedToken, context: Sequence[WrappedToken], pos: int) -> Iterable[MecabParsedToken]:
    """Apply the first matching contextual correction, or yield the original token unchanged.

    This ordered rule block intentionally exceeds the usual function-length limit.
    Keep it together because precedence and token consumption form one logical correction operation.
    """
    if to_arabic_numbers(slice_context(context, pos, pos + 4)) == "2人3脚":
        # ２ + 人 + 三 + 脚 → ２人三脚
        # Match ２ + 人 + 三 + 脚 before the generic ２ + 人 rule consumes the numeral.
        yield merge_context(context, pos=pos, end=pos + 4, new_katakana_reading="ニニンサンキャク")
    elif to_arabic_numbers(slice_context(context, pos, pos + 3)) == "1人相撲":
        # １ + 人 + 相撲 → １人相撲
        # １ + 人 + 相撲 needs ひとりずもう, not concatenated いちにんすもう.
        yield merge_context(context, pos=pos, end=pos + 3, new_katakana_reading="ヒトリズモウ")
    elif to_arabic_numbers(slice_context(context, pos, pos + 3)) == "2人3脚":
        # ２ + 人 + 三脚 → ２人三脚, or 二人 + 三 + 脚 → 二人三脚
        yield merge_context(context, pos=pos, end=pos + 3, new_katakana_reading="ニニンサンキャク")
    elif to_arabic_numbers(slice_context(context, pos, pos + 2)) == "2人3脚":
        # ２人 + 三脚 → ２人三脚
        yield merge_context(context, pos=pos, end=pos + 2, new_katakana_reading="ニニンサンキャク")
    elif to_arabic_numbers(token.headword) == "1人" and take_headword(context, pos + 1) in ("称", "前"):
        # １人 + 称 → １人称, or １人 + 前 → １人前
        other = context[pos + 1].token
        yield merge_context(context, pos=pos, end=pos + 2, new_katakana_reading="イチニン" + other.katakana_reading)
    elif to_arabic_numbers(token.headword) == "2人" and take_headword(context, pos + 1) in ("称", "前"):
        # ２人 + 称 → ２人称, or ２人 + 前 → ２人前
        other = context[pos + 1].token
        yield merge_context(context, pos=pos, end=pos + 2, new_katakana_reading="ニニン" + other.katakana_reading)
    elif to_arabic_numbers(token.headword) == "1人" and needs_regular_person_counter_reading(context, pos):
        # 十 + 一人: read 一人 as イチニン, not ヒトリ.
        yield dataclasses.replace(token, katakana_reading="イチニン")
    elif to_arabic_numbers(token.headword) == "2人" and needs_regular_person_counter_reading(context, pos):
        # 十 + 二人: read 二人 as ニニン, not フタリ.
        yield dataclasses.replace(token, katakana_reading="ニニン")
    elif to_arabic_numbers(slice_context(context, pos, pos + 2)) == "1人相撲":
        # １人 + 相撲 → １人相撲, or １ + 人相撲 → １人相撲
        # Keep the compound's voiced ずもう when the counter entry splits 一人相撲 into two words.
        # Preserve 1人相撲 and １人相撲 as written instead of replacing their digits with kanji.
        yield merge_context(context, pos=pos, end=pos + 2, new_katakana_reading="ヒトリズモウ")
    elif is_numeral_string(token.headword) and slice_headwords(context, pos + 1, pos + 3) in (
        ("人", "称"),
        ("人", "前"),
    ):
        # １ + 人 + 称 → １人称, or ２ + 人 + 前 → ２人前
        # Match complete 称 or 前 tokens, never the first character of 称賛 or 前進.
        other = context[pos + 2].token
        reading = token.katakana_reading + "ニン" + other.katakana_reading
        yield merge_context(context, pos=pos, end=pos + 3, new_katakana_reading=reading)
    elif not token_comes_after_number(context, pos) and is_short_counter(context, pos, pos + 4):
        # 三 + 十 + 三 + 人 needs one corrected count, not a correction to its trailing digit alone.
        yield correct_short_counter_reading(merge_context(context, pos=pos, end=pos + 4))
    elif not token_comes_after_number(context, pos) and is_short_counter(context, pos, pos + 3):
        # Full-width counts may arrive as ２ + １ + 人 even when ASCII 21 is a single token.
        yield correct_short_counter_reading(merge_context(context, pos=pos, end=pos + 3))
    elif not token_comes_after_number(context, pos) and is_short_counter(context, pos, pos + 2):
        # ASCII digit tokens can have empty readings even for simple examples such as 2 + 個.
        yield correct_short_counter_reading(merge_context(context, pos=pos, end=pos + 2))
    elif (
        is_numeral_string(token.headword)
        and is_counter_string(take_headword(context, pos + 1))
        and not token_comes_after_number(context, pos)
    ):
        # １ + 人 → １人, 二 + 日 → 二日, ９ + 円 → ９円
        # Do not merge only the final ０ + 人 of １ + ０ + ０ + 人.
        combined = merge_context(context, pos=pos, end=pos + 2)
        yield correct_person_counter_reading(combined)
    elif to_arabic_numbers(token.headword) == "6本" and token.katakana_reading == "ロクモト":
        # 六本[ロクモト] → 六本[ロッポン], retaining the original word and headword for dictionary alternatives.
        yield correct_short_counter_reading(token)
    elif (
        token.headword.endswith("分")
        and token.katakana_reading.endswith("ブ")
        and is_short_counter(context, pos, pos + 1)
        and slice_headwords(context, pos + 1, pos + 3) in (("くらい", "で"), ("ほど", "で"))
    ):
        # 七分[シチブ] + くらい + で → 七分[ナナフン] + くらい + で for an approximate duration.
        # 十二分[ジュウニブン] and 七分丈[しちぶたけ] do not match this contextual rule.
        yield correct_short_counter_reading(token)
    elif slice_context(context, pos, pos + 2) == "三色":
        # 三 + 色 must stay a whole word so 色 is not looked up separately as a suffix.
        yield merge_context(context, pos=pos, end=pos + 2, new_katakana_reading="サンシキ")
    elif slice_context(context, pos, pos + 2) == "真莉":
        # 真 + 莉 is the given-name reading マリ, not an independently annotated 真 followed by unknown 莉.
        yield merge_context(context, pos=pos, end=pos + 2, new_katakana_reading="マリ")
    elif token.headword in ("遣る", "やる") and slice_headwords(context, pos + 1, pos + 3) == ("方", "無い"):
        # In 遣る方無い, 方無い reads カタナイ rather than separate ホウ + ナイ.
        yield token
        skip_context(context, pos + 1)
        yield merge_context(context, pos=pos + 1, end=pos + 3, new_katakana_reading="カタナイ")
    elif (merged_word := slice_context(context, pos, pos + 3)) in ("かもしれない", "かも知れない"):
        # Pitch accent lookup indexes both spellings as katakana.
        skip_context(context, pos + 1, pos + 3)
        yield MecabParsedToken(
            word=merged_word,
            headword=merged_word,
            katakana_reading="カモシレナイ",
            part_of_speech=PartOfSpeech.bound_auxiliary,
            inflection_type=Inflection.dictionary_form,
        )
    elif token.word == "放っ" and slice_headwords(context, pos + 1, pos + 3) in (("て", "おく"), ("て", "おける")):
        yield dataclasses.replace(token, headword="放る", katakana_reading="ホウッ")
    elif token.word == "美しゅう":
        # Prefer 美醜[びしゅう] for this mixed spelling.
        # Keep token.word unchanged so generated readings retain the spelling on the user's card.
        yield dataclasses.replace(
            token,
            headword="美醜",
            katakana_reading="ビシュウ",
            part_of_speech=PartOfSpeech.noun,
            inflection_type=Inflection.unknown,
        )
    elif token.word == "温玉" and token.headword == "オンセンタマゴ":
        yield dataclasses.replace(
            token,
            headword="温玉",
        )
    elif token.headword == "した" and token.word == "した":
        yield dataclasses.replace(
            token,
            headword="する",
            part_of_speech=PartOfSpeech.verb,
        )
    elif token.headword == "打付ける":
        yield dataclasses.replace(
            token,
            katakana_reading=token.katakana_reading.replace("ウチツケ", "ブツケ"),
        )
    elif token.word == "拗ら" and token.headword == "拗る" and take_headword(context, pos + 1).startswith("せ"):
        yield dataclasses.replace(
            token,
            headword="拗らせる",
        )
    elif token.word == "弄っ" and token.headword == "弄う" and "てる" == take_headword(context, pos + 1):
        yield dataclasses.replace(
            token,
            headword="弄る",
            katakana_reading="イジッ",
        )
    elif token.word == "荒ん" and token.headword == "荒ぶ" and "だ" == take_headword(context, pos + 1):
        yield dataclasses.replace(
            token,
            headword="荒む",
        )
    elif token.word == "歩いた" and token.headword == "歩み板":
        yield dataclasses.replace(
            token,
            headword="歩く",
            katakana_reading="アルイタ",
            part_of_speech=PartOfSpeech.verb,
            inflection_type=Inflection.continuative_ta,
        )
    elif token.word == "しろっ" and "て" == take_headword(context, pos + 1):
        # しろって
        yield MecabParsedToken(
            word="しろ",
            headword="する",
            katakana_reading="シロ",
            part_of_speech=PartOfSpeech.verb,
            inflection_type=Inflection.imperative_ro,
        )
        yield MecabParsedToken(
            word="って",
            headword="って",
            katakana_reading="ッテ",
            part_of_speech=PartOfSpeech.particle,
            inflection_type=Inflection.unknown,
        )
    elif token.word == "はおら" and token.headword == "はおる" and "ぬ" == take_headword(context, pos + 1):
        # Xはおらぬ
        yield MecabParsedToken(
            word="は",
            headword="は",
            katakana_reading="ハ",
            part_of_speech=PartOfSpeech.particle,
            inflection_type=Inflection.unknown,
        )
        yield MecabParsedToken(
            word="おら",
            headword="おる",
            katakana_reading="オラ",
            part_of_speech=PartOfSpeech.verb,
            inflection_type=Inflection.irrealis,
        )
    elif token.word == "降り" and token.katakana_reading == "オリ" and "が" == take_headword(context, pos - 1):
        # 雪が降りました: オ=>フ
        yield dataclasses.replace(
            token,
            headword="降る",
            katakana_reading="フリ",
        )
    elif token.word == "旅立て" and token.headword == "旅立てる":
        # 旅立てる isn't listed in the pitch accent database; replace it with 旅立つ
        yield dataclasses.replace(
            token,
            headword="旅立つ",
        )
    elif token.word == "羽" and take_headword(context, pos + 1) == "撃":
        skip_context(context, pos + 1)
        yield MecabParsedToken(
            word="羽撃",
            headword="羽撃く",
            katakana_reading="ハバタ",
            part_of_speech=PartOfSpeech.verb,
            inflection_type=Inflection.irrealis,
        )
    elif token.word == "阿良" and slice_headwords(context, pos + 1, pos + 3) == ("々", "木"):
        skip_context(context, pos + 1, pos + 3)
        yield MecabParsedToken(
            word="阿良々木",
            headword="阿良々木",
            katakana_reading="アララギ",
            part_of_speech=PartOfSpeech.noun,
            inflection_type=Inflection.dictionary_form,
        )
    elif token.word == "乗り" and slice_headwords(context, pos + 1, pos + 3) == ("込", "え"):
        skip_context(context, pos + 1, pos + 3)
        yield MecabParsedToken(
            word="乗り込え",
            headword="乗り込える",
            katakana_reading="ノリコエ",
            part_of_speech=PartOfSpeech.verb,
            inflection_type=Inflection.continuative,
        )
    elif (
        token.word == "助"
        and token.katakana_reading == "スケ"
        and slice_headwords(context, pos + 1, pos + 3) == ("から", "ない")
    ):
        skip_context(context, pos + 1)
        yield MecabParsedToken(
            word="助から",
            headword="助かる",
            katakana_reading="タスカラ",
            part_of_speech=PartOfSpeech.verb,
            inflection_type=Inflection.irrealis,
        )
    elif token.word == "いい気" and take_headword(context, pos + 1) == "分":
        skip_context(context, pos + 1)
        yield MecabParsedToken(
            word="いい",
            headword="いい",
            katakana_reading="イイ",
            part_of_speech=PartOfSpeech.i_adjective,
            inflection_type=Inflection.dictionary_form,
        )
        yield MecabParsedToken(
            word="気分",
            headword="気分",
            katakana_reading="キブン",
            part_of_speech=PartOfSpeech.noun,
            inflection_type=Inflection.dictionary_form,
        )
    elif token.word == "しや" and token.headword == "視野":
        yield dataclasses.replace(
            token,
            headword="してやる",
            part_of_speech=PartOfSpeech.verb,
            inflection_type=Inflection.nominal_connection_2,
        )
    elif token.word == "いいっ" and token.headword == "いい":
        yield MecabParsedToken(
            word="いい",
            headword="いい",
            katakana_reading="イイ",
            part_of_speech=PartOfSpeech.i_adjective,
            inflection_type=Inflection.dictionary_form,
        )
        yield MecabParsedToken(
            word="っ",
            headword="っ",
            katakana_reading="ッ",
            part_of_speech=PartOfSpeech.unknown,
            inflection_type=Inflection.unknown,
        )
    elif token.word == "本当のところ":
        yield MecabParsedToken(
            word="本当",
            headword="本当",
            katakana_reading="ホントウ",
            part_of_speech=PartOfSpeech.noun,
            inflection_type=Inflection.dictionary_form,
        )
        yield MecabParsedToken(
            word="の",
            headword="の",
            katakana_reading="ノ",
            part_of_speech=PartOfSpeech.particle,
            inflection_type=Inflection.unknown,
        )
        yield MecabParsedToken(
            word="ところ",
            headword="ところ",
            katakana_reading="トコロ",
            part_of_speech=PartOfSpeech.noun,
            inflection_type=Inflection.dictionary_form,
        )
    elif token.word == "有り難う" and token.katakana_reading == "アリガタウ":
        yield dataclasses.replace(token, katakana_reading="アリガトウ")
    elif token.word == "出て" and token.headword == "出し手" and token.katakana_reading == "ダシテ":
        yield dataclasses.replace(token, headword="出る", katakana_reading="デテ")
    elif token.word == "悪い" and token.katakana_reading == "アクイ" and token.headword == "悪意":
        yield dataclasses.replace(token, headword="悪い", katakana_reading="ワルイ")
    elif token.word == "では" and token.katakana_reading == "デハ" and token.headword == "出端":
        yield MecabParsedToken(
            word="で",
            headword="で",
            katakana_reading="デ",
            part_of_speech=PartOfSpeech.particle,
            inflection_type=Inflection.unknown,
        )
        yield MecabParsedToken(
            word="は",
            headword="は",
            katakana_reading="ハ",
            part_of_speech=PartOfSpeech.particle,
            inflection_type=Inflection.unknown,
        )
    elif token.word == "いた目" and token.katakana_reading == "イタメ" and token.headword == "板目":
        yield MecabParsedToken(
            word="い",
            headword="いる",
            katakana_reading="イ",
            part_of_speech=PartOfSpeech.verb,
            inflection_type=Inflection.continuative,
        )
        yield MecabParsedToken(
            word="た",
            headword="た",
            katakana_reading="タ",
            part_of_speech=PartOfSpeech.bound_auxiliary,
            inflection_type=Inflection.continuative,
        )
        yield MecabParsedToken(
            word="目",
            headword="目",
            katakana_reading="メ",
            part_of_speech=PartOfSpeech.noun,
            inflection_type=Inflection.unknown,
        )
    elif token.word == "軽そう" and token.katakana_reading == "ケイソウ" and token.headword == "軽装":
        yield MecabParsedToken(
            word="軽",
            headword="軽い",
            katakana_reading="カル",
            part_of_speech=PartOfSpeech.i_adjective,
            inflection_type=Inflection.garu_attached,
        )
        yield MecabParsedToken(
            word="そう",
            headword="そう",
            katakana_reading="ソウ",
            part_of_speech=PartOfSpeech.adverb,
            inflection_type=Inflection.unknown,
        )
    elif token.headword == "接ぎ目":
        yield dataclasses.replace(token, katakana_reading="ツギメ")
    elif token.headword == "卵胞ホルモン":
        yield dataclasses.replace(token, katakana_reading="ランポウホルモン")
    elif token.headword == "足浴":
        yield dataclasses.replace(token, katakana_reading="ソクヨク")
    elif token.headword == "足" and take_headword(context, pos + 1) == "浴":
        skip_context(context, pos + 1)
        yield dataclasses.replace(token, word="足浴", headword="足浴", katakana_reading="ソクヨク")
    else:
        yield token
