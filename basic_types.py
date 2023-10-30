# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import enum
from types import SimpleNamespace
from typing import Optional, NamedTuple, Iterable


class IterableSimpleNamespace(Iterable, SimpleNamespace):
    def __iter__(self):
        return iter(self.__dict__.values())


Separators = SimpleNamespace(
    # Separators that are passed as command line arguments to mecab and used to parse mecab's output.
    component="<ajt__component_separator>",
    node="<ajt__node_separator>",
    footer="<ajt__footer>",
)

Components = IterableSimpleNamespace(
    # What info about each word mecab should output to the user.
    word='%m',
    headword='%f[6]',
    katakana_reading='%f[7]',
    part_of_speech='%f[0]',
    inflection_type='%f[5]',
)


class PartOfSpeech(enum.Enum):
    """
    Parts of speech that mecab can output.
    """
    unknown = None
    other = "その他"  # e.g. よ, ァ
    filler = "フィラー"  # e.g. なんか, あのー, ま, えーと
    adverb = "副詞"  # e.g. たちまち, やや, あたかも, どんどん, 飽くまで
    bound_auxiliary = "助動詞"  # e.g らしい, です, ない, ます, たい, だ
    particle = "助詞"  # e.g. は, から, を, て
    verb = "動詞"  # e.g. 出る, 見せる, あげる, 雇う, 患う
    noun = "名詞"  # e.g. 全員, 国, 言語学, 代金. Note: non-i adjectives (e.g. 綺麗) are classified as nouns too.
    i_adjective = "形容詞"  # e.g. 広い, づらい, 近い, 深い, 怖い
    interjection = "感動詞"  # e.g. おはよう, ありがとう, お疲れ様
    conjunction = "接続詞"  # e.g. それなら, それより, ですけれど, ただし
    prefix = "接頭詞"  # e.g. 超, 無, 御, 前, 初
    symbol = "記号"  # e.g. (-_-;), ■, (^.^)/~~~, ￥, ＊
    adnominal_adjective = "連体詞"  # e.g. いかなる, ろくな, この, いろんな, 小さな

    @classmethod
    def _missing_(cls, value):
        """
        If mecab for some reason outputs something that's not a member of this enum,
        fall back to "unknown".
        """
        return cls.unknown


class MecabParsedToken(NamedTuple):
    word: str
    headword: str
    katakana_reading: Optional[str]
    part_of_speech: PartOfSpeech
    inflection_type: Optional[str]


assert tuple(MecabParsedToken._fields) == tuple(Components.__dict__.keys())


def main():
    for k in Components:
        print(k)
    print(PartOfSpeech("invalid"))
    print(PartOfSpeech("副詞"))
    print(PartOfSpeech("感動詞"))


if __name__ == '__main__':
    main()
