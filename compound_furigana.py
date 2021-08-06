# -*- coding: utf-8 -*-

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

def break_compound_furigana(expr: str) -> str:
    furigana_start = expr.find('[')

    def find_common_kana(out_pos_start: int, in_pos_start: int):
        out_pos_end, in_pos_end = out_pos_start, in_pos_start

        while expr[out_pos_end] == expr[in_pos_end]:
            out_pos_end += 1
            in_pos_end += 1

        return (out_pos_start, out_pos_end), (in_pos_start, in_pos_end)

    def traverse():
        # starting from the second character and traversing to [
        for out_i in range(1, furigana_start):
            # starting inside the parentheses
            # +2 because at least 1 kana character must always belong to the first clause
            # as in `言い方[いいかた]`, the first `い` belongs to `言`.
            # -1 because the last character closes furigana - `]`
            for in_i in range(furigana_start + 2, len(expr) - 1):
                if expr[out_i] == expr[in_i]:
                    return find_common_kana(out_i, in_i)
        return None

    found = traverse()
    if found:
        result_expr = f"{expr[:found[0][0]]}{expr[furigana_start:found[1][0]]}]{expr[found[0][0]:found[0][1]]} "
        result_expr += break_compound_furigana(f"{expr[found[0][1]:furigana_start]}[{expr[found[1][1]:]}")
    else:
        result_expr = expr

    return result_expr


if __name__ == "__main__":
    print(break_compound_furigana('取って置[とってお]き'))
    print(break_compound_furigana('言い方[いいかた]'))
    print(break_compound_furigana('丸め込[まるめこ]む'))
