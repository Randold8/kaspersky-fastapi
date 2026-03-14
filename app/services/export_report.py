from dataclasses import dataclass
from pathlib import Path
import uuid

from app.core.config import TEMP_DIR
from app.domain.text_processing import count_normalized_words_in_line, iter_file_lines
from app.infrastructure.morphology import PymorphyNormalizer
from app.infrastructure.stats_storage import SQLiteStatsStorage
from app.infrastructure.xlsx_writer import XlsxReportWriter


@dataclass(frozen=True)
class ExportResult:
    output_path: Path
    filename: str


class ExportReportService:
    def __init__(self) -> None:
        self._normalizer = PymorphyNormalizer()
        self._writer = XlsxReportWriter()

    def export(self, source_path: Path) -> ExportResult:
        job_id = uuid.uuid4().hex
        db_path = TEMP_DIR / f"{job_id}.sqlite3"
        output_path = TEMP_DIR / f"{job_id}.xlsx"

        line_count = 0

        try:
            with SQLiteStatsStorage(db_path) as storage:
                for line_no, line in iter_file_lines(source_path):
                    counts = count_normalized_words_in_line(line, self._normalizer)
                    storage.add_line_counts(line_no, counts)
                    line_count = line_no

                storage.commit()
                self._writer.write(output_path, storage, line_count)

            return ExportResult(
                output_path=output_path,
                filename="report.xlsx",
            )
        finally:
            db_path.unlink(missing_ok=True)
