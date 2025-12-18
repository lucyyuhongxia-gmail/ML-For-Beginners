"""学生管理服务。"""
from __future__ import annotations

from typing import Dict, List

from .file_store import load_students, save_students
from .models import find_student, is_unique_student


def list_students() -> List[Dict[str, str]]:
    return load_students()


def add_student(student: Dict[str, str]) -> bool:
    students = load_students()
    if not is_unique_student(students, student.get("id", "")):
        return False
    students.append(student)
    save_students(students)
    return True


def update_student(student_id: str, updates: Dict[str, str]) -> bool:
    students = load_students()
    student = find_student(students, student_id)
    if not student:
        return False
    for key, value in updates.items():
        if key != "id":
            student[key] = value
    save_students(students)
    return True


def delete_student(student_id: str) -> bool:
    students = load_students()
    filtered: List[Dict[str, str]] = []
    found = False
    for student in students:
        if student.get("id") == student_id:
            found = True
            continue
        filtered.append(student)
    if not found:
        return False
    save_students(filtered)
    return True


def search_students(keyword: str) -> List[Dict[str, str]]:
    keyword_lower = keyword.lower()
    results: List[Dict[str, str]] = []
    for student in load_students():
        if keyword_lower in student.get("name", "").lower() or keyword_lower in student.get("id", "").lower():
            results.append(student)
    return results
