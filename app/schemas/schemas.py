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
    id: int
    task_id: int
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