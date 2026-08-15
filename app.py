import streamlit as st
import requests
import pandas as pd
from datetime import date


# ==========================================
# CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Smart Attendance System",
    page_icon="🎓",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"

import streamlit as st

st.set_page_config(
    page_title="AI Attendance",
    page_icon="🎓"
)

st.title("🎓 AI Smart Attendance System")

st.success("Streamlit is working!")

st.write("Frontend test successful.")

# ==========================================
# API FUNCTIONS
# ==========================================

def api_get(endpoint):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        st.error(f"API Error: {response.text}")
        return []

    except requests.exceptions.ConnectionError:
        st.error(
            "❌ FastAPI backend is not running. "
            "Start the backend first."
        )
        return []

    except Exception as e:
        st.error(f"❌ {e}")
        return []


def api_post(endpoint, data=None, files=None):
    try:
        if files is not None:
            response = requests.post(
                f"{API_URL}{endpoint}",
                files=files,
                timeout=30
            )
        else:
            response = requests.post(
                f"{API_URL}{endpoint}",
                json=data,
                timeout=30
            )

        return response

    except requests.exceptions.ConnectionError:
        st.error(
            "❌ FastAPI backend is not running."
        )
        return None

    except Exception as e:
        st.error(f"❌ {e}")
        return None


# ==========================================
# TITLE
# ==========================================

st.title("🎓 AI Smart Attendance Monitoring System")

st.caption(
    "Face Recognition • Automatic Attendance • AI Monitoring"
)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("⚙️ Navigation")

page = st.sidebar.radio(
    "Select Feature",
    [
        "📊 Dashboard",
        "➕ Add Student",
        "📸 Face Registration",
        "🎥 Face Recognition",
        "📋 Mark Attendance",
        "👨‍🎓 Students",
        "📅 Today's Attendance",
        "🤖 Recognition Logs"
    ]
)


# ==========================================
# DASHBOARD
# ==========================================

if page == "📊 Dashboard":

    st.header("📊 Dashboard")

    students = api_get("/students")
    attendance = api_get("/attendance")
    logs = api_get("/recognition/logs")

    total_students = len(students) if students else 0
    total_attendance = len(attendance) if attendance else 0
    total_logs = len(logs) if logs else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "👨‍🎓 Total Students",
            total_students
        )

    with col2:
        st.metric(
            "✅ Attendance Records",
            total_attendance
        )

    with col3:
        st.metric(
            "🤖 Recognition Logs",
            total_logs
        )

    st.divider()

    st.subheader("🚀 System Features")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.info(
            """
            👨‍🎓 Student Management

            Add and manage students.
            """
        )

    with c2:
        st.info(
            """
            📸 Face Registration

            Register student face images.
            """
        )

    with c3:
        st.info(
            """
            🤖 AI Recognition

            Recognize students automatically.
            """
        )


# ==========================================
# ADD STUDENT
# ==========================================

elif page == "➕ Add Student":

    st.header("➕ Add New Student")

    with st.form("student_form"):

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
            "➕ Add Student"
        )

        if submit:

            if not student_id or not name:

                st.warning(
                    "Student ID and Name are required."
                )

            else:

                data = {
                    "student_id": student_id,
                    "name": name,
                    "email": email,
                    "department": department,
                    "year": year
                }

                response = api_post(
                    "/students",
                    data=data
                )

                if response:

                    if response.status_code in [200, 201]:

                        st.success(
                            "🎉 Student added successfully!"
                        )

                    else:

                        st.error(
                            response.text
                        )


# ==========================================
# FACE REGISTRATION
# ==========================================

