import os
import pickle
import numpy as np
import cv2

from insightface.app import FaceAnalysis


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

FACE_DATA_DIR = os.path.join(
    DATA_DIR,
    "faces"
)

EMBEDDINGS_FILE = os.path.join(
    DATA_DIR,
    "embeddings.pkl"
)


# ============================================================
# CREATE REQUIRED FOLDERS
# ============================================================

os.makedirs(
    FACE_DATA_DIR,
    exist_ok=True
)

print("====================================")
print("AI SMART ATTENDANCE SYSTEM")
print("FACE EMBEDDING GENERATOR")
print("====================================")

print(f"\nProject Directory:")
print(BASE_DIR)

print(f"\nFace Images Directory:")
print(FACE_DATA_DIR)

print(f"\nEmbeddings File:")
print(EMBEDDINGS_FILE)


# ============================================================
# LOAD INSIGHTFACE MODEL
# ============================================================

print("\n====================================")
print("Loading AI Face Recognition Model...")
print("====================================")

face_app = FaceAnalysis(
    name="buffalo_l",
    providers=[
        "CPUExecutionProvider"
    ]
)

face_app.prepare(
    ctx_id=-1,
    det_size=(640, 640)
)

print("\nFace Recognition Model Loaded Successfully!")


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

def generate_embeddings():

    embeddings_data = {}

    print("\n====================================")
    print("CHECKING FACE DATA")
    print("====================================")

    print(
        f"\nFace Data Directory:\n{FACE_DATA_DIR}"
    )


    # --------------------------------------------------------
    # GET STUDENT FOLDERS
    # --------------------------------------------------------

    students = []

    for item in os.listdir(FACE_DATA_DIR):

        item_path = os.path.join(
            FACE_DATA_DIR,
            item
        )

        if os.path.isdir(item_path):

            students.append(item)


    # --------------------------------------------------------
    # CHECK STUDENTS
    # --------------------------------------------------------

    if len(students) == 0:

        print("\n❌ NO STUDENT FACE DATA FOUND")

        print(
            "\nPlease register a student face first."
        )

        print(
            "\nExpected folder structure:"
        )

        print(
            "data/faces/101/1.jpg"
        )

        print(
            "data/faces/101/2.jpg"
        )

        print(
            "\nYou can use:"
        )

        print(
            "python register_student.py"
        )

        return


    print(
        f"\nFound {len(students)} student folder(s)"
    )


    # ========================================================
    # PROCESS EACH STUDENT
    # ========================================================

    for student_id in students:

        print("\n====================================")
        print(
            f"PROCESSING STUDENT: {student_id}"
        )
        print("====================================")


        student_folder = os.path.join(
            FACE_DATA_DIR,
            student_id
        )


        student_embeddings = []


        # ----------------------------------------------------
        # GET IMAGES
        # ----------------------------------------------------

        image_files = []

        for file_name in os.listdir(
            student_folder
        ):

            if file_name.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp"
                )
            ):

                image_files.append(
                    file_name
                )


        if len(image_files) == 0:

            print(
                "\n⚠ No images found for this student."
            )

            continue


        print(
            f"\nFound {len(image_files)} image(s)"
        )


        # ====================================================
        # PROCESS EACH IMAGE
        # ====================================================

        for image_name in image_files:

            image_path = os.path.join(
                student_folder,
                image_name
            )


            print(
                f"\nProcessing: {image_name}"
            )


            # ------------------------------------------------
            # READ IMAGE
            # ------------------------------------------------

            image = cv2.imread(
                image_path
            )


            if image is None:

                print(
                    "❌ Cannot read image"
                )

                continue


            # ------------------------------------------------
            # DETECT FACE
            # ------------------------------------------------

            try:

                faces = face_app.get(
                    image
                )

            except Exception as e:

                print(
                    f"❌ Face detection error: {e}"
                )

                continue


            # ------------------------------------------------
            # CHECK FACE
            # ------------------------------------------------

            if len(faces) == 0:

                print(
                    "⚠ No face detected"
                )

                continue


            # ------------------------------------------------
            # SELECT LARGEST FACE
            # ------------------------------------------------

            face = max(
                faces,
                key=lambda x:
                (x.bbox[2] - x.bbox[0])
                *
                (x.bbox[3] - x.bbox[1])
            )


            # ------------------------------------------------
            # GET EMBEDDING
            # ------------------------------------------------

            embedding = face.embedding


            if embedding is None:

                print(
                    "❌ Embedding not generated"
                )

                continue


            # ------------------------------------------------
            # NORMALIZE EMBEDDING
            # ------------------------------------------------

            norm = np.linalg.norm(
                embedding
            )


            if norm == 0:

                print(
                    "❌ Invalid embedding"
                )

                continue


            embedding = (
                embedding / norm
            )


            student_embeddings.append(
                embedding
            )


            print(
                "✅ Face processed successfully"
            )


        # ====================================================
        # CREATE AVERAGE EMBEDDING
        # ====================================================

        if len(student_embeddings) > 0:

            print(
                "\nCreating average embedding..."
            )


            average_embedding = np.mean(
                student_embeddings,
                axis=0
            )


            norm = np.linalg.norm(
                average_embedding
            )


            if norm != 0:

                average_embedding = (
                    average_embedding / norm
                )


            embeddings_data[
                str(student_id)
            ] = average_embedding


            print(
                f"\n✅ EMBEDDING CREATED FOR STUDENT: {student_id}"
            )

            print(
                f"Valid Images Used: {len(student_embeddings)}"
            )


        else:

            print(
                "\n❌ No valid face found for this student"
            )


    # ========================================================
    # SAVE EMBEDDINGS
    # ========================================================

    print("\n====================================")
    print("SAVING EMBEDDINGS")
    print("====================================")


    try:

        with open(
            EMBEDDINGS_FILE,
            "wb"
        ) as file:

            pickle.dump(
                embeddings_data,
                file
            )


        print(
            "\n🎉 EMBEDDINGS GENERATED SUCCESSFULLY!"
        )

        print(
            f"\nTotal Students: {len(embeddings_data)}"
        )

        print(
            f"\nSaved File:"
        )

        print(
            EMBEDDINGS_FILE
        )


    except Exception as e:

        print(
            f"\n❌ ERROR SAVING EMBEDDINGS: {e}"
        )


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

def load_embeddings():

    if not os.path.exists(
        EMBEDDINGS_FILE
    ):

        return {}


    try:

        with open(
            EMBEDDINGS_FILE,
            "rb"
        ) as file:

            embeddings = pickle.load(
                file
            )


        return embeddings


    except Exception as e:

        print(
            f"Error loading embeddings: {e}"
        )

        return {}


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    generate_embeddings()