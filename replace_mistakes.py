# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import dataclasses
from collections.abc import Iterable

try:
    from .basic_types import Inflection, MecabParsedToken, PartOfSpeech
except ImportError:
    from basic_types import Inflection, MecabParsedToken, PartOfSpeech


def replace_mistakes(token: MecabParsedToken) -> Iterable[MecabParsedToken]:
    if token.word == "悪い" and token.katakana_reading == "アクイ" and token.headword == "悪意":
        yield dataclasses.replace(token, headword="悪い", katakana_reading="ワルイ")
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
