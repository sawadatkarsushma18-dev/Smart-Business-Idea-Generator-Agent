"""
agents/feasibility_agent.py – Feasibility Evaluation Agent.
Evaluates the practicality and viability of each business idea.
"""

import logging
from typing import List

from llm_client import granite_client
from models import BusinessIdea, FeasibilityReport, UserProfile
from agents.prompts import build_feasibility_prompt
from utils.parsers import parse_feasibility

logger = logging.getLogger(__name__)


class FeasibilityAgent:
    """
    Agent responsible for evaluating the feasibility of business ideas.
    """

    def evaluate_idea(
        self, idea: BusinessIdea, profile: UserProfile
    ) -> FeasibilityReport:
        """
        Evaluate the feasibility of a single idea.

        Args:
            idea: The BusinessIdea to evaluate.
            profile: User profile for budget / skills context.

        Returns:
            A populated FeasibilityReport object.
        """
        prompt = build_feasibility_prompt(idea, profile)
        logger.info("FeasibilityAgent: evaluating '%s'", idea.name)

        try:
            raw_response = granite_client.generate(prompt, max_new_tokens=900)
            return parse_feasibility(raw_response, idea_name=idea.name)
        except Exception as exc:
            logger.error("FeasibilityAgent error for '%s': %s", idea.name, exc)
            return FeasibilityReport(
                idea_name=idea.name,
                overall_verdict="[Unavailable — model error]",
            )

    def evaluate_all(
        self, ideas: List[BusinessIdea], profile: UserProfile
    ) -> List[FeasibilityReport]:
        """
        Evaluate feasibility for a list of ideas.

        Args:
            ideas: List of BusinessIdea objects.
            profile: User profile.

        Returns:
            List of FeasibilityReport objects.
        """
        results: List[FeasibilityReport] = []
        for idea in ideas:
            report = self.evaluate_idea(idea, profile)
            results.append(report)
        return results
