import re
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol


WORD_RE = re.compile(r"[А-Яа-яA-Za-zЁё]+")


class WordNormalizer(Protocol):
    def normalize(self, word: str) -> str:
        ...


def extract_words(text: str) -> list[str]:
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def count_normalized_words_in_line(
    text: str,
    normalizer: WordNormalizer,
) -> Counter[str]:
    return Counter(normalizer.normalize(word) for word in extract_words(text))


def iter_file_lines(path: Path) -> Iterator[tuple[int, str]]:
    with path.open("r", encoding="utf-8", errors="ignore") as file:
        for line_no, line in enumerate(file, start=1):
            yield line_no, line
