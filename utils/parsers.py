"""
utils/parsers.py – Helpers to parse structured text from LLM responses
into typed Python objects.
"""

import re
import logging
from typing import List, Optional

from models import BusinessIdea, MarketAnalysis, FeasibilityReport

logger = logging.getLogger(__name__)


# ── Generic extraction helpers ──────────────────────────────────────────────

def _extract_block(text: str, label: str) -> str:
    """Extract the value after a label like 'Business Name:' up to the next label."""
    pattern = rf"{re.escape(label)}\s*[:\-]?\s*(.*?)(?=\n[A-Z][^\n]{{2,}}[:\-]|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def _extract_score(text: str, label: str) -> float:
    """Extract a numeric score (e.g. 'Innovation Score: 8/10' → 8.0).

    Handles both 'Innovation: 8/10' and 'Innovation Score: 8/10' forms.
    """
    # Allow optional word(s) between label and the number (e.g. "Score")
    pattern = rf"{re.escape(label)}(?:\s+\w+)?\s*[:\-]?\s*([\d.]+)\s*/?\s*10?"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            val = float(match.group(1))
            return min(max(val, 0.0), 10.0)
        except ValueError:
            pass
    return 0.0


def _split_ideas(text: str) -> List[str]:
    """
    Split a multi-idea LLM response into individual idea blocks.
    Tries numbered headings (IDEA 1, Idea #2, 1., **1**) first,
    then falls back on '---' separators.
    """
    # Try splitting on idea headers
    parts = re.split(
        r"(?:^|\n)\s*(?:\*{0,2})\s*(?:IDEA|Idea|idea)\s*[#\-]?\s*\d+[:\.\)]*\s*(?:\*{0,2})",
        text,
    )
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    # Numbered list: "1. ...", "2. ..."
    parts = re.split(r"(?:^|\n)\s*\d+\.\s+", text)
    if len(parts) > 2:
        return [p.strip() for p in parts if p.strip()]

    # Separator: ---
    parts = re.split(r"\n[-—=]{3,}\n", text)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    return [text.strip()]


# ── Business idea parser ────────────────────────────────────────────────────

def parse_business_ideas(raw_text: str) -> List[BusinessIdea]:
    """
    Parse the LLM's raw text output into a list of BusinessIdea objects.
    Falls back gracefully if the text is not perfectly structured.
    """
    idea_blocks = _split_ideas(raw_text)
    ideas: List[BusinessIdea] = []

    for i, block in enumerate(idea_blocks[:5]):  # cap at 5
        idea = BusinessIdea(index=i + 1)
        idea.name = (
            _extract_block(block, "Business Name")
            or _extract_block(block, "Name")
            or f"Business Idea {i + 1}"
        )
        idea.tagline = _extract_block(block, "Tagline") or _extract_block(block, "One-liner")
        idea.problem_statement = (
            _extract_block(block, "Problem Statement")
            or _extract_block(block, "Problem")
        )
        idea.proposed_solution = (
            _extract_block(block, "Proposed Solution")
            or _extract_block(block, "Solution")
        )
        idea.target_audience = _extract_block(block, "Target Audience")
        idea.usp = (
            _extract_block(block, "Unique Selling Proposition")
            or _extract_block(block, "USP")
        )
        idea.required_resources = _extract_block(block, "Required Resources")
        idea.estimated_startup_cost = (
            _extract_block(block, "Estimated Startup Cost")
            or _extract_block(block, "Startup Cost")
        )
        idea.revenue_model = (
            _extract_block(block, "Revenue Model")
            or _extract_block(block, "Revenue")
        )
        idea.implementation_difficulty = (
            _extract_block(block, "Implementation Difficulty")
            or _extract_block(block, "Difficulty")
        )
        idea.scalability = _extract_block(block, "Scalability")

        # Scores
        idea.innovation_score = _extract_score(block, "Innovation")
        idea.feasibility_score = _extract_score(block, "Feasibility")
        idea.market_demand_score = _extract_score(block, "Market Demand")
        idea.affordability_score = _extract_score(block, "Affordability")
        idea.profitability_score = _extract_score(block, "Profitability")
        idea.social_impact_score = _extract_score(block, "Social Impact")
        idea.scalability_score = _extract_score(block, "Scalability Score")
        idea.overall_score = _extract_score(block, "Overall Score")
        idea.score_rationale = _extract_block(block, "Score Rationale") or _extract_block(block, "Rationale")

        if not idea.problem_statement:
            # Store the whole block as problem_statement as a fallback
            idea.problem_statement = block[:400]

        ideas.append(idea)

    return ideas


# ── Market analysis parser ──────────────────────────────────────────────────

def parse_market_analysis(raw_text: str, idea_name: str = "") -> MarketAnalysis:
    """Parse market analysis text into a MarketAnalysis object."""
    ma = MarketAnalysis(idea_name=idea_name)
    ma.market_size = _extract_block(raw_text, "Market Size")
    ma.growth_rate = _extract_block(raw_text, "Growth Rate")
    ma.competitor_overview = _extract_block(raw_text, "Competitor Overview") or _extract_block(raw_text, "Competitors")
    ma.customer_pain_points = _extract_block(raw_text, "Customer Pain Points") or _extract_block(raw_text, "Pain Points")
    ma.emerging_technologies = _extract_block(raw_text, "Emerging Technologies") or _extract_block(raw_text, "Technologies")

    # Extract key trends as a list
    trends_raw = _extract_block(raw_text, "Key Trends") or _extract_block(raw_text, "Trends")
    if trends_raw:
        ma.key_trends = [t.strip("- •*").strip() for t in re.split(r"\n|;", trends_raw) if t.strip()]
    return ma


# ── Feasibility parser ───────────────────────────────────────────────────────

def parse_feasibility(raw_text: str, idea_name: str = "") -> FeasibilityReport:
    """Parse feasibility analysis text into a FeasibilityReport object."""
    fr = FeasibilityReport(idea_name=idea_name)
    fr.technical_feasibility = _extract_block(raw_text, "Technical Feasibility")
    fr.financial_feasibility = _extract_block(raw_text, "Financial Feasibility")
    fr.operational_feasibility = _extract_block(raw_text, "Operational Feasibility")
    fr.risk_assessment = _extract_block(raw_text, "Risk Assessment") or _extract_block(raw_text, "Risks")
    fr.mitigation_strategies = _extract_block(raw_text, "Mitigation Strategies") or _extract_block(raw_text, "Mitigation")
    fr.overall_verdict = _extract_block(raw_text, "Overall Verdict") or _extract_block(raw_text, "Verdict")
    return fr
