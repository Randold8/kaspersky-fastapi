from pathlib import Path

from openpyxl import Workbook

from app.infrastructure.stats_storage import SQLiteStatsStorage


class XlsxReportWriter:
    def write(
        self,
        output_path: Path,
        storage: SQLiteStatsStorage,
        line_count: int,
    ) -> None:
        workbook = Workbook(write_only=True)
        sheet = workbook.create_sheet(title="report")

        sheet.append(
            [
                "словоформа",
                "кол-во во всём документе",
                "кол-во словоформ в каждой строке",
            ]
        )

        for lemma, total in storage.iter_totals():
            line_counts = storage.get_line_counts(lemma)
            counts_as_string = ",".join(
                str(line_counts.get(line_no, 0))
                for line_no in range(1, line_count + 1)
            )
            sheet.append([lemma, total, counts_as_string])

        workbook.save(output_path)
