# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

# Japanese units group large numbers by ten thousand, not by one thousand.
# https://en.wikipedia.org/wiki/Japanese_numerals#Powers_of_10
JAPANESE_DIGITS = "零一二三四五六七八九"
ARABIC_DIGITS = "0123456789"
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
