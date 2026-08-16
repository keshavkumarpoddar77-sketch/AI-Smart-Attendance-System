from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

import models
from database import get_db


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db)
):

    total_students = db.query(
        models.Student
    ).count()

    total_attendance = db.query(
        models.Attendance
    ).count()

    today = datetime.now().date()

    present_today = db.query(
        models.Attendance
    ).filter(
        models.Attendance.date == today
    ).count()

    total_logs = db.query(
        models.RecognitionLog
    ).count()

    return {
        "success": True,
        "total_students": total_students,
        "total_attendance": total_attendance,
        "present_today": present_today,
        "total_recognition_logs": total_logs
    }