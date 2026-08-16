from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# ==========================================
# STUDENT MODEL
# ==========================================

class Student(BaseModel):
    id: str
    name: str
    department: str
    year: str


# Temporary in-memory student database
students_db = []


# ==========================================
# GET ALL STUDENTS
# ==========================================

@router.get("/")
def get_students():

    return {
        "total_students": len(students_db),
        "students": students_db
    }


# ==========================================
# GET SINGLE STUDENT
# ==========================================

@router.get("/{student_id}")
def get_student(student_id: str):

    for student in students_db:

        if student["id"] == student_id:

            return student

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )


# ==========================================
# ADD STUDENT
# ==========================================

@router.post("/")
def add_student(student: Student):

    # Check if student already exists
    for existing_student in students_db:

        if existing_student["id"] == student.id:

            raise HTTPException(
                status_code=400,
                detail="Student ID already exists"
            )

    student_data = student.model_dump()

    students_db.append(student_data)

    return {
        "message": "Student added successfully",
        "student": student_data
    }


# ==========================================
# DELETE STUDENT
# ==========================================

@router.delete("/{student_id}")
def delete_student(student_id: str):

    for student in students_db:

        if student["id"] == student_id:

            students_db.remove(student)

            return {
                "message": "Student deleted successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )