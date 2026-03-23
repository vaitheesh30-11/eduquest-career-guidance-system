"""Streamlit UI for EduQuest career guidance system."""

import streamlit as st
import json
from datetime import datetime, timezone
from typing import Dict, Any
from graph import assess_career
from state import get_initial_state
from ml.evaluation import evaluate_all_models
import os


def initialize_session_state ()->None :
    """Initialize required session state variables."""
    if "assessment_result" not in st.session_state:
        st.session_state.assessment_result = None
    if "eval_results" not in st.session_state :
        st.session_state.eval_results = None
    if "run_evaluation" not in st.session_state :
        st.session_state.run_evaluation = False
    if "assessment_completed" not in st.session_state:
        st.session_state.assessment_completed = False

def export_assessment(assessment: Dict[str,Any])->str:
    export_data = {
        "metadata":{
            "request_id":assessment.get("request_id"),
            "timestamp":datetime.now(timezone.utc).isoformat()
        },
        "assessment": assessment
    }
    return json.dumps(export_data,indent=2)

def display_overview_tab(result: Dict[str,Any])->None:
    st.subheader("Career Assessment Overview")
    
    # Extract actual values from result
    viability_score = result.get("viability_score")
    academic_fit_score = result.get("academic_fit_score")
    path_taken = result.get("path_taken", "N/A")
    
    # Display metrics with actual backend values
    col1,col2,col3 = st.columns(3)
    col1.metric("Viability Score", f"{viability_score:.2f}" if viability_score is not None else "N/A")
    col2.metric("Academic Fit Score", f"{academic_fit_score:.2f}" if academic_fit_score is not None else "N/A")
    col3.metric("Path Taken", path_taken)

    st.markdown("### Summary")
    profile = result.get("extracted_profile",{})
    if profile:
        st.json(profile)
    else:
        st.info("No profile data available")


def display_roadmap_tab(result: Dict[str, Any])->None:
    st.subheader("Career Roadmap")
    path = result.get("path_taken")
    
    if not path:
        st.warning("No path determined. Please run assessment first.")
        return

    # Get roadmap based on path taken
    if path == "HARD_PATH":
        roadmap = result.get("roadmap_output",{})
    elif path == "MEDIUM_PATH":
        roadmap = result.get("roadmap_medium_output", {})
    else:
        roadmap = result.get("roadmap_light_output", {})

    # Display path information
    st.info(f"📍 **Path Taken:** {path}")
    
    if not roadmap:
        st.warning(f"No roadmap data available for {path}")
        return
    
    # Display phases (phase_1_months, phase_2_months, phase_3_months, etc.)
    phase_names = [k for k in roadmap.keys() if k.startswith('phase_')]
    if not phase_names:
        st.info("No phases available in roadmap")
        return
    
    for phase_key in sorted(phase_names):
        phase = roadmap[phase_key]
        with st.expander(f"📚 {phase_key.replace('_', ' ').title()}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Goals**")
                goals = phase.get("goals", [])
                if isinstance(goals, list):
                    for goal in goals:
                        st.write(f"- {goal}")
                else:
                    st.write(goals)
            
            with col2:
                st.write("**Actions**")
                actions = phase.get("actions", [])
                if isinstance(actions, list):
                    for action in actions:
                        st.write(f"- {action}")
                else:
                    st.write(actions)
    
    # Display milestones
    if "key_milestones" in roadmap:
        st.markdown("### 🎯 Key Milestones")
        milestones = roadmap.get("key_milestones", [])
        if isinstance(milestones, list):
            for milestone in milestones:
                st.write(f"✓ {milestone}")
        else:
            st.write(milestones)
    
    # Display resources
    if "success_resources" in roadmap:
        st.markdown("### 📖 Success Resources")
        resources = roadmap.get("success_resources", [])
        if isinstance(resources, list):
            for resource in resources:
                st.write(f"• {resource}")
        else:
            st.write(resources)

