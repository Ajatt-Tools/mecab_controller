# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

try:
    from .compound_furigana import break_compound_furigana
    from .kana_conv import to_katakana
except ImportError:
    from compound_furigana import break_compound_furigana
    from kana_conv import to_katakana


def mk_eq_trans_table():
    treat_equal = {
        "ハ": "ワ",
        "ヂ": "ジ",
        "ヅ": "ズ",
        "ヲ": "オ",
        "ヴ": "ブ",
    }
    return str.maketrans("".join(treat_equal.keys()), "".join(treat_equal.values()))


TREAT_EQUAL = mk_eq_trans_table()


def to_eq(text: str) -> str:
    """
    Used to compare strings when formatting furigana.
    """
    return to_katakana(text).translate(TREAT_EQUAL)


def format_output(kanji: str, reading: str) -> str:
    """Convert (kanji, reading) input to output that Anki understands: kanji[reading]"""
    # strip matching characters and beginning and end of reading and kanji
    # reading should always be at least as long as the kanji
    place_l = 0
    place_r = 0
    for i in range(1, len(kanji)):
        if to_eq(kanji[-i]) != to_eq(reading[-i]):
            break
        place_r = i
    for i in range(0, len(kanji) - 1):
        if to_eq(kanji[i]) != to_eq(reading[i]):
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


if __name__ == "__main__":
    assert format_output("秘訣", "ひけつ") == " 秘訣[ひけつ]"
    assert format_output("食べた", "たべた") == " 食[た]べた"
    assert format_output("高級レストラン", "こうきゅうれすとらん") == " 高級[こうきゅう]レストラン"
    assert format_output("サイン会", "さいんかい") == "サイン 会[かい]"
    assert format_output("あり得る", "ありえる") == "あり 得[え]る"
    assert format_output("取って置き", "とっておき") == " 取[と]って 置[お]き"
    assert format_output("あなた方", "あなたがた") == "あなた 方[がた]"
    assert format_output("突っ込んだ", "つっこんだ") == " 突[つ]っ 込[こ]んだ"
    assert format_output("相合い傘", "あいあいがさ") == " 相合[あいあ]い 傘[がさ]"
    assert format_output("あいあい傘", "あいあいがさ") == "あいあい 傘[がさ]"
    assert format_output("今は", "いまわ") == " 今[いま]は"
    print("Done.")
