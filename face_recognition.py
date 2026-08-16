import os
import pickle
import numpy as np

from insightface.app import FaceAnalysis


# ==========================================
# PATH CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "embeddings.pkl"
)


# ==========================================
# LOAD FACE RECOGNITION MODEL
# ==========================================

print("====================================")
print("Loading Face Recognition Model...")
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

print("Face Recognition Model Loaded Successfully!")


# ==========================================
# LOAD EMBEDDINGS
# ==========================================

def load_embeddings():

    if not os.path.exists(EMBEDDINGS_FILE):

        print(
            f"Embeddings file not found:\n{EMBEDDINGS_FILE}"
        )

        return {}

    try:

        with open(
            EMBEDDINGS_FILE,
            "rb"
        ) as file:

            embeddings_data = pickle.load(
                file
            )

        print(
            f"Loaded embeddings for "
            f"{len(embeddings_data)} student(s)"
        )

        return embeddings_data

    except Exception as e:

        print(
            f"Error loading embeddings: {e}"
        )

        return {}


# ==========================================
# RECOGNIZE FACE
# ==========================================

def recognize_face(image):

    try:

        # ----------------------------------
        # LOAD SAVED EMBEDDINGS
        # ----------------------------------

        embeddings_data = load_embeddings()

        if not embeddings_data:

            return {
                "success": False,
                "message": (
                    "No face embeddings found. "
                    "Please generate embeddings first."
                )
            }


        # ----------------------------------
        # DETECT FACE
        # ----------------------------------

        faces = face_app.get(image)

        if len(faces) == 0:

            return {
                "success": False,
                "message": "No face detected in the image."
            }


        # ----------------------------------
        # SELECT LARGEST FACE
        # ----------------------------------

        face = max(
            faces,
            key=lambda x:
            (x.bbox[2] - x.bbox[0])
            *
            (x.bbox[3] - x.bbox[1])
        )


        # ----------------------------------
        # GET FACE EMBEDDING
        # ----------------------------------

        query_embedding = face.embedding

        if query_embedding is None:

            return {
                "success": False,
                "message": "Face embedding could not be generated."
            }


        # Normalize query embedding
        norm = np.linalg.norm(
            query_embedding
        )

        if norm == 0:

            return {
                "success": False,
                "message": "Invalid face embedding."
            }

        query_embedding = (
            query_embedding / norm
        )


        # ==================================
        # COMPARE WITH ALL STUDENTS
        # ==================================

        best_match_id = None
        best_similarity = -1.0


        for student_id, stored_embedding in embeddings_data.items():

            stored_embedding = np.array(
                stored_embedding,
                dtype=np.float32
            )


            # Normalize stored embedding
            stored_norm = np.linalg.norm(
                stored_embedding
            )

            if stored_norm == 0:
                continue

            stored_embedding = (
                stored_embedding / stored_norm
            )


            # Cosine similarity
            similarity = float(
                np.dot(
                    query_embedding,
                    stored_embedding
                )
            )


            if similarity > best_similarity:

                best_similarity = similarity

                best_match_id = student_id


        # ==================================
        # CHECK MATCH THRESHOLD
        # ==================================

        # You can adjust this later
        MATCH_THRESHOLD = 0.40


        if (
            best_match_id is None
            or best_similarity < MATCH_THRESHOLD
        ):

            return {
                "success": False,
                "message": "Face not recognized.",
                "confidence": round(
                    best_similarity,
                    4
                )
            }


        # ==================================
        # SUCCESS
        # ==================================

        return {
            "success": True,
            "student_id": str(
                best_match_id
            ),
            "confidence": round(
                best_similarity,
                4
            ),
            "message": "Face recognized successfully"
        }


    except Exception as e:

        print(
            f"Recognition Error: {e}"
        )

        return {
            "success": False,
            "message": "Face recognition failed.",
            "error": str(e)
        }