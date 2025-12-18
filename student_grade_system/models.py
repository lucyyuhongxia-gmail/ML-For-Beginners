"""核心数据结构与校验函数。"""
from __future__ import annotations

from typing import Dict, List, Optional


def find_student(students: List[Dict[str, str]], student_id: str) -> Optional[Dict[str, str]]:
    for student in students:
        if student.get("id") == student_id:
            return student
    return None


def find_exam(exams: List[Dict[str, str]], exam_id: str) -> Optional[Dict[str, str]]:
    for exam in exams:
        if str(exam.get("exam_id")) == str(exam_id):
            return exam
    return None


def is_unique_student(students: List[Dict[str, str]], student_id: str) -> bool:
    return find_student(students, student_id) is None


def is_unique_exam(exams: List[Dict[str, str]], title: str) -> bool:
    for exam in exams:
        if exam.get("title") == title:
            return False
    return True


def validate_score(value: str) -> bool:
    try:
        score = float(value)
    except ValueError:
        return False
    return 0.0 <= score <= 100.0


def normalize_score(value: str) -> str:
    return f"{float(value):.1f}"


def next_exam_id(exams: List[Dict[str, str]]) -> int:
    max_id = 0
    for exam in exams:
        try:
            current = int(exam.get("exam_id", 0))
            if current > max_id:
                max_id = current
        except ValueError:
            continue
    return max_id + 1
