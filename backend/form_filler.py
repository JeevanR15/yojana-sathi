"""Voice form-fill: a deterministic Hindi fallback question bank + PDF generation.

The question list is carried inside `collected_so_far` between /form-fill/start and
/form-fill/answer, so the flow is fully stateless and costs zero extra API calls per
answer. The PDF is rendered with reportlab.
"""

import base64
import io
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Deterministic fallback questions (used if Gemini question-generation is unavailable).
BASE_QUESTIONS = [
    "आपका पूरा नाम क्या है?",
    "आपके पिता या पति का नाम क्या है?",
    "आपकी उम्र कितनी है?",
    "आपका पूरा पता क्या है (गाँव, जिला, राज्य)?",
    "आपका बैंक खाता नंबर क्या है?",
    "आपका आधार नंबर क्या है?",
    "आपका मोबाइल नंबर क्या है?",
]

_BODY_FONT = "Helvetica"


def build_questions(scheme_name: str, profile: dict | None = None) -> list:
    """Deterministic question list. Reliable, aligned across calls, and cost-free."""
    return list(BASE_QUESTIONS)


def _ensure_devanagari_font() -> str:
    """Register a Devanagari-capable Windows font so Hindi answers render in the PDF.

    Falls back to Helvetica (English-only) if no such font is found.
    """
    global _BODY_FONT
    if _BODY_FONT != "Helvetica":
        return _BODY_FONT
    for path in (r"C:\Windows\Fonts\Nirmala.ttf", r"C:\Windows\Fonts\mangal.ttf"):
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("DevanagariUI", path))
                _BODY_FONT = "DevanagariUI"
                break
            except Exception as e:  # noqa: BLE001
                print(f"[form] font register failed for {path}: {e}")
    return _BODY_FONT


def generate_pdf(scheme_name: str, questions: list, collected: dict) -> str:
    """Render a filled application-form draft PDF. Returns a base64 string.

    `collected` maps each question string to the user's spoken answer.
    """
    print(f"[form] → generate_pdf for '{scheme_name}' ({len(questions)} fields)")
    body_font = _ensure_devanagari_font()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _, height = A4
    left = 20 * mm
    y = height - 30 * mm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(left, y, "Government Scheme Application (Draft)")
    y -= 10 * mm

    c.setFont("Helvetica", 11)
    c.drawString(left, y, f"Scheme: {scheme_name}")
    y -= 7 * mm
    c.drawString(left, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 12 * mm

    for q in questions:
        if q.startswith("__"):  # skip internal keys like __questions__
            continue
        answer = str(collected.get(q, "")).strip() or "—"
        c.setFont(body_font, 11)
        c.drawString(left, y, q)
        y -= 6 * mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left + 6 * mm, y, f"→ {answer}")
        y -= 11 * mm
        if y < 30 * mm:
            c.showPage()
            y = height - 30 * mm

    y -= 4 * mm
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(
        left,
        y,
        "Auto-generated draft by Yojana Sathi. Please verify all details before submission.",
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
