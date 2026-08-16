from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

from students import router as students_router
from attendance import router as attendance_router
from recognition import router as recognition_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Smart Attendance Monitoring System",
    description="Face Recognition Based Smart Attendance System",
    version="1.0.0"
)


# Allow Streamlit frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(recognition_router)


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "message": "AI Smart Attendance Monitoring System API is running",
        "status": "success"
    }


# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Backend is connected and working correctly"
    }