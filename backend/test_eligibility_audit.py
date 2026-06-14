"""Eligibility audit harness — proves the helpline never recommends a scheme the
caller's own facts contradict (the "the card disproves itself" bug).

Run:  python test_eligibility_audit.py

It drives several realistic personas through /converse to a recommendation, then checks
EVERY recommended (person, scheme) with two INDEPENDENT oracles:
  1. a deterministic age-range checker (regex, NO LLM) — catches e.g. an 18-40 pension
     recommended to a 55-year-old, exactly like the screenshot bug;
  2. an adversarial LLM contradiction check (a fresh, skeptical sarvam-105b call) — catches
     wrong gender / caste / marital status / occupation.
Goal: ZERO violations across all personas.
"""

import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from fastapi.testclient import TestClient

import main
import sarvam_client

client = TestClient(main.app)


# ── Oracle 1: deterministic age-range check (independent of the app's own verifier) ──
def age_violations(age, eligibility_text: str):
    """Return a list of eligibility age-ranges the person's age violates, or []. Only looks
    at ELIGIBILITY age phrases ('aged 18 to 40', 'age 60 or above'), NOT benefit ages
    ('pension after age 60'), which is exactly the distinction the model used to get wrong.
    """
    if age is None:
        return []
    t = eligibility_text.lower()
    bad = set()
    for lo, hi in re.findall(r"(?:aged?\s+)?(\d{1,2})\s+to\s+(\d{1,2})\s+years", t):
        lo, hi = int(lo), int(hi)
        if not (lo <= age <= hi):
            bad.add(f"{lo}-{hi}")
    for lo, hi in re.findall(r"between\s+(\d{1,2})\s+and\s+(\d{1,2})\s+year", t):
        lo, hi = int(lo), int(hi)
        if not (lo <= age <= hi):
            bad.add(f"{lo}-{hi}")
    for lo in re.findall(r"aged?\s+(\d{1,2})\s+(?:years?\s+)?(?:or|and)\s+above", t):
        if age < int(lo):
            bad.add(f">={lo}")
    return sorted(bad)


# ── Oracle 2: adversarial LLM contradiction check (fresh, skeptical call) ──
def llm_contradiction(facts: dict, eligibility_text: str):
    """Ask a skeptical model whether the facts CLEARLY violate a stated requirement.
    Returns (violation: bool, reason: str). Unknowns are NOT violations.
    """
    prompt = f"""Person's known facts (JSON): {json.dumps(facts, ensure_ascii=False)}
Scheme eligibility rule: "{eligibility_text}"

Does the person CLEARLY and DEFINITELY violate any stated requirement of this scheme,
based ONLY on the known facts? Consider age range, gender, caste/category, marital/widow
status, occupation, land owned, income. A requirement that is simply UNKNOWN is NOT a
violation — only flag a clear contradiction with a stated fact.

Return ONLY JSON: {{"violation": true|false, "reason": "<short>"}}"""
    raw = sarvam_client._chat(
        "You are a strict, skeptical eligibility auditor. Return ONLY JSON.",
        prompt,
        temperature=0.0,
        model=sarvam_client.LLM_MODEL_BIG,
    )
    data = sarvam_client._safe_json(raw) or {}
    return bool(data.get("violation")), str(data.get("reason", ""))


# ── Direct, deterministic test of the verifier (the screenshot scenario) ──
def test_verifier_rejects_overage_pension():
    """Feed verify_group a 55-year-old farmer with 18-40 pensions among the candidates and
    assert it REJECTS them (the exact bug from the screenshot)."""
    print("\n" + "=" * 78)
    print("DIRECT VERIFIER TEST: 55-yo farmer vs 18-40 pension schemes")
    person = {
        "relation": "self",
        "facts": {"age": 55, "occupation": "farmer", "land_ownership": True,
                  "below_poverty_line": True, "category": "OBC", "area": "rural"},
        "candidates": [
            {"name": "PM Kisan Maan Dhan Yojana",
             "eligibility_text": "Small or marginal farmer aged 18 to 40 years at time of enrolment. Owns less than 2 hectares of farmland."},
            {"name": "Atal Pension Yojana",
             "eligibility_text": "Indian citizen aged 18 to 40 years who does not have a formal pension scheme. Works in unorganised sector."},
            {"name": "PM Kisan Samman Nidhi",
             "eligibility_text": "Small and marginal farmer family owning cultivable land. Income support of Rs.6000 per year in three installments. No age limit."},
        ],
    }
    verdict = sarvam_client.verify_group([person], "en-IN")
    kept_names = []
    for g in verdict.get("groups", []):
        for k in g.get("kept", []):
            idx = k.get("index")
            if isinstance(idx, int) and 0 <= idx < len(person["candidates"]):
                kept_names.append(person["candidates"][idx]["name"])
    print(f"  kept: {kept_names}")
    bad = [n for n in kept_names if "Maan Dhan" in n or "Atal Pension" in n]
    if bad:
        print(f"  ❌ FAIL — verifier kept an 18-40 scheme for a 55-year-old: {bad}")
        return False
    print("  ✅ PASS — both 18-40 pensions rejected for the 55-year-old.")
    return True


