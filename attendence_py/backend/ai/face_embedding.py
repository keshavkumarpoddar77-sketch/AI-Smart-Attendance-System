import os
import pickle
import numpy as np
import cv2

from insightface.app import FaceAnalysis


# ==========================================
# PATH CONFIGURATION
# ==========================================

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

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "embeddings.pkl"
)


# ==========================================
# LOAD INSIGHTFACE MODEL
# ==========================================

print("Loading AI Face Recognition Model...")

face_app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

face_app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)


# ==========================================
# GENERATE FACE EMBEDDINGS
# ==========================================

def generate_embeddings():

    embeddings_data = {}

    if not os.path.exists(FACE_DATA_DIR):

        print("Face data folder not found.")

        return

    students = os.listdir(FACE_DATA_DIR)

    print(f"Found {len(students)} student folders")

    for student_id in students:

        student_folder = os.path.join(
            FACE_DATA_DIR,
            student_id
        )

        if not os.path.isdir(student_folder):
            continue

        print(
            f"\nProcessing Student ID: {student_id}"
        )

        student_embeddings = []

        for image_name in os.listdir(student_folder):

            image_path = os.path.join(
                student_folder,
                image_name
            )

            image = cv2.imread(image_path)

            if image is None:

                print(
                    f"Cannot read: {image_name}"
                )

                continue

            faces = face_app.get(image)

            if len(faces) == 0:

                print(
                    f"No face detected: {image_name}"
                )

                continue

            # Select the largest detected face
            face = max(
                faces,
                key=lambda x:
                (x.bbox[2] - x.bbox[0])
                * (x.bbox[3] - x.bbox[1])
            )

            embedding = face.embedding

            student_embeddings.append(
                embedding
            )

            print(
                f"Processed: {image_name}"
            )

        # Create average embedding for student
        if len(student_embeddings) > 0:

            average_embedding = np.mean(
                student_embeddings,
                axis=0
            )

            # Normalize embedding
            average_embedding = (
                average_embedding /
                np.linalg.norm(average_embedding)
            )

            embeddings_data[
                student_id
            ] = average_embedding

            print(
                f"Embedding created for {student_id}"
            )

        else:

            print(
                f"No valid face images for {student_id}"
            )

    # ==========================================
    # SAVE EMBEDDINGS
    # ==========================================

    with open(
        EMBEDDINGS_FILE,
        "wb"
    ) as file:

        pickle.dump(
            embeddings_data,
            file
        )

    print("\n===================================")
    print("FACE EMBEDDINGS GENERATED")
    print("===================================")

    print(
        f"Total Students: {len(embeddings_data)}"
    )

    print(
        f"Saved to: {EMBEDDINGS_FILE}"
    )


# ==========================================
# RUN SCRIPT
# ==========================================

if __name__ == "__main__":

    generate_embeddings()