import streamlit as st
import requests
import pandas as pd


# ==================================================
# STREAMLIT CONFIG
# ==================================================

st.set_page_config(
    page_title="AI Smart Attendance System",
    page_icon="🎓",
    layout="wide"
)


# ==================================================
# BACKEND API
# ==================================================

API_URL = "http://127.0.0.1:8002"


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

        if files is not None:

            response = requests.post(
                f"{API_URL}{endpoint}",
                files=files,
                timeout=60
            )

        else:

            response = requests.post(
                f"{API_URL}{endpoint}",
                json=data,
                timeout=30
            )

        return response

    except requests.exceptions.RequestException as e:
        st.error(f"Backend connection error: {e}")
        return None


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("🎓 AI Attendance System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👨‍🎓 Add Student",
        "📷 Face Registration",
        "🔍 Face Recognition",
        "📋 Attendance",
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
        "Face Recognition Based Smart Attendance System"
    )

    st.divider()

    response = api_get("/health")

    if response is not None and response.status_code == 200:

        st.success("🟢 Backend Connected")

    else:

        st.error("🔴 Backend Not Connected")

    col1, col2, col3 = st.columns(3)

    # ---------------- TOTAL STUDENTS ----------------

    with col1:

        response = api_get("/students/")

        if response is not None and response.status_code == 200:

            students = response.json()
            total_students = len(students)

        else:

            total_students = 0

        st.metric(
            "👨‍🎓 Total Students",
            total_students
        )

    # ---------------- ATTENDANCE ----------------

    with col2:

        response = api_get("/attendance/")

        if response is not None and response.status_code == 200:

            attendance = response.json()
            total_attendance = len(attendance)

        else:

            total_attendance = 0

        st.metric(
            "✅ Attendance Records",
            total_attendance
        )

    # ---------------- RECOGNITION LOGS ----------------

    with col3:

        response = api_get("/recognition/logs")

        if response is not None and response.status_code == 200:

            logs = response.json()
            total_logs = len(logs)

        else:

            total_logs = 0

        st.metric(
            "🔍 Recognition Logs",
            total_logs
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
                "/students/",
                data=data
            )

            if response is not None:

                if response.status_code in [200, 201]:

                    st.success(
                        "Student added successfully!"
                    )

                else:

                    st.error(
                        f"Error: {response.text}"
                    )


# ==================================================
# FACE REGISTRATION
# ==================================================

elif menu == "📷 Face Registration":

    st.title("📷 Register Student Face")

    st.write(
        "Upload clear face images for the registered student."
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

        st.write("Preview:")

        columns = st.columns(3)

        for index, image in enumerate(uploaded_files):

            with columns[index % 3]:

                st.image(
                    image,
                    use_container_width=True
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

            for image in uploaded_files:

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

                if (
                    response is not None
                    and response.status_code == 200
                ):

                    success_count += 1

            if success_count > 0:

                st.success(
                    f"Successfully registered {success_count} face image(s)."
                )

                st.info(
                    "Now run face_embedding.py to generate embeddings."
                )

            else:

                st.error(
                    "Face registration failed."
                )


# ==================================================
# FACE RECOGNITION
# ==================================================

elif menu == "🔍 Face Recognition":

    st.title("🔍 Face Recognition")

    st.write(
        "Capture an image from webcam or upload a face image."
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
            caption="Image for Recognition",
            use_container_width=True
        )

        if st.button("🔍 Recognize Face"):

            file_name = getattr(
                image,
                "name",
                "camera_image.jpg"
            )

            files = {
                "file": (
                    file_name,
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

            if response is not None:

                if response.status_code == 200:

                    result = response.json()

                    if result.get("success"):

                        st.success(
                            "🎉 Face Recognized Successfully!"
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

                            if isinstance(
                                confidence,
                                (int, float)
                            ):

                                confidence_text = (
                                    f"{confidence:.2f}"
                                )

                            else:

                                confidence_text = str(
                                    confidence
                                )

                            st.metric(
                                "Confidence",
                                confidence_text
                            )

                        st.success(
                            result.get(
                                "attendance",
                                "Attendance processed successfully"
                            )
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
                        f"Recognition failed: {response.text}"
                    )


# ==================================================
# ATTENDANCE
# ==================================================

elif menu == "📋 Attendance":

    st.title("📋 Attendance Records")

    response = api_get(
        "/attendance/"
    )

    if response is not None:

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

                csv = df.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    label="⬇️ Download Attendance CSV",
                    data=csv,
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
        "/students/"
    )

    if response is not None:

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

    if response is not None:

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