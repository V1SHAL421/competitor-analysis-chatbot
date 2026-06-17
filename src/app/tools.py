import logging
import os
from langchain_core.tools import tool
from models import AgentResponse
from tavily import TavilyClient
from firecrawl import Firecrawl
from typing import List, Dict

logger = logging.getLogger(__name__)

MAX_SCRAPED_CHARS = 1000

_ANALYSIS_PROMPT_TEMPLATE = """
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


def _build_analysis_prompt(industry: str, product_summary: str, competitor_data: List[Dict]) -> str:
    return _ANALYSIS_PROMPT_TEMPLATE.format(
        industry=industry,
        product_summary=product_summary,
        competitor_data=competitor_data,
    )


def _search(industry: str, product_summary: str, client: TavilyClient) -> List[str]:
    search_query = f"top competitors in {industry} similar to {product_summary}"
    search_results = client.search(search_query, max_results=3)
    if not search_results.get("results"):
        logger.warning(f"No competitors found for {industry}")
        return []
    competitor_urls = [hit["url"] for hit in search_results["results"][:3]]
    logger.info(f"Found competitor URLs: {competitor_urls}")
    return competitor_urls


@tool
def search_competitors(industry: str, product_summary: str) -> List[str]:
    """Search for competitor URLs for a given industry and product summary.

    Args:
        industry: The industry or category (e.g., 'AI coding assistants')
        product_summary: Brief description of the product (max 300 chars)

    Returns:
        List of competitor URLs found via web search
    """
    logger.info(f"Searching competitors for industry: {industry}")
    try:
        return _search(industry, product_summary, TavilyClient(api_key=os.getenv("TAVILY_API_KEY")))
    except Exception as e:
        logger.error(f"Failed to search competitors: {e}")
        return []


def _scrape(url: str, client: Firecrawl) -> Dict:
    doc = client.scrape(url, formats=["markdown"])
    content = doc.markdown[:MAX_SCRAPED_CHARS] if hasattr(doc, "markdown") else ""
    return {"url": url, "content": content}


@tool
def scrape_competitor_page(url: str) -> Dict:
    """Scrape a single competitor website and return its content.

    Use this to selectively scrape URLs you judge worth investigating based on
    search result context. Prefer company homepages and pricing pages over
    aggregator or Wikipedia links.

    Args:
        url: The URL to scrape

    Returns:
        Dict with 'url' and 'content' keys, or 'error' key on failure
    """
    logger.info(f"Scraping {url}")
    try:
        return _scrape(url, Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY")))
    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {type(e).__name__}: {e}")
        return {"url": url, "error": str(e)}


@tool
def analyse_competitors(industry: str, product_summary: str, competitor_data: List[Dict]) -> str:
    """Analyse competitors based on scraped content.

    Args:
        industry: The industry or category (e.g., 'AI coding assistants')
        product_summary: Brief description of the product (max 300 chars)
        competitor_data: List of dicts with 'url' and 'content' keys from scrape_competitor_page

    Returns:
        JSON string containing structured competitor analysis
    """
    from constants import get_llm

    logger.info(f"Analysing {len(competitor_data)} competitors for industry: {industry}")
    prompt = _build_analysis_prompt(industry, product_summary, competitor_data)
    structured_llm = get_llm().with_structured_output(AgentResponse)
    try:
        analysis = structured_llm.invoke(prompt)
        return analysis.model_dump_json()
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise RuntimeError(f"Failed to analyse competitors: {e}") from e
