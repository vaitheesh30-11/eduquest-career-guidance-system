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
    if "evaluated_request_id" not in st.session_state:
        st.session_state.evaluated_request_id = None
    # Initialize input field widgets in session state
    if "input_dream_career" not in st.session_state:
        st.session_state.input_dream_career = ""
    if "input_current_academics" not in st.session_state:
        st.session_state.input_current_academics = ""
    if "input_constraints" not in st.session_state:
        st.session_state.input_constraints = ""
    if "input_interests" not in st.session_state:
        st.session_state.input_interests = ""
    if "input_other_concerns" not in st.session_state:
        st.session_state.input_other_concerns = ""

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

    st.markdown("### Assessment Insights")
    if viability_score is not None and academic_fit_score is not None:
        blended = (0.6 * float(viability_score)) + (0.4 * (float(academic_fit_score) / 100.0))
        if blended >= 0.7:
            level = "Strong readiness"
        elif blended >= 0.5:
            level = "Moderate readiness"
        else:
            level = "Early-stage readiness"
        st.write(f"**Readiness Level:** {level}")
        st.write(f"**Blended Feasibility Score:** {blended:.2f}")
        if path_taken == "HARD_PATH":
            st.write("**Path Meaning:** Full-depth support path selected with reality check, planning, roadmap, alternatives, and market analysis.")
        elif path_taken == "MEDIUM_PATH":
            st.write("**Path Meaning:** Balanced path selected with focused reality check, roadmap, and market context.")
        else:
            st.write("**Path Meaning:** Lightweight path selected with concise guidance and starter roadmap.")

    roadmap = result.get("roadmap_output") or result.get("roadmap_medium_output") or result.get("roadmap_light_output") or {}
    if roadmap:
        key_milestones = roadmap.get("key_milestones", [])
        weekly_routine = roadmap.get("weekly_routine", [])
        strategy_summary = roadmap.get("strategy_summary", "")
        if strategy_summary:
            st.write(f"**Roadmap Strategy:** {strategy_summary}")
        if key_milestones:
            st.write("**Top Milestones:**")
            for milestone in key_milestones[:3]:
                st.write(f"- {milestone}")
        if weekly_routine:
            st.write("**Suggested Weekly Rhythm:**")
            for step in weekly_routine[:3]:
                st.write(f"- {step}")

    st.markdown("### Your Profile Summary")
    profile = result.get("extracted_profile",{})
    if profile:
        years_exp = profile.get("years_of_experience")
        gpa_pct = profile.get("gpa_percentile")
        research_months = profile.get("research_experience_months")
        project_count = profile.get("project_portfolio_count")

        # Display profile as human-friendly text instead of JSON
        st.write(f"**Career Field:** {profile.get('career_field', 'Not specified')}")
        st.write(f"**Education Level:** {profile.get('current_education_level', 'Not specified')}")
        st.write(f"**Years of Experience:** {f'{years_exp} years' if years_exp is not None else 'Not specified'}")
        st.write(f"**Budget Constraints:** {profile.get('budget_constraints', 'Not specified')}")
        st.write(f"**Timeline Urgency:** {profile.get('timeline_urgency', 'Not specified')}")
        
        interests = profile.get('interests_list', [])
        if interests:
            st.write(f"**Interests:** {', '.join(interests)}")
        
        concerns = profile.get('concerns_list', [])
        if concerns:
            st.write(f"**Concerns:** {', '.join(concerns)}")
        
        st.write(f"**GPA/Percentile:** {gpa_pct if gpa_pct is not None else 'Not specified'}")
        st.write(f"**Research Experience:** {f'{research_months} months' if research_months is not None else 'Not specified'}")
        st.write(f"**Project Portfolio:** {f'{project_count} projects' if project_count is not None else 'Not specified'}")
    else:
        st.info("No profile data available")


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

    strategy_summary = roadmap.get("strategy_summary")
    if strategy_summary:
        st.success(f"Strategy: {strategy_summary}")

    if not roadmap:
        st.warning(f"No roadmap data available for {path}")
        return

    phase_names = [
        key
        for key, value in roadmap.items()
        if (key.startswith("phase_") or key.startswith("q")) and isinstance(value, dict)
    ]
    if not phase_names:
        st.info("No phases available in roadmap")
        return

    for phase_key in sorted(phase_names):
        phase = roadmap[phase_key]
        with st.expander(phase_key.replace("_", " ").title()):
            if isinstance(phase, list):
                st.write("**Phase Items**")
                for item in phase:
                    st.write(f"- {item}")
                continue
            if not isinstance(phase, dict):
                st.write(phase)
                continue

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

            success_signals = phase.get("success_signals", [])
            if success_signals:
                st.write("**Success Signals**")
                if isinstance(success_signals, list):
                    for signal in success_signals:
                        st.write(f"- {signal}")
                else:
                    st.write(success_signals)

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

    phase_success_signals = roadmap.get("phase_success_signals", [])
    if phase_success_signals:
        st.markdown("### Phase Guidance")
        for signal in phase_success_signals:
            st.write(f"- {signal}")

    weekly_routine = roadmap.get("weekly_routine", [])
    if weekly_routine:
        st.markdown("### Weekly Execution Guide")
        for routine_item in weekly_routine:
            st.write(f"- {routine_item}")


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

    roadmap = result.get("roadmap_output") or result.get("roadmap_medium_output") or result.get("roadmap_light_output")
    if roadmap:
        st.markdown("### Execution Planning Guide")
        strategy_summary = roadmap.get("strategy_summary")
        if strategy_summary:
            st.write("**Strategy Summary**", strategy_summary)
        weekly_routine = roadmap.get("weekly_routine", [])
        if weekly_routine:
            st.write("**Weekly Routine**")
            for item in weekly_routine:
                st.write(f"- {item}")
        phase_signals = roadmap.get("phase_success_signals", [])
        if phase_signals:
            st.write("**Progress Signals**")
            for item in phase_signals:
                st.write(f"- {item}")


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

    status = eval_results.get("status", "unknown")
    if status == "error":
        st.error(f"Model evaluation failed: {eval_results.get('message', 'Unknown error')}")
        return
    if status == "partial_success":
        st.warning("Model evaluation completed with partial success. One model could not be evaluated.")
    else:
        st.success("Model evaluation completed successfully.")

    models = eval_results.get("models", {})
    viability = models.get("viability", {})
    academic = models.get("academic", {})

    col1,col2 = st.columns(2)

    def render_model_metrics(title: str, data: Dict[str, Any]) -> None:
        st.markdown(f"### {title}")
        if data.get("status") == "error":
            st.error(data.get("message", "Evaluation failed"))
            return

        c1, c2, c3 = st.columns(3)
        c1.metric("R2", f"{data.get('r2', 0):.3f}")
        c2.metric("MAE", f"{data.get('mae', 0):.3f}")
        c3.metric("RMSE", f"{data.get('rmse', 0):.3f}")

        c4, c5, c6 = st.columns(3)
        c4.metric("NMAE", f"{100 * data.get('nmae', 0):.2f}%")
        c5.metric("NRMSE", f"{100 * data.get('nrmse', 0):.2f}%")
        c6.metric("Skill vs Baseline", f"{100 * data.get('skill_over_baseline', 0):.1f}%")

        c7, c8 = st.columns(2)
        c7.metric("P90 Abs Error", f"{data.get('p90_abs_error', 0):.3f}")
        c8.metric("Samples", f"{data.get('samples', 0)}")

        if data.get("consistency_warning"):
            st.warning("Metric consistency warning: R2 and baseline skill are misaligned. Recheck evaluation pipeline.")

        r2 = data.get("r2", 0)
        if r2 >= 0.75 and data.get("skill_over_baseline", 0) >= 0.25:
            impact = "Strong predictive performance"
        elif r2 >= 0.5 and data.get("skill_over_baseline", 0) >= 0.15:
            impact = "Moderate predictive performance"
        else:
            impact = "Weak predictive performance - consider retraining or better features"
        st.write(f"**Performance Summary:** {impact}")
        st.caption(f"Model file: {data.get('model_path', 'N/A')}")

        cv = data.get("cv", {})
        if cv:
            st.markdown("**CV Stability (5-Fold)**")
            cv1, cv2, cv3 = st.columns(3)
            cv1.metric("CV R2 (mean+-std)", f"{cv.get('r2_mean', 0):.3f} +- {cv.get('r2_std', 0):.3f}")
            cv2.metric("CV MAE (mean)", f"{cv.get('mae_mean', 0):.3f}")
            cv3.metric("CV RMSE (mean)", f"{cv.get('rmse_mean', 0):.3f}")
            st.caption(
                f"Normalized CV errors: NMAE {100*cv.get('nmae_mean', 0):.2f}% | "
                f"NRMSE {100*cv.get('nrmse_mean', 0):.2f}%"
            )

    with col1 :
        render_model_metrics("Viability Model", viability)

    with col2 :
        render_model_metrics("Academic Matcher Model", academic)