def display_roadmap_tab(result: Dict[str, Any])->None:
    st.subheader("Career Roadmap")
    path = result.get("path_taken")

    if not path:
        st.warning("No path determined. Please run assessment first.")
        return

    if path == "HARD_PATH":
        roadmap = result.get("roadmap_output", {})
    elif path == "MEDIUM_PATH":
        roadmap = result.get("roadmap_medium_output", {})
    else:
        roadmap = result.get("roadmap_light_output", {})

    st.info(f"Path Taken: {path}")

    if not roadmap:
        st.warning(f"No roadmap data available for {path}")
        return

    phase_names = [key for key in roadmap.keys() if key.startswith("phase_") or key.startswith("q")]
    if not phase_names:
        st.info("No phases available in roadmap")
        return

    for phase_key in sorted(phase_names):
        phase = roadmap[phase_key]
        with st.expander(phase_key.replace("_", " ").title()):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Goals**")
                goals = phase.get("goals", [])
                if not goals and phase.get("focus"):
                    goals = [phase.get("focus")]
                if isinstance(goals, list):
                    for goal in goals:
                        st.write(f"- {goal}")
                else:
                    st.write(goals)

            with col2:
                st.write("**Actions**")
                actions = phase.get("actions", [])
                if isinstance(actions, list):
                    for action in actions:
                        st.write(f"- {action}")
                else:
                    st.write(actions)

    if "key_milestones" in roadmap:
        st.markdown("### Key Milestones")
        milestones = roadmap.get("key_milestones", [])
        if isinstance(milestones, list):
            for milestone in milestones:
                st.write(f"- {milestone}")
        else:
            st.write(milestones)

    resources_key = "success_resources" if "success_resources" in roadmap else "critical_resources"
    if resources_key in roadmap:
        st.markdown("### Success Resources")
        resources = roadmap.get(resources_key, [])
        if isinstance(resources, list):
            for resource in resources:
                st.write(f"- {resource}")
        else:
            st.write(resources)


def display_planning_tab(result: Dict[str,Any])->None:
    st.subheader("Planning Insights")
    path = result.get("path_taken")

    # Financial Plan (HARD_PATH only)
    if path == "HARD_PATH":
        st.markdown("### 💰 Financial Plan")
        financial = result.get("financial_plan_output", {})
        if financial:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Estimated Total Cost", financial.get("estimated_total_cost", "N/A"))
                st.metric("Monthly Budget", financial.get("monthly_budget", "N/A"))
            with col2:
                st.metric("ROI Analysis", financial.get("roi_analysis", "N/A"))
            
            st.write("**Cost Breakdown**", financial.get("cost_breakdown", "N/A"))
            st.write("**Funding Sources**", financial.get("funding_sources", "N/A"))
            st.write("**Risk Mitigation**", financial.get("risk_mitigation", "N/A"))
        else:
            st.warning("No financial plan available")

    # Market Context
    st.markdown("### 📊 Market Context")
    market = result.get("market_context") or result.get("market_context_medium") or result.get("market_context_light")
    
    if market:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Job Demand Trend**", market.get("job_demand_trend", "N/A"))
            st.write("**Salary Range (INR)**", market.get("salary_rang_inr", "N/A"))
            st.write("**Competitive Landscape**", market.get("competitive_landscape", "N/A"))
        with col2:
            st.write("**Growth Forecast**", market.get("growth_forecast", "N/A"))
            st.write("**Geographic Hotspots**", market.get("geographic_hotspots", "N/A"))
            st.write("**Emerging Opportunities**", market.get("emerging_opportunities", "N/A"))
        
        st.write("**Industry Insights**", market.get("industry_insights", "N/A"))
        st.write("**Required Certifications**", market.get("required_certifications", "N/A"))
        st.write("**Market Risks**", market.get("market_risks", "N/A"))
    else:
        st.warning("No market context available")
    
    # Reality Check
    st.markdown("### ⚡ Reality Check")
    reality = result.get("reality_check_output") or result.get("reality_check_medium_output") or result.get("reality_check_light_output")
    
    if reality:
        st.write("**Honest Assessment**", reality.get("honest_assessment", "N/A"))
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Major Challenges**")
            challenges = reality.get("major_challenges", [])
            if isinstance(challenges, list):
                for challenge in challenges:
                    st.write(f"- {challenge}")
            else:
                st.write(challenges)
        
        with col2:
            st.write("**Mindset Requirements**")
            mindset = reality.get("mindset_requirements", [])
            if isinstance(mindset, list):
                for req in mindset:
                    st.write(f"- {req}")
            else:
                st.write(mindset)
        
        st.metric("Success Probability", f"{reality.get('success_probability', 'N/A')}%")
    else:
        st.warning("No reality check available")


