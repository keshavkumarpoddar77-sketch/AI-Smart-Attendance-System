from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from attendence_py.backend import models
from attendence_py.backend import schemas
from attendence_py.backend.database import get_db


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# =========================
# CREATE STUDENT
# =========================

@router.post("/", response_model=schemas.StudentResponse)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db)
):

    existing_student = db.query(
        models.Student
    ).filter(
        models.Student.student_id == student.student_id
    ).first()

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Student ID already exists"
        )

    new_student = models.Student(
        student_id=student.student_id,
        name=student.name,
        email=student.email,
        department=student.department,
        year=student.year
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


# =========================
# GET ALL STUDENTS
# =========================

@router.get("/", response_model=list[schemas.StudentResponse])
def get_students(
    db: Session = Depends(get_db)
):

    students = db.query(
        models.Student
    ).all()

    return students


# =========================
# GET SINGLE STUDENT
# =========================

@router.get("/{student_id}", response_model=schemas.StudentResponse)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):

    student = db.query(
        models.Student
    ).filter(
        models.Student.student_id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student