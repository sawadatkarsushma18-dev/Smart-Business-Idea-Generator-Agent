"""
models.py – Pydantic-style dataclasses for all structured data exchanged
between agents and the UI layer.
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ── User profile ────────────────────────────────────────────────────────────
@dataclass
class UserProfile:
    name: str = ""
    interest: str = ""
    skills: str = ""
    background: str = ""
    budget: str = ""
    city: str = ""
    country: str = ""
    target_audience: str = ""
    preferred_industry: str = ""
    business_goals: str = ""


# ── A single business idea ──────────────────────────────────────────────────
@dataclass
class BusinessIdea:
    index: int = 0
    name: str = ""
    tagline: str = ""
    problem_statement: str = ""
    proposed_solution: str = ""
    target_audience: str = ""
    usp: str = ""                       # Unique Selling Proposition
    required_resources: str = ""
    estimated_startup_cost: str = ""
    revenue_model: str = ""
    implementation_difficulty: str = ""  # Easy / Medium / Hard
    scalability: str = ""
    # Evaluation scores (0–10)
    innovation_score: float = 0.0
    feasibility_score: float = 0.0
    market_demand_score: float = 0.0
    affordability_score: float = 0.0
    profitability_score: float = 0.0
    social_impact_score: float = 0.0
    scalability_score: float = 0.0
    overall_score: float = 0.0
    score_rationale: str = ""


# ── Market analysis snapshot ─────────────────────────────────────────────────
@dataclass
class MarketAnalysis:
    idea_name: str = ""
    market_size: str = ""
    growth_rate: str = ""
    key_trends: List[str] = field(default_factory=list)
    competitor_overview: str = ""
    customer_pain_points: str = ""
    emerging_technologies: str = ""
    data_disclaimer: str = (
        "[AI-estimated] Market figures are model-generated approximations. "
        "Verify with authoritative sources before making decisions."
    )


# ── Feasibility report ───────────────────────────────────────────────────────
@dataclass
class FeasibilityReport:
    idea_name: str = ""
    technical_feasibility: str = ""
    financial_feasibility: str = ""
    operational_feasibility: str = ""
    risk_assessment: str = ""
    mitigation_strategies: str = ""
    overall_verdict: str = ""           # Viable / Needs Adjustment / Not Recommended


# ── Full business plan ───────────────────────────────────────────────────────
@dataclass
class BusinessPlan:
    idea: Optional[BusinessIdea] = None
    market_analysis: Optional[MarketAnalysis] = None
    feasibility: Optional[FeasibilityReport] = None
    roadmap: str = ""           # Step-by-step execution plan
    mvp_plan: str = ""          # Minimum Viable Product plan
    tools_and_tech: str = ""
    marketing_strategies: str = ""
    risks_and_mitigations: str = ""
    next_steps: str = ""


# ── Agent session (holds all state for one user session) ─────────────────────
@dataclass
class AgentSession:
    profile: Optional[UserProfile] = None
    ideas: List[BusinessIdea] = field(default_factory=list)
    market_analyses: List[MarketAnalysis] = field(default_factory=list)
    feasibility_reports: List[FeasibilityReport] = field(default_factory=list)
    recommended_index: int = 0
    business_plan: Optional[BusinessPlan] = None
    conversation_history: List[dict] = field(default_factory=list)
