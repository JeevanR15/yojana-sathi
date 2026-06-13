"""One-time seeding script: embed each scheme and insert it into MongoDB Atlas.

Run:  python seed_schemes.py

This is the ONLY place (besides a live user query) that touches the embedding API,
so re-run it sparingly to conserve credits.
"""

import sys

# Windows PowerShell/cmd default to cp1252, which crashes on ✅/→ etc. Force UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv

from gemini_client import embed_texts
from mongo_client import COLLECTION_NAME, DB_NAME, get_collection

load_dotenv()

# Imported after load_dotenv so env vars are available to the modules above.
from schemes_data import SCHEMES  # noqa: E402

INDEX_INSTRUCTIONS = """
═══════════════════════════════════════════════════════════════════════════
NEXT STEP — Make sure the Vector Search Index exists.

If you just dropped the collection, the 'vector_index' was deleted too. Recreate it:

    python create_index.py        # creates 'vector_index' and waits until ACTIVE

(create_index.py is idempotent — if the index already exists it just reports status.)
Once it prints ACTIVE, run the backend:  uvicorn main:app --reload --port 8000

Manual alternative (Atlas UI → Search → Create Search Index → Atlas Vector Search):
db yojana_sathi, collection schemes, name vector_index, JSON:
{"fields": [{"type": "vector", "path": "embedding", "numDimensions": 768, "similarity": "cosine"}]}
═══════════════════════════════════════════════════════════════════════════
"""


def main() -> None:
    collection = get_collection()

    # Clear documents for a clean re-run. We use delete_many (NOT drop) on purpose:
    # dropping the collection also DELETES the Atlas vector_index, forcing a rebuild
    # every time. delete_many empties the data but keeps the collection + its index.
    print(f"[seed] Clearing existing documents in '{DB_NAME}.{COLLECTION_NAME}'…")
    deleted = collection.delete_many({}).deleted_count
    print(f"[seed] Removed {deleted} old document(s).")

    # Embed every scheme's eligibility_text in BATCHES (few requests, not one-per-scheme),
    # so we stay under the free-tier 100-embeddings/minute limit.
    # task_type="retrieval_document" because these are the documents being searched.
    texts = [s["eligibility_text"] for s in SCHEMES]
    print(f"[seed] Embedding {len(texts)} schemes in batches…")
    embeddings = embed_texts(texts, task_type="retrieval_document")

    docs = [
        {
            "name": s["name"],
            "benefit": s["benefit"],
            "eligibility_text": s["eligibility_text"],
            "required_docs": s["required_docs"],
            "apply_url": s["apply_url"],
            "embedding": emb,
        }
        for s, emb in zip(SCHEMES, embeddings)
    ]
    collection.insert_many(docs)

    print(f"\n[seed] Done. Inserted {len(docs)}/{len(SCHEMES)} schemes with {len(embeddings[0])}-dim embeddings.")
    print(INDEX_INSTRUCTIONS)


if __name__ == "__main__":
    main()
