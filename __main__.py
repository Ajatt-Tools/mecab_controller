from .mecab_controller import MecabController

mecab = MecabController()

expr = u"カリン、自分でまいた種は自分で刈り取れ"
print(mecab.reading(expr))
expr = u"昨日、林檎を2個買った。"
print(mecab.reading(expr))
expr = u"真莉、大好きだよん＾＾"
print(mecab.reading(expr))
expr = u"彼２０００万も使った。"
print(mecab.reading(expr))
expr = u"彼二千三百六十円も使った。"
print(mecab.reading(expr))
expr = u"千葉"
print(mecab.reading(expr))
