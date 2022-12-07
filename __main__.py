from .mecab_controller import MecabController

mecab = MecabController()

expr = "カリン、自分でまいた種は自分で刈り取れ"
print(mecab.reading(expr))
expr = "昨日、林檎を2個買った。"
print(mecab.reading(expr))
expr = "真莉、大好きだよん＾＾"
print(mecab.reading(expr))
expr = "彼２０００万も使った。"
print(mecab.reading(expr))
expr = "彼二千三百六十円も使った。"
print(mecab.reading(expr))
expr = "千葉"
print(mecab.reading(expr))
expr = "昨日すき焼きを食べました"
print(mecab.reading(expr))
expr = "二人の美人"
print(mecab.reading(expr))
expr = "詳細はお気軽にお問い合わせ下さい。"
print(mecab.reading(expr))
