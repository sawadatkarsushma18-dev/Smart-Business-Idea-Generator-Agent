"""
utils/pdf_exporter.py – Generate a downloadable PDF report from an AgentSession.
Uses fpdf2 (FPDF2) library.
"""

import logging
from io import BytesIO
from datetime import datetime
from typing import Optional

from models import AgentSession, BusinessPlan

logger = logging.getLogger(__name__)


def _safe(text: str, max_len: int = 0) -> str:
    """Clean text for FPDF (remove non-latin1 chars that would crash the encoder)."""
    if not text:
        return ""
    # Replace common unicode that FPDF core fonts can't handle
    replacements = {
        "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2022": "*", "\u25cf": "*",
        "\u00e9": "e", "\u00e8": "e", "\u00e0": "a", "\u00ea": "e",
        "\u2026": "...", "\u00ae": "(R)", "\u00a9": "(C)", "\u2122": "(TM)",
    }
    for uni, ascii_rep in replacements.items():
        text = text.replace(uni, ascii_rep)
    # Strip remaining non-latin1 chars
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    if max_len and len(text) > max_len:
        text = text[:max_len] + "..."
    return text


def generate_pdf_report(session: AgentSession) -> bytes:
    """
    Generate a PDF report for the session and return it as bytes.
    Falls back to a plain-text bytes if PDF generation fails.
    """
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ── Title ─────────────────────────────────────────────────────
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(31, 35, 40)
        pdf.cell(0, 12, "Smart Business Idea Generator Report", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(87, 96, 106)
        pdf.cell(0, 6, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
        pdf.ln(4)

        # ── Disclaimer ─────────────────────────────────────────────────
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 100, 50)
        disclaimer = _safe(
            "DISCLAIMER: AI-generated ideas, market assessments, and financial estimates "
            "are informational suggestions only and do not guarantee business success, "
            "profitability, or investment returns."
        )
        pdf.multi_cell(0, 5, disclaimer)
        pdf.ln(4)

        # ── User Profile ───────────────────────────────────────────────
        if session.profile:
            p = session.profile
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(31, 35, 40)
            pdf.cell(0, 8, "User Profile", ln=True)
            pdf.set_font("Helvetica", "", 10)
            fields = [
                ("Name", p.name or "Not provided"),
                ("Interest", p.interest),
                ("Skills", p.skills),
                ("Background", p.background),
                ("Budget", p.budget),
                ("Location", f"{p.city} {p.country}".strip()),
                ("Target Audience", p.target_audience),
                ("Industry", p.preferred_industry),
                ("Goals", p.business_goals),
            ]
            for label, val in fields:
                if val:
                    pdf.cell(45, 6, f"{label}:", ln=False)
                    pdf.multi_cell(0, 6, _safe(val, 200))
            pdf.ln(4)

        # ── Generated Ideas ─────────────────────────────────────────────
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(31, 35, 40)
        pdf.cell(0, 8, f"Generated Business Ideas ({len(session.ideas)})", ln=True)
        pdf.ln(2)

        for i, idea in enumerate(session.ideas):
            is_rec = i == session.recommended_index
            # Idea header
            pdf.set_fill_color(240, 244, 255) if not is_rec else pdf.set_fill_color(235, 255, 245)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(31, 35, 40)
            prefix = "[TOP PICK] " if is_rec else ""
            pdf.cell(0, 8, _safe(f"{prefix}{i+1}. {idea.name}"), ln=True, fill=True)
            pdf.set_font("Helvetica", "", 10)

            fields = [
                ("Tagline", idea.tagline),
                ("Problem", idea.problem_statement),
                ("Solution", idea.proposed_solution),
                ("Target Audience", idea.target_audience),
                ("USP", idea.usp),
                ("Startup Cost (AI-est.)", idea.estimated_startup_cost),
                ("Revenue Model", idea.revenue_model),
                ("Difficulty", idea.implementation_difficulty),
                ("Scalability", idea.scalability),
                ("Overall Score", f"{idea.overall_score:.1f}/10"),
            ]
            for label, val in fields:
                if val:
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(52, 5, f"  {label}:", ln=False)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.multi_cell(0, 5, _safe(str(val), 300))
            pdf.ln(3)

        # ── Business Plan ─────────────────────────────────────────────
        if session.business_plan and session.business_plan.idea:
            bp = session.business_plan
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(31, 35, 40)
            pdf.cell(0, 10, _safe(f"Business Plan: {bp.idea.name}"), ln=True)
            pdf.ln(2)

            sections = [
                ("Execution Roadmap", bp.roadmap),
                ("MVP Plan", bp.mvp_plan),
                ("Tools & Technologies", bp.tools_and_tech),
                ("Marketing Strategies", bp.marketing_strategies),
                ("Risks & Mitigations", bp.risks_and_mitigations),
                ("Next Steps", bp.next_steps),
            ]
            for section_title, content in sections:
                if content:
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.set_text_color(59, 130, 212)
                    pdf.cell(0, 8, section_title, ln=True)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(31, 35, 40)
                    pdf.multi_cell(0, 5, _safe(content, 2000))
                    pdf.ln(3)

        output = pdf.output()
        return bytes(output)

    except Exception as exc:
        logger.error("PDF generation failed: %s", exc)
        # Return a plain-text fallback
        return _generate_text_report(session).encode("utf-8")


def _generate_text_report(session: AgentSession) -> str:
    """Generate a plain-text report as a fallback."""
    lines = ["=" * 60, "SMART BUSINESS IDEA GENERATOR — REPORT", "=" * 60, ""]
    if session.profile:
        p = session.profile
        lines += [
            "USER PROFILE",
            "-" * 30,
            f"Name: {p.name or 'N/A'}",
            f"Interest: {p.interest}",
            f"Skills: {p.skills}",
            f"Budget: {p.budget}",
            f"Location: {p.city} {p.country}",
            "",
        ]
    for i, idea in enumerate(session.ideas):
        is_rec = i == session.recommended_index
        lines += [
            f"{'[TOP PICK] ' if is_rec else ''}IDEA {i+1}: {idea.name}",
            "-" * 40,
            f"Problem: {idea.problem_statement}",
            f"Solution: {idea.proposed_solution}",
            f"Cost (AI-est.): {idea.estimated_startup_cost}",
            f"Revenue Model: {idea.revenue_model}",
            f"Overall Score: {idea.overall_score:.1f}/10",
            "",
        ]
    if session.business_plan and session.business_plan.roadmap:
        bp = session.business_plan
        lines += [
            "BUSINESS PLAN", "=" * 40,
            "ROADMAP:", bp.roadmap or "",
            "MVP PLAN:", bp.mvp_plan or "",
            "NEXT STEPS:", bp.next_steps or "",
        ]
    lines.append(
        "\nDISCLAIMER: AI-generated content. Does not guarantee business success."
    )
    return "\n".join(lines)
