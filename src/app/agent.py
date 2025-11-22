from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from typing import TypedDict, List
from models import llm_smart
from utils import analyse_competitors

class AgentState(TypedDict):
    messages: List[HumanMessage]
    industry: str
    product_summary: str
    analysis_result: str

def create_competitor_analysis_graph():
    """Create the LangGraph workflow for competitor analysis"""
    
    def analyse_node(state: AgentState):
        # Call the function directly to avoid callback issues
        result = analyse_competitors.func(state["industry"], state["product_summary"])
        return {"analysis_result": result}
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyse", analyse_node)
    
    # Set entry point
    workflow.set_entry_point("analyse")
    
    # Add edges
    workflow.add_edge("analyse", END)
    
    return workflow.compile()

def run_competitor_analysis(industry: str, product_summary: str) -> str:
    """Run the competitor analysis workflow"""
    graph = create_competitor_analysis_graph()
    
    initial_state = {
        "messages": [HumanMessage(content=f"Analyse competitors for {industry}")],
        "industry": industry,
        "product_summary": product_summary,
        "analysis_result": ""
    }
    
    result = graph.invoke(initial_state)
    return result["analysis_result"]