"""
agents/recommendation_agent.py – Recommendation & Business-Plan Agent.
Synthesises idea evaluations into a ranked recommendation and a full business plan.
"""

import logging
from typing import List, Tuple

from llm_client import granite_client
from models import (
    BusinessIdea,
    FeasibilityReport,
    MarketAnalysis,
    BusinessPlan,
    UserProfile,
)
from agents.prompts import build_recommendation_prompt, build_business_plan_prompt

logger = logging.getLogger(__name__)


class RecommendationAgent:
    """
    Agent that ranks ideas and generates the detailed business plan for the
    top recommendation.
    """

    # ── Scoring & Ranking ───────────────────────────────────────────────────

    @staticmethod
    def _weighted_score(idea: BusinessIdea) -> float:
        """
        Compute a composite weighted score for ranking.
        Weights reflect entrepreneurial importance: market demand and
        feasibility are weighted highest.
        """
        weights = {
            "innovation": 0.10,
            "feasibility": 0.20,
            "market_demand": 0.20,
            "affordability": 0.15,
            "profitability": 0.15,
            "social_impact": 0.10,
            "scalability": 0.10,
        }
        score = (
            idea.innovation_score * weights["innovation"]
            + idea.feasibility_score * weights["feasibility"]
            + idea.market_demand_score * weights["market_demand"]
            + idea.affordability_score * weights["affordability"]
            + idea.profitability_score * weights["profitability"]
            + idea.social_impact_score * weights["social_impact"]
            + idea.scalability_score * weights["scalability"]
        )
        # If the model already provided an overall_score, blend it
        if idea.overall_score > 0:
            score = 0.5 * score + 0.5 * (idea.overall_score * 0.10)
        return round(score, 2)

    def rank_ideas(
        self,
        ideas: List[BusinessIdea],
        feasibility_reports: List[FeasibilityReport],
    ) -> List[Tuple[BusinessIdea, float]]:
        """
        Rank ideas by weighted composite score.
        Penalises ideas marked 'Not Recommended' in feasibility.

        Returns:
            List of (idea, score) tuples sorted descending.
        """
        ranked = []
        feasibility_map = {fr.idea_name: fr for fr in feasibility_reports}

        for idea in ideas:
            score = self._weighted_score(idea)
            fr = feasibility_map.get(idea.name)
            if fr and "not recommended" in (fr.overall_verdict or "").lower():
                score *= 0.7  # 30 % penalty for non-viable ideas
            ranked.append((idea, score))

        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    # ── LLM-based recommendation narrative ─────────────────────────────────

    def get_recommendation_narrative(
        self,
        ideas: List[BusinessIdea],
        profile: UserProfile,
    ) -> str:
        """
        Ask the LLM to write a personalised recommendation narrative.
        """
        ideas_summary = "\n".join(
            [
                f"- {idea.name} (Overall: {idea.overall_score}/10, "
                f"Feasibility: {idea.feasibility_score}/10, "
                f"Market Demand: {idea.market_demand_score}/10)"
                for idea in ideas
            ]
        )
        prompt = build_recommendation_prompt(ideas_summary, profile)
        try:
            return granite_client.generate(prompt, max_new_tokens=700)
        except Exception as exc:
            logger.error("RecommendationAgent narrative error: %s", exc)
            return "[Recommendation narrative unavailable — model error]"

    # ── Business Plan Generation ────────────────────────────────────────────

    def generate_business_plan(
        self,
        idea: BusinessIdea,
        profile: UserProfile,
        market_analysis: MarketAnalysis | None = None,
        feasibility: FeasibilityReport | None = None,
    ) -> BusinessPlan:
        """
        Generate a detailed business plan for the selected idea.

        Args:
            idea: The chosen BusinessIdea.
            profile: User profile.
            market_analysis: Optional pre-computed market analysis.
            feasibility: Optional pre-computed feasibility report.

        Returns:
            A fully populated BusinessPlan object.
        """
        logger.info("RecommendationAgent: generating business plan for '%s'", idea.name)
        prompt = build_business_plan_prompt(idea, profile)

        try:
            raw_plan = granite_client.generate(prompt, max_new_tokens=3000)
        except Exception as exc:
            logger.error("Business plan generation error: %s", exc)
            raw_plan = "[Business plan unavailable — model error]"

        plan = BusinessPlan(
            idea=idea,
            market_analysis=market_analysis,
            feasibility=feasibility,
        )

        # Parse sections from the raw plan text
        import re

        def _extract(label: str) -> str:
            pattern = rf"{re.escape(label)}[:\n]\s*(.*?)(?=\n[A-Z][A-Z ]+[:\n]|\Z)"
            match = re.search(pattern, raw_plan, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else ""

        plan.roadmap = _extract("ROADMAP")
        plan.mvp_plan = _extract("MVP PLAN")
        plan.tools_and_tech = _extract("TOOLS AND TECHNOLOGIES")
        plan.marketing_strategies = _extract("MARKETING STRATEGIES")
        plan.risks_and_mitigations = _extract("RISKS AND MITIGATIONS")
        plan.next_steps = _extract("NEXT STEPS")

        # Fallback: store entire response if parsing yielded nothing
        if not plan.roadmap:
            plan.roadmap = raw_plan

        return plan
