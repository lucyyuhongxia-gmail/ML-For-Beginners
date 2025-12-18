"""排序与排名模块，使用基础算法。"""
from __future__ import annotations

from typing import Dict, List

from .file_store import load_scores
from .student_service import list_students


def selection_sort_desc(pairs: List[Dict[str, str]]) -> None:
    length = len(pairs)
    for i in range(length):
        max_index = i
        for j in range(i + 1, length):
            if float(pairs[j]["score"]) > float(pairs[max_index]["score"]):
                max_index = j
        if max_index != i:
            pairs[i], pairs[max_index] = pairs[max_index], pairs[i]


def exam_ranking(exam_id: str) -> List[Dict[str, str]]:
    rows = []
    for row in load_scores():
        if row.get("exam_id") == str(exam_id) and row.get("score") != "":
            rows.append({"student_id": row["student_id"], "score": row["score"]})
    selection_sort_desc(rows)
    for index, row in enumerate(rows):
        row["rank"] = index + 1
    return rows


def average_ranking() -> List[Dict[str, str]]:
    students = list_students()
    student_scores: List[Dict[str, str]] = []
    for student in students:
        total = 0.0
        count = 0
        for row in load_scores():
            if row.get("student_id") == student.get("id") and row.get("score") != "":
                total += float(row["score"])
                count += 1
        if count > 0:
            student_scores.append({"student_id": student.get("id", ""), "avg": total / count})
    # 插入排序按平均分降序
    for i in range(1, len(student_scores)):
        key_item = student_scores[i]
        j = i - 1
        while j >= 0 and student_scores[j]["avg"] < key_item["avg"]:
            student_scores[j + 1] = student_scores[j]
            j -= 1
        student_scores[j + 1] = key_item
    for index, row in enumerate(student_scores):
        row["rank"] = index + 1
        row["avg"] = float(f"{row['avg']:.1f}")
    return student_scores
