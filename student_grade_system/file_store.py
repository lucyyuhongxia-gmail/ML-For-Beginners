"""文件读写与备份工具模块。"""
from __future__ import annotations

from datetime import datetime
from importlib.util import find_spec
from pathlib import Path
import csv
import json
import shutil
from typing import Dict, Iterable, List, Optional

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backup"
LOG_DIR = BASE_DIR / "logs"

STUDENT_FILE = DATA_DIR / "students.json"
EXAM_FILE = DATA_DIR / "exams.json"
SCORE_FILE = DATA_DIR / "scores.csv"
LOG_FILE = LOG_DIR / "system.log"

# 避免在导入时抛出异常，提前探测依赖
HAS_FPDF = find_spec("fpdf") is not None
if HAS_FPDF:
    from fpdf import FPDF  # type: ignore


def ensure_directories() -> None:
    for path in (DATA_DIR, BACKUP_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def ensure_data_files() -> None:
    """确保基础数据文件存在，若缺失则创建空文件。"""
    ensure_directories()
    if not STUDENT_FILE.exists():
        STUDENT_FILE.write_text("[]", encoding="utf-8")
    if not EXAM_FILE.exists():
        EXAM_FILE.write_text("[]", encoding="utf-8")
    if not SCORE_FILE.exists():
        SCORE_FILE.write_text("exam_id,student_id,score\n", encoding="utf-8")


def load_students() -> List[Dict[str, str]]:
    ensure_data_files()
    with STUDENT_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_students(students: List[Dict[str, str]]) -> None:
    ensure_data_files()
    with STUDENT_FILE.open("w", encoding="utf-8") as f:
        json.dump(students, f, ensure_ascii=False, indent=2)


def load_exams() -> List[Dict[str, str]]:
    ensure_data_files()
    with EXAM_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_exams(exams: List[Dict[str, str]]) -> None:
    ensure_data_files()
    with EXAM_FILE.open("w", encoding="utf-8") as f:
        json.dump(exams, f, ensure_ascii=False, indent=2)


def load_scores() -> List[Dict[str, str]]:
    ensure_data_files()
    scores: List[Dict[str, str]] = []
    with SCORE_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("exam_id") and row.get("student_id"):
                scores.append({
                    "exam_id": row.get("exam_id", ""),
                    "student_id": row.get("student_id", ""),
                    "score": row.get("score", ""),
                })
    return scores


def save_scores(scores: Iterable[Dict[str, str]]) -> None:
    ensure_data_files()
    with SCORE_FILE.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["exam_id", "student_id", "score"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in scores:
            writer.writerow({
                "exam_id": row.get("exam_id", ""),
                "student_id": row.get("student_id", ""),
                "score": row.get("score", ""),
            })


def append_log(message: str) -> None:
    ensure_directories()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def backup_data(target_dir: Optional[Path] = None) -> Path:
    """复制数据文件到备份目录。"""
    ensure_data_files()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = target_dir or (BACKUP_DIR / timestamp)
    destination.mkdir(parents=True, exist_ok=True)
    for file_path in (STUDENT_FILE, EXAM_FILE, SCORE_FILE):
        shutil.copy2(file_path, destination / file_path.name)
    return destination


def restore_backup(backup_dir: Path) -> None:
    """将备份文件恢复到数据目录。"""
    ensure_data_files()
    for source in backup_dir.iterdir():
        if source.name in {STUDENT_FILE.name, EXAM_FILE.name, SCORE_FILE.name}:
            shutil.copy2(source, DATA_DIR / source.name)


def export_text_report(lines: List[str], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    return output_path


def export_pdf_report(title: str, headers: List[str], rows: List[List[str]], output_path: Path) -> Path:
    if not HAS_FPDF:
        return export_text_report([title] + [" ".join(headers)] + [" ".join(row) for row in rows], output_path)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align="C")
    pdf.ln(5)
    column_width = 180 // max(1, len(headers))
    for header in headers:
        pdf.cell(column_width, 10, header, border=1)
    pdf.ln()
    for row in rows:
        for cell in row:
            pdf.cell(column_width, 10, str(cell), border=1)
        pdf.ln()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path
