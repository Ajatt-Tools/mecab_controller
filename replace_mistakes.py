# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import dataclasses
from collections.abc import Iterable, Sequence
from typing import Optional

try:
    from .basic_types import Inflection, MecabParsedToken, PartOfSpeech
except ImportError:
    from basic_types import Inflection, MecabParsedToken, PartOfSpeech


def replace_mistakes(tokens: Sequence[MecabParsedToken]) -> Iterable[MecabParsedToken]:
    for idx in range(len(tokens)):
        yield from replace_mistake(tokens, idx)


def slice_headwords(context: Sequence[MecabParsedToken], start: int, end: int) -> Optional[tuple[str, ...]]:
    try:
        return tuple(context[idx].headword for idx in range(start, end))
    except IndexError:
        return None


def replace_mistake(context: Sequence[MecabParsedToken], pos: int) -> Iterable[MecabParsedToken]:
    token = context[pos]
    if token.word == "放っ" and slice_headwords(context, pos + 1, pos + 3) in (("て", "おく"), ("て", "おける")):
        yield dataclasses.replace(token, headword="放る", katakana_reading="ホウッ")
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
    else:
        yield token