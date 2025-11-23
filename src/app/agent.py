from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from typing import TypedDict, List, Dict
from constants import llm_smart
from utils import search_competitors, scrape_competitor_sites, analyse_competitors

class AgentState(TypedDict):
    messages: List[HumanMessage]
    industry: str
    product_summary: str
    competitor_urls: List[str]
    competitor_data: List[Dict]
    analysis_result: str

def create_competitor_analysis_graph():
    """Create the LangGraph workflow for competitor analysis"""

    def search_node(state: AgentState):
        result = search_competitors.func(state["industry"], state["product_summary"])
        return {"competitor_urls": result}

    def scrape_node(state: AgentState):
        result = scrape_competitor_sites.func(state["competitor_urls"])
        return {"competitor_data": result}
    
    def analyse_node(state: AgentState):
        result = analyse_competitors.func(state["industry"], state["product_summary"], state["competitor_data"])
        return {"analysis_result": result}

    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("search", search_node)
    workflow.add_node("scrape", scrape_node)
    workflow.add_node("analyse", analyse_node)
    
    # Set entry point
    workflow.set_entry_point("search")
    
    # Add edges
    workflow.add_edge("search", "scrape")
    workflow.add_edge("scrape", "analyse")
    workflow.add_edge("analyse", END)
    
    return workflow.compile()

def run_competitor_analysis(industry: str, product_summary: str) -> str:
    """Run the competitor analysis workflow"""
    graph = create_competitor_analysis_graph()
    
    initial_state = {
        "messages": [HumanMessage(content=f"Analyse competitors for {industry}")],
        "industry": industry,
        "product_summary": product_summary,
        "competitor_urls": [],
        "competitor_data": [],
        "analysis_result": ""
    }
    
    result = graph.invoke(initial_state)
    return result["analysis_result"]