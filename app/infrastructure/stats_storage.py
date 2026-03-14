import sqlite3
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

from app.core.config import SQLITE_COMMIT_EVERY


class SQLiteStatsStorage:
    def __init__(self, db_path: Path) -> None:
        self._connection = sqlite3.connect(db_path)
        self._connection.execute("PRAGMA journal_mode=WAL;")
        self._connection.execute("PRAGMA synchronous=NORMAL;")
        self._create_tables()
        self._pending_lines = 0

    def __enter__(self) -> "SQLiteStatsStorage":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _create_tables(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS word_totals (
                lemma TEXT PRIMARY KEY,
                total INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS word_line_counts (
                lemma TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                count INTEGER NOT NULL,
                PRIMARY KEY (lemma, line_no)
            );
            """
        )
        self._connection.commit()

    def add_line_counts(self, line_no: int, counts: Counter[str]) -> None:
        if counts:
            totals_rows = list(counts.items())
            line_rows = [(lemma, line_no, count) for lemma, count in counts.items()]

            self._connection.executemany(
                """
                INSERT INTO word_totals (lemma, total)
                VALUES (?, ?)
                ON CONFLICT(lemma) DO UPDATE SET
                    total = total + excluded.total
                """,
                totals_rows,
            )

            self._connection.executemany(
                """
                INSERT INTO word_line_counts (lemma, line_no, count)
                VALUES (?, ?, ?)
                ON CONFLICT(lemma, line_no) DO UPDATE SET
                    count = count + excluded.count
                """,
                line_rows,
            )

        self._pending_lines += 1
        if self._pending_lines >= SQLITE_COMMIT_EVERY:
            self.commit()

    def commit(self) -> None:
        if self._pending_lines:
            self._connection.commit()
            self._pending_lines = 0

    def iter_totals(self) -> Iterator[tuple[str, int]]:
        self.commit()
        cursor = self._connection.execute(
            """
            SELECT lemma, total
            FROM word_totals
            ORDER BY lemma
            """
        )
        yield from cursor

    def get_line_counts(self, lemma: str) -> dict[int, int]:
        cursor = self._connection.execute(
            """
            SELECT line_no, count
            FROM word_line_counts
            WHERE lemma = ?
            ORDER BY line_no
            """,
            (lemma,),
        )
        return {line_no: count for line_no, count in cursor.fetchall()}

    def close(self) -> None:
        self.commit()
        self._connection.close()
