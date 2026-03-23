"""Shared personalization helpers for deterministic fallback content."""

from __future__ import annotations

import re
from typing import Any, Dict, List


def split_items(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"[,\n;/]+", text)
    return [part.strip() for part in parts if part.strip()]


def infer_budget(constraints: str) -> str:
    text = (constraints or "").lower()
    if any(token in text for token in ["low budget", "limited budget", "tight budget", "financial", "cheap", "afford", "loan"]):
        return "Limited"
    if any(token in text for token in ["comfortable", "strong budget", "can invest", "adequate budget", "high budget"]):
        return "Adequate"
    return "Moderate"


def infer_timeline(constraints: str, concerns: str) -> str:
    text = f"{constraints} {concerns}".lower()
    if any(token in text for token in ["urgent", "asap", "immediately", "quickly", "6 month", "3 month"]):
        return "High"
    if any(token in text for token in ["1 year", "12 month", "steady", "gradual", "long term", "2 year"]):
        return "Low"
    return "Medium"


def infer_education_level(current_academics: str) -> str:
    text = (current_academics or "").lower()
    mapping = [
        ("phd", "PhD"),
        ("doctorate", "PhD"),
        ("master", "Master"),
        ("mba", "Master"),
        ("bachelor", "Bachelor"),
        ("b.tech", "Bachelor"),
        ("btech", "Bachelor"),
        ("undergraduate", "Bachelor"),
        ("diploma", "Diploma"),
        ("12th", "High School"),
        ("high school", "High School"),
    ]
    for token, label in mapping:
        if token in text:
            return label
    return "Unknown"


def infer_degree_field(current_academics: str, dream_career: str) -> str:
    text = (current_academics or "").lower()
    mapping = [
        ("computer science", "Computer Science"),
        ("information technology", "Information Technology"),
        ("electronics", "Electronics"),
        ("mechanical", "Mechanical Engineering"),
        ("civil", "Civil Engineering"),
        ("commerce", "Commerce"),
        ("business", "Business"),
        ("management", "Management"),
        ("economics", "Economics"),
        ("math", "Mathematics"),
        ("statistics", "Statistics"),
    ]
    for token, label in mapping:
        if token in text:
            return label
    return dream_career or "Unknown"


def infer_years_experience(current_academics: str, constraints: str) -> int:
    text = f"{current_academics} {constraints}".lower()
    match = re.search(r"(\d+)\+?\s*(?:years|yrs)", text)
    if match:
        return int(match.group(1))
    if any(token in text for token in ["fresher", "student", "beginner", "no experience"]):
        return 0
    if any(token in text for token in ["working professional", "full-time", "part-time job"]):
        return 2
    return 1


def infer_gpa(current_academics: str) -> float:
    text = current_academics or ""
    pct_match = re.search(r"(\d{2})(?:\.\d+)?\s*%", text)
    if pct_match:
        return max(0.0, min(float(pct_match.group(1)) / 100.0, 1.0))
    gpa_match = re.search(r"(\d(?:\.\d+)?)\s*/\s*4", text)
    if gpa_match:
        return max(0.0, min(float(gpa_match.group(1)) / 4.0, 1.0))
    return 0.7


def infer_research_months(current_academics: str, interests: str) -> int:
    text = f"{current_academics} {interests}".lower()
    if "research" in text or "thesis" in text:
        return 6
    return 0


def infer_projects(current_academics: str, interests: str, concerns: str) -> int:
    text = f"{current_academics} {interests} {concerns}".lower()
    match = re.search(r"(\d+)\s*(?:projects|project)", text)
    if match:
        return max(1, int(match.group(1)))
    if "portfolio" in text or "github" in text:
        return 3
    return 1


def career_track(career_field: str) -> str:
    text = (career_field or "").lower()
    if any(token in text for token in ["data", "ai", "ml", "machine learning", "analytics"]):
        return "data"
    if any(token in text for token in ["product", "manager", "strategy", "business analyst"]):
        return "product"
    if any(token in text for token in ["design", "ux", "ui", "graphic"]):
        return "design"
    if any(token in text for token in ["marketing", "sales", "growth", "seo"]):
        return "marketing"
    return "software"


def learning_mode(constraints: str) -> str:
    text = (constraints or "").lower()
    if any(token in text for token in ["full-time job", "must work", "part-time", "weekend", "busy"]):
        return "part_time"
    return "focused"


def roadmap_theme(track: str) -> Dict[str, List[str]]:
    themes = {
        "data": {
            "foundation": ["statistics basics", "Python and SQL", "data storytelling"],
            "build": ["analysis projects", "dashboard portfolio", "model experiments"],
            "launch": ["case-study resume", "mock interviews", "targeted applications"],
        },
        "product": {
            "foundation": ["product thinking", "market research", "stakeholder communication"],
            "build": ["PRD writing", "user interviews", "roadmap exercises"],
            "launch": ["portfolio case studies", "product interview prep", "network outreach"],
        },
        "design": {
            "foundation": ["design principles", "user research", "visual systems"],
            "build": ["portfolio projects", "wireframes and prototypes", "usability reviews"],
            "launch": ["case-study refinement", "design critique practice", "role applications"],
        },
        "marketing": {
            "foundation": ["channel fundamentals", "customer segmentation", "analytics basics"],
            "build": ["campaign simulations", "portfolio metrics", "content systems"],
            "launch": ["interview stories", "market positioning", "job outreach"],
        },
        "software": {
            "foundation": ["core programming", "system fundamentals", "version control"],
            "build": ["end-to-end projects", "testing and deployment", "problem solving practice"],
            "launch": ["resume and GitHub polish", "interview preparation", "targeted applications"],
        },
    }
    return themes.get(track, themes["software"])


def budget_ranges(budget: str) -> Dict[str, str]:
    ranges = {
        "Limited": {"total": "Rs.25k-75k", "monthly": "Rs.4k-8k"},
        "Moderate": {"total": "Rs.75k-2L", "monthly": "Rs.8k-20k"},
        "Adequate": {"total": "Rs.2L-6L", "monthly": "Rs.20k-50k"},
    }
    return ranges.get(budget, ranges["Moderate"])


def city_hotspots(track: str) -> str:
    mapping = {
        "data": "Bengaluru, Hyderabad, Pune, Remote analytics teams",
        "product": "Bengaluru, Gurgaon, Mumbai, Startup hubs",
        "design": "Bengaluru, Mumbai, Remote product teams",
        "marketing": "Mumbai, Gurgaon, Bengaluru, Remote growth teams",
        "software": "Bengaluru, Hyderabad, Pune, Chennai, Remote engineering teams",
    }
    return mapping.get(track, mapping["software"])


def market_salary(track: str, budget: str) -> str:
    base = {
        "data": "Rs.6L-22L",
        "product": "Rs.8L-28L",
        "design": "Rs.5L-18L",
        "marketing": "Rs.4L-16L",
        "software": "Rs.6L-24L",
    }.get(track, "Rs.6L-20L")
    if budget == "Limited":
        return base
    if budget == "Adequate":
        return f"{base} with faster upside through premium programs and networking"
    return base
