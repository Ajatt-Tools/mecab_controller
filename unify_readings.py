# Copyright: Ren Tatsumoto <tatsu at autistici.org> and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import unicodedata

try:
    from .kana_conv import to_katakana
except ImportError:
    from kana_conv import to_katakana

EQUIVALENT_SOUNDS = {
    "このうえ": "[この][うえ]",  # corner case fix.
    "ふうう": "ふーう",
    "いまは": "いまわ",
    "おおう": "おーう",
    "じゃあ": "じゃー",
    "じゅう": "じゅー",
    "じょう": "じょー",
    "つづ": "つず",
    "ぼお": "ぼー",
    "もお": "もー",
    "れい": "れー",
    "めい": "めー",
    "べい": "べー",
    "けい": "けー",
    "ぐう": "ぐー",
    "ごう": "ごー",
    "ずう": "ずー",
    "づう": "ずー",
    "づー": "ずー",
    "ぞう": "ぞー",
    "どう": "どー",
    "どお": "どー",
    "ぶう": "ぶー",
    "ぼう": "ぼー",
    "ぷう": "ぷー",
    "ぽう": "ぽー",
    "うう": "うー",
    "おう": "おー",
    "おお": "おー",
    "くう": "くー",
    "こう": "こー",
    "すう": "すー",
    "そう": "そー",
    "つう": "つー",
    "とう": "とー",
    "とお": "とー",
    "こお": "こー",
    "ぬう": "ぬー",
    "のう": "のー",
    "ふう": "ふー",
    "ほう": "ほー",
    "ほお": "ほー",
    "むう": "むー",
    "もう": "もー",
    "よう": "よー",
    "るう": "るー",
    "ろう": "ろー",
    "ぅう": "ぅー",
    "ぉう": "ぉー",
    "ょう": "ょー",
    "ゆう": "ゆー",
    "いい": "いー",
    "ちい": "ちー",
    "せい": "せー",
    "じい": "じー",
    "かあ": "かー",
    "ゅう": "ゅー",
    "ぜい": "ぜー",
    "よお": "よー",
    "ねえ": "ねー",
    "にい": "にー",
    "ばあ": "ばー",
    "らあ": "らー",
    "ごお": "ごー",
    "ひい": "ひー",
    "へい": "ヘー",
    "しい": "しー",
    "さあ": "さー",
    "れえ": "れー",
    "ぱあ": "ぱー",
    "てい": "てー",
    "ぢ": "じ",
    "づ": "ず",
    "を": "お",
    "ゔ": "ぶ",
    "[この][うえ]": "このうえ",
}
EQUIVALENT_SOUNDS |= {to_katakana(key): to_katakana(val) for key, val in EQUIVALENT_SOUNDS.items()}


def unify_repr(reading: str) -> str:
    """
    NHK pitch accents file contains entries with redundant readings.
    They only differ by the use of 'ー' or kana characters that sound the same.
    Try to de-duplicate them.
    """
    for key, value in EQUIVALENT_SOUNDS.items():
        if key in reading:
            reading = reading.replace(key, value)
    return reading


def replace_handakuten(reading: str) -> str:
    # corner cases for some entries present in the NHK 2016 audio source
    return (
        reading.replace("か゚", "が")
        .replace("カ゚", "ガ")
        .replace("き゚", "ぎ")
        .replace("キ゚", "ギ")
        .replace("く゚", "ぐ")
        .replace("ク゚", "グ")
        .replace("け゚", "げ")
        .replace("ケ゚", "ゲ")
        .replace("こ゚", "ご")
        .replace("コ゚", "ゴ")
    )


def literal_pronunciation(text: str) -> str:
    """Return a canonical katakana pronunciation across Unicode, vowel, nasal, and compound spellings."""
    # NFKC expands half-width kana and middle dots before compound separators are removed.
    # https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize
    text = unicodedata.normalize("NFKC", text)
    # Mixed-script リょウシん needs a single script before long-vowel matching to produce リョーシン in one pass.
    return unify_repr(replace_handakuten(to_katakana(text.replace("・", "")))) or text


def main() -> None:
    assert unify_repr("おおうなばら") == "おーうなばら"
    assert unify_repr("おはよう") == "おはよー"
    assert unify_repr("おお") == "おー"
    assert unify_repr("よじょうはん") == "よじょーはん"
    assert unify_repr("たましい") == "たましー"
    assert unify_repr("コノウエ") == "コノウエ"
    assert literal_pronunciation("がっこう") == "ガッコー"
    assert literal_pronunciation("イマハ") == "イマワ"
    assert literal_pronunciation("リュウ") == "リュー"
    assert literal_pronunciation("リょウシん") == "リョーシン"
    assert literal_pronunciation("コ゚ょウシん") == "ゴョーシン"
    assert literal_pronunciation("コ゚ょく゚シん") == "ゴョグシン"
    assert literal_pronunciation("ﾘｮｳｼﾝ") == "リョーシン"
    assert literal_pronunciation("ｷｼ･ｶｲｾｲ") == "キシカイセー"
    print("Ok.")


if __name__ == "__main__":
    main()
