"""
tests/test_recommendation_agent.py – Unit tests for the ranking logic
in the RecommendationAgent (no LLM calls required).
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import BusinessIdea, FeasibilityReport
from agents.recommendation_agent import RecommendationAgent


def _make_idea(name: str, **scores) -> BusinessIdea:
    idea = BusinessIdea(name=name)
    for k, v in scores.items():
        setattr(idea, k, v)
    return idea


class TestWeightedScore:
    def test_higher_scores_rank_higher(self):
        agent = RecommendationAgent()
        high = _make_idea(
            "HighScore",
            innovation_score=9, feasibility_score=9, market_demand_score=9,
            affordability_score=9, profitability_score=9, social_impact_score=9,
            scalability_score=9,
        )
        low = _make_idea(
            "LowScore",
            innovation_score=3, feasibility_score=3, market_demand_score=3,
            affordability_score=3, profitability_score=3, social_impact_score=3,
            scalability_score=3,
        )
        score_high = agent._weighted_score(high)
        score_low = agent._weighted_score(low)
        assert score_high > score_low

    def test_score_within_range(self):
        agent = RecommendationAgent()
        idea = _make_idea(
            "MidScore",
            innovation_score=5, feasibility_score=5, market_demand_score=5,
            affordability_score=5, profitability_score=5, social_impact_score=5,
            scalability_score=5,
        )
        score = agent._weighted_score(idea)
        assert 0 <= score <= 10

    def test_zero_scores_return_zero(self):
        agent = RecommendationAgent()
        idea = _make_idea("ZeroScore")
        assert agent._weighted_score(idea) == 0.0


class TestRankIdeas:
    def test_returns_sorted_list(self):
        agent = RecommendationAgent()
        ideas = [
            _make_idea("A", feasibility_score=5, market_demand_score=5),
            _make_idea("B", feasibility_score=9, market_demand_score=9),
            _make_idea("C", feasibility_score=3, market_demand_score=3),
        ]
        ranked = agent.rank_ideas(ideas, [])
        names = [idea.name for idea, _ in ranked]
        assert names[0] == "B"
        assert names[-1] == "C"

    def test_not_recommended_penalty(self):
        agent = RecommendationAgent()
        good = _make_idea(
            "Good", feasibility_score=8, market_demand_score=8,
            innovation_score=8, affordability_score=8, profitability_score=8,
            social_impact_score=8, scalability_score=8,
        )
        penalised = _make_idea(
            "Bad", feasibility_score=8, market_demand_score=8,
            innovation_score=8, affordability_score=8, profitability_score=8,
            social_impact_score=8, scalability_score=8,
        )
        fr_bad = FeasibilityReport(
            idea_name="Bad",
            overall_verdict="Not Recommended — too risky",
        )
        ranked = agent.rank_ideas([good, penalised], [fr_bad])
        assert ranked[0][0].name == "Good"

    def test_empty_ideas_returns_empty(self):
        agent = RecommendationAgent()
        ranked = agent.rank_ideas([], [])
        assert ranked == []
