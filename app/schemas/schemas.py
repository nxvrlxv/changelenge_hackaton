from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum

class _Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class MaterialResponse(_Base):
    mat_id: int
    course_id: int
    content_type: str
    url: str

class AnswerResponse(_Base):
    answer_id: int
    task_id: int
    student_id: str
    file_url: str
    version: int = 1
    submitted_at: datetime
    score: int = 0

class TaskResponse(_Base):
    task_id: int
    course_id: int
    title: str
    description: Optional[str] = None
    attachment_url: Optional[str] = None
    answers: Optional[List[AnswerResponse]] = []

class CourseResponse(_Base):
    course_id: int
    title: str
    description: str
    materials: List[MaterialResponse] = []
    tasks: List[TaskResponse] = []

class UserResponse(_Base):
    email: str
    password: str
    firstname: str
    lastname : str
    role: str
    answers: List[AnswerResponse] = []
    courses: List[CourseResponse] = []

class AnswerCreate(_Base):
    task_id: int
    student_id: str
    file_url: str
    version: int
    submitted_at: datetime
    score: int | None = None

class progressBar(_Base):
    progress: float
    progress_display: str
    progress_bar: str
    tasks_total: int
    tasks_completed: int

class AnswerScoreResponse(BaseModel):
    answer_id: int
    version: int
    score: int
    teacher_comment: Optional[str]

class TaskWithScoreResponse(BaseModel):
    task_id: int
    task_title: str
    answer: AnswerScoreResponse

class CourseWithScoresResponse(BaseModel):
    course_id: int
    course_title: str
    tasks: List[TaskWithScoreResponse]