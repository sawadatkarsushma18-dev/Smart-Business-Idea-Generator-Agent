"""
agents/idea_agent.py – Idea Generation Agent.
Calls the LLM to generate a list of business ideas from a user profile.
"""

import logging
from typing import List

from llm_client import granite_client
from models import UserProfile, BusinessIdea
from agents.prompts import build_idea_generation_prompt
from utils.parsers import parse_business_ideas
from utils.validators import sanitize_input

logger = logging.getLogger(__name__)


class IdeaGenerationAgent:
    """
    Agent responsible for generating business ideas from a user profile.
    """

    def generate_ideas(
        self,
        profile: UserProfile,
        num_ideas: int = 5,
    ) -> List[BusinessIdea]:
        """
        Generate business ideas for the given user profile.

        Args:
            profile: Validated UserProfile dataclass.
            num_ideas: Number of ideas to generate (3–5).

        Returns:
            List of BusinessIdea objects.
        """
        # Sanitize all free-text profile fields to reduce injection risk
        clean_profile = UserProfile(
            name=sanitize_input(profile.name),
            interest=sanitize_input(profile.interest),
            skills=sanitize_input(profile.skills),
            background=sanitize_input(profile.background),
            budget=sanitize_input(profile.budget),
            city=sanitize_input(profile.city),
            country=sanitize_input(profile.country),
            target_audience=sanitize_input(profile.target_audience),
            preferred_industry=sanitize_input(profile.preferred_industry),
            business_goals=sanitize_input(profile.business_goals),
        )

        prompt = build_idea_generation_prompt(clean_profile, num_ideas=num_ideas)
        logger.info("IdeaGenerationAgent: generating %d ideas", num_ideas)

        raw_response = granite_client.generate(prompt, max_new_tokens=3500)
        ideas = parse_business_ideas(raw_response)

        if not ideas:
            logger.warning("IdeaGenerationAgent: parser returned empty list; wrapping raw response")
            fallback = BusinessIdea(
                index=1,
                name="AI-Generated Idea",
                problem_statement=raw_response[:600],
            )
            ideas = [fallback]

        logger.info("IdeaGenerationAgent: parsed %d ideas", len(ideas))
        return ideas
