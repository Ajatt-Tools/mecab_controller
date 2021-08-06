# Mecab controller

Mecab controller is a simple wrapper around
[mecab](https://github.com/taku910/mecab).
It can be used to generate furigana for Japanese words and sentences.

Example:

```
>>> import mecab_controller
>>> mecab = mecab_controller.MecabController()
>>> print(mecab.reading('昨日すき焼きを食べました'))
昨日[きのう]すき 焼[や]きを 食[た]べました
```

Originally based on
[Japanese support](https://github.com/ankitects/anki-addons/tree/main/code/japanese).
