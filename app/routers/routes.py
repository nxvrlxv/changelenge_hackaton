from fastapi import APIRouter, Depends, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from app.models.models import Course, Material, Task, Answer
from app.schemas import CourseResponse, AnswerCreate

router = APIRouter()