import streamlit as st
import requests
import pandas as pd


# ==================================================
# STREAMLIT CONFIG
# IMPORTANT: Only call this ONCE
# ==================================================

st.set_page_config(
    page_title="AI Smart Attendance System",
    page_icon="🎓",
    layout="wide"
)


# ==================================================
# BACKEND API
# ==================================================

# LOCAL BACKEND FOR TESTING
API_URL = "http://127.0.0.1:8000"

# AFTER DEPLOYING FASTAPI ON RENDER, REPLACE ABOVE WITH:
# API_URL = "https://your-backend-name.onrender.com"


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def api_get(endpoint):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=10
        )
        return response

    except requests.exceptions.RequestException as e:
        st.error(f"Backend connection error: {e}")
        return None


def api_post(endpoint, data=None, files=None):
    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            json=data if files is None else None,
            files=files,
            timeout=30
        )
        return response

    except requests.exceptions.RequestException as e:
        st.error(f"Backend connection error: {e}")
        return None


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("🎓 AI Attendance")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👨‍🎓 Add Student",
        "📷 Face Registration",
        "🔍 Face Recognition",
        "📅 Attendance",
        "👥 Students",
        "📊 Recognition Logs"
    ]
)


# ==================================================
# DASHBOARD
# ==================================================

if menu == "🏠 Dashboard":

    st.title("🤖 AI Smart Attendance Monitoring System")

    st.write(
        "Face Recognition based Smart Attendance System"
    )

    st.divider()

    response = api_get("/health")

    if response and response.status_code == 200:

        st.success("🟢 Backend Connected")

    else:

        st.warning(
            "🟡 Backend is not connected. "
            "If deployed online, deploy FastAPI first."
        )

    col1, col2, col3 = st.columns(3)

    # ----------------------------------------------

    with col1:

        students_response = api_get("/students")

        if students_response and students_response.status_code == 200:

            students = students_response.json()

            st.metric(
                "👨‍🎓 Total Students",
                len(students)
            )

        else:

            st.metric(
                "👨‍🎓 Total Students",
                0
            )

    # ----------------------------------------------

    with col2:

        attendance_response = api_get("/attendance")

        if attendance_response and attendance_response.status_code == 200:

            attendance = attendance_response.json()

            st.metric(
                "✅ Attendance Records",
                len(attendance)
            )

        else:

            st.metric(
                "✅ Attendance Records",
                0
            )

    # ----------------------------------------------

    with col3:

        logs_response = api_get("/recognition/logs")

        if logs_response and logs_response.status_code == 200:

            logs = logs_response.json()

            st.metric(
                "🔍 Recognition Logs",
                len(logs)
            )

        else:

            st.metric(
                "🔍 Recognition Logs",
                0
            )


# ==================================================
# ADD STUDENT
# ==================================================

elif menu == "👨‍🎓 Add Student":

    st.title("👨‍🎓 Add New Student")

    with st.form("student_form"):

        student_id = st.text_input(
            "Student ID"
        )

        name = st.text_input(
            "Student Name"
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

        submitted = st.form_submit_button(
            "➕ Add Student"
        )

        if submitted:

            if not student_id or not name:

                st.warning(
                    "Student ID and Name are required"
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
                            "Student added successfully!"
                        )

                    else:

                        st.error(
                            response.text
                        )


# ==================================================
# FACE REGISTRATION
# ==================================================

elif menu == "📷 Face Registration":

    st.title("📷 Register Student Face")

    student_id = st.text_input(
        "Enter Student ID"
    )

    uploaded_files = st.file_uploader(
        "Upload Face Images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_files:

        for uploaded_file in uploaded_files:

            st.image(
                uploaded_file,
                width=200
            )

    if st.button("📷 Register Face"):

        if not student_id:

            st.warning(
                "Please enter Student ID"
            )

        elif not uploaded_files:

            st.warning(
                "Please upload at least one image"
            )

        else:

            success_count = 0

            for uploaded_file in uploaded_files:

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

                if response and response.status_code == 200:

                    success_count += 1

            st.success(
                f"{success_count} face image(s) registered successfully!"
            )

            st.info(
                "Next step: Generate face embeddings from the backend."
            )


# ==================================================
# FACE RECOGNITION
# ==================================================

elif menu == "🔍 Face Recognition":

    st.title("🔍 Face Recognition")

    st.write(
        "Capture an image using your webcam or upload a face image."
    )

    camera_image = st.camera_input(
        "📸 Open Camera"
    )

    uploaded_image = st.file_uploader(
        "Or Upload Image",
        type=["jpg", "jpeg", "png"]
    )

    image = None

    if camera_image is not None:

        image = camera_image

    elif uploaded_image is not None:

        image = uploaded_image

    if image is not None:

        st.image(
            image,
            caption="Image for Recognition"
        )

        if st.button("🔍 Recognize Face"):

            files = {
                "file": (
                    image.name
                    if hasattr(image, "name")
                    else "camera_image.jpg",

                    image.getvalue(),

                    "image/jpeg"
                )
            }

            with st.spinner(
                "Recognizing face..."
            ):

                response = api_post(
                    "/recognition/recognize",
                    files=files
                )

            if response:

                if response.status_code == 200:

                    result = response.json()

                    if result.get("success"):

                        st.success(
                            "Face Recognized Successfully!"
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
                                    "Unknown"
                                )
                            )

                        with col3:

                            confidence = result.get(
                                "confidence",
                                0
                            )

                            st.metric(
                                "Confidence",
                                f"{confidence:.2f}%"
                                if isinstance(
                                    confidence,
                                    (int, float)
                                )
                                else confidence
                            )

                        st.success(
                            "Attendance Marked Present"
                        )

                    else:

                        st.warning(
                            result.get(
                                "message",
                                "Face not recognized"
                            )
                        )

                else:

                    st.error(
                        response.text
                    )


# ==================================================
# ATTENDANCE
# ==================================================

elif menu == "📅 Attendance":

    st.title("📅 Attendance Records")

    response = api_get(
        "/attendance"
    )

    if response:

        if response.status_code == 200:

            data = response.json()

            if data:

                df = pd.DataFrame(
                    data
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

                st.download_button(
                    label="⬇️ Download Attendance CSV",
                    data=df.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="attendance.csv",
                    mime="text/csv"
                )

            else:

                st.info(
                    "No attendance records found."
                )

        else:

            st.error(
                response.text
            )


# ==================================================
# STUDENTS
# ==================================================

elif menu == "👥 Students":

    st.title("👥 Registered Students")

    response = api_get(
        "/students"
    )

    if response:

        if response.status_code == 200:

            students = response.json()

            if students:

                df = pd.DataFrame(
                    students
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

            else:

                st.info(
                    "No students found."
                )

        else:

            st.error(
                response.text
            )


# ==================================================
# RECOGNITION LOGS
# ==================================================

elif menu == "📊 Recognition Logs":

    st.title("📊 Face Recognition Logs")

    response = api_get(
        "/recognition/logs"
    )

    if response:

        if response.status_code == 200:

            logs = response.json()

            if logs:

                df = pd.DataFrame(
                    logs
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

            else:

                st.info(
                    "No recognition logs found."
                )

        else:

            st.error(
                response.text
            )


# ==================================================
# FOOTER
# ==================================================

st.sidebar.divider()

st.sidebar.caption(
    "🤖 AI Smart Attendance Monitoring System"
)
