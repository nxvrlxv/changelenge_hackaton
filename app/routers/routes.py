from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from app.models.models import Course, Material, Task, Answer, User
from app.schemas.schemas import AnswerResponse, CourseResponse, UserResponse
import shutil
import os
from datetime import datetime
import re
from app.another.procs import is_valid_email

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
    # Сохраняем файл
    os.makedirs("uploads", exist_ok=True)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_path = f"uploads/{filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Считаем количество существующих ответов для данного задания и студента
    last_version = db.query(Answer).filter(Answer.task_id == task_id, Answer.student_id == 1).count()
    new_version = last_version + 1

    # Создаем новый ответ
    answer = Answer(
        task_id=task_id,
        student_id=1,
        file_url=f"/uploads/{filename}",
        version=new_version,
        submitted_at=datetime.utcnow(),
        score = 0
    )

    db.add(answer)
    db.commit()
    db.refresh(answer)

    return answer

@router.post("/register_student", response_model=UserResponse)
async def reg_user(
    email: str,
    password: str,
    firstname: str,
    lastname: str,
    db: Session = Depends(get_db)
):
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Некорректный email")
    
    users = db.query(User).filter(User.email == email).first()

    if users:

        raise HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")
   
    user = User(
    email=email,
    password=password,
    firstname=firstname,
    lastname=lastname,
    role = 'student',
    answers = []

    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.get("/auth_student", response_model=UserResponse)
def get_student(email, password, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь еще не зарегистрирован")
    elif user.password != password:
         raise HTTPException(status_code=400, detail="Вы ввели неверный пароль")
    else:
        return user






