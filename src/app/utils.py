import logging
import os
from langchain_core.tools import tool
from models import CompetitorSummary, StrategicAnalysis, AgentResponse
from constants import llm_fast, llm_smart
from tavily import TavilyClient
from firecrawl import Firecrawl
from typing import List, Dict
from reportlab.platypus import Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from io import BytesIO
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib

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

def create_pdf_report(analysis_json: str, industry: str, product_summary: str) -> BytesIO:
    """Create a PDF report from the analysis JSON.

    Args:
        analysis_json (str): The analysis JSON string
        industry (str): The industry or category (e.g., 'AI coding assistants')
        product_summary (str): Brief description of the product (max 300 chars)

    Returns:
        BytesIO object containing the PDF report
    """
    try:
        # Parse the analysis JSON
        analysis_data = json.loads(analysis_json)

        # Create a PDF report using the parsed data
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Add title
        elements.append(Paragraph("Competitor Analysis Report", styles['Title']))
        elements.append(Spacer(1, 12))

        # Product Summary
        elements.append(Paragraph("Product Summary", styles["Heading2"]))
        elements.append(Paragraph(product_summary, styles["BodyText"]))
        elements.append(Spacer(1, 12))

        # Competitor Summaries
        elements.append(Paragraph("Competitor Summaries", styles["Heading2"]))
        for comp in analysis_data.get("competitor_summaries", []):
            elements.append(Paragraph(comp['name'], styles['Heading3']))
            elements.append(Paragraph(f"Company Description: {comp['company_description']}", styles['Normal']))
            elements.append(Paragraph(f"Key Features: {', '.join(comp['key_features'])}", styles['Normal']))
            elements.append(Paragraph(f"Pricing Model: {comp['pricing_model']}", styles['Normal']))
            elements.append(Paragraph(f"Target Market: {comp['target_market']}", styles['Normal']))
            elements.append(Paragraph(f"Strengths: {', '.join(comp['strengths'])}", styles['Normal']))
            elements.append(Paragraph(f"Weaknesses: {', '.join(comp['weaknesses'])}", styles['Normal']))
            elements.append(Paragraph(f"Unique Value Proposition: {comp['unique_value_proposition']}", styles['Normal']))
            elements.append(Paragraph(f"Market Position: {comp['market_position']}", styles['Normal']))
            elements.append(Spacer(1, 6))

        # Comparison Matrix
        elements.append(Paragraph("Comparison Matrix", styles["Heading2"]))
        comparison_matrix = analysis_data.get("comparison_matrix", [])
        if comparison_matrix:
            table_data = [[key] + [comp[key] for comp in comparison_matrix] for key in comparison_matrix[0].keys()]
            table = Table(table_data)
            elements.append(table)

        # Strategic Analysis
        elements.append(Paragraph("Strategic Analysis", styles["Heading2"]))
        strategic = analysis_data.get("strategic_analysis", {})
        elements.append(Paragraph(f"Market Positioning: {strategic.get('market_positioning', 'Not provided')}", styles['Normal']))
        elements.append(Paragraph(f"Competitive Advantages: {', '.join(strategic.get('competitive_advantages', []))}", styles['Normal']))
        elements.append(Paragraph(f"Areas of Overlap: {', '.join(strategic.get('areas_of_overlap', []))}", styles['Normal']))
        elements.append(Paragraph(f"Gaps & Opportunities: {', '.join(strategic.get('gaps_and_opportunities', []))}", styles['Normal']))
        elements.append(Paragraph(f"Recommended Differentiators: {', '.join(strategic.get('recommended_differentiators', []))}", styles['Normal']))
        elements.append(Paragraph(f"Go-to-Market Strategy: {strategic.get('go_to_market_strategy', 'Not provided')}", styles['Normal']))
        elements.append(Paragraph(f"Threat Assessment: {strategic.get('threat_assessment', 'Not provided')}", styles['Normal']))
        elements.append(Paragraph(f"Market Size Insights: {strategic.get('market_size_insights', 'Not provided')}", styles['Normal']))

        doc.build(elements)
        pdf_buffer.seek(0)

        return pdf_buffer

    except Exception as e:
        logger.error(f"Failed to create PDF report: {e}")
        raise RuntimeError(f"Failed to create PDF report: {e}")

def send_email_with_pdf(pdf_buffer: BytesIO, recipient_email: str, industry: str):
    """Send the PDF report as an email attachment.

    Args:
        pdf_buffer (BytesIO): The PDF report as a BytesIO object
        recipient_email (str): The email address of the recipient
        industry (str): The industry or category (e.g., 'AI coding assistants')
    """
    try:
        logger.info(f"Sending email to {recipient_email}")
        # Create a message with the PDF attachment
        message = MIMEMultipart()
        message["From"] = os.getenv("EMAIL_SENDER")
        message["To"] = recipient_email
        message["Subject"] = f"Competitor Analysis Report for {industry}"

        # Attach the PDF report
        pdf_buffer.seek(0)
        attachment = MIMEApplication(pdf_buffer.read(), _subtype="pdf")
        attachment.add_header("Content-Disposition", "attachment", filename="competitor_analysis_report.pdf")
        message.attach(attachment)

        logger.info(f"Email content: {message.as_string()}")

        # Send the email
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(message)
            
        logger.info(f"Email sent to {recipient_email}")

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise RuntimeError(f"Failed to send email: {e}")