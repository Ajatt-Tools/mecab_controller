# Japanese support add-on for Anki 2.1
# Copyright (C) 2021  Ren Tatsumoto. <tatsu at autistici.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Any modifications to this file must keep this entire header intact.

from typing import NamedTuple, Optional


class Pos(NamedTuple):
    out_start: int
    out_end: int
    in_start: int
    in_end: int


def find_common_kana(expr: str, out_pos_start: int, in_pos_start: int) -> Pos:
    out_pos_end, in_pos_end = out_pos_start, in_pos_start

    while expr[out_pos_end] == expr[in_pos_end]:
        out_pos_end += 1
        in_pos_end += 1

    return Pos(out_pos_start, out_pos_end, in_pos_start, in_pos_end)


def traverse(expr: str, furigana_start: int) -> Optional[Pos]:
    # starting from the second character and traversing to [
    for out_i in range(1, furigana_start):
        # starting inside the parentheses
        # +2 because at least 1 kana character must always belong to the first clause
        # as in `言い方[いいかた]`, the first `い` belongs to `言`.
        # -1 because the last character closes furigana - `]`
        for in_i in range(furigana_start + 2, len(expr) - 1):
            if expr[out_i] == expr[in_i]:
                return find_common_kana(expr, out_i, in_i)
    return None


def break_compound_furigana(expr: str) -> str:
    furigana_start = expr.find('[')

    if p := traverse(expr, furigana_start):
        result_expr = f"{expr[:p.out_start]}{expr[furigana_start:p.in_start]}]{expr[p.out_start:p.out_end]} "
        result_expr += break_compound_furigana(f"{expr[p.out_end:furigana_start]}[{expr[p.in_end:]}")
    else:
        result_expr = expr

    return result_expr


if __name__ == "__main__":
    print(break_compound_furigana('取って置[とってお]き'))
    print(break_compound_furigana('言い方[いいかた]'))
    print(break_compound_furigana('丸め込[まるめこ]む'))
    print(break_compound_furigana('繋[つなが]る'))
    print(break_compound_furigana('お 問い合[といあ]わせ'))
