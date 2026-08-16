from fastapi import APIRouter
import os
import pickle

from face_embedding import generate_embeddings


router = APIRouter(
    prefix="/embeddings",
    tags=["Face Embeddings"]
)


# ==========================================
# GENERATE EMBEDDINGS
# ==========================================

@router.post("/generate")
def generate():

    try:

        generate_embeddings()

        return {
            "success": True,
            "message": "Face embeddings generated successfully"
        }

    except Exception as e:

        return {
            "success": False,
            "message": "Embedding generation failed",
            "error": str(e)
        }


# ==========================================
# EMBEDDING STATUS
# ==========================================

@router.get("/status")
def embedding_status():

    embedding_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "embeddings.pkl"
    )

    if not os.path.exists(embedding_file):

        return {
            "success": True,
            "exists": False,
            "total_students": 0,
            "message": "Embeddings not generated yet"
        }


    try:

        with open(
            embedding_file,
            "rb"
        ) as file:

            data = pickle.load(file)


        return {
            "success": True,
            "exists": True,
            "total_students": len(data),
            "students": list(data.keys())
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }