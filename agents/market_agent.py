"""
agents/market_agent.py – Market Analysis Agent.
Performs a concise market analysis for each generated business idea.
"""

import logging
from typing import List

from llm_client import granite_client
from models import BusinessIdea, MarketAnalysis, UserProfile
from agents.prompts import build_market_analysis_prompt
from utils.parsers import parse_market_analysis

logger = logging.getLogger(__name__)


class MarketAnalysisAgent:
    """
    Agent responsible for producing market analysis reports for business ideas.
    """

    def analyse_idea(self, idea: BusinessIdea, profile: UserProfile) -> MarketAnalysis:
        """
        Generate a market analysis for a single business idea.

        Args:
            idea: The BusinessIdea to analyse.
            profile: User profile providing location context.

        Returns:
            A populated MarketAnalysis object.
        """
        prompt = build_market_analysis_prompt(idea, profile)
        logger.info("MarketAnalysisAgent: analysing '%s'", idea.name)

        try:
            raw_response = granite_client.generate(prompt, max_new_tokens=1000)
            return parse_market_analysis(raw_response, idea_name=idea.name)
        except Exception as exc:
            logger.error("MarketAnalysisAgent error for '%s': %s", idea.name, exc)
            return MarketAnalysis(
                idea_name=idea.name,
                market_size="[Unavailable — model error]",
                growth_rate="[Unavailable — model error]",
            )

    def analyse_all(
        self, ideas: List[BusinessIdea], profile: UserProfile
    ) -> List[MarketAnalysis]:
        """
        Run market analysis on a list of ideas sequentially.

        Args:
            ideas: List of BusinessIdea objects.
            profile: User profile.

        Returns:
            List of MarketAnalysis objects (one per idea).
        """
        results: List[MarketAnalysis] = []
        for idea in ideas:
            ma = self.analyse_idea(idea, profile)
            results.append(ma)
        return results
