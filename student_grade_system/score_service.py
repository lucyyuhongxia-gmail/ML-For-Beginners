"""成绩管理、导入导出与统计。"""
from __future__ import annotations

from typing import Dict, List

from .file_store import append_log, load_scores, save_scores
from .models import find_exam, find_student, normalize_score, validate_score
from .student_service import list_students
from .exam_service import list_exams


def _find_score_index(scores: List[Dict[str, str]], exam_id: str, student_id: str) -> int:
    for index, row in enumerate(scores):
        if row.get("exam_id") == str(exam_id) and row.get("student_id") == student_id:
            return index
    return -1


def add_or_update_score(exam_id: str, student_id: str, score_value: str) -> bool:
    if not validate_score(score_value):
        return False
    students = list_students()
    exams = list_exams()
    if not find_student(students, student_id) or not find_exam(exams, exam_id):
        return False
    scores = load_scores()
    index = _find_score_index(scores, exam_id, student_id)
    normalized = normalize_score(score_value)
    if index >= 0:
        scores[index]["score"] = normalized
    else:
        scores.append({"exam_id": str(exam_id), "student_id": student_id, "score": normalized})
    save_scores(scores)
    return True


def import_scores(rows: List[Dict[str, str]]) -> None:
    successes = 0
    for row in rows:
        exam_id = row.get("exam_id", "")
        student_id = row.get("student_id", "")
        score_value = row.get("score", "")
        if add_or_update_score(exam_id, student_id, score_value):
            successes += 1
        else:
            append_log(f"导入失败 exam_id={exam_id}, student_id={student_id}")
    append_log(f"导入完成，成功 {successes} 条，共 {len(rows)} 条")


def export_scores() -> List[Dict[str, str]]:
    return load_scores()


def stats_for_exam(exam_id: str) -> Dict[str, float]:
    scores = [float(row["score"]) for row in load_scores() if row.get("exam_id") == str(exam_id) and row.get("score") != ""]
    if not scores:
        return {"max": 0.0, "min": 0.0, "avg": 0.0, "count": 0}
    total = 0.0
    maximum = scores[0]
    minimum = scores[0]
    for value in scores:
        total += value
        if value > maximum:
            maximum = value
        if value < minimum:
            minimum = value
    avg = total / len(scores)
    return {"max": maximum, "min": minimum, "avg": avg, "count": len(scores)}
