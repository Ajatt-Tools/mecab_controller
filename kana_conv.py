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

__all__ = ['to_katakana', 'to_hiragana', 'is_kana_word']

_hiragana = [
    'が', 'ぎ', 'ぐ', 'げ', 'ご',
    'ざ', 'じ', 'ず', 'ぜ', 'ぞ',
    'だ', 'ぢ', 'づ', 'で', 'ど',
    'ば', 'び', 'ぶ', 'べ', 'ぼ',
    'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ',
    'あ', 'い', 'う', 'え', 'お',
    'か', 'き', 'く', 'け', 'こ',
    'さ', 'し', 'す', 'せ', 'そ',
    'た', 'ち', 'つ', 'て', 'と',
    'な', 'に', 'ぬ', 'ね', 'の',
    'は', 'ひ', 'ふ', 'へ', 'ほ',
    'ま', 'み', 'む', 'め', 'も',
    'や', 'ゆ', 'よ',
    'ら', 'り', 'る', 'れ', 'ろ',
    'わ', 'を', 'ん',
    'ぁ', 'ぃ', 'ぅ', 'ぇ', 'ぉ',
    'ゃ', 'ゅ', 'ょ',
    'っ',
]
_katakana = [
    'ガ', 'ギ', 'グ', 'ゲ', 'ゴ',
    'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ',
    'ダ', 'ヂ', 'ヅ', 'デ', 'ド',
    'バ', 'ビ', 'ブ', 'ベ', 'ボ',
    'パ', 'ピ', 'プ', 'ペ', 'ポ',
    'ア', 'イ', 'ウ', 'エ', 'オ',
    'カ', 'キ', 'ク', 'ケ', 'コ',
    'サ', 'シ', 'ス', 'セ', 'ソ',
    'タ', 'チ', 'ツ', 'テ', 'ト',
    'ナ', 'ニ', 'ヌ', 'ネ', 'ノ',
    'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
    'マ', 'ミ', 'ム', 'メ', 'モ',
    'ヤ', 'ユ', 'ヨ',
    'ラ', 'リ', 'ル', 'レ', 'ロ',
    'ワ', 'ヲ', 'ン',
    'ァ', 'ィ', 'ゥ', 'ェ', 'ォ',
    'ャ', 'ュ', 'ョ',
    'ッ',
]
_kana = _hiragana + _katakana

katakana_to_hiragana = dict(zip(_katakana, _hiragana))
hiragana_to_katakana = {y: x for x, y in katakana_to_hiragana.items()}


def to_hiragana(katakana: str) -> str:
    return ''.join(katakana_to_hiragana.get(k, k) for k in katakana)


def to_katakana(hiragana: str) -> str:
    return ''.join(hiragana_to_katakana.get(h, h) for h in hiragana)


def is_kana_word(word: str) -> bool:
    return sum(map(lambda char: int(char in _kana or char == 'ー'), word)) == len(word)


def main():
    print(to_hiragana('オープンソース形態素解析エンジンです。'))
    print(to_katakana('お前はもう死んでいる。'))
    print(is_kana_word('ひらがなカタカナ'), is_kana_word('ニュース'), is_kana_word('故郷は'))


if __name__ == '__main__':
    main()
