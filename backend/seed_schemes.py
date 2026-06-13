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

from gemini_client import embed_text
from mongo_client import COLLECTION_NAME, DB_NAME, get_collection

load_dotenv()

# Imported after load_dotenv so env vars are available to the modules above.
from schemes_data import SCHEMES  # noqa: E402

INDEX_INSTRUCTIONS = """
═══════════════════════════════════════════════════════════════════════════
NEXT STEP — Create the Vector Search Index in the Atlas UI:

1. Go to your Atlas cluster → Search → Create Search Index
2. Choose "Atlas Vector Search" (NOT regular search)
3. Select database: yojana_sathi, collection: schemes
4. Use this JSON configuration:
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    }
  ]
}
5. Name the index: vector_index
6. Click Create — it takes 2-3 minutes to become ACTIVE
7. Once ACTIVE, run the backend:  uvicorn main:app --reload --port 8000
═══════════════════════════════════════════════════════════════════════════
"""


def main() -> None:
    collection = get_collection()

    # Drop for clean re-runs.
    print(f"[seed] Dropping existing collection '{DB_NAME}.{COLLECTION_NAME}' (if any)…")
    collection.drop()

    inserted = 0
    for scheme in SCHEMES:
        # task_type="retrieval_document" because these are the documents being searched.
        embedding = embed_text(scheme["eligibility_text"], task_type="retrieval_document")
        collection.insert_one(
            {
                "name": scheme["name"],
                "benefit": scheme["benefit"],
                "eligibility_text": scheme["eligibility_text"],
                "required_docs": scheme["required_docs"],
                "apply_url": scheme["apply_url"],
                "embedding": embedding,
            }
        )
        inserted += 1
        print(f"  ✅ Embedded and inserted: {scheme['name']}  (dims={len(embedding)})")

    print(f"\n[seed] Done. Inserted {inserted}/{len(SCHEMES)} schemes with 768-dim embeddings.")
    print(INDEX_INSTRUCTIONS)


if __name__ == "__main__":
    main()