elif page == "📸 Face Registration":

    st.header("📸 Face Registration")

    st.write(
        "Upload clear face images for the student."
    )

    student_id = st.text_input(
        "Enter Student ID"
    )

    uploaded_files = st.file_uploader(
        "Upload Face Images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_files:

        st.write(
            f"Selected {len(uploaded_files)} image(s)"
        )

        cols = st.columns(3)

        for i, image in enumerate(uploaded_files):

            with cols[i % 3]:

                st.image(
                    image,
                    caption=image.name,
                    use_container_width=True
                )

    if st.button("📸 Register Face"):

        if not student_id:

            st.warning(
                "Please enter Student ID."
            )

        elif not uploaded_files:

            st.warning(
                "Please upload at least one image."
            )

        else:

            success_count = 0

            for image in uploaded_files:

                image.seek(0)

                files = {
                    "file": (
                        image.name,
                        image.getvalue(),
                        image.type
                    )
                }

                response = api_post(
                    f"/recognition/register-face/{student_id}",
                    files=files
                )

                if response:

                    if response.status_code == 200:

                        success_count += 1

                    else:

                        st.error(
                            response.text
                        )

            if success_count > 0:

                st.success(
                    f"🎉 Successfully registered "
                    f"{success_count} face image(s)!"
                )

                st.info(
                    "Next: Generate face embeddings."
                )


# ==========================================
# FACE RECOGNITION
# ==========================================

elif page == "🎥 Face Recognition":

    st.header("🎥 AI Face Recognition")

    st.info(
        "Take a photo using your webcam "
        "and let the AI recognize the student."
    )

    camera_image = st.camera_input(
        "📷 Take a photo"
    )

    if camera_image:

        st.image(
            camera_image,
            caption="Captured Image",
            use_container_width=True
        )

        if st.button("🤖 Recognize Face"):

            with st.spinner(
                "🔍 Recognizing face..."
            ):

                try:

                    files = {
                        "file": (
                            "capture.jpg",
                            camera_image.getvalue(),
                            "image/jpeg"
                        )
                    }

                    response = requests.post(
                        f"{API_URL}/recognition/recognize",
                        files=files,
                        timeout=30
                    )

                    if response.status_code == 200:

                        result = response.json()

                        if result.get("success"):

                            st.success(
                                "✅ Face recognized successfully!"
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
                                    "confidence"
                                )

                                if confidence is not None:

                                    st.metric(
                                        "Confidence",
                                        f"{float(confidence):.2f}%"
                                    )

                                else:

                                    st.metric(
                                        "Confidence",
                                        "N/A"
                                    )

                            st.success(
                                f"📋 Attendance: "
                                f"{result.get('attendance', 'N/A')}"
                            )

                        else:

                            st.error(
                                result.get(
                                    "message",
                                    "Face not recognized"
                                )
                            )

                            if result.get("error"):

                                st.warning(
                                    result["error"]
                                )

                    else:

                        st.error(
                            f"API Error "
                            f"{response.status_code}"
                        )

                        st.code(
                            response.text
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "❌ FastAPI backend is not running."
                    )

                except Exception as e:

                    st.error(
                        f"❌ Recognition error: {e}"
                    )


# ==========================================
# MARK ATTENDANCE
# ==========================================

elif page == "📋 Mark Attendance":

    st.header("📋 Manual Attendance")

    students = api_get("/students")

    if students:

        student_options = {
            f"{student['student_id']} - {student['name']}":
            student["student_id"]
            for student in students
        }

        selected = st.selectbox(
            "Select Student",
            list(student_options.keys())
        )

        status = st.selectbox(
            "Status",
            ["Present", "Absent"]
        )

        if st.button("✅ Mark Attendance"):

            selected_id = student_options[selected]

            data = {
                "student_id": selected_id,
                "date": str(date.today()),
                "status": status
            }

            response = api_post(
                "/attendance",
                data=data
            )

            if response:

                if response.status_code in [200, 201]:

                    st.success(
                        "✅ Attendance marked successfully!"
                    )

                else:

                    st.error(
                        response.text
                    )

    else:

        st.warning(
            "No students found. Add a student first."
        )


# ==========================================
# STUDENTS
# ==========================================

elif page == "👨‍🎓 Students":

    st.header("👨‍🎓 Registered Students")

    students = api_get("/students")

    if students:

        df = pd.DataFrame(students)

        st.dataframe(
            df,
            use_container_width=True
        )

        st.metric(
            "Total Students",
            len(df)
        )

    else:

        st.info(
            "No students registered yet."
        )


# ==========================================
# TODAY'S ATTENDANCE
# ==========================================

elif page == "📅 Today's Attendance":

    st.header("📅 Today's Attendance")

    attendance = api_get("/attendance")

    if attendance:

        df = pd.DataFrame(attendance)

        st.dataframe(
            df,
            use_container_width=True
        )

        st.metric(
            "Attendance Records",
            len(df)
        )

    else:

        st.info(
            "No attendance records found."
        )


# ==========================================
# RECOGNITION LOGS
# ==========================================

elif page == "🤖 Recognition Logs":

    st.header("🤖 AI Recognition Logs")

    logs = api_get("/recognition/logs")

    if logs:

        df = pd.DataFrame(logs)

        st.dataframe(
            df,
            use_container_width=True
        )

        st.metric(
            "Total Recognition Logs",
            len(df)
        )

    else:

        st.info(
            "No recognition logs available."
        )


# ==========================================
# FOOTER
# ==========================================

st.sidebar.divider()

st.sidebar.success(
    "🟢 AI Attendance System"
)

st.sidebar.caption(
    "FastAPI + Streamlit + SQLite + OpenCV"
)