def main()->None:
    st.set_page_config(page_title = "EduQuest Career Guidance", layout = "wide")
    st.title("EduQuest Career Guidance System")
    initialize_session_state()
    
    st.sidebar.header("Career Input")
    
    # Get current input values (fresh from user input)
    dream_career = st.sidebar.text_input("Dream Career", key="input_dream_career")
    current_academics = st.sidebar.text_input("Current Academics", key="input_current_academics")
    constraints = st.sidebar.text_area("Constraints", key="input_constraints")
    interests = st.sidebar.text_area("Interests", key="input_interests")
    other_concerns = st.sidebar.text_area("Other Concerns", key="input_other_concerns")

    col1, col2 = st.sidebar.columns(2)
    
    assess_button = col1.button("Assess Career", key="assess_button")
    clear_button = col2.button("Clear Results", key="clear_button")

    # Handle clear button
    if clear_button:
        st.session_state.assessment_result = None
        st.session_state.assessment_completed = False
        # Clear all input fields by resetting them
        st.session_state.input_dream_career = ""
        st.session_state.input_current_academics = ""
        st.session_state.input_constraints = ""
        st.session_state.input_interests = ""
        st.session_state.input_other_concerns = ""
        st.rerun()

    if assess_button:
        # Validate inputs
        if not dream_career.strip():
            st.sidebar.error("Please enter your dream career")
            st.stop()
        
        # DEBUG: Print inputs to terminal
        import sys
        print(f"\n{'='*70}", file=sys.stderr)
        print(f"USER INPUT DEBUG:", file=sys.stderr)
        print(f"  dream_career: '{dream_career}'", file=sys.stderr)
        print(f"  current_academics: '{current_academics}'", file=sys.stderr)
        print(f"  constraints: '{constraints}'", file=sys.stderr)
        print(f"  interests: '{interests}'", file=sys.stderr)
        print(f"  other_concerns: '{other_concerns}'", file=sys.stderr)
        print(f"{'='*70}\n", file=sys.stderr)
        
        form_data = {
            "dream_career": dream_career,
            "current_academics": current_academics,
            "constraints": constraints,
            "interests": interests,
            "other_concerns": other_concerns
        }
        
        with st.spinner("Analyzing career path..."):
            result = assess_career(form_data)
            st.session_state.assessment_result = result
            st.session_state.assessment_completed = True
            # New assessment means evaluation cache should refresh on next request.
            st.session_state.evaluated_request_id = None
            
            # DEBUG: Show extracted profile
            extracted_profile = result.get("extracted_profile", {})
            print(f"\nEXTRACTED PROFILE DEBUG:", file=sys.stderr)
            print(f"  career_field: '{extracted_profile.get('career_field')}'", file=sys.stderr)
            print(f"{'='*70}\n", file=sys.stderr)
            
            # Debug: Show any errors
            if result.get("error_occurred"):
                st.error(f"Error during assessment: {result.get('error_message', 'Unknown error')}")
            
            # Debug: Show what was returned
            with st.expander("Debug: Assessment Result"):
                st.json({
                    "viability_score": result.get("viability_score"),
                    "academic_fit_score": result.get("academic_fit_score"),
                    "path_taken": result.get("path_taken"),
                    "dream_career_input": dream_career,
                    "extracted_career_field": extracted_profile.get("career_field"),
                    "error_occurred": result.get("error_occurred"),
                    "error_message": result.get("error_message"),
                })
        st.rerun()
    
    # Display results if assessment was completed and result exists in session state
    result = st.session_state.assessment_result
    if result and st.session_state.assessment_completed:
        st.markdown("---")
        st.success("Career Assessment Complete!")
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
        current_request_id = None
        if st.session_state.assessment_result:
            current_request_id = st.session_state.assessment_result.get("request_id")

        if (
            st.session_state.eval_results is not None
            and st.session_state.evaluated_request_id == current_request_id
        ):
            st.sidebar.info("Using cached evaluation for current assessment.")
            st.session_state.run_evaluation = True
        else:
            with st.spinner("Running ML Evaluation..."):
                st.session_state.eval_results = evaluate_all_models()
                st.session_state.run_evaluation = True
                st.session_state.evaluated_request_id = current_request_id
        st.rerun()
    
    if st.session_state.eval_results and st.session_state.run_evaluation:
        display_model_evaluation_section(st.session_state.eval_results)




if __name__ == "__main__":
    main()

