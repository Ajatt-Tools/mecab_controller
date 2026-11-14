# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import re
from types import MappingProxyType

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

# Build counter readings from the number and counter ending, adjusting both when pronunciation changes.
# For example, 六本 combines ロク and ホン, but becomes ロッポン rather than ロクホン.
# These tables provide digit readings, counter endings, and their voiced or p-sound variants.
NUMERAL_READINGS = ("", "イチ", "ニ", "サン", "ヨン", "ゴ", "ロク", "ナナ", "ハチ", "キュウ")
SHORT_COUNTER_ENDINGS = MappingProxyType({
    "個": "コ",
    "枚": "マイ",
    "本": "ホン",
    "台": "ダイ",
    "匹": "ヒキ",
    "冊": "サツ",
    "階": "カイ",
    "歳": "サイ",
    "回": "カイ",
    "杯": "ハイ",
    "分": "フン",
})
VOICED_COUNTER_ENDINGS = MappingProxyType({"本": "ボン", "匹": "ビキ", "杯": "バイ", "階": "ガイ"})
P_COUNTER_ENDINGS = MappingProxyType({"本": "ポン", "匹": "ピキ", "杯": "パイ", "分": "プン"})
NATIVE_TSU_READINGS = ("ヒトツ", "フタツ", "ミッツ", "ヨッツ", "イツツ", "ムッツ", "ナナツ", "ヤッツ", "ココノツ")

# Keep CLI demonstration data out of main() so the executable flow stays short.
DEMO_EXPRESSIONS = (
    "カリン、自分でまいた種は自分で刈り取れ",
    "昨日、林檎を2個買った。",
    "真莉、大好きだよん＾＾",
    "彼２０００万も使った。",
    "彼二千三百六十円も使った。",
    "千葉",
    "昨日すき焼きを食べました",
    "二人の美人",
    "詳細はお気軽にお問い合わせ下さい。",
    "Lorem ipsum dolor sit amet. ",
    "Съешь ещё этих мягких французских булок, да выпей же чаю.",
    "粗末な家に住んでいる",
    "向けていた目",
    "軽そうに見える",
    "相合い傘",
    "放っておけない",
    "放っておいて",
    "有り難う",
    "プールから出て",
    "一人暮らし",
    "今日は",
    "いい気分に当たって",
    "助からない。",
    "乗り込え",
    "ほほ笑む",
    "歩いた",
    "荒んだ",
    "温玉",
    "他人のアソコ弄ってる",
    "拗らせる,拗らせちゃった",
    "打付ける,打付けた",
    "遣る方無い",
    "死んだよ",
    "卵胞ホルモンと接ぎ目と足浴",
)
