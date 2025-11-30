from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from app.models.models import Course, Material, Task, Answer, User
from app.schemas.schemas import AnswerResponse, CourseResponse
import shutil
import os
from datetime import datetime

router = APIRouter(prefix="/student", tags=["Студент"])
@router.get("/courses", response_model=list[CourseResponse])
def get_my_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    
    if not courses:
        course = Course(title="Python от новичка до джуна", description="Полный курс")
        db.add(course)
        db.commit()
        db.refresh(course)
        
        # демо-материалы
        db.add_all([
            Material(mat_id=1, content_type="video", url="https://youtube.com/watch?v=rfscVS0vtbw", course_id=course.course_id),
            Material(mat_id=2, content_type="scorm", url="/static/course1.zip", course_id=course.course_id),
        ])
        # демо-задание
        db.add(Task(task_id=1, title="Написать Hello World", description="На любом языке", course_id=course.course_id))
        db.commit()
        courses = [course]
    
    for c in courses:
        c.progress = 68.5
    return courses


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course_detail(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(404, "Курс не найден")
    course.progress = 72.3
    return course


@router.get("/tasks/{task_id}/my-answers", response_model=list[AnswerResponse])
def get_my_answers(task_id: int, db: Session = Depends(get_db)):
    answers = db.query(Answer).filter(Answer.task_id == task_id, Answer.student_id == 1).order_by(Answer.version).all()
    if answers:
        answers[-1].score = 95
        answers[-1].feedback = "Отличная работа! Всё правильно."
    return answers


@router.post("/answers", response_model=AnswerResponse)
async def submit_homework(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # сохраняем файл
    os.makedirs("uploads", exist_ok=True)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_path = f"uploads/{filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # считаем версию
    last_version = db.query(Answer).filter(Answer.task_id == task_id, Answer.student_id == 1).count()
    new_version = last_version + 1

    answer = Answer(
        task_id=task_id,
        student_id=1,  # на демо один студент
        file_url=f"/uploads/{filename}",
        version=new_version,
        submitted_at=datetime.utcnow()
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer