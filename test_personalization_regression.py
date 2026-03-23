from graph import assess_career


def _active_roadmap(result):
    path = result.get("path_taken")
    if path == "HARD_PATH":
        return result.get("roadmap_output", {})
    if path == "MEDIUM_PATH":
        return result.get("roadmap_medium_output", {})
    return result.get("roadmap_light_output", {})


def _active_market(result):
    return result.get("market_context") or result.get("market_context_medium") or result.get("market_context_light") or {}


def _active_reality(result):
    return result.get("reality_check_output") or result.get("reality_check_medium_output") or result.get("reality_check_light_output") or {}


def test_distinct_inputs_produce_distinct_ui_content():
    software_result = assess_career({
        "dream_career": "Software Engineer",
        "current_academics": "Bachelor in Computer Science, GPA 3.8/4, 2 years experience",
        "constraints": "Can invest strongly, focused learning, flexible timeline",
        "interests": "backend systems, cloud, distributed systems",
        "other_concerns": "want strong interview prep and relocation support",
    })

    product_result = assess_career({
        "dream_career": "Product Manager",
        "current_academics": "MBA student with business background",
        "constraints": "Limited budget, must work full-time, need a quick transition in 6 months",
        "interests": "strategy, user research, stakeholder communication",
        "other_concerns": "career switch risk and portfolio gaps",
    })

    software_profile = software_result.get("extracted_profile", {})
    product_profile = product_result.get("extracted_profile", {})

    assert software_profile.get("career_field") != product_profile.get("career_field")
    assert software_profile.get("budget_constraints") != product_profile.get("budget_constraints")
    assert software_profile.get("timeline_urgency") != product_profile.get("timeline_urgency")

    assert _active_roadmap(software_result) != _active_roadmap(product_result)
    assert _active_market(software_result) != _active_market(product_result)
    assert _active_reality(software_result) != _active_reality(product_result)


def test_profile_extractor_uses_constraints_and_academics():
    result = assess_career({
        "dream_career": "Data Analyst",
        "current_academics": "Bachelor in Statistics, GPA 82%, 1 year experience",
        "constraints": "Limited budget and must study on weekends while working full-time",
        "interests": "sql, dashboards, business analysis",
        "other_concerns": "need remote work",
    })

    profile = result.get("extracted_profile", {})

    assert profile.get("current_education_level") == "Bachelor"
    assert profile.get("budget_constraints") == "Limited"
    assert profile.get("years_of_experience") == 1
    assert profile.get("timeline_urgency") in {"Medium", "High"}
    assert "sql" in [item.lower() for item in profile.get("interests_list", [])]