def display_alternatives_tab(result: Dict[str,Any])->None:
    st.subheader("Alternative Career Options")
    alternatives_data = result.get("alternatives_output", {})
    alternatives = alternatives_data.get("alternatives", [])

    if not alternatives:
        st.info("No alternatives available")
        return
    
    # Show summary if available
    summary = alternatives_data.get("summary", "")
    if summary:
        st.info(summary)
    
    for idx, alt in enumerate(alternatives, 1):
        career_name = alt.get("career", f"Alternative {idx}")
        similarity = alt.get("similarity_to_dream", "N/A")
        
        with st.expander(f"🔄 {career_name} (Similarity: {similarity})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Similarity to Dream", f"{similarity}" if isinstance(similarity, (int, float)) else similarity)
                st.metric("Viability Estimate", f"{alt.get('viability_estimate', 'N/A')}")
            
            with col2:
                st.metric("Transition Effort", alt.get("transition_effort", "N/A"))
            
            st.write("**Reasoning**")
            st.write(alt.get("reasoning", "No reasoning provided"))


def display_model_evaluation_section(eval_results: Dict[str,Any])->None:
    st.subheader("ML Model Evaluation")

    col1,col2 = st.columns(2)

    viability = eval_results.get("viability_model", {})
    academic = eval_results.get("academic_matcher_model", {})

    with col1 :
        st.markdown("### Viability Model")
        st.write(viability)

    with col2 :
        st.markdown("### Academic Matcher Model")
        st.write(academic)

def main()->None:
    st.set_page_config(page_title = "EduQuest Career Guidance", layout = "wide")
    st.title("EduQuest Career Guidance System")
    initialize_session_state()
    st.sidebar.header("Career Input")

    dream_career = st.sidebar.text_input("Dream Career")
    current_academics = st.sidebar.text_input("Current Academics")
    constraints = st.sidebar.text_area("Constraints")
    interests = st.sidebar.text_area("Interests")
    other_concerns = st.sidebar.text_area("Other Concerns")

    if st.sidebar.button("Assess Career"):
        form_data = {
            "dream_career":dream_career,
            "current_academics":current_academics,
            "constraints":constraints,
            "interests":interests,
            "other_concerns":other_concerns
        }
        with st.spinner("Analyzing career path..."):
            result = assess_career(form_data)
            st.session_state.assessment_result = result
            st.session_state.assessment_completed = True
            
            # Debug: Show any errors
            if result.get("error_occurred"):
                st.error(f"Error during assessment: {result.get('error_message', 'Unknown error')}")
            
            # Debug: Show what was returned
            with st.expander("Debug: Assessment Result"):
                st.json({
                    "viability_score": result.get("viability_score"),
                    "academic_fit_score": result.get("academic_fit_score"),
                    "path_taken": result.get("path_taken"),
                    "extracted_profile": result.get("extracted_profile"),
                    "overall_feasibility": result.get("overall_feasibility"),
                    "error_occurred": result.get("error_occurred"),
                    "error_message": result.get("error_message"),
                })
        st.rerun()
    
    # Display results if assessment was completed and result exists in session state
    result = st.session_state.assessment_result
    if result and st.session_state.assessment_completed:
        tab1,tab2,tab3,tab4 = st.tabs(
            ["Overview","Roadmap","Planning","Alternatives"]
        )
        with tab1:
            display_overview_tab(result)
        with tab2:
            display_roadmap_tab(result)
        with tab3 :
            display_planning_tab(result)
        with tab4 :
            display_alternatives_tab(result)
        export_data = export_assessment(result)
        st.download_button(
            "Export Assessment",
            export_data,
            file_name = "career_assessment.json"
        )
    st.sidebar.markdown("---")
    if st.sidebar.button("Run Model Evaluation"):
        with st.spinner("Running ML Evaluation..."):
            st.session_state.eval_results = evaluate_all_models()
            st.session_state.run_evaluation = True
        st.rerun()
    
    if st.session_state.eval_results and st.session_state.run_evaluation:
        display_model_evaluation_section(st.session_state.eval_results)




if __name__ == "__main__":
    main()
