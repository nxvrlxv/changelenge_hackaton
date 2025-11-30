from fastapi import FastAPI
from database import init_db
from app.routers.routes import router as student_router  
import uvicorn 

app = FastAPI(
    title="Commit to Learn — Трек СТУДЕНТ",
    version="1.0"
)

app.include_router(student_router)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Трек СТУДЕНТ — всё работает! Иди в /docs"}
