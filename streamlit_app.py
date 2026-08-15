import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from PIL import Image


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Smart Attendance Monitoring System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CONFIGURATION
# =========================================================

# Local FastAPI backend
API_URL = "http://127.0.0.1:8000"

# You can change this later when backend is deployed.
# Example:
# API_URL = "https://your-backend-url.com"


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .sub-title {
        color: #6c757d;
        font-size: 17px;
        margin-bottom: 30px;
    }

    .feature-card {
        background-color: #f5f7fb;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }

    .section-title {
        font-size: 28px;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# API FUNCTIONS
# =========================================================

def api_get(endpoint):

    try:

        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=10
        )

        return response

    except requests.exceptions.ConnectionError:

        return None

    except requests.exceptions.Timeout:

        return None

    except Exception:

        return None


def api_post(endpoint, data=None, files=None):

    try:

        response = requests.post(
            f"{API_URL}{endpoint}",
            data=data,
            files=files,
            timeout=30
        )

        return response

    except requests.exceptions.ConnectionError:

        return None

    except requests.exceptions.Timeout:

        return None

    except Exception:

        return None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚙️ Navigation")

    st.caption("Select Feature")

    page = st.radio(
        "",
        [
            "📊 Dashboard",
            "➕ Add Student",
            "📸 Face Registration",
            "🤖 Face Recognition",
            "📝 Mark Attendance",
            "👨‍🎓 Students",
            "📅 Today's Attendance",
            "📜 Recognition Logs"
        ]
    )

    st.divider()

    st.success("🟢 AI Attendance System")

    st.caption(
        "FastAPI + Streamlit + SQLite + InsightFace"
    )

    st.divider()

    st.write("### Backend Status")

    health = api_get("/health")

    if health is not None:

        if health.status_code == 200:

            st.success("🟢 Backend Connected")

        else:

            st.warning("🟡 Backend Response Error")

    else:

        st.error("🔴 Backend Offline")

        st.caption(
            "Run FastAPI locally or deploy your backend."
        )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🎓 AI Smart Attendance Monitoring System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Face Recognition • Automatic Attendance • AI Monitoring</div>',
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "📊 Dashboard":

    st.markdown(
        '<div class="section-title">📊 Dashboard</div>',
        unsafe_allow_html=True
    )

    students_count = 0
    attendance_count = 0
    logs_count = 0

    students_response = api_get("/students")

    if students_response is not None:

        try:

            students_data = students_response.json()

            students_count = len(students_data)

        except Exception:

            students_count = 0


    attendance_response = api_get("/attendance/today")

    if attendance_response is not None:

        try:

            attendance_data = attendance_response.json()

            attendance_count = len(attendance_data)

        except Exception:

            attendance_count = 0


    logs_response = api_get("/recognition/logs")

    if logs_response is not None:

        try:

            logs_data = logs_response.json()

            logs_count = len(logs_data)

        except Exception:

            logs_count = 0


    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "👨‍🎓 Total Students",
            students_count
        )

    with col2:

        st.metric(
            "✅ Present Today",
            attendance_count
        )

    with col3:

        st.metric(
            "📸 Recognition Logs",
            logs_count
        )

    with col4:

        backend_status = "Online"

        if health is None:

            backend_status = "Offline"

        st.metric(
            "🖥️ Backend",
            backend_status
        )


    st.divider()

    st.subheader("🚀 System Features")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="feature-card">
            <h3>🤖 AI Face Recognition</h3>
            <p>Recognize registered students using AI face embeddings.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="feature-card">
            <h3>📝 Automatic Attendance</h3>
            <p>Automatically mark attendance after successful recognition.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            """
            <div class="feature-card">
            <h3>📊 Attendance Monitoring</h3>
            <p>View students, attendance records and recognition logs.</p>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# ADD STUDENT
# =========================================================

elif page == "➕ Add Student":

    st.markdown(
        '<div class="section-title">➕ Add Student</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Enter student details and save them to the attendance system."
    )

    with st.form("add_student_form"):

        student_id = st.text_input(
            "Student ID"
        )

        name = st.text_input(
            "Full Name"
        )

        email = st.text_input(
            "Email"
        )

        department = st.text_input(
            "Department"
        )

        year = st.text_input(
            "Year"
        )

        submit = st.form_submit_button(
            "➕ Add Student",
            use_container_width=True
        )


    if submit:

        if not student_id or not name:

            st.error(
                "Student ID and Name are required."
            )

        else:

            student_data = {
                "student_id": student_id,
                "name": name,
                "email": email,
                "department": department,
                "year": year
            }

            try:

                response = requests.post(
                    f"{API_URL}/students",
                    json=student_data,
                    timeout=10
                )

                if response.status_code in [200, 201]:

                    st.success(
                        "Student added successfully!"
                    )

                else:

                    st.error(
                        f"Error: {response.text}"
                    )

            except Exception as e:

                st.error(
                    "Cannot connect to backend."
                )


# =========================================================
# FACE REGISTRATION
# =========================================================

elif page == "📸 Face Registration":

    st.markdown(
        '<div class="section-title">📸 Face Registration</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Upload a clear face image for a registered student."
    )

    student_id = st.text_input(
        "Enter Student ID"
    )

    uploaded_file = st.file_uploader(
        "Upload Face Image",
        type=["jpg", "jpeg", "png"]
    )


    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Selected Face Image",
            width=300
        )


        if st.button(
            "📸 Register Face",
            use_container_width=True
        ):

            if not student_id:

                st.error(
                    "Please enter Student ID."
                )

            else:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                response = api_post(
                    f"/recognition/register-face/{student_id}",
                    files=files
                )

                if response is None:

                    st.error(
                        "Backend is not connected."
                    )

                elif response.status_code == 200:

                    st.success(
                        "Face registered successfully!"
                    )

                    st.json(
                        response.json()
                    )

                else:

                    st.error(
                        response.text
                    )


# =========================================================
# FACE RECOGNITION
# =========================================================

elif page == "🤖 Face Recognition":

    st.markdown(
        '<div class="section-title">🤖 AI Face Recognition</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Open your webcam, take a photo and recognize the registered student."
    )

    st.subheader(
        "📷 Webcam Recognition"
    )

    camera_image = st.camera_input(
        "Take a photo for recognition"
    )


    if camera_image is not None:

        st.image(
            camera_image,
            caption="Captured Image",
            width=400
        )


        if st.button(
            "🤖 Recognize Face",
            use_container_width=True
        ):

            with st.spinner(
                "AI is analyzing the face..."
            ):

                files = {
                    "file": (
                        "webcam_image.jpg",
                        camera_image.getvalue(),
                        "image/jpeg"
                    )
                }

                response = api_post(
                    "/recognition/recognize",
                    files=files
                )


            if response is None:

                st.error(
                    "Cannot connect to FastAPI backend."
                )

                st.warning(
                    "Make sure your backend endpoint is running."
                )

            else:

                try:

                    result = response.json()

                except Exception:

                    result = None


                if (
                    response.status_code == 200
                    and result
                    and result.get("success")
                ):

                    st.success(
                        "🎉 Face recognized successfully!"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Student ID",
                            result.get(
                                "student_id",
                                "N/A"
                            )
                        )

                    with col2:

                        st.metric(
                            "Name",
                            result.get(
                                "name",
                                "N/A"
                            )
                        )

                    with col3:

                        confidence = result.get(
                            "confidence",
                            0
                        )

                        try:

                            confidence = float(confidence)

                            confidence_text = (
                                f"{confidence:.2f}"
                            )

                        except Exception:

                            confidence_text = str(
                                confidence
                            )

                        st.metric(
                            "Confidence",
                            confidence_text
                        )


                    st.success(
                        "Attendance marked: Present"
                    )

                else:

                    message = (
                        result.get(
                            "message",
                            "Face recognition failed"
                        )
                        if result
                        else "Recognition failed"
                    )

                    st.error(
                        message
                    )


# =========================================================
# MANUAL ATTENDANCE
# =========================================================

elif page == "📝 Mark Attendance":

    st.markdown(
        '<div class="section-title">📝 Mark Attendance</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Manually mark student attendance."
    )

    student_id = st.text_input(
        "Student ID"
    )

    status = st.selectbox(
        "Attendance Status",
        [
            "Present",
            "Absent"
        ]
    )


    if st.button(
        "📝 Mark Attendance",
        use_container_width=True
    ):

        if not student_id:

            st.error(
                "Please enter Student ID."
            )

        else:

            attendance_data = {
                "student_id": student_id,
                "status": status
            }

            try:

                response = requests.post(
                    f"{API_URL}/attendance",
                    json=attendance_data,
                    timeout=10
                )

                if response.status_code in [200, 201]:

                    st.success(
                        f"Attendance marked as {status}!"
                    )

                else:

                    st.error(
                        response.text
                    )

            except Exception:

                st.error(
                    "Cannot connect to backend."
                )


# =========================================================
# STUDENTS LIST
# =========================================================

elif page == "👨‍🎓 Students":

    st.markdown(
        '<div class="section-title">👨‍🎓 Registered Students</div>',
        unsafe_allow_html=True
    )

    response = api_get(
        "/students"
    )

    if response is None:

        st.error(
            "Backend is offline."
        )

    elif response.status_code == 200:

        try:

            students = response.json()

            if students:

                df = pd.DataFrame(
                    students
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

                st.success(
                    f"Total Students: {len(students)}"
                )

            else:

                st.info(
                    "No students found."
                )

        except Exception:

            st.error(
                "Unable to read student data."
            )

    else:

        st.error(
            response.text
        )


# =========================================================
# TODAY ATTENDANCE
# =========================================================

elif page == "📅 Today's Attendance":

    st.markdown(
        '<div class="section-title">📅 Today\'s Attendance</div>',
        unsafe_allow_html=True
    )

    response = api_get(
        "/attendance/today"
    )

    if response is None:

        st.error(
            "Backend is offline."
        )

    elif response.status_code == 200:

        try:

            attendance = response.json()

            if attendance:

                df = pd.DataFrame(
                    attendance
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

                present_count = 0

                if "status" in df.columns:

                    present_count = len(
                        df[
                            df["status"] == "Present"
                        ]
                    )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Total Records",
                        len(df)
                    )

                with col2:

                    st.metric(
                        "Present",
                        present_count
                    )

            else:

                st.info(
                    "No attendance records for today."
                )

        except Exception:

            st.error(
                "Unable to load attendance."
            )

    else:

        st.error(
            response.text
        )


# =========================================================
# RECOGNITION LOGS
# =========================================================

elif page == "📜 Recognition Logs":

    st.markdown(
        '<div class="section-title">📜 AI Recognition Logs</div>',
        unsafe_allow_html=True
    )

    response = api_get(
        "/recognition/logs"
    )

    if response is None:

        st.error(
            "Backend is offline."
        )

    elif response.status_code == 200:

        try:

            logs = response.json()

            if logs:

                df = pd.DataFrame(
                    logs
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

                st.success(
                    f"Total Recognition Logs: {len(logs)}"
                )

            else:

                st.info(
                    "No recognition logs available."
                )

        except Exception:

            st.error(
                "Unable to load recognition logs."
            )

    else:

        st.error(
            response.text
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "© 2026 AI Smart Attendance Monitoring System | "
    "Built with FastAPI, Streamlit, SQLite and InsightFace"
)