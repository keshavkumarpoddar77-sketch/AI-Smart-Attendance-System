from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.students import router as students_router
from routes.attendance import router as attendance_router
from routes.recognition import router as recognition_router
from routes.embeddings import router as embeddings_router
from routes.dashboard import router as dashboard_router


app = FastAPI(
    title="AI Smart Attendance System",
    description="Complete Face Recognition Attendance Backend",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add all routers
app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(recognition_router)
app.include_router(embeddings_router)
app.include_router(dashboard_router)


@app.get("/")
def home():
    return {
        "success": True,
        "message": "AI Smart Attendance Backend is running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "message": "Backend is connected successfully"
    }
