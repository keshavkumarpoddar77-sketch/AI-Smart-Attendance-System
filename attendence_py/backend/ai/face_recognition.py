import os
import pickle
import numpy as np

from insightface.app import FaceAnalysis


# =====================================
# PATHS
# =====================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "embeddings.pkl"
)


# =====================================
# LOAD FACE RECOGNITION MODEL
# =====================================

print("Loading AI Face Recognition Model...")

face_app = FaceAnalysis(
    name="buffalo_l",
    providers=[
        "CPUExecutionProvider"
    ]
)

face_app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)


# =====================================
# LOAD EMBEDDINGS
# =====================================

def load_embeddings():

    if not os.path.exists(
        EMBEDDINGS_FILE
    ):

        print(
            "Embeddings file not found"
        )

        return {}

    with open(
        EMBEDDINGS_FILE,
        "rb"
    ) as file:

        embeddings = pickle.load(
            file
        )

    return embeddings


# =====================================
# COSINE SIMILARITY
# =====================================

def cosine_similarity(
    embedding1,
    embedding2
):

    embedding1 = np.array(
        embedding1
    )

    embedding2 = np.array(
        embedding2
    )

    similarity = np.dot(
        embedding1,
        embedding2
    ) / (
        np.linalg.norm(embedding1)
        *
        np.linalg.norm(embedding2)
    )

    return similarity


# =====================================
# RECOGNIZE FACE
# =====================================

def recognize_face(
    image
):

    # Detect face
    faces = face_app.get(
        image
    )

    if len(faces) == 0:

        return {
            "success": False,
            "message": "No face detected"
        }


    # Get detected face embedding
    detected_embedding = faces[
        0
    ].embedding


    # Load saved student embeddings
    known_embeddings = load_embeddings()


    if not known_embeddings:

        return {
            "success": False,
            "message": "No registered face embeddings found"
        }


    best_match = None

    best_similarity = -1


    # Compare detected face with students
    for student_id, student_embedding in known_embeddings.items():

        similarity = cosine_similarity(
            detected_embedding,
            student_embedding
        )

        if similarity > best_similarity:

            best_similarity = similarity

            best_match = student_id


    # =====================================
    # CONFIDENCE THRESHOLD
    # =====================================

    THRESHOLD = 0.45


    if best_similarity < THRESHOLD:

        return {
            "success": False,
            "message": "Face not recognized",
            "confidence": float(
                best_similarity
            )
        }


    return {
        "success": True,
        "student_id": str(
            best_match
        ),
        "confidence": float(
            best_similarity
        )
    }