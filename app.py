"""
app.py – Main Streamlit application entry point for the
Smart Business Idea Generator Agent.

Run with:  streamlit run app.py
"""

import streamlit as st
import logging

from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Smart Business Idea Generator",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports (after page config) ──────────────────────────────────────
from config import DISCLAIMER, APP_VERSION
from models import UserProfile, AgentSession
from agents.orchestrator import BusinessIdeaOrchestrator
from ui.components import (
    render_idea_card,
    render_comparison_table,
    render_comparison_bar,
    render_business_plan,
    PipelineProgress,
)
from utils.validators import validate_profile, sanitize_input
from utils.pdf_exporter import generate_pdf_report


# ── Session state initialisation ────────────────────────────────────────────
def _init_session() -> None:
    defaults = {
        "session": None,          # AgentSession
        "orchestrator": None,     # BusinessIdeaOrchestrator
        "page": "home",           # home | results | plan | chat
        "chat_history": [],
        "selected_idea_idx": 0,
        "compare_a": 0,
        "compare_b": 1,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_session()


# ── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    with st.sidebar:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg",
            width=80,
        )
        st.markdown(f"## 💡 Idea Generator\n*v{APP_VERSION}*")
        st.divider()

        if st.session_state.session:
            st.success("✅ Ideas Generated")
            nav = st.radio(
                "Navigate",
                ["🏠 Home", "💡 Ideas", "📊 Compare", "📋 Business Plan", "💬 Chat"],
                label_visibility="collapsed",
            )
            page_map = {
                "🏠 Home": "home",
                "💡 Ideas": "results",
                "📊 Compare": "compare",
                "📋 Business Plan": "plan",
                "💬 Chat": "chat",
            }
            st.session_state.page = page_map.get(nav, "home")

            st.divider()
            if st.button("🔄 Start Over", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

            # Download report
            agent_session: AgentSession = st.session_state.session
            if agent_session and agent_session.ideas:
                st.markdown("### 📥 Download Report")
                try:
                    pdf_bytes = generate_pdf_report(agent_session)
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name="business_ideas_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    from utils.pdf_exporter import _generate_text_report
                    txt = _generate_text_report(agent_session)
                    st.download_button(
                        label="⬇️ Download Text Report",
                        data=txt,
                        file_name="business_ideas_report.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
        else:
            st.info("Fill in your profile on the Home page to get started.")

        st.divider()
        st.caption(
            "Powered by **Llama 3.3 70B Instruct** via IBM WatsonX AI.\n\n"
            "All outputs are AI-generated suggestions."
        )


# ── Home / Profile Form ──────────────────────────────────────────────────────
def render_home() -> None:
    st.markdown("# 💡 Smart Business Idea Generator Agent")
    st.markdown(
        "*Powered by Meta Llama 3.3 70B Instruct via IBM WatsonX AI — Transform your interests into actionable business opportunities.*"
    )
    st.warning(DISCLAIMER)
    st.divider()

    st.markdown("## 👤 Tell Us About Yourself")
    st.caption("Fields marked with \\* are required.")

    with st.form("profile_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Your Name (optional)", placeholder="e.g. Alex Kumar")
            interest = st.text_input(
                "Area of Interest *",
                placeholder="e.g. EdTech, Healthcare AI, Sustainable Fashion",
            )
            skills = st.text_area(
                "Your Skills *",
                placeholder="e.g. Python, graphic design, marketing, teaching",
                height=90,
            )
            background = st.text_input(
                "Educational / Professional Background",
                placeholder="e.g. Computer Science graduate, 2 years in sales",
            )
            budget = st.text_input(
                "Available Budget *",
                placeholder="e.g. $5000, ₹50,000, Bootstrap / Zero budget",
            )
        with c2:
            city = st.text_input("City", placeholder="e.g. Sydney, Mumbai, Nairobi")
            country = st.text_input(
                "Country *",
                placeholder="e.g. Australia, India, Nigeria",
            )
            target_audience = st.text_input(
                "Target Audience *",
                placeholder="e.g. College students, small business owners, parents",
            )
            preferred_industry = st.text_input(
                "Preferred Industry",
                placeholder="e.g. FinTech, AgriTech, E-commerce, Education",
            )
            business_goals = st.text_area(
                "Business Goals",
                placeholder="e.g. Generate side income, solve a local problem, build a scalable startup",
                height=90,
            )

        num_ideas = st.slider(
            "Number of ideas to generate", min_value=3, max_value=5, value=5
        )

        submitted = st.form_submit_button(
            "🚀 Generate Business Ideas", use_container_width=True, type="primary"
        )

    if submitted:
        profile_data = {
            "name": sanitize_input(name),
            "interest": sanitize_input(interest),
            "skills": sanitize_input(skills),
            "background": sanitize_input(background),
            "budget": sanitize_input(budget),
            "city": sanitize_input(city),
            "country": sanitize_input(country),
            "target_audience": sanitize_input(target_audience),
            "preferred_industry": sanitize_input(preferred_industry),
            "business_goals": sanitize_input(business_goals),
        }
        valid, errors = validate_profile(profile_data)
        if not valid:
            for err in errors:
                st.error(f"⚠️ {err}")
            return

        profile = UserProfile(**profile_data)
        _run_pipeline(profile, num_ideas)


def _run_pipeline(profile: UserProfile, num_ideas: int) -> None:
    """Execute the agentic pipeline with a live progress bar."""
    st.divider()
    progress_ui = PipelineProgress()

    try:
        if st.session_state.orchestrator is None:
            st.session_state.orchestrator = BusinessIdeaOrchestrator()

        orchestrator: BusinessIdeaOrchestrator = st.session_state.orchestrator

        def _cb(step, total, msg):
            progress_ui.update(step, total, msg)

        session = orchestrator.run_full_pipeline(
            profile=profile,
            num_ideas=num_ideas,
            progress_callback=_cb,
        )
        progress_ui.complete()
        st.session_state.session = session
        st.session_state.page = "results"
        st.success("✅ Business ideas generated! Navigate to **Ideas** in the sidebar.")
        st.rerun()

    except RuntimeError as exc:
        progress_ui.error(str(exc))
        st.error(
            "**Connection Error:** Could not reach IBM WatsonX. "
            "Please check your API key and internet connection.\n\n"
            f"Detail: `{exc}`"
        )
    except Exception as exc:
        logger.exception("Unexpected pipeline error")
        progress_ui.error("Unexpected error")
        st.error(f"An unexpected error occurred: `{exc}`")


# ── Ideas Page ───────────────────────────────────────────────────────────────
def render_ideas() -> None:
    session: AgentSession = st.session_state.session
    if not session or not session.ideas:
        st.warning("No ideas generated yet. Go to Home to generate ideas.")
        return

    st.markdown("# 💡 Generated Business Ideas")
    st.caption(
        f"**{len(session.ideas)} ideas** generated for **{session.profile.interest}** "
        f"in **{session.profile.country}**."
    )
    st.warning(DISCLAIMER)
    st.divider()

    # Quick metric row
    m_cols = st.columns(len(session.ideas))
    for i, (col, idea) in enumerate(zip(m_cols, session.ideas)):
        with col:
            delta = "🏆 TOP PICK" if i == session.recommended_index else None
            st.metric(
                label=idea.name[:20],
                value=f"{idea.overall_score:.1f}/10",
                delta=delta,
            )

    st.divider()
    show_detail = st.checkbox("Show full details for all ideas", value=False)

    for i, idea in enumerate(session.ideas):
        market = session.market_analyses[i] if i < len(session.market_analyses) else None
        feasibility = (
            session.feasibility_reports[i]
            if i < len(session.feasibility_reports)
            else None
        )
        render_idea_card(
            idea=idea,
            market=market,
            feasibility=feasibility,
            is_recommended=(i == session.recommended_index),
            show_detail=show_detail,
        )


# ── Compare Page ─────────────────────────────────────────────────────────────
def render_compare() -> None:
    session: AgentSession = st.session_state.session
    if not session or not session.ideas:
        st.warning("No ideas to compare yet.")
        return

    st.markdown("# 📊 Compare Business Ideas")
    st.divider()

    idea_names = [f"{i+1}. {idea.name}" for i, idea in enumerate(session.ideas)]

    st.markdown("### 📈 Score Comparison — All Ideas")
    render_comparison_bar(session.ideas)

    st.divider()
    st.markdown("### 🔍 Side-by-Side Comparison Table")
    render_comparison_table(session.ideas)

    st.divider()
    st.markdown("### ⚖️ Deep Compare: Pick Two Ideas")
    c1, c2 = st.columns(2)
    with c1:
        idx_a = st.selectbox("Idea A", range(len(idea_names)), format_func=lambda x: idea_names[x], key="cmp_a")
    with c2:
        idx_b = st.selectbox("Idea B", range(len(idea_names)), format_func=lambda x: idea_names[x], index=min(1, len(idea_names)-1), key="cmp_b")

    if st.button("⚖️ Compare These Two", type="primary"):
        if idx_a == idx_b:
            st.warning("Please select two different ideas to compare.")
        else:
            with st.spinner("Asking Llama 3.3 to compare your ideas…"):
                orchestrator: BusinessIdeaOrchestrator = st.session_state.orchestrator
                comparison = orchestrator.compare_ideas(
                    session.ideas[idx_a],
                    session.ideas[idx_b],
                    session.profile,
                )
            st.markdown("#### Comparison Result")
            st.write(comparison)
            st.caption("*AI-generated comparison — for reference only.*")


# ── Business Plan Page ────────────────────────────────────────────────────────
def render_plan_page() -> None:
    session: AgentSession = st.session_state.session
    if not session or not session.ideas:
        st.warning("No ideas available. Generate ideas first.")
        return

    st.markdown("# 📋 Business Plan Generator")
    st.divider()

    idea_names = [f"{i+1}. {idea.name}" for i, idea in enumerate(session.ideas)]
    selected_idx = st.selectbox(
        "Select an idea to generate / view its business plan:",
        range(len(idea_names)),
        format_func=lambda x: idea_names[x],
        index=session.recommended_index,
    )

    if st.button("📋 Generate / View Business Plan", type="primary"):
        selected_idea = session.ideas[selected_idx]
        # Check if the plan is already for this idea
        current_plan = session.business_plan
        if current_plan and current_plan.idea and current_plan.idea.name == selected_idea.name:
            render_business_plan(current_plan)
        else:
            with st.spinner(f"Generating business plan for '{selected_idea.name}'…"):
                orchestrator: BusinessIdeaOrchestrator = st.session_state.orchestrator
                market = (
                    session.market_analyses[selected_idx]
                    if selected_idx < len(session.market_analyses)
                    else None
                )
                feasibility = (
                    session.feasibility_reports[selected_idx]
                    if selected_idx < len(session.feasibility_reports)
                    else None
                )
                plan = orchestrator.generate_plan_for_idea(
                    selected_idea, session.profile, market, feasibility
                )
                session.business_plan = plan
                st.session_state.session = session
            render_business_plan(plan)

    elif session.business_plan:
        render_business_plan(session.business_plan)

    st.divider()
    st.caption(DISCLAIMER)


# ── Chat / Follow-up Page ─────────────────────────────────────────────────────
def render_chat() -> None:
    session: AgentSession = st.session_state.session
    if not session:
        st.warning("Please generate ideas first from the Home page.")
        return

    st.markdown("# 💬 Refine & Explore Your Ideas")
    st.markdown(
        "Ask follow-up questions about your business ideas. Examples:\n"
        "- *Suggest ideas under a smaller budget*\n"
        "- *What are AI-based startup ideas for students?*\n"
        "- *Compare Idea 1 and Idea 3*\n"
        "- *How can I market my top idea on social media?*\n"
        "- *Generate a low-investment alternative*"
    )
    st.divider()

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input
    user_query = st.chat_input("Ask anything about your business ideas…")
    if user_query:
        user_query = sanitize_input(user_query)
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Llama 3.3 is thinking…"):
                orchestrator: BusinessIdeaOrchestrator = st.session_state.orchestrator
                if orchestrator is None:
                    orchestrator = BusinessIdeaOrchestrator()
                    st.session_state.orchestrator = orchestrator
                response = orchestrator.answer_followup(user_query, session)
            st.write(response)
            st.caption("*AI-generated response — verify before acting.*")

        st.session_state.chat_history.append({"role": "assistant", "content": response})


# ── Main Router ───────────────────────────────────────────────────────────────
def main() -> None:
    render_sidebar()

    page = st.session_state.page

    if page == "home" or not st.session_state.session:
        render_home()
    elif page == "results":
        render_ideas()
    elif page == "compare":
        render_compare()
    elif page == "plan":
        render_plan_page()
    elif page == "chat":
        render_chat()
    else:
        render_home()

    # Footer
    st.divider()
    st.caption(
        "Made with ❤️ using Llama 3.3 70B · IBM WatsonX AI · Streamlit &nbsp;|&nbsp; "
        "All outputs are AI-generated suggestions. Not financial advice."
    )


if __name__ == "__main__":
    main()
