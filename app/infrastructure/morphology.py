from functools import lru_cache

import pymorphy3


class PymorphyNormalizer:
    def __init__(self) -> None:
        self._morph = pymorphy3.MorphAnalyzer()

    @lru_cache(maxsize=200_000)
    def normalize(self, word: str) -> str:
        return self._morph.parse(word)[0].normal_form
