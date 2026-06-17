import json
import logging
from io import BytesIO
from typing import List, Dict

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

logger = logging.getLogger(__name__)


def _build_competitor_elements(competitors: List[Dict], styles) -> list:
    elements = []
    for comp in competitors:
        elements.append(Paragraph(comp["name"], styles["Heading3"]))
        elements.append(Paragraph(f"Company Description: {comp['company_description']}", styles["Normal"]))
        elements.append(Paragraph(f"Key Features: {', '.join(comp['key_features'])}", styles["Normal"]))
        elements.append(Paragraph(f"Pricing Model: {comp['pricing_model']}", styles["Normal"]))
        elements.append(Paragraph(f"Target Market: {comp['target_market']}", styles["Normal"]))
        elements.append(Paragraph(f"Strengths: {', '.join(comp['strengths'])}", styles["Normal"]))
        elements.append(Paragraph(f"Weaknesses: {', '.join(comp['weaknesses'])}", styles["Normal"]))
        elements.append(Paragraph(f"Unique Value Proposition: {comp['unique_value_proposition']}", styles["Normal"]))
        elements.append(Paragraph(f"Market Position: {comp['market_position']}", styles["Normal"]))
        elements.append(Spacer(1, 6))
    return elements


def _build_matrix_table(comparison_matrix: List[Dict]) -> Table | None:
    if not comparison_matrix:
        return None
    matrix_rows = [[key] + [row[key] for row in comparison_matrix] for key in comparison_matrix[0].keys()]
    return Table(matrix_rows)


def _build_strategic_elements(strategic: Dict, styles) -> list:
    elements = []
    elements.append(Paragraph(f"Market Positioning: {strategic.get('market_positioning', 'Not provided')}", styles["Normal"]))
    elements.append(Paragraph(f"Competitive Advantages: {', '.join(strategic.get('competitive_advantages', []))}", styles["Normal"]))
    elements.append(Paragraph(f"Areas of Overlap: {', '.join(strategic.get('areas_of_overlap', []))}", styles["Normal"]))
    elements.append(Paragraph(f"Gaps & Opportunities: {', '.join(strategic.get('gaps_and_opportunities', []))}", styles["Normal"]))
    elements.append(Paragraph(f"Recommended Differentiators: {', '.join(strategic.get('recommended_differentiators', []))}", styles["Normal"]))
    elements.append(Paragraph(f"Go-to-Market Strategy: {strategic.get('go_to_market_strategy', 'Not provided')}", styles["Normal"]))
    elements.append(Paragraph(f"Threat Assessment: {strategic.get('threat_assessment', 'Not provided')}", styles["Normal"]))
    elements.append(Paragraph(f"Market Size Insights: {strategic.get('market_size_insights', 'Not provided')}", styles["Normal"]))
    return elements


def create_pdf_report(analysis_json: str, industry: str, product_summary: str) -> BytesIO:
    """Build a PDF report from the analysis JSON string.

    Args:
        analysis_json: JSON string from analyse_competitors
        industry: Industry label (used in report header)
        product_summary: Product description shown near the top of the report

    Returns:
        BytesIO containing the rendered PDF
    """
    try:
        analysis_data = json.loads(analysis_json)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Competitor Analysis Report", styles["Title"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Product Summary", styles["Heading2"]))
        elements.append(Paragraph(product_summary, styles["BodyText"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Competitor Summaries", styles["Heading2"]))
        elements.extend(_build_competitor_elements(analysis_data.get("competitor_summaries", []), styles))

        elements.append(Paragraph("Comparison Matrix", styles["Heading2"]))
        matrix_table = _build_matrix_table(analysis_data.get("comparison_matrix", []))
        if matrix_table:
            elements.append(matrix_table)

        elements.append(Paragraph("Strategic Analysis", styles["Heading2"]))
        elements.extend(_build_strategic_elements(analysis_data.get("strategic_analysis", {}), styles))

        pdf_buffer = BytesIO()
        SimpleDocTemplate(pdf_buffer, pagesize=letter).build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer

    except Exception as e:
        logger.error(f"Failed to create PDF report: {e}")
        raise RuntimeError(f"Failed to create PDF report: {e}") from e
