"""Quick read-only check: is the schemes collection seeded correctly?

Run:  python check_db.py
Makes NO API calls (no Gemini/Sarvam) — it only reads from MongoDB, so it's free.
Prints the document count, each scheme name, and verifies the embedding dimensions.
"""

import sys

# Windows consoles default to cp1252, which crashes on ✅/→ etc. Force UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from mongo_client import COLLECTION_NAME, DB_NAME, get_collection

EXPECTED_DIMS = 768


def main() -> None:
    col = get_collection()
    count = col.count_documents({})
    print(f"[check] Collection '{DB_NAME}.{COLLECTION_NAME}' has {count} document(s).\n")

    if count == 0:
        print("[check] ❌ EMPTY. The schemes were NOT seeded. Run:  python seed_schemes.py")
        return

    print("[check] Schemes found:")
    bad_dims = 0
    for i, doc in enumerate(col.find({}, {"name": 1, "embedding": 1}), start=1):
        emb = doc.get("embedding") or []
        dims = len(emb)
        ok = "✅" if dims == EXPECTED_DIMS else "⚠️"
        if dims != EXPECTED_DIMS:
            bad_dims += 1
        print(f"  {i:>2}. {ok} {doc.get('name', '(no name)')}  (embedding dims={dims})")

    print()
    if bad_dims:
        print(f"[check] ⚠️  {bad_dims} doc(s) do NOT have {EXPECTED_DIMS}-dim embeddings — re-seed needed.")
    else:
        print(f"[check] ✅ All {count} schemes have {EXPECTED_DIMS}-dim embeddings. Seeding looks correct.")

    # Show one full document (minus the huge embedding array) as a sanity check.
    sample = col.find_one({}, {"embedding": 0})
    print("\n[check] Sample document (embedding hidden):")
    for k, v in (sample or {}).items():
        print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
