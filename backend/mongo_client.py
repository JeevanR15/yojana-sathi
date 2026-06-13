"""MongoDB Atlas connection + Atlas Vector Search ($vectorSearch).

This is the technical heart of the project: instead of keyword matching, we run a
semantic similarity search of the user's situation against the 15 scheme embeddings.
"""

import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "yojana_sathi"
COLLECTION_NAME = "schemes"
VECTOR_INDEX_NAME = "vector_index"

_client = None


def get_client() -> MongoClient:
    """Lazily create a single shared MongoClient."""
    global _client
    if _client is None:
        if not MONGODB_URI:
            raise RuntimeError("MONGODB_URI is not set in backend/.env")
        _client = MongoClient(MONGODB_URI, tlsCAFile=None, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
    return _client


def get_collection():
    return get_client()[DB_NAME][COLLECTION_NAME]


def ping() -> bool:
    """Quick connectivity check."""
    get_client().admin.command("ping")
    return True


def vector_search(query_embedding, limit: int = 3, num_candidates: int = 50):
    """Run the Atlas $vectorSearch aggregation pipeline.

    Returns a list of matched scheme docs, each with a `score` (cosine similarity,
    normalized to 0..1 by Atlas) and the _id stripped out.
    """
    collection = get_collection()
    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": num_candidates,
                "limit": limit,
            }
        },
        {
            "$project": {
                "name": 1,
                "benefit": 1,
                "eligibility_text": 1,
                "required_docs": 1,
                "apply_url": 1,
                "score": {"$meta": "vectorSearchScore"},
                "_id": 0,
            }
        },
    ]
    print(
        f"[mongo] → $vectorSearch on '{COLLECTION_NAME}' "
        f"(index={VECTOR_INDEX_NAME}, numCandidates={num_candidates}, limit={limit})"
    )
    return list(collection.aggregate(pipeline))
