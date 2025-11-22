import logging
import os
from langchain_core.tools import tool
from models import CompetitorSummary, StrategicAnalysis, AgentResponse
from constants import llm_fast, llm_smart
from tavily import TavilyClient
from firecrawl import Firecrawl
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def analyse_competitors(industry: str, product_summary: str) -> str:
    """Analyse competitors for a given industry and product summary.
    
    Args:
        industry: The industry or category (e.g., 'AI coding assistants')
        product_summary: Brief description of the product (max 300 chars)
    
    Returns:
        Analysis results of competitors in the specified industry
    """
    logger.info(f"Analysing competitors for industry: {industry}")
    logger.info(f"Product summary: {product_summary}")

    try:
        # Search for competitors using Tavily
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        search_query = f"top competitors in {industry} similar to {product_summary}"
        response = tavily_client.search(search_query, max_results=3)
        
        if not response.get('results'):
            return f"No competitors found for {industry}"
        
        # Extract URLs from search results
        competitor_urls = [result['url'] for result in response['results'][:3]]
        logger.info(f"Found competitor URLs: {competitor_urls}")
        
        # Scrape competitor websites
        firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
        competitor_data = []
        
        for url in competitor_urls:
            try:
                doc = firecrawl.scrape(url, formats=["markdown"])
                content = doc.markdown[:1000] if hasattr(doc, 'markdown') else ''
                competitor_data.append({
                    'url': url,
                    'content': content
                })
            except Exception as e:
                logger.warning(f"Failed to scrape {url}: {e}")
        
        analysis_prompt = create_prompt(industry, product_summary, competitor_data)
        
        structured_llm = llm_smart.with_structured_output(AgentResponse)
        analysis = structured_llm.invoke(analysis_prompt)
        return analysis.model_dump_json()
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return f"Failed to analyse competitors: {str(e)}"
    
def create_prompt(industry: str, product_summary: str, competitor_data: List[Dict]):
    """Create the prompt for competitor analysis.
    
    Args:
        industry (str): The industry or category (e.g., 'AI coding assistants')
        product_summary (str): Brief description of the product (max 300 chars)
        competitor_data (list): List of competitor URLs and its respective content
    
    Returns:
        Prompt to send to the LLM
    """

    analysis_prompt = f"""
        You are an expert in competitive intelligence, product analysis, and strategic positioning.

        Your task is to analyse competitors based strictly on the information provided.  
        Do NOT hallucinate features or assumptions that are not directly supported by the data.

        --------------------
        CONTEXT ON USER'S STARTUP
        --------------------
        Industry: {industry}
        Product Summary: {product_summary}

        --------------------
        COMPETITOR DATA (CLEANED + EXTRACTED FROM SCRAPED PAGES)
        --------------------
        {competitor_data}

        --------------------
        DETAILED ANALYSIS REQUIREMENTS
        --------------------
        1. COMPREHENSIVE COMPETITOR PROFILES:
        For each competitor, provide detailed analysis of:
        - Company name and website URL
        - Detailed company description and business model
        - Complete feature breakdown with technical details
        - Pricing model and cost structure (if available)
        - Target market segments and customer personas
        - Detailed strengths analysis (what they do exceptionally well)
        - Comprehensive weaknesses assessment (gaps, limitations, complaints)
        - Unique value proposition and market positioning
        - Technology stack and technical approach (if mentioned)
        - Market position (leader, challenger, niche player)

        2. DEEP COMPETITIVE COMPARISON:
        - Feature-by-feature comparison across all competitors
        - Technology approach differences
        - User experience and interface comparisons
        - Integration capabilities and ecosystem partnerships
        - Scalability and performance characteristics
        - Security and compliance features
        - Customer support and service models
        - Pricing and business model variations

        3. STRATEGIC MARKET ANALYSIS:
        - Market positioning analysis for your startup
        - Competitive advantages you can leverage
        - Detailed gap analysis and white space opportunities
        - Go-to-market strategy recommendations
        - Threat assessment with risk levels and mitigation strategies
        - Market size and growth insights
        - Customer acquisition and retention strategies
        - Partnership and integration opportunities
        - Strategic Next Steps

        --------------------
        OUTPUT REQUIREMENTS
        --------------------
        Provide structured analysis with:
        1. Competitor summaries (name, features, strengths, weaknesses, target user)
        2. Feature comparison matrix as list of objects like:
           [{{"Feature": "Computer Vision", "Your Product": "✓", "Competitor 1": "✗"}}]
           Use ✓ for present, ✗ for absent, ? for unclear
        3. Strategic analysis (overlaps, gaps, differentiators, threats)
        
        Only use information explicitly found in the competitor data.
        """
    return analysis_prompt