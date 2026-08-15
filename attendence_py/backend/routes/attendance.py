from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from attendence_py.backend import models
from attendence_py.backend import schemas
from attendence_py.backend.database import get_db


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


# ============================================================
# MARK ATTENDANCE
# ============================================================

@router.post("/mark")
def mark_attendance(
    attendance: schemas.AttendanceCreate,
    db: Session = Depends(get_db)
):

    student = db.query(
        models.Student
    ).filter(
        models.Student.student_id == attendance.student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    today = datetime.now().date()

    existing_attendance = db.query(
        models.Attendance
    ).filter(
        models.Attendance.student_id == attendance.student_id,
        models.Attendance.date == today
    ).first()

    if existing_attendance:
        raise HTTPException(
            status_code=400,
            detail="Attendance already marked today"
        )

    now = datetime.now()

    new_attendance = models.Attendance(
        student_id=attendance.student_id,
        date=now.date(),
        time=now.time(),
        status=attendance.status or "Present",
        confidence=attendance.confidence
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return {
        "success": True,
        "message": "Attendance marked successfully",
        "student_id": student.student_id,
        "student": student.name,
        "status": new_attendance.status,
        "date": str(new_attendance.date),
        "time": str(new_attendance.time)
    }


# ============================================================
# GET ALL ATTENDANCE
# ============================================================

@router.get("/")
def get_all_attendance(
    db: Session = Depends(get_db)
):

    records = db.query(
        models.Attendance
    ).all()

    return records


# ============================================================
# GET TODAY'S ATTENDANCE
# ============================================================

@router.get("/today")
def get_today_attendance(
    db: Session = Depends(get_db)
):

    today = datetime.now().date()

    records = db.query(
        models.Attendance
    ).filter(
        models.Attendance.date == today
    ).all()

    return records


# ============================================================
# GET STUDENT ATTENDANCE
# ============================================================

@router.get("/student/{student_id}")
def get_student_attendance(
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

    records = db.query(
        models.Attendance
    ).filter(
        models.Attendance.student_id == student_id
    ).all()

    return records