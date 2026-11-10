# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import re

# Japanese units group large numbers by ten thousand, not by one thousand.
# https://en.wikipedia.org/wiki/Japanese_numerals#Powers_of_10
JAPANESE_DIGITS = "零一二三四五六七八九"
ARABIC_DIGITS = "0123456789"
FULL_WIDTH_DIGITS = "０１２３４５６７８９"
JAPANESE_NUMBER_UNITS = (
    (10**16, "京"),
    (10**12, "兆"),
    (10**8, "億"),
    (10**4, "万"),
    (1000, "千"),
    (100, "百"),
    (10, "十"),
)
MAX_NUMERAL_VALUE = 10**20
NUMERAL_CACHE_SIZE = 16384
ARAB_TO_FULL_WIDTH_DIGITS = str.maketrans(ARABIC_DIGITS, FULL_WIDTH_DIGITS)
RE_NUMERAL = re.compile(r"[0-9０-９零〇一二三四五六七八九十百千万億兆京]+")
KANJI_TO_DIGITS = str.maketrans(JAPANESE_DIGITS + "〇", ARABIC_DIGITS + "0")
