from sqlalchemy import Column, Integer, String, ARRAY, Date, ForeignKey, DateTime, Text, Boolean, Identity, Table, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

enrollments = Table(
    "enrollments",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("users.email"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.course_id"), primary_key=True),
    Column("progress", Float, default=0.0),
    Column("completed", Boolean, default=False)
)

#users
class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, nullable=False)
    firstname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    role = Column(String, nullable=False)

    answers = relationship("Answer", back_populates="student")
    courses = relationship("Course", secondary=enrollments, back_populates="students")


#courses
class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, server_default=Identity(start=1, increment=1), nullable=False, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    

    materials = relationship("Material", back_populates="course")
    tasks = relationship("Task", back_populates="course")
    students = relationship("User", secondary=enrollments, back_populates="courses")


#материалы
class Material(Base):
    __tablename__ = "materials"

    mat_id = Column(Integer, primary_key=True, server_default=Identity(start=1, increment=1), nullable=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    content_type = Column(String, nullable=False)  
    url = Column(String, nullable=False)

    course = relationship("Course", back_populates="materials")

#дзшки
class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, server_default=Identity(start=1, increment=1), nullable=False, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    attachment_url = Column(String, nullable=True)

    course = relationship("Course", back_populates="tasks")
    answers = relationship("Answer", back_populates="task")


#ответы студентов
class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, server_default=Identity(start=1, increment=1), autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)
    student_id = Column(String, ForeignKey("users.email"), nullable=False)
    
    file_url = Column(String(500), nullable=False)      
    version = Column(Integer, default=1)                
    submitted_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Integer, nullable=True)              

    task = relationship("Task", back_populates="answers")
    student = relationship("User", back_populates="answers")