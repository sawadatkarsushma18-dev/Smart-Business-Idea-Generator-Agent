"""
agents/prompts.py – All prompt templates used by the agentic workflow.
Centralising prompts here makes them easy to tune and test independently.
"""

from models import UserProfile, BusinessIdea


# ── Idea Generation ─────────────────────────────────────────────────────────

def build_idea_generation_prompt(profile: UserProfile, num_ideas: int = 5) -> str:
    return f"""You are an expert business innovation consultant and startup strategist.
A user wants to generate smart business ideas based on their profile.

USER PROFILE:
- Name: {profile.name or 'Not provided'}
- Area of Interest: {profile.interest}
- Skills: {profile.skills}
- Educational/Professional Background: {profile.background or 'Not specified'}
- Budget: {profile.budget}
- Location: {profile.city or ''} {profile.country}
- Target Audience: {profile.target_audience}
- Preferred Industry: {profile.preferred_industry or 'Open to suggestions'}
- Business Goals: {profile.business_goals or 'Not specified'}

TASK:
Generate exactly {num_ideas} unique, innovative, and actionable business ideas tailored to this user's profile, budget, location, and goals.

For EACH idea, provide ALL of the following sections in EXACTLY this format:

IDEA [NUMBER]
Business Name: [Creative, memorable business name]
Tagline: [One-sentence value proposition]
Problem Statement: [Specific problem this business solves]
Proposed Solution: [How this business solves the problem]
Target Audience: [Who are the customers]
Unique Selling Proposition (USP): [What makes this uniquely better than alternatives]
Required Resources: [Key resources needed to start]
Estimated Startup Cost: [Cost range in user's local currency — label as AI-estimated]
Revenue Model: [How the business makes money]
Implementation Difficulty: [Easy / Medium / Hard — with brief reason]
Scalability: [How and how much this can scale]
Innovation Score: [X/10]
Feasibility Score: [X/10]
Market Demand Score: [X/10]
Affordability Score: [X/10]
Profitability Score: [X/10]
Social Impact Score: [X/10]
Scalability Score: [X/10]
Overall Score: [X/10]
Score Rationale: [2–3 sentences explaining the scores]

---

IMPORTANT RULES:
- Ideas must be realistic and achievable within the stated budget.
- Ideas must be relevant to the user's location and culture.
- Do NOT guarantee profits or success.
- Label ALL cost figures as AI-estimated.
- Be inclusive and avoid discriminatory assumptions.
- Avoid repeating similar ideas — make each one distinctly different.
- Cover a mix of domains: digital, physical, service, and social impact.
"""


# ── Market Analysis ─────────────────────────────────────────────────────────

def build_market_analysis_prompt(idea: BusinessIdea, profile: UserProfile) -> str:
    return f"""You are a market research analyst specialising in startup ecosystems.
Perform a concise market analysis for the following business idea.

BUSINESS IDEA: {idea.name}
DESCRIPTION: {idea.problem_statement}
LOCATION: {profile.city or ''} {profile.country}
TARGET AUDIENCE: {idea.target_audience or profile.target_audience}

Provide a structured market analysis using EXACTLY these sections:

Market Size: [Estimated global or local market size — label as AI-estimated]
Growth Rate: [Estimated annual growth rate — label as AI-estimated]
Key Trends:
- [Trend 1]
- [Trend 2]
- [Trend 3]
Competitor Overview: [2–3 main competitors or alternatives]
Customer Pain Points: [Top 3 pain points this idea addresses]
Emerging Technologies: [Relevant technologies driving this market]

IMPORTANT: All statistics are AI-generated estimates. Clearly label them.
Do NOT fabricate specific company names as verified facts.
"""


# ── Feasibility Evaluation ──────────────────────────────────────────────────

