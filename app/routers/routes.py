from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from app.models.models import Course, Material, Task, Answer, User
from app.schemas.schemas import AnswerResponse, CourseResponse, UserResponse
from app.another.proc import is_valid_email
import shutil
import os
from datetime import datetime

router = APIRouter(prefix="/student", tags=["Студент"])
@router.get("/courses", response_model=list[CourseResponse])
def get_my_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    
    if not courses:
        courses = []
        for i in range(1, 10):
            course = Course(title="Python от новичка до джуна", description="Полный курс")
            db.add(course)
            db.commit()
            db.refresh(course)
        
        # демо-материалы
            db.add_all([
                Material(content_type="video", url="https://youtube.com/watch?v=rfscVS0vtbw", course_id=course.course_id),
                Material(content_type="scorm", url="/static/course1.zip", course_id=course.course_id),
            ])
        # демо-задание
            db.add(Task(title="Написать Hello World", description="На любом языке", course_id=course.course_id))
            db.commit()
            courses.append(course)
    

    return courses

@router.put("/get_courses", response_model=UserResponse)
def get_some_cources(user_email: str, course_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_email).first()
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if course in user.courses:
        raise HTTPException(status_code=444, detail="Такой курс уже добавлен.")
    else:
        user.courses.append(course)
    db.commit()
    return user

@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course_detail(course_id: int, user_id: int,  db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    tasks_count = len(course.tasks)
    answers = db.query(Answer).filter(Answer.student_id == user_id, Answer.task_id in course.tasks).all()
    count_answers = len(answers)
    progress = round(count_answers / tasks_count * 100, 2)

    if not course:
        raise HTTPException(404, "Курс не найден")
    return course


@router.get("/tasks/{task_id}/my-answers", response_model=list[AnswerResponse])
def get_my_answers(task_id: int, db: Session = Depends(get_db)):
    answers = db.query(Answer).filter(Answer.task_id == task_id, Answer.student_id == 1).order_by(Answer.version).all()
    if answers:
        answers[-1].score = 95
    return answers

@router.post("/answers", response_model=AnswerResponse)
async def submit_homework(
    task_id: int,
    user_email: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # сохраняем файл
    os.makedirs("uploads", exist_ok=True)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_path = f"uploads/{filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

   
    last_version = db.query(Answer).filter(Answer.task_id == task_id, Answer.student_id == user_email).count()
    new_version = last_version + 1

    answer = AnswerResponse(
        task_id=task_id,
        student_id=user_email,  
        file_url=f"/uploads/{filename}",
        version=new_version,
        submitted_at=datetime.utcnow()
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
