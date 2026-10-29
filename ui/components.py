"""
ui/components.py – Reusable Streamlit UI components for the Smart Business
Idea Generator Agent.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import List, Optional

from models import BusinessIdea, MarketAnalysis, FeasibilityReport, BusinessPlan


# ── Score radar chart ───────────────────────────────────────────────────────

def render_score_radar(idea: BusinessIdea) -> None:
    """Render a Plotly radar chart for a single idea's scores."""
    categories = [
        "Innovation",
        "Feasibility",
        "Market Demand",
        "Affordability",
        "Profitability",
        "Social Impact",
        "Scalability",
    ]
    values = [
        idea.innovation_score,
        idea.feasibility_score,
        idea.market_demand_score,
        idea.affordability_score,
        idea.profitability_score,
        idea.social_impact_score,
        idea.scalability_score,
    ]
    fig = go.Figure(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=idea.name,
            line_color="#3b82d4",
            fillcolor="rgba(59,130,212,0.2)",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Score bar chart for comparison ─────────────────────────────────────────

def render_comparison_bar(ideas: List[BusinessIdea]) -> None:
    """Render a grouped bar chart comparing all ideas across score dimensions."""
    categories = [
        "Innovation", "Feasibility", "Market Demand",
        "Affordability", "Profitability", "Social Impact", "Scalability",
    ]
    fig = go.Figure()
    colors = ["#3b82d4", "#7c5cd8", "#22c55e", "#f59e0b", "#ef4444"]
    for i, idea in enumerate(ideas):
        vals = [
            idea.innovation_score, idea.feasibility_score,
            idea.market_demand_score, idea.affordability_score,
            idea.profitability_score, idea.social_impact_score,
            idea.scalability_score,
        ]
        fig.add_trace(go.Bar(
            name=idea.name[:20],
            x=categories,
            y=vals,
            marker_color=colors[i % len(colors)],
        ))
    fig.update_layout(
        barmode="group",
        yaxis=dict(range=[0, 10], title="Score (out of 10)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=60),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Idea card ────────────────────────────────────────────────────────────────

def render_idea_card(
    idea: BusinessIdea,
    market: Optional[MarketAnalysis] = None,
    feasibility: Optional[FeasibilityReport] = None,
    is_recommended: bool = False,
    show_detail: bool = False,
) -> None:
    """Render a single idea as an expandable card."""
    badge = "🏆 **Top Pick** &nbsp;" if is_recommended else ""
    difficulty_colors = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
    diff_icon = difficulty_colors.get(
        (idea.implementation_difficulty or "").split()[0], "⚪"
    )

    with st.expander(
        f"{badge}💡 **{idea.name}** — {idea.tagline or ''}  •  Overall: {idea.overall_score:.1f}/10  •  {diff_icon} {idea.implementation_difficulty}",
        expanded=is_recommended,
    ):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"### {idea.name}")
            if idea.tagline:
                st.caption(idea.tagline)
            st.markdown("**🎯 Problem Statement**")
            st.write(idea.problem_statement or "_Not available_")
            st.markdown("**💡 Proposed Solution**")
            st.write(idea.proposed_solution or "_Not available_")
            st.markdown("**👥 Target Audience**")
            st.write(idea.target_audience or "_Not available_")
            st.markdown("**⭐ USP (Unique Selling Proposition)**")
            st.write(idea.usp or "_Not available_")

        with col2:
            render_score_radar(idea)
            st.caption("*Scores are AI-estimated*")

        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**💰 Startup Cost**")
            st.info(idea.estimated_startup_cost or "N/A")
        with c2:
            st.markdown("**📈 Revenue Model**")
            st.info(idea.revenue_model or "N/A")
        with c3:
            st.markdown("**📐 Scalability**")
            st.info(idea.scalability or "N/A")

        if show_detail:
            st.markdown("**🛠️ Required Resources**")
            st.write(idea.required_resources or "_Not available_")
            if idea.score_rationale:
                st.markdown("**📊 Score Rationale**")
                st.write(idea.score_rationale)
            if market:
                st.divider()
                st.markdown("#### 📊 Market Analysis")
                mc1, mc2 = st.columns(2)
                with mc1:
                    st.metric("Market Size", market.market_size or "N/A")
                    st.metric("Growth Rate", market.growth_rate or "N/A")
                with mc2:
                    if market.key_trends:
                        st.markdown("**Key Trends**")
                        for t in market.key_trends[:3]:
                            st.markdown(f"• {t}")
                st.caption(market.data_disclaimer)
            if feasibility:
                st.divider()
                st.markdown("#### ✅ Feasibility Report")
                verdict = feasibility.overall_verdict or "N/A"
                colour = (
                    "green" if "viable" in verdict.lower()
                    else "red" if "not" in verdict.lower()
                    else "orange"
                )
                st.markdown(f"**Verdict:** :{colour}[{verdict}]")
                st.markdown("**Technical:** " + (feasibility.technical_feasibility or "N/A"))
                st.markdown("**Financial:** " + (feasibility.financial_feasibility or "N/A"))
                st.markdown("**Operational:** " + (feasibility.operational_feasibility or "N/A"))


# ── Ideas comparison table ───────────────────────────────────────────────────

def render_comparison_table(ideas: List[BusinessIdea]) -> None:
    """Render a side-by-side comparison table for all ideas."""
    data = {
        "Field": [
            "Business Name", "Startup Cost", "Revenue Model",
            "Difficulty", "Scalability",
            "Innovation", "Feasibility", "Market Demand",
            "Affordability", "Profitability", "Social Impact", "Overall",
        ]
    }
    for idea in ideas:
        data[idea.name[:18]] = [
            idea.name,
            idea.estimated_startup_cost or "N/A",
            idea.revenue_model or "N/A",
            idea.implementation_difficulty or "N/A",
            idea.scalability[:40] + "…" if len(idea.scalability or "") > 40 else (idea.scalability or "N/A"),
            f"{idea.innovation_score:.1f}/10",
            f"{idea.feasibility_score:.1f}/10",
            f"{idea.market_demand_score:.1f}/10",
            f"{idea.affordability_score:.1f}/10",
            f"{idea.profitability_score:.1f}/10",
            f"{idea.social_impact_score:.1f}/10",
            f"{idea.overall_score:.1f}/10",
        ]
    df = pd.DataFrame(data).set_index("Field")
    st.dataframe(df, use_container_width=True)


# ── Business plan view ───────────────────────────────────────────────────────

def render_business_plan(plan: BusinessPlan) -> None:
    """Render the full business plan in a structured layout."""
    if not plan or not plan.idea:
        st.warning("No business plan available.")
        return

    idea = plan.idea
    st.markdown(f"## 📋 Business Plan: {idea.name}")
    if idea.tagline:
        st.caption(f"*{idea.tagline}*")
    st.divider()

    tabs = st.tabs([
        "🗺️ Roadmap", "🚀 MVP Plan", "🛠️ Tools & Tech",
        "📣 Marketing", "⚠️ Risks", "👣 Next Steps",
    ])

    with tabs[0]:
        st.markdown("### Step-by-Step Execution Roadmap")
        st.write(plan.roadmap or "_Roadmap not available._")

    with tabs[1]:
        st.markdown("### Minimum Viable Product (MVP) Plan")
        st.write(plan.mvp_plan or "_MVP plan not available._")
        st.caption("*Estimated costs are AI-generated and should be verified independently.*")

    with tabs[2]:
        st.markdown("### Tools, Technologies & Resources")
        st.write(plan.tools_and_tech or "_Tools list not available._")

    with tabs[3]:
        st.markdown("### Marketing Strategies")
        st.write(plan.marketing_strategies or "_Marketing strategy not available._")

    with tabs[4]:
        st.markdown("### Risks & Mitigation Strategies")
        st.write(plan.risks_and_mitigations or "_Risk assessment not available._")

    with tabs[5]:
        st.markdown("### Recommended Next Steps")
        st.write(plan.next_steps or "_Next steps not available._")


# ── Progress bar helper ──────────────────────────────────────────────────────

class PipelineProgress:
    """Manages a Streamlit progress bar and status text during pipeline execution."""

    def __init__(self) -> None:
        self._bar = st.progress(0, text="Initialising…")
        self._status = st.empty()

    def update(self, step: int, total: int, message: str) -> None:
        pct = int((step / total) * 100)
        self._bar.progress(pct, text=f"Step {step}/{total}: {message}")
        self._status.info(f"⏳ {message}")

    def complete(self) -> None:
        self._bar.progress(100, text="Complete!")
        self._status.success("✅ All agents have finished!")

    def error(self, msg: str) -> None:
        self._bar.progress(0, text="Error")
        self._status.error(f"❌ {msg}")
