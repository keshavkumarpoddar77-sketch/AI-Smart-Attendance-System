import os
import pickle
import numpy as np

try:
    from insightface.app import FaceAnalysis
except ImportError:
    FaceAnalysis = None


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# Project:
# attendence_py/
# └── attendence_py/
#     └── backend/
#         └── ai/
#             └── face_recognition.py


# ============================================================
# EMBEDDINGS FILE
# ============================================================

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "embeddings.pkl"
)


# ============================================================
# INSIGHTFACE MODEL
# ============================================================

face_app = None


def load_model():
    """
    Load InsightFace model only once.
    """

    global face_app

    if face_app is not None:
        return face_app

    if FaceAnalysis is None:
        raise ImportError(
            "InsightFace is not installed. "
            "Run: pip install insightface"
        )

    face_app = FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"]
    )

    face_app.prepare(
        ctx_id=0,
        det_size=(640, 640)
    )

    return face_app


# ============================================================
# LOAD SAVED EMBEDDINGS
# ============================================================

def load_embeddings():
    """
    Load student face embeddings from embeddings.pkl.
    """

    if not os.path.exists(EMBEDDINGS_FILE):
        return {}

    try:

        with open(
            EMBEDDINGS_FILE,
            "rb"
        ) as file:

            data = pickle.load(file)

        return data

    except Exception as e:

        print(
            f"Error loading embeddings: {e}"
        )

        return {}


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    embedding1,
    embedding2
):
    """
    Calculate cosine similarity between two embeddings.
    """

    embedding1 = np.asarray(
        embedding1,
        dtype=np.float32
    )

    embedding2 = np.asarray(
        embedding2,
        dtype=np.float32
    )

    norm1 = np.linalg.norm(
        embedding1
    )

    norm2 = np.linalg.norm(
        embedding2
    )

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(
        np.dot(
            embedding1,
            embedding2
        )
        /
        (norm1 * norm2)
    )


# ============================================================
# EXTRACT FACE EMBEDDING
# ============================================================

def get_face_embedding(image):
    """
    Detect face and generate embedding from image.

    image:
        OpenCV BGR image
    """

    app = load_model()

    faces = app.get(image)

    if not faces:
        return None

    # Select largest face
    face = max(
        faces,
        key=lambda f: (
            f.bbox[2] - f.bbox[0]
        ) * (
            f.bbox[3] - f.bbox[1]
        )
    )

    embedding = face.embedding

    if embedding is None:
        return None

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    # Normalize embedding
    norm = np.linalg.norm(
        embedding
    )

    if norm != 0:
        embedding = embedding / norm

    return embedding


# ============================================================
# NORMALIZE EMBEDDING DATA
# ============================================================

def extract_embedding_from_item(item):
    """
    Handles different possible embedding.pkl formats.
    """

    # Direct numpy array
    if isinstance(
        item,
        np.ndarray
    ):
        return item

    # List / tuple
    if isinstance(
        item,
        (list, tuple)
    ):

        try:

            arr = np.asarray(
                item,
                dtype=np.float32
            )

            if arr.ndim == 1:
                return arr

        except Exception:
            pass

    # Dictionary
    if isinstance(
        item,
        dict
    ):

        possible_keys = [
            "embedding",
            "embeddings",
            "face_embedding",
            "vector"
        ]

        for key in possible_keys:

            if key in item:

                try:

                    arr = np.asarray(
                        item[key],
                        dtype=np.float32
                    )

                    if arr.ndim == 1:
                        return arr

                except Exception:
                    pass

    return None


# ============================================================
# FIND BEST MATCH
# ============================================================

def find_best_match(
    query_embedding,
    embeddings,
    threshold=0.45
):
    """
    Compare query embedding with all stored embeddings.

    Returns:

    {
        "student_id": "...",
        "confidence": 0.87
    }

    or None
    """

    best_student_id = None
    best_score = -1.0

    # --------------------------------------------------------
    # Format 1:
    #
    # {
    #     "101": embedding,
    #     "102": embedding
    # }
    # --------------------------------------------------------

    if isinstance(
        embeddings,
        dict
    ):

        for student_id, stored_data in embeddings.items():

            # One embedding
            stored_embedding = extract_embedding_from_item(
                stored_data
            )

            if stored_embedding is not None:

                score = cosine_similarity(
                    query_embedding,
                    stored_embedding
                )

                if score > best_score:

                    best_score = score
                    best_student_id = str(
                        student_id
                    )

                continue

            # ------------------------------------------------
            # Multiple embeddings
            # {
            #     "102": [
            #         embedding1,
            #         embedding2
            #     ]
            # }
            # ------------------------------------------------

            if isinstance(
                stored_data,
                (list, tuple)
            ):

                for item in stored_data:

                    embedding = extract_embedding_from_item(
                        item
                    )

                    if embedding is None:
                        continue

                    score = cosine_similarity(
                        query_embedding,
                        embedding
                    )

                    if score > best_score:

                        best_score = score
                        best_student_id = str(
                            student_id
                        )

    # --------------------------------------------------------
    # Threshold check
    # --------------------------------------------------------

    if (
        best_student_id is None
        or best_score < threshold
    ):

        return None

    return {
        "student_id": best_student_id,
        "confidence": best_score
    }


# ============================================================
# MAIN FACE RECOGNITION FUNCTION
# ============================================================

def recognize_face(image):
    """
    Recognize a face from an OpenCV image.

    Returns:

    {
        "success": True,
        "student_id": "102",
        "confidence": 0.82,
        "message": "Face recognized"
    }

    """

    try:

        # ----------------------------------------------------
        # Validate image
        # ----------------------------------------------------

        if image is None:

            return {
                "success": False,
                "message": "Image is empty"
            }

        # ----------------------------------------------------
        # Load embeddings
        # ----------------------------------------------------

        embeddings = load_embeddings()

        if not embeddings:

            return {
                "success": False,
                "message": (
                    "No face embeddings found. "
                    "Please register students first."
                )
            }

        # ----------------------------------------------------
        # Generate query embedding
        # ----------------------------------------------------

        query_embedding = get_face_embedding(
            image
        )

        if query_embedding is None:

            return {
                "success": False,
                "message": "No face detected in image"
            }

        # ----------------------------------------------------
        # Find best match
        # ----------------------------------------------------

        match = find_best_match(
            query_embedding,
            embeddings,
            threshold=0.45
        )

        if match is None:

            return {
                "success": False,
                "message": "Face not recognized"
            }

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        return {
            "success": True,
            "student_id": match["student_id"],
            "confidence": match["confidence"],
            "message": "Face recognized successfully"
        }

    except Exception as e:

        print(
            f"Face recognition error: {e}"
        )

        return {
            "success": False,
            "message": "Face recognition failed",
            "error": str(e)
        }