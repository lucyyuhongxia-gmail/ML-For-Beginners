"""控制台入口，演示学生成绩管理流程。"""
from __future__ import annotations

from pathlib import Path
from typing import List

from . import file_store
from .exam_service import add_exam, delete_exam, list_exams, update_exam
from .ranking import average_ranking, exam_ranking
from .reporting import export_report, print_table, score_rows_for_exam
from .score_service import add_or_update_score, stats_for_exam
from .student_service import add_student, delete_student, list_students, search_students, update_student


MENU = """
============================
学生成绩管理系统（示例版）
1. 学生管理
2. 考试管理
3. 成绩与统计
4. 生成报表
5. 数据备份
0. 退出
============================
选择功能：
"""


SUB_MENUS = {
    "1": "1) 新增学生 2) 列表 3) 搜索 4) 修改 5) 删除",
    "2": "1) 新增考试 2) 列表 3) 修改 4) 删除",
    "3": "1) 录入成绩 2) 单次排名 3) 平均排名 4) 考试统计",
    "4": "1) 导出单次考试报表 2) 导出平均分报表",
}


REPORT_DIR = Path(__file__).resolve().parent / "reports"


def prompt(text: str) -> str:
    return input(text).strip()


def handle_student_menu(option: str) -> None:
    if option == "1":
        student_id = prompt("学号：")
        name = prompt("姓名：")
        clazz = prompt("班级：")
        phone = prompt("联系方式(可空)：")
        if add_student({"id": student_id, "name": name, "class": clazz, "phone": phone}):
            print("新增成功。")
        else:
            print("学号已存在，新增失败。")
    elif option == "2":
        students = list_students()
        rows = [[s.get("id", ""), s.get("name", ""), s.get("class", ""), s.get("phone", "")] for s in students]
        print_table(["学号", "姓名", "班级", "电话"], rows)
    elif option == "3":
        keyword = prompt("输入学号或姓名关键字：")
        results = search_students(keyword)
        rows = [[s.get("id", ""), s.get("name", ""), s.get("class", ""), s.get("phone", "")] for s in results]
        print_table(["学号", "姓名", "班级", "电话"], rows)
    elif option == "4":
        student_id = prompt("学号：")
        name = prompt("新姓名(回车跳过)：")
        clazz = prompt("新班级(回车跳过)：")
        phone = prompt("新电话(回车跳过)：")
        updates = {}
        if name:
            updates["name"] = name
        if clazz:
            updates["class"] = clazz
        if phone:
            updates["phone"] = phone
        if update_student(student_id, updates):
            print("修改成功。")
        else:
            print("未找到学生。")
    elif option == "5":
        student_id = prompt("学号：")
        if delete_student(student_id):
            print("已删除学生（关联成绩请手动清理）。")
        else:
            print("未找到学生。")


def handle_exam_menu(option: str) -> None:
    if option == "1":
        title = prompt("考试名称：")
        date = prompt("日期(YYYY-MM-DD)：")
        note = prompt("备注：")
        exam = add_exam({"title": title, "date": date, "note": note})
        if exam:
            print(f"创建成功，考试ID: {exam.get('exam_id')}")
        else:
            print("考试名称重复，创建失败。")
    elif option == "2":
        rows = [[e.get("exam_id", ""), e.get("title", ""), e.get("date", ""), e.get("note", "")] for e in list_exams()]
        print_table(["考试ID", "名称", "日期", "备注"], rows)
    elif option == "3":
        exam_id = prompt("考试ID：")
        title = prompt("新名称(可空)：")
        date = prompt("新日期(可空)：")
        note = prompt("新备注(可空)：")
        updates = {}
        if title:
            updates["title"] = title
        if date:
            updates["date"] = date
        if note:
            updates["note"] = note
        if update_exam(exam_id, updates):
            print("修改成功。")
        else:
            print("未找到考试。")
    elif option == "4":
        exam_id = prompt("考试ID：")
        if delete_exam(exam_id):
            print("删除成功（请同步清理成绩文件）。")
        else:
            print("未找到考试。")


def handle_score_menu(option: str) -> None:
    if option == "1":
        exam_id = prompt("考试ID：")
        student_id = prompt("学号：")
        score_value = prompt("成绩：")
        if add_or_update_score(exam_id, student_id, score_value):
            print("成绩已保存。")
        else:
            print("保存失败，请检查学号/考试或成绩格式。")
    elif option == "2":
        exam_id = prompt("考试ID：")
        ranking = exam_ranking(exam_id)
        rows: List[List[str]] = []
        for item in ranking:
            rows.append([item.get("rank", ""), item.get("student_id", ""), item.get("score", "")])
        print_table(["名次", "学号", "成绩"], rows)
    elif option == "3":
        ranking = average_ranking()
        rows: List[List[str]] = []
        for item in ranking:
            rows.append([item.get("rank", ""), item.get("student_id", ""), item.get("avg", "")])
        print_table(["名次", "学号", "平均分"], rows)
    elif option == "4":
        exam_id = prompt("考试ID：")
        stats = stats_for_exam(exam_id)
        print_table(["项目", "数值"], [["最高分", stats["max"]], ["最低分", stats["min"]], ["平均分", f"{stats['avg']:.1f}"], ["成绩数", stats["count"]]])


def handle_report_menu(option: str) -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    if option == "1":
        exam_id = prompt("考试ID：")
        ranking = exam_ranking(exam_id)
        headers = ["名次", "学号", "成绩"]
        rows = score_rows_for_exam(exam_id, ranking)
        output = REPORT_DIR / f"exam_{exam_id}.pdf"
        export_report(f"考试 {exam_id} 成绩单", headers, rows, output)
        print(f"报表已生成：{output}")
    elif option == "2":
        ranking = average_ranking()
        headers = ["名次", "学号", "平均分"]
        rows: List[List[str]] = []
        for item in ranking:
            rows.append([str(item.get("rank", "")), item.get("student_id", ""), str(item.get("avg", ""))])
        output = REPORT_DIR / "average.pdf"
        export_report("平均分排名", headers, rows, output)
        print(f"报表已生成：{output}")


def handle_backup() -> None:
    backup_path = file_store.backup_data()
    print(f"已备份到 {backup_path}")


def main() -> None:
    file_store.ensure_data_files()
    while True:
        choice = prompt(MENU)
        if choice == "0":
            print("感谢使用，再见！")
            break
        if choice not in SUB_MENUS:
            print("无效输入，请重新选择。")
            continue
        sub = prompt(SUB_MENUS[choice] + " ：")
        if choice == "1":
            handle_student_menu(sub)
        elif choice == "2":
            handle_exam_menu(sub)
        elif choice == "3":
            handle_score_menu(sub)
        elif choice == "4":
            handle_report_menu(sub)
        elif choice == "5":
            handle_backup()


if __name__ == "__main__":
    main()
