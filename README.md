# Mecab controller

Mecab controller is a simple wrapper around
[mecab](https://github.com/taku910/mecab).
It was created primarily to be used in
[AJT Japanese](https://ankiweb.net/shared/info/1344485230),
an Anki add-on
that generates furigana for Japanese text.

Example of standalone usage:

```
>>> import mecab_controller
>>> mecab = mecab_controller.MecabController()
>>> print(mecab.reading('昨日すき焼きを食べました'))
昨日[きのう]すき 焼[や]きを 食[た]べました
```

Originally based on
[Japanese support](https://github.com/ankitects/anki-addons/tree/main/code/japanese).
