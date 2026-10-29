"""
agents/orchestrator.py – Master Agentic Workflow Orchestrator.
Co-ordinates idea generation → market analysis → feasibility → recommendation.
"""

import logging
from typing import List, Tuple

from models import (
    AgentSession,
    UserProfile,
    BusinessIdea,
    MarketAnalysis,
    FeasibilityReport,
    BusinessPlan,
)
from agents.idea_agent import IdeaGenerationAgent
from agents.market_agent import MarketAnalysisAgent
from agents.feasibility_agent import FeasibilityAgent
from agents.recommendation_agent import RecommendationAgent

logger = logging.getLogger(__name__)


class BusinessIdeaOrchestrator:
    """
    High-level agentic orchestrator that drives the full idea-generation pipeline:

    1. IdeaGenerationAgent   → Generate N business ideas
    2. MarketAnalysisAgent   → Analyse each idea's market
    3. FeasibilityAgent      → Evaluate each idea's feasibility
    4. RecommendationAgent   → Rank, recommend, and build the business plan
    """

    def __init__(self) -> None:
        self._idea_agent = IdeaGenerationAgent()
        self._market_agent = MarketAnalysisAgent()
        self._feasibility_agent = FeasibilityAgent()
        self._recommendation_agent = RecommendationAgent()

    # ── Full pipeline ───────────────────────────────────────────────────────

    def run_full_pipeline(
        self,
        profile: UserProfile,
        num_ideas: int = 5,
        progress_callback=None,
    ) -> AgentSession:
        """
        Execute the complete agentic pipeline and return a populated AgentSession.

        Args:
            profile: Validated UserProfile.
            num_ideas: Number of ideas to generate.
            progress_callback: Optional callable(step: int, total: int, message: str)
                               used to update a progress bar in the UI.

        Returns:
            AgentSession with ideas, analyses, feasibility reports, and a business plan.
        """
        total_steps = 5
        session = AgentSession(profile=profile)

        def _progress(step: int, msg: str) -> None:
            if progress_callback:
                progress_callback(step, total_steps, msg)
            logger.info("[Step %d/%d] %s", step, total_steps, msg)

        # ── Step 1: Generate ideas ──────────────────────────────────────────
        _progress(1, "Generating business ideas with Llama 3.3 70B…")
        session.ideas = self._idea_agent.generate_ideas(profile, num_ideas=num_ideas)

        # ── Step 2: Market analysis ─────────────────────────────────────────
        _progress(2, "Conducting market analysis…")
        session.market_analyses = self._market_agent.analyse_all(session.ideas, profile)

        # ── Step 3: Feasibility evaluation ─────────────────────────────────
        _progress(3, "Evaluating feasibility of each idea…")
        session.feasibility_reports = self._feasibility_agent.evaluate_all(
            session.ideas, profile
        )

        # ── Step 4: Rank and recommend ──────────────────────────────────────
        _progress(4, "Ranking ideas and preparing recommendation…")
        ranked: List[Tuple[BusinessIdea, float]] = self._recommendation_agent.rank_ideas(
            session.ideas, session.feasibility_reports
        )
        # Store weighted scores back into idea objects for UI display
        score_map = {idea.name: score for idea, score in ranked}
        for idea in session.ideas:
            idea.overall_score = max(idea.overall_score, score_map.get(idea.name, 0.0))

        best_idea = ranked[0][0] if ranked else session.ideas[0]
        session.recommended_index = session.ideas.index(best_idea)

        # ── Step 5: Generate business plan for top idea ─────────────────────
        _progress(5, f"Generating detailed business plan for '{best_idea.name}'…")
        market_for_best = (
            session.market_analyses[session.recommended_index]
            if session.market_analyses
            else None
        )
        feasibility_for_best = (
            session.feasibility_reports[session.recommended_index]
            if session.feasibility_reports
            else None
        )
        session.business_plan = self._recommendation_agent.generate_business_plan(
            best_idea, profile, market_for_best, feasibility_for_best
        )

        logger.info(
            "Pipeline complete. %d ideas generated. Recommended: '%s'",
            len(session.ideas),
            best_idea.name,
        )
        return session

    # ── Standalone plan generation ─────────────────────────────────────────

    def generate_plan_for_idea(
        self,
        idea: BusinessIdea,
        profile: UserProfile,
        market_analysis: MarketAnalysis | None = None,
        feasibility: FeasibilityReport | None = None,
    ) -> BusinessPlan:
        """
        Generate a business plan for any selected idea (not just the top one).
        """
        return self._recommendation_agent.generate_business_plan(
            idea, profile, market_analysis, feasibility
        )

    # ── Follow-up query ────────────────────────────────────────────────────

    def answer_followup(
        self, query: str, session: AgentSession
    ) -> str:
        """
        Answer a user follow-up question in the context of the current session.
        """
        from agents.prompts import build_followup_prompt
        from llm_client import granite_client

        # Build a short context summary from the session
        if session.ideas:
            context_lines = ["Previously generated ideas:"]
            for idea in session.ideas:
                context_lines.append(
                    f"  - {idea.name}: {idea.tagline or idea.problem_statement[:80]}"
                )
            context = "\n".join(context_lines)
        else:
            context = "No ideas have been generated yet."

        prompt = build_followup_prompt(query, context, session.profile or UserProfile())
        try:
            return granite_client.generate(prompt, max_new_tokens=900)
        except Exception as exc:
            logger.error("Follow-up query error: %s", exc)
            return f"Sorry, I couldn't process your query right now. Please try again.\n({exc})"

    # ── Idea comparison ────────────────────────────────────────────────────

    def compare_ideas(
        self, idea_a: BusinessIdea, idea_b: BusinessIdea, profile: UserProfile
    ) -> str:
        """Ask the LLM to compare two specific ideas side by side."""
        from agents.prompts import build_followup_prompt
        from llm_client import granite_client

        query = (
            f"Please compare these two business ideas in detail:\n"
            f"1. {idea_a.name}: {idea_a.tagline}\n"
            f"2. {idea_b.name}: {idea_b.tagline}\n\n"
            f"Include: strengths, weaknesses, suitability for my profile, "
            f"which one I should choose and why."
        )
        context = (
            f"Idea A — {idea_a.name}: Problem: {idea_a.problem_statement[:150]} | "
            f"Cost: {idea_a.estimated_startup_cost}\n"
            f"Idea B — {idea_b.name}: Problem: {idea_b.problem_statement[:150]} | "
            f"Cost: {idea_b.estimated_startup_cost}"
        )
        prompt = build_followup_prompt(query, context, profile)
        try:
            return granite_client.generate(prompt, max_new_tokens=1200)
        except Exception as exc:
            logger.error("Compare ideas error: %s", exc)
            return f"Comparison unavailable. Error: {exc}"
