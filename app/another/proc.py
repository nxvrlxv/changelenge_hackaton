import re
from collections import defaultdict
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.models import Course, Task, Answer
from database import get_db
from fastapi import Depends


def is_valid_email(email: str) -> bool:
    # Регулярное выражение для проверки email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.fullmatch(pattern, email) is not None



def format_student_scores(results):
    # Группируем по курсам
    courses_data = defaultdict(list)
    for course, task, answer in results:
        courses_data[course.course_id].append({
            "task_id": task.task_id,
            "task_title": task.title,
            "answer_id": answer.id,
            "score": answer.score,
            "version": answer.version,
            "teacher_comment": answer.teacher_comment,
        })

    # Формируем итоговый список
    formatted_results = [
        {
            "course_id": course_id,
            "course_title": next(course.title for course, _, _ in results if course.course_id == course_id),
            "tasks": tasks_data,
        }
        for course_id, tasks_data in courses_data.items()
    ]

    return formatted_results



def get_student_scores_by_course(student_email: str, db: Session = Depends(get_db)):
    # Подзапрос для получения последней версии ответа для каждой задачи
    latest_answers_subquery = (
        db.query(
            Answer.task_id,
            func.max(Answer.version).label("max_version")
        )
        .filter(Answer.student_id == student_email)
        .group_by(Answer.task_id)
        .subquery()
    )

    # Основной запрос: курсы → задачи → последние ответы студента
    results = (
        db.query(Course, Task, Answer)
        .join(Task, Task.course_id == Course.course_id)
        .join(Answer, Answer.task_id == Task.task_id)
        .join(
            latest_answers_subquery,
            (Answer.task_id == latest_answers_subquery.c.task_id) &
            (Answer.version == latest_answers_subquery.c.max_version)
        )
        .filter(
            Answer.student_id == student_email,
            Answer.score.isnot(None)  # Только ответы с оценкой
        )
        .order_by(Course.course_id, Task.task_id)
        .all()
    )

    return results