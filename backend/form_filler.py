"""Voice form-fill: a deterministic Hindi fallback question bank + PDF generation.

The question list is carried inside `collected_so_far` between /form-fill/start and
/form-fill/answer, so the flow is fully stateless and costs zero extra API calls per
answer. The PDF is rendered with reportlab.
"""

import base64
import io
import os
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

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
    # (path, subfontIndex). Nirmala UI ships as a .ttc collection on Windows 11 and is
    # pan-Indic (Devanagari, Telugu, Tamil, Kannada, Bengali, Gujarati, …) + Latin — so we
    # must register it with subfontIndex=0, not as a plain .ttf.
    candidates = [
        (r"C:\Windows\Fonts\Nirmala.ttc", 0),
        (r"C:\Windows\Fonts\Nirmala.ttf", None),
        (r"C:\Windows\Fonts\mangal.ttf", None),
        (os.path.join(os.path.dirname(__file__), "fonts", "NotoSansDevanagari.ttf"), None),
    ]
    for path, idx in candidates:
        if not os.path.exists(path):
            continue
        try:
            if idx is None:
                pdfmetrics.registerFont(TTFont("DevanagariUI", path))
            else:
                pdfmetrics.registerFont(TTFont("DevanagariUI", path, subfontIndex=idx))
            _BODY_FONT = "DevanagariUI"
            break
        except Exception as e:  # noqa: BLE001
            print(f"[form] font register failed for {path}: {e}")
    return _BODY_FONT


def generate_scheme_pdf(scheme: dict) -> bytes:
    """Render a clean one-page PDF summary of a matched scheme. Returns raw PDF bytes.

    Uses the Indic-capable font (Nirmala UI covers Devanagari, Telugu, Tamil, Kannada,
    etc. + Latin) so the regional-language explanation renders, not boxes. Platypus
    handles text wrapping automatically.
    """
    font = _ensure_devanagari_font()  # "DevanagariUI" (Indic+Latin) or "Helvetica" fallback
    name = str(scheme.get("name", "Scheme"))
    pct = round(float(scheme.get("match_score") or 0) * 100)
    print(f"[form] → generate_scheme_pdf for '{name}' (font={font})")

    title = ParagraphStyle("t", fontName=font, fontSize=20, leading=25, textColor=HexColor("#065f46"), spaceAfter=2)
    match = ParagraphStyle("m", fontName=font, fontSize=10, leading=13, textColor=HexColor("#047857"), spaceAfter=12)
    benefit = ParagraphStyle("b", fontName=font, fontSize=13, leading=18, textColor=HexColor("#047857"), spaceAfter=10)
    lbl = ParagraphStyle("l", fontName=font, fontSize=9, leading=12, textColor=HexColor("#64748b"), spaceBefore=14, spaceAfter=4)
    body = ParagraphStyle("bd", fontName=font, fontSize=11, leading=16, textColor=HexColor("#0f172a"))
    box = ParagraphStyle("bx", fontName=font, fontSize=11, leading=17, textColor=HexColor("#064e3b"),
                         backColor=HexColor("#f0fdf4"), borderColor=HexColor("#bbf7d0"), borderWidth=1,
                         borderPadding=10, borderRadius=8, spaceBefore=4)
    foot = ParagraphStyle("f", fontName=font, fontSize=8, leading=11, textColor=HexColor("#94a3b8"), spaceBefore=22)

    flow = [
        Paragraph(escape(name), title),
        Paragraph(f"{pct}% match", match),
    ]
    if scheme.get("benefit"):
        flow.append(Paragraph(escape(str(scheme["benefit"])), benefit))
    if scheme.get("hindi_explanation"):
        flow.append(Paragraph(escape(str(scheme["hindi_explanation"])), box))
    if scheme.get("eligibility_summary"):
        flow.append(Paragraph("WHY YOU QUALIFY", lbl))
        flow.append(Paragraph(escape(str(scheme["eligibility_summary"])), body))
    docs = scheme.get("required_docs") or []
    if docs:
        flow.append(Paragraph("DOCUMENTS / CERTIFICATES TO CARRY", lbl))
        for d in docs:
            flow.append(Paragraph(f"•&nbsp;&nbsp;{escape(str(d))}", body))
    if scheme.get("apply_url"):
        flow.append(Paragraph("WHERE TO APPLY (OFFICIAL PORTAL)", lbl))
        url = escape(str(scheme["apply_url"]))
        flow.append(Paragraph(f'<a href="{url}" color="#047857">{url}</a>', body))
    flow.append(Spacer(1, 6))
    flow.append(Paragraph(
        "Generated by Yojana Saathi — please verify the latest details on the official "
        "portal before applying.", foot))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, title=name,
        leftMargin=20 * mm, rightMargin=20 * mm, topMargin=22 * mm, bottomMargin=18 * mm,
    )
    doc.build(flow)
    buffer.seek(0)
    return buffer.read()


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
