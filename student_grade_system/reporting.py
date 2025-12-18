"""控制台输出与报表导出。"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .file_store import export_pdf_report


def format_table(headers: List[str], rows: List[List[str]]) -> List[str]:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            if len(str(cell)) > widths[index]:
                widths[index] = len(str(cell))
    lines: List[str] = []
    header_line = " | ".join(header.ljust(widths[i]) for i, header in enumerate(headers))
    lines.append(header_line)
    lines.append("-+-".join("-" * width for width in widths))
    for row in rows:
        line = " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
        lines.append(line)
    return lines


def print_table(headers: List[str], rows: List[List[str]]) -> None:
    for line in format_table(headers, rows):
        print(line)


def export_report(title: str, headers: List[str], rows: List[List[str]], output: Path) -> Path:
    return export_pdf_report(title, headers, rows, output)


def score_rows_for_exam(exam_id: str, ranking: List[Dict[str, str]]) -> List[List[str]]:
    rows: List[List[str]] = []
    for item in ranking:
        rows.append([str(item.get("rank", "")), item.get("student_id", ""), str(item.get("score", ""))])
    return rows