# ── Personas — front-loaded so they converge to a recommendation quickly ──
PERSONAS = {
    "over-age farmer (must NOT get 18-40 pensions)": [
        "I am a 55 year old married small farmer in Maharashtra. I own about one hectare of farmland. "
        "We are below the poverty line, OBC category, with a ration card and a bank account. "
        "My wife is 50. Our yearly income is about 40000 rupees. I have no pension.",
        "That is everything about us. Please tell me all the schemes I can get.",
    ],
    "65 yo widow (60+ pensions ok, NOT 18-40 schemes)": [
        "I am a 65 year old widow living alone in a village in Bihar. We are below the poverty line, "
        "general category, I have a BPL card, I own no land, and I get no pension.",
        "That is everything. What can I get?",
    ],
    "19 yo SC student (scholarship, NOT pension/maternity)": [
        "I am a 19 year old unmarried male student from a scheduled caste family in Tamil Nadu. "
        "My family yearly income is about 80000 rupees and I need help to pay for college.",
        "That is all about me. What schemes can I get?",
    ],
    "family: 58 widow + pregnant daughter + 16 student son": [
        "I am a 58 year old widow. My daughter is 26, married, and pregnant with her first child. "
        "My son is 16 and studies in class 11. We live in rural Bihar.",
        "We are below the poverty line, OBC category, with a ration card. Our yearly family income "
        "is about 50000 rupees.",
        "Nobody in the family has a disability. We all have bank accounts and Aadhaar cards. "
        "That is everything — please tell me what each of us can get now.",
    ],
}


def run_persona(name, turns):
    print("\n" + "=" * 78)
    print(f"PERSONA: {name}")
    state = {"language": "en-IN"}
    final = None
    for msg in turns:
        r = client.post("/converse", data={"text": msg, "state": json.dumps(state)})
        j = r.json()
        state = j["state"]
        if j["action"] == "recommend":
            final = j
            break
    if final is None:
        # Push once more to force a recommendation out of the loop.
        r = client.post("/converse", data={"text": "Please just tell me now.", "state": json.dumps(state)})
        final = r.json()
        state = final["state"]

    # Map relation -> facts for the age oracle.
    facts_by_rel = {p["relation"]: p["facts"] for p in state["people"]}
    print(f"BOT: {final['message'][:160]}")

    violations = []
    if final["action"] != "recommend" or not final.get("groups"):
        print("  (no schemes recommended — honest empty is acceptable)")
        return violations

    for g in final["groups"]:
        facts = facts_by_rel.get(g["relation"], {})
        age = facts.get("age")
        print(f"  ▸ {g['label']} (age={age}):")
        for s in g["schemes"]:
            elig = s["eligibility_summary"]
            av = age_violations(age, elig)
            viol, reason = llm_contradiction(facts, elig)
            tag = "OK"
            if av:
                tag = f"AGE-VIOLATION {av}"
                violations.append((name, g["label"], s["name"], f"age {age} not in {av}"))
            elif viol:
                tag = f"CONTRADICTION: {reason[:60]}"
                violations.append((name, g["label"], s["name"], reason))
            print(f"      [{tag}] {s['name']}")
    return violations


def main_run():
    direct_ok = test_verifier_rejects_overage_pension()

    all_violations = []
    for name, turns in PERSONAS.items():
        all_violations += run_persona(name, turns)

    print("\n" + "=" * 78)
    if not direct_ok:
        print("❌ Direct verifier test FAILED (18-40 scheme kept for a 55-year-old).")
        sys.exit(1)
    if all_violations:
        print(f"❌ {len(all_violations)} ELIGIBILITY VIOLATION(S) FOUND:")
        for name, who, scheme, why in all_violations:
            print(f"   - [{name}] {who}: '{scheme}' — {why}")
        sys.exit(1)
    print("✅ ZERO eligibility violations — no recommended scheme contradicts the caller's facts.")


if __name__ == "__main__":
    main_run()
