"""Pydantic output contracts for agent responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RoadmapPhaseLight(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    duration: str = ""
    focus: str = ""
    goals: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)


class RoadmapPhaseQuarter(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    goals: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)


class RoadmapPhaseMonthly(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    months: str = ""
    goals: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)


class LightRoadmapOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    phase_1_foundation: RoadmapPhaseLight
    phase_2_foundation: RoadmapPhaseLight
    phase_3_foundation: RoadmapPhaseLight
    key_milestones: list[str] = Field(default_factory=list)
    critical_resources: list[str] = Field(default_factory=list)
    strategy_summary: str = ""
    phase_success_signals: list[str] = Field(default_factory=list)
    weekly_routine: list[str] = Field(default_factory=list)
    status: str
    response_source: Literal["llm_structured", "llm_direct", "fallback"]


class MediumRoadmapOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    q1: RoadmapPhaseQuarter
    q2: RoadmapPhaseQuarter
    q3: RoadmapPhaseQuarter
    q4: RoadmapPhaseQuarter
    key_milestones: list[str] = Field(default_factory=list)
    critical_resources: list[str] = Field(default_factory=list)
    strategy_summary: str = ""
    phase_success_signals: list[str] = Field(default_factory=list)
    weekly_routine: list[str] = Field(default_factory=list)
    status: str
    response_source: Literal["llm_structured", "llm_direct", "fallback"]


class FullRoadmapOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    phase_1_months: RoadmapPhaseMonthly
    phase_2_months: RoadmapPhaseMonthly
    phase_3_months: RoadmapPhaseMonthly
    key_milestones: list[str] = Field(default_factory=list)
    success_resources: list[str] = Field(default_factory=list)
    strategy_summary: str = ""
    phase_success_signals: list[str] = Field(default_factory=list)
    weekly_routine: list[str] = Field(default_factory=list)
    status: str
    response_source: Literal["llm_structured", "llm_direct", "fallback"]


class RealityCheckOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    honest_assessment: str = ""
    major_challenges: list[str] = Field(default_factory=list)
    success_probability: float = 0.0
    mindset_requirements: list[str] = Field(default_factory=list)
    status: str
    response_source: Literal["llm_structured", "llm_direct", "fallback"]


class MarketContextOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    job_demand_trend: str = ""
    salary_rang_inr: str = ""
    growth_forecast: str = ""
    industry_insights: str = ""
    competitive_landscape: str = ""
    geographic_hotspots: str = ""
    required_certifications: str = ""
    emerging_opportunities: str = ""
    market_risks: str = ""
    status: str
    response_source: Literal["llm_structured", "llm_direct", "fallback"]


class AlternativeItem(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    career: str = ""
    similarity_to_dream: float = 0.0
    viability_estimate: float = 0.0
    reasoning: str = ""
    transition_effort: Literal["Low", "Medium", "High"] = "Medium"


class AlternativesOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    alternatives: list[AlternativeItem] = Field(default_factory=list)
    summary: str = ""
    status: str
    response_source: Literal["llm_structured", "llm_direct", "fallback"]


class FinancialPlanOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    estimated_total_cost: str = ""
    monthly_budget: str = ""
    cost_breakdown: str = ""
    funding_sources: str = ""
    roi_analysis: str = ""
    risk_mitigation: str = ""
    status: str
    response_source: Literal["llm_structured", "llm_direct", "fallback"]
