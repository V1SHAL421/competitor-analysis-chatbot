from pydantic import BaseModel
from typing import List, Dict

class CompetitorSummary(BaseModel):
    """Summary of the competitors retrieved"""
    name: str
    website_url: str
    company_description: str
    key_features: List[str]
    pricing_model: str
    target_market: str
    strengths: List[str]
    weaknesses: List[str]
    unique_value_proposition: str
    technology_stack: List[str]
    market_position: str

class StrategicAnalysis(BaseModel):
    """Strategic analysis of startup vs competing startups"""
    market_positioning: str
    competitive_advantages: List[str]
    areas_of_overlap: List[str]
    gaps_and_opportunities: List[str]
    recommended_differentiators: List[str]
    go_to_market_strategy: str
    threat_assessment: str
    market_size_insights: str
    next_steps: List[str]

class AgentResponse(BaseModel):
    """Response model for the agent"""
    competitor_summaries: List[CompetitorSummary]
    comparison_matrix: List[Dict[str, str]]
    strategic_analysis: StrategicAnalysis