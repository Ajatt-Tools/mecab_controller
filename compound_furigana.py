# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import NamedTuple, Optional

__all__ = ['break_compound_furigana', ]


class Dismembered(NamedTuple):
    word: str
    reading: str
    tail: str


class CompoundSplit(NamedTuple):
    first: Dismembered
    second: Dismembered


def dismember(expr: str) -> Optional[Dismembered]:
    if (furigana_start := expr.find('[')) < 1:
        return None
    elif (furigana_end := expr.find(']')) < 3:
        return None
    else:
        return Dismembered(
            expr[:furigana_start],
            expr[furigana_start + 1:furigana_end],
            expr[furigana_end + 1:]
        )


def find_common_str_len(common_stem: str, common_reading: str):
    common_len = 0
    for c1, c2 in zip(common_stem, common_reading):
        if c1 == c2:
            common_len += 1
        else:
            return common_len


def find_common_kana(expr: Dismembered) -> Optional[CompoundSplit]:
    start_index = max(1, find_common_str_len(expr.word, expr.reading))

    for i in range(start_index, len(expr.word)):
        for j in range(start_index, len(expr.reading)):
            if expr.word[i] == expr.reading[j]:
                common_len = find_common_str_len(expr.word[i:], expr.reading[j:])
                return CompoundSplit(
                    Dismembered(expr.word[:i], expr.reading[:j], expr.reading[j:j + common_len]),
                    Dismembered(expr.word[i + common_len:], expr.reading[j + common_len:], expr.tail)
                )


def break_compound_furigana_chunk(expr: str) -> str:
    if (d := dismember(expr)) and (c := find_common_kana(d)):
        return (
                f'{c.first.word}[{c.first.reading}]{c.first.tail} '
                + break_compound_furigana_chunk(f'{c.second.word}[{c.second.reading}]{c.second.tail}')
        )
    else:
        return expr


def break_compound_furigana(expr: str) -> str:
    return ' '.join(map(break_compound_furigana_chunk, expr.split(' ')))


if __name__ == "__main__":
    assert (break_compound_furigana(' 取って置[とってお]き') == ' 取[と]って 置[お]き')
    assert (break_compound_furigana('言い方[いいかた]') == '言[い]い 方[かた]')
    assert (break_compound_furigana('丸め込[まるめこ]む') == '丸[まる]め 込[こ]む')
    assert (break_compound_furigana('繋[つなが]る') == '繋[つなが]る')
    assert (break_compound_furigana('お 問い合[といあ]わせ') == 'お 問[と]い 合[あ]わせ')
    assert (break_compound_furigana('あなた 方[がた]') == 'あなた 方[がた]')
    print("Done.")
