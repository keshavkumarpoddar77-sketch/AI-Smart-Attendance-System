from fastapi import FastAPI

from database import engine
import models

from routes import students
from routes import attendance
from routes import recognition


# Create database tables
models.Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="AI Smart Attendance Monitoring System",
    description="AI-powered Face Recognition Attendance System",
    version="1.0.0"
)


# ==============================
# Include API Routes
# ==============================

app.include_router(students.router)

app.include_router(attendance.router)

app.include_router(recognition.router)


# ==============================
# Home API
# ==============================

@app.get("/")
def home():
    return {
        "message": "AI Smart Attendance Monitoring System API is running"
    }


# ==============================
# Health Check API
# ==============================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Backend is working correctly"
    }