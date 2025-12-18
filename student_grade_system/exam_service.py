"""考试管理服务。"""
from __future__ import annotations

from typing import Dict, List

from .file_store import load_exams, save_exams
from .models import find_exam, is_unique_exam, next_exam_id


def list_exams() -> List[Dict[str, str]]:
    return load_exams()


def add_exam(exam: Dict[str, str]) -> Dict[str, str]:
    exams = load_exams()
    exam_id = next_exam_id(exams)
    exam["exam_id"] = exam_id
    if not is_unique_exam(exams, exam.get("title", "")):
        return {}
    exams.append(exam)
    save_exams(exams)
    return exam


def update_exam(exam_id: str, updates: Dict[str, str]) -> bool:
    exams = load_exams()
    exam = find_exam(exams, exam_id)
    if not exam:
        return False
    for key, value in updates.items():
        exam[key] = value
    save_exams(exams)
    return True


def delete_exam(exam_id: str) -> bool:
    exams = load_exams()
    filtered: List[Dict[str, str]] = []
    found = False
    for exam in exams:
        if str(exam.get("exam_id")) == str(exam_id):
            found = True
            continue
        filtered.append(exam)
    if not found:
        return False
    save_exams(filtered)
    return True
