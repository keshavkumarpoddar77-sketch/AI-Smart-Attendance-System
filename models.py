from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    DateTime,
    Float,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


# =========================
# STUDENTS TABLE
# =========================

class Student(Base):

    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=True
    )

    department = Column(
        String,
        nullable=False
    )

    year = Column(
        String,
        nullable=False
    )

    face_registered = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.now
    )

    attendance_records = relationship(
        "Attendance",
        back_populates="student"
    )

    recognition_logs = relationship(
        "RecognitionLog",
        back_populates="student"
    )


# =========================
# ATTENDANCE TABLE
# =========================

class Attendance(Base):

    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        String,
        ForeignKey("students.student_id"),
        nullable=False
    )

    date = Column(
        Date,
        nullable=False
    )

    time = Column(
        Time,
        nullable=False
    )

    status = Column(
        String,
        default="Present"
    )

    confidence = Column(
        Float,
        nullable=True
    )

    student = relationship(
        "Student",
        back_populates="attendance_records"
    )


# =========================
# RECOGNITION LOGS TABLE
# =========================

class RecognitionLog(Base):

    __tablename__ = "recognition_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        String,
        ForeignKey("students.student_id"),
        nullable=True
    )

    recognized_name = Column(
        String,
        nullable=True
    )

    confidence = Column(
        Float,
        nullable=True
    )

    status = Column(
        String,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.now
    )

    camera_location = Column(
        String,
        nullable=True
    )

    student = relationship(
        "Student",
        back_populates="recognition_logs"
    )
