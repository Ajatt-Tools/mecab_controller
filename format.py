# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import typing

try:
    from .compound_furigana import break_compound_furigana as bcf
    from .kana_conv import is_kana_char
except ImportError:
    from compound_furigana import break_compound_furigana as bcf
    from kana_conv import is_kana_char


class KanjiBoundaries(typing.NamedTuple):
    len_kana_before: int = 0
    len_kana_after: int = 0
    has_kanji: bool = True


def find_kanji_boundaries(word: str) -> KanjiBoundaries:
    """
    Return the number of kana characters before the first kanji
    and the number of kana characters after the last kanji.
    """
    len_kana_before = 0
    len_kana_after = 0
    for idx, char in enumerate(word):
        if not is_kana_char(char):
            break
        len_kana_before += 1
    if len_kana_before == len(word):
        return KanjiBoundaries(has_kanji=False)
    for idx, char in enumerate(reversed(word)):
        if not is_kana_char(char):
            break
        len_kana_after += 1
    return KanjiBoundaries(len_kana_before, len_kana_after)


def format_output(kanji: str, reading: str) -> str:
    """Convert (kanji, reading) input to output that Anki understands: kanji[reading]"""
    # strip matching characters and beginning and end of reading and kanji
    # reading should always be at least as long as the kanji
    match find_kanji_boundaries(kanji):
        case KanjiBoundaries(has_kanji=False):
            return kanji
        case KanjiBoundaries(len_kana_before=0, len_kana_after=0):
            return bcf(f" {kanji}[{reading}]")
        case KanjiBoundaries(len_kana_before=0, len_kana_after=n_after):
            return bcf(f" {kanji[:-n_after]}[{reading[:-n_after]}]{kanji[-n_after:]}")
        case KanjiBoundaries(len_kana_before=n_before, len_kana_after=0):
            return bcf(f"{kanji[:n_before]} {kanji[n_before:]}[{reading[n_before:]}]")
        case KanjiBoundaries(len_kana_before=n_before, len_kana_after=n_after):
            return bcf(f"{kanji[:n_before]} {kanji[n_before:-n_after]}[{reading[n_before:-n_after]}]{kanji[-n_after:]}")
    raise RuntimeError("unreachable")


if __name__ == "__main__":
    assert find_kanji_boundaries("秘訣") == (0, 0, True)
    assert find_kanji_boundaries("食べた") == (0, 2, True)
    assert find_kanji_boundaries("サイン会") == (3, 0, True)
    assert find_kanji_boundaries("取って置き") == (0, 1, True)
    assert find_kanji_boundaries("ほほ笑む") == (2, 1, True)
    assert find_kanji_boundaries("相合い傘") == (0, 0, True)
    assert find_kanji_boundaries("ひらがな") == (0, 0, False)
    print("1 Done.")
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
    assert format_output("ほほ笑む", "ほおえむ") == "ほほ 笑[え]む"
    assert format_output("ほほ笑む", "ほほえむ") == "ほほ 笑[え]む"
    assert format_output("ほほえむ", "ほほえむ") == "ほほえむ"
    print("2 Done.")
