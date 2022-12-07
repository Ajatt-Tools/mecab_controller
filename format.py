# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

try:
    from .compound_furigana import break_compound_furigana
    from .kana_conv import to_katakana as _
except ImportError:
    from compound_furigana import break_compound_furigana
    from kana_conv import to_katakana as _


def format_output(kanji: str, reading: str) -> str:
    """Convert (kanji, reading) input to output that Anki understands: kanji[reading]"""
    # strip matching characters and beginning and end of reading and kanji
    # reading should always be at least as long as the kanji
    place_l = 0
    place_r = 0
    for i in range(1, len(kanji)):
        if _(kanji[-i]) != _(reading[-i]):
            break
        place_r = i
    for i in range(0, len(kanji) - 1):
        if _(kanji[i]) != _(reading[i]):
            break
        place_l = i + 1
    if place_l == 0:
        if place_r == 0:
            out_expr = f" {kanji}[{reading}]"
        else:
            out_expr = f" {kanji[:-place_r]}[{reading[:-place_r]}]{kanji[-place_r:]}"
    else:
        if place_r == 0:
            out_expr = f"{kanji[:place_l]} {kanji[place_l:]}[{reading[place_l:]}]"
        else:
            out_expr = f"{kanji[:place_l]} {kanji[place_l:-place_r]}[{reading[place_l:-place_r]}]{kanji[-place_r:]}"

    return break_compound_furigana(out_expr)


if __name__ == '__main__':
    print(format_output('秘訣', 'ひけつ'))
    print(format_output('食べた', 'たべた'))
    print(format_output('高級レストラン', 'こうきゅうれすとらん'))
    print(format_output('サイン会', 'さいんかい'))
    print(format_output('あり得る', 'ありえる'))
    print(format_output('取って置き', 'とっておき'))