def build_feasibility_prompt(idea: BusinessIdea, profile: UserProfile) -> str:
    return f"""You are a business feasibility expert evaluating startup viability.
Evaluate the feasibility of this business idea for the given user.

BUSINESS IDEA: {idea.name}
SOLUTION: {idea.proposed_solution}
BUDGET: {profile.budget}
USER SKILLS: {profile.skills}
LOCATION: {profile.city or ''} {profile.country}
IMPLEMENTATION DIFFICULTY: {idea.implementation_difficulty}

Provide a structured feasibility report using EXACTLY these sections:

Technical Feasibility: [Can it be built with available technology and the user's skills?]
Financial Feasibility: [Is it achievable within the stated budget? What are the financial risks?]
Operational Feasibility: [Can the user realistically run this business day-to-day?]
Risk Assessment: [Top 3–4 risks]
Mitigation Strategies: [How to mitigate each risk]
Overall Verdict: [Viable / Needs Adjustment / Not Recommended — with 2–3 sentence justification]
"""


# ── Recommendation ──────────────────────────────────────────────────────────

def build_recommendation_prompt(ideas_summary: str, profile: UserProfile) -> str:
    return f"""You are a senior startup advisor making personalised recommendations.
Based on the following evaluated business ideas and the user's profile, recommend the BEST single idea.

USER PROFILE SUMMARY:
- Skills: {profile.skills}
- Budget: {profile.budget}
- Location: {profile.city or ''} {profile.country}
- Goals: {profile.business_goals or 'Build a sustainable business'}

IDEAS EVALUATED:
{ideas_summary}

Provide:
1. RECOMMENDED IDEA: [Name of the best idea]
2. WHY THIS IDEA: [3–4 sentences explaining why this suits the user best]
3. KEY ADVANTAGES: [Bullet list of 3 strengths]
4. MAIN CHALLENGES: [Bullet list of 2–3 challenges to overcome]
5. FIRST 30-DAY ACTION PLAN: [5 concrete steps to take in the first month]
"""


# ── Business Plan ──────────────────────────────────────────────────────────

def build_business_plan_prompt(idea: BusinessIdea, profile: UserProfile) -> str:
    return f"""You are an expert business plan writer and startup coach.
Create a detailed, actionable business plan for the following idea.

BUSINESS IDEA: {idea.name}
TAGLINE: {idea.tagline}
PROBLEM: {idea.problem_statement}
SOLUTION: {idea.proposed_solution}
TARGET AUDIENCE: {idea.target_audience}
USP: {idea.usp}
REVENUE MODEL: {idea.revenue_model}
USER SKILLS: {profile.skills}
BUDGET: {profile.budget}
LOCATION: {profile.city or ''} {profile.country}

Generate a comprehensive business plan with EXACTLY these sections:

ROADMAP:
[Step-by-step execution plan — minimum 8 steps with timeframes]

MVP PLAN:
[Minimum Viable Product: what to build first, core features only, estimated MVP cost — label as AI-estimated]

TOOLS AND TECHNOLOGIES:
[List of essential tools, platforms, frameworks, and services with brief descriptions]

MARKETING STRATEGIES:
[5–6 practical marketing tactics suited to the budget and audience]

RISKS AND MITIGATIONS:
[Top 5 risks with mitigation strategy for each]

NEXT STEPS:
[Immediate next 7 actions the entrepreneur should take starting today]

IMPORTANT: Label all financial figures as AI-estimated. Do not guarantee success or returns.
"""


# ── Follow-up / Refinement ─────────────────────────────────────────────────

def build_followup_prompt(query: str, context: str, profile: UserProfile) -> str:
    return f"""You are a smart business advisor helping an entrepreneur refine their business ideas.

USER CONTEXT:
{context}

USER PROFILE (for reference):
- Interest: {profile.interest}
- Skills: {profile.skills}
- Budget: {profile.budget}
- Location: {profile.country}

USER QUERY:
{query}

Respond helpfully, concisely, and with actionable advice.
If comparing ideas, use a structured comparison table format.
If suggesting refinements, be specific and practical.
Always label estimated costs and projections as AI-estimated.
"""
