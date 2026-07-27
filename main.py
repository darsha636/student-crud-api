from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models import StudentDB

app = FastAPI(
    title="Student CRUD API",
    description="My First FastAPI Project",
    version="1.0"
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Student(BaseModel):
    name: str
    age: int
    email: EmailStr


class StudentResponse(Student):
    id: int

    class Config:
        from_attributes = True


@app.get("/")
def home():
    return {"message": "Welcome to Student CRUD API"}


@app.get("/students", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(StudentDB).all()


@app.post("/students", response_model=StudentResponse)
def create_student(student: Student, db: Session = Depends(get_db)):

    existing_student = (
        db.query(StudentDB)
        .filter(StudentDB.email == student.email)
        .first()
    )

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    db_student = StudentDB(
        name=student.name,
        age=student.age,
        email=student.email
    )

    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return db_student


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):

    student = (
        db.query(StudentDB)
        .filter(StudentDB.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    updated_student: Student,
    db: Session = Depends(get_db)
):

    student = (
        db.query(StudentDB)
        .filter(StudentDB.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.name = updated_student.name
    student.age = updated_student.age
    student.email = updated_student.email

    db.commit()
    db.refresh(student)

    return student


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):

    student = (
        db.query(StudentDB)
        .filter(StudentDB.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully"
    }