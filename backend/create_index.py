"""Create the Atlas Vector Search index programmatically, then wait until it's ACTIVE.

Run:  python create_index.py
Read-only on your data (makes NO Gemini/Sarvam calls). It creates the search index
named 'vector_index' on the `embedding` field and polls until it becomes queryable.

This is the SECOND half of RAG setup: seeding stored the vectors, this makes them
searchable by similarity. The config MUST match the query side:
  - field path:   embedding   (where seed_schemes.py stored the vectors)
  - numDimensions: 768        (gemini-embedding-001 truncated to 768)
  - similarity:   cosine
  - index name:   vector_index  (matches VECTOR_INDEX_NAME in mongo_client.py)
"""

import sys
import time

# Windows consoles default to cp1252, which crashes on ✅/→ etc. Force UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from pymongo.operations import SearchIndexModel

from mongo_client import VECTOR_INDEX_NAME, get_collection

INDEX_DEFINITION = {
    "fields": [
        {
            "type": "vector",
            "path": "embedding",
            "numDimensions": 768,
            "similarity": "cosine",
        }
    ]
}


def _existing_index(col):
    """Return the existing search-index doc with our name, or None."""
    try:
        for idx in col.list_search_indexes():
            if idx.get("name") == VECTOR_INDEX_NAME:
                return idx
    except Exception as e:
        print(f"[index] Could not list search indexes: {e}")
    return None


def main() -> None:
    col = get_collection()

    # Idempotent: if it already exists, don't recreate — just report/wait on status.
    existing = _existing_index(col)
    if existing is None:
        print(f"[index] Creating Vector Search index '{VECTOR_INDEX_NAME}'…")
        model = SearchIndexModel(
            definition=INDEX_DEFINITION,
            name=VECTOR_INDEX_NAME,
            type="vectorSearch",
        )
        try:
            col.create_search_index(model=model)
        except Exception as e:
            print(f"[index] ❌ create_search_index failed: {e}")
            print("[index] Your pymongo may be too old (need >=4.7) or your tier may not")
            print("[index] support driver-side creation. Use the Atlas UI instead (see chat).")
            return
        print("[index] Submitted. Atlas now builds it in the background…")
    else:
        print(f"[index] Index '{VECTOR_INDEX_NAME}' already exists — checking status.")

    # Poll until the index reports queryable=True (usually 1-3 minutes).
    print("[index] Waiting for the index to become ACTIVE/queryable…")
    for _ in range(60):  # up to ~5 minutes
        idx = _existing_index(col)
        if idx:
            status = idx.get("status", "UNKNOWN")
            queryable = idx.get("queryable", False)
            print(f"[index]   status={status}, queryable={queryable}")
            if queryable:
                print(f"\n[index] ✅ '{VECTOR_INDEX_NAME}' is ACTIVE. RAG is fully wired — go test a query!")
                return
        time.sleep(5)

    print("\n[index] Still building. Re-run this script in a minute, or check the Atlas UI.")


if __name__ == "__main__":
    main()
