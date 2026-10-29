"""
tests/test_parsers.py – Unit tests for LLM response parsers.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.parsers import (
    parse_business_ideas,
    parse_market_analysis,
    parse_feasibility,
    _split_ideas,
    _extract_score,
)


SAMPLE_IDEA_TEXT = """
IDEA 1
Business Name: EduBot AI
Tagline: Personalised AI tutoring for every student
Problem Statement: Students in rural areas lack access to quality tutors.
Proposed Solution: An AI-powered chatbot that provides 24/7 personalised tutoring.
Target Audience: High school students in Tier-2 and Tier-3 cities
Unique Selling Proposition (USP): Affordable, offline-capable, multilingual tutoring bot
Required Resources: Python developer, cloud hosting, curriculum content
Estimated Startup Cost: $3,000–$8,000 (AI-estimated)
Revenue Model: Freemium subscription — free basic tier, paid premium plans
Implementation Difficulty: Medium — requires NLP expertise
Scalability: Highly scalable via SaaS model
Innovation Score: 8/10
Feasibility Score: 7/10
Market Demand Score: 9/10
Affordability Score: 8/10
Profitability Score: 7/10
Social Impact Score: 9/10
Scalability Score: 9/10
Overall Score: 8/10
Score Rationale: High demand in underserved education markets with strong social impact.

---

IDEA 2
Business Name: GreenRoute
Tagline: Eco-friendly last-mile delivery for local businesses
Problem Statement: Local couriers contribute significantly to urban CO2 emissions.
Proposed Solution: A bicycle and e-scooter delivery network for sustainable last-mile logistics.
Target Audience: Small retail stores and eco-conscious consumers
Unique Selling Proposition (USP): Zero-emission delivery at competitive prices
Required Resources: Fleet of bicycles/e-scooters, logistics app, delivery partners
Estimated Startup Cost: $10,000–$25,000 (AI-estimated)
Revenue Model: Per-delivery fee + monthly subscription for retailers
Implementation Difficulty: Hard — requires operational logistics setup
Scalability: Scalable city by city
Innovation Score: 7/10
Feasibility Score: 6/10
Market Demand Score: 8/10
Affordability Score: 5/10
Profitability Score: 6/10
Social Impact Score: 9/10
Scalability Score: 7/10
Overall Score: 7/10
Score Rationale: Addresses a real environmental problem but requires significant capital.
"""

SAMPLE_MARKET_TEXT = """
Market Size: $45 billion (AI-estimated)
Growth Rate: 18% CAGR (AI-estimated)
Key Trends:
- AI-driven personalisation in education
- Rise of mobile-first learning
- Government EdTech subsidies
Competitor Overview: Byju's, Khan Academy, Duolingo
Customer Pain Points: High cost of private tutoring, limited local teachers
Emerging Technologies: NLP, Generative AI, Adaptive Learning algorithms
"""

SAMPLE_FEASIBILITY_TEXT = """
Technical Feasibility: Fully achievable using existing NLP frameworks and cloud APIs.
Financial Feasibility: Within a $5,000–$8,000 bootstrap budget with lean development.
Operational Feasibility: One developer can manage MVP phase with part-time support.
Risk Assessment: Competition from established players; content accuracy risks.
Mitigation Strategies: Focus on niche market; partner with subject-matter experts.
Overall Verdict: Viable — strong alignment between skills, budget, and market demand.
"""


class TestSplitIdeas:
    def test_splits_two_ideas(self):
        parts = _split_ideas(SAMPLE_IDEA_TEXT)
        assert len(parts) >= 2

    def test_single_idea_returns_list(self):
        parts = _split_ideas("Just one idea text here.")
        assert isinstance(parts, list)
        assert len(parts) == 1


class TestExtractScore:
    def test_extracts_integer_score(self):
        score = _extract_score("Innovation Score: 8/10", "Innovation Score")
        assert score == 8.0

    def test_extracts_decimal_score(self):
        score = _extract_score("Feasibility Score: 7.5/10", "Feasibility Score")
        assert score == 7.5

    def test_returns_zero_if_not_found(self):
        score = _extract_score("No score here", "Innovation")
        assert score == 0.0

    def test_clamps_to_ten(self):
        score = _extract_score("Innovation Score: 15/10", "Innovation Score")
        assert score == 10.0


class TestParseBusinessIdeas:
    def test_parses_multiple_ideas(self):
        ideas = parse_business_ideas(SAMPLE_IDEA_TEXT)
        assert len(ideas) >= 2

    def test_first_idea_has_name(self):
        ideas = parse_business_ideas(SAMPLE_IDEA_TEXT)
        assert ideas[0].name == "EduBot AI"

    def test_second_idea_has_name(self):
        ideas = parse_business_ideas(SAMPLE_IDEA_TEXT)
        assert ideas[1].name == "GreenRoute"

    def test_scores_parsed(self):
        ideas = parse_business_ideas(SAMPLE_IDEA_TEXT)
        assert ideas[0].innovation_score == 8.0
        assert ideas[0].social_impact_score == 9.0

    def test_fallback_on_empty(self):
        ideas = parse_business_ideas("")
        # Should return one fallback idea
        assert len(ideas) == 1

    def test_index_assigned(self):
        ideas = parse_business_ideas(SAMPLE_IDEA_TEXT)
        assert ideas[0].index == 1
        assert ideas[1].index == 2


class TestParseMarketAnalysis:
    def test_parses_market_size(self):
        ma = parse_market_analysis(SAMPLE_MARKET_TEXT, idea_name="EduBot AI")
        assert "45 billion" in ma.market_size

    def test_parses_growth_rate(self):
        ma = parse_market_analysis(SAMPLE_MARKET_TEXT)
        assert "18%" in ma.growth_rate

    def test_parses_trends(self):
        ma = parse_market_analysis(SAMPLE_MARKET_TEXT)
        assert len(ma.key_trends) >= 2

    def test_idea_name_set(self):
        ma = parse_market_analysis(SAMPLE_MARKET_TEXT, idea_name="TestIdea")
        assert ma.idea_name == "TestIdea"

    def test_disclaimer_present(self):
        ma = parse_market_analysis(SAMPLE_MARKET_TEXT)
        assert "AI-estimated" in ma.data_disclaimer


class TestParseFeasibility:
    def test_parses_technical(self):
        fr = parse_feasibility(SAMPLE_FEASIBILITY_TEXT, idea_name="EduBot AI")
        assert "NLP" in fr.technical_feasibility or len(fr.technical_feasibility) > 5

    def test_parses_verdict(self):
        fr = parse_feasibility(SAMPLE_FEASIBILITY_TEXT)
        assert "Viable" in fr.overall_verdict

    def test_idea_name_set(self):
        fr = parse_feasibility(SAMPLE_FEASIBILITY_TEXT, idea_name="TestIdea")
        assert fr.idea_name == "TestIdea"
