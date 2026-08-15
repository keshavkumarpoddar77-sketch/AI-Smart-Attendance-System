from pydantic import BaseModel
from datetime import date, time, datetime


# =========================
# STUDENT
# =========================

class StudentCreate(BaseModel):
    student_id: str
    name: str
    email: str | None = None
    department: str
    year: str


class StudentResponse(StudentCreate):
    id: int
    face_registered: bool

    class Config:
        from_attributes = True


# =========================
# ATTENDANCE
# =========================

class AttendanceCreate(BaseModel):
    student_id: str
    status: str = "Present"
    confidence: float | None = None


class AttendanceResponse(BaseModel):
    id: int
    student_id: str
    date: date
    time: time
    status: str
    confidence: float | None = None

    class Config:
        from_attributes = True


# =========================
# RECOGNITION LOG
# =========================

class RecognitionLogCreate(BaseModel):
    student_id: str | None = None
    recognized_name: str | None = None
    confidence: float | None = None
    status: str
    camera_location: str | None = None


class RecognitionLogResponse(RecognitionLogCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True