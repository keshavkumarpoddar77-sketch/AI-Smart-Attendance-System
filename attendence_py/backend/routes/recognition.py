from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

import os
import shutil
import numpy as np
import cv2

from datetime import date, datetime

import models
import schemas

from database import get_db
from ai.face_recognition import recognize_face


# =====================================
# ROUTER
# =====================================

router = APIRouter(
    prefix="/recognition",
    tags=["Recognition"]
)


# =====================================
# FACE DATA FOLDER
# =====================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FACE_DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
    "faces"
)

os.makedirs(
    FACE_DATA_DIR,
    exist_ok=True
)


# =====================================
# REGISTER FACE IMAGE
# =====================================

@router.post("/register-face/{student_id}")
async def register_face(
    student_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Check whether student exists
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

    # Create folder for student
    student_folder = os.path.join(
        FACE_DATA_DIR,
        student_id
    )

    os.makedirs(
        student_folder,
        exist_ok=True
    )

    # Create file path
    file_path = os.path.join(
        student_folder,
        file.filename
    )

    # Save uploaded image
    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "success": True,
        "message": "Face registered successfully",
        "student_id": student_id,
        "file": file.filename
    }


# =====================================
# GET REGISTERED FACE IMAGES
# =====================================

@router.get("/faces/{student_id}")
def get_registered_faces(
    student_id: str
):

    student_folder = os.path.join(
        FACE_DATA_DIR,
        student_id
    )

    if not os.path.exists(student_folder):

        return {
            "success": True,
            "student_id": student_id,
            "images": [],
            "total_images": 0
        }

    # Get image files only
    images = []

    for file_name in os.listdir(student_folder):

        if file_name.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):

            images.append(file_name)

    return {
        "success": True,
        "student_id": student_id,
        "images": images,
        "total_images": len(images)
    }


# =====================================
# CREATE RECOGNITION LOG
# =====================================

@router.post("/log")
def create_recognition_log(
    log: schemas.RecognitionLogCreate,
    db: Session = Depends(get_db)
):

    new_log = models.RecognitionLog(
        student_id=log.student_id,
        recognized_name=log.recognized_name,
        confidence=log.confidence,
        status=log.status,
        camera_location=log.camera_location
    )

    db.add(new_log)

    db.commit()

    db.refresh(new_log)

    return {
        "success": True,
        "message": "Recognition log saved",
        "id": new_log.id
    }


# =====================================
# GET RECOGNITION LOGS
# =====================================

@router.get("/logs")
def get_recognition_logs(
    db: Session = Depends(get_db)
):

    logs = db.query(
        models.RecognitionLog
    ).order_by(
        models.RecognitionLog.timestamp.desc()
    ).all()

    return logs


# =====================================
# RECOGNIZE FACE
# =====================================

@router.post("/recognize")
async def recognize_student(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:

        # Read uploaded image
        image_bytes = await file.read()

        # Convert bytes to NumPy array
        image_array = np.frombuffer(
            image_bytes,
            np.uint8
        )

        # Convert array into OpenCV image
        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        # Check image
        if image is None:

            return {
                "success": False,
                "message": "Invalid image"
            }


        # =====================================
        # RECOGNIZE FACE USING AI MODEL
        # =====================================

        result = recognize_face(
            image
        )


        # If face is not recognized
        if not result.get(
            "success",
            False
        ):

            return {
                "success": False,
                "message": result.get(
                    "message",
                    "Face not recognized"
                )
            }


        # Get recognized student ID
        student_id = str(
            result["student_id"]
        )


        # =====================================
        # FIND STUDENT IN DATABASE
        # =====================================

        student = db.query(
            models.Student
        ).filter(
            models.Student.student_id == student_id
        ).first()


        if not student:

            return {
                "success": False,
                "message": "Face recognized but student is not found in database",
                "student_id": student_id
            }


        # Get confidence safely
        confidence = float(
            result.get(
                "confidence",
                0.0
            )
        )


        # =====================================
        # SAVE RECOGNITION LOG
        # =====================================

        recognition_log = models.RecognitionLog(
            student_id=student.student_id,
            recognized_name=student.name,
            confidence=confidence,
            status="Recognized",
            camera_location="Webcam"
        )

        db.add(
            recognition_log
        )


        # =====================================
        # CHECK TODAY'S ATTENDANCE
        # =====================================

        today = date.today()

        existing_attendance = db.query(
            models.Attendance
        ).filter(
            models.Attendance.student_id
            == student.student_id,

            models.Attendance.date
            == today
        ).first()


        # =====================================
        # MARK ATTENDANCE
        # =====================================

        if not existing_attendance:

            attendance = models.Attendance(
                student_id=student.student_id,
                status="Present",
                date=today,
                time=datetime.now().time()
            )

            db.add(
                attendance
            )

            attendance_message = (
                "Attendance marked successfully"
            )

        else:

            attendance_message = (
                "Attendance already marked today"
            )


        # =====================================
        # SAVE DATABASE
        # =====================================

        db.commit()


        # =====================================
        # SUCCESS RESPONSE
        # =====================================

        return {
            "success": True,
            "message": "Face recognized successfully",
            "student_id": student.student_id,
            "name": student.name,
            "confidence": confidence,
            "attendance": attendance_message
        }


    except Exception as e:

        db.rollback()

        return {
            "success": False,
            "message": "Recognition failed",
            "error": str(e)
        }