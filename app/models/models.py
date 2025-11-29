from sqlalchemy import Column, Integer, String, ARRAY, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

#users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    role = Column(String, nullable=False)


#courses
class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    materials = relationship("Material", back_populates="course")
    tasks = relationship("Task", back_populates="course")


#материалы
class Material(Base):
    __tablename__ = "materials"

    mat_id = Column(Integer, primary_key=True, nullable=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    content_type = Column(String, nullable=False)  
    url = Column(String, nullable=False)

    course = relationship("Course", back_populates="materials")

#дзшки
class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    attachment_url = Column(String, nullable=True)

    course = relationship("Course", back_populates="tasks")


#ответы студентов
class Answer(Base):
    __tablename__ = "answers"

    answer_id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id