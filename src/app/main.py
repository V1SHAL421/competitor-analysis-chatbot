import streamlit as st
import pandas as pd
import json
from constants import categories
from agent import run_competitor_analysis

st.title("Competitor Analyser")

# Dropdown for industry selection
industry = st.selectbox(
    "Industry / Category",
    categories,
    index=None,
    placeholder="Select an industry...",
    help="Helps agent search for relevant competitors"
)

# User input of product summary for context
product_summary = st.text_area(
    "Product Summary",
    placeholder="Describe your product in 2-3 sentences.",
    max_chars=300,
    help="Keep it under 300 characters"
)

# Analyse button to trigger agentic workflow
if st.button(
    "🔍 Analyse Competitors", 
    type="primary", 
    use_container_width=True,
    disabled=not (industry and product_summary and len(product_summary.strip()) > 0)
):
    st.success("Starting competitor analysis...")
    result = run_competitor_analysis(industry, product_summary)
    
    try:
        analysis_data = json.loads(result)
        
        # Display competitor summaries
        st.subheader("Competitor Summaries")
        for comp in analysis_data.get("competitor_summaries", []):
            with st.expander(comp.get("name", "Unknown Competitor")):
                st.write(f"**Website:** {comp.get('website_url', 'Not available')}")
                st.write(f"**Description:** {comp.get('company_description', 'Not available')}")
                st.write(f"**Key Features:** {', '.join(comp.get('key_features', []))}")
                st.write(f"**Pricing Model:** {comp.get('pricing_model', 'Not specified')}")
                st.write(f"**Target Market:** {comp.get('target_market', 'Not specified')}")
                st.write(f"**Strengths:** {', '.join(comp.get('strengths', []))}")
                st.write(f"**Weaknesses:** {', '.join(comp.get('weaknesses', []))}")
                st.write(f"**Value Proposition:** {comp.get('unique_value_proposition', 'Not specified')}")
                st.write(f"**Technology Stack:** {', '.join(comp.get('technology_stack', []))}")
                st.write(f"**Market Position:** {comp.get('market_position', 'Not specified')}")
        
        # Display comparison matrix as dataframe
        st.subheader("Feature Comparison Matrix")
        if analysis_data.get("comparison_matrix"):
            df = pd.DataFrame(analysis_data["comparison_matrix"])
            st.dataframe(df, use_container_width=True)
        
        # Display strategic analysis
        st.subheader("Strategic Analysis")
        strategic = analysis_data.get("strategic_analysis", {})
        st.write(f"**Market Positioning:** {strategic.get('market_positioning', 'Not provided')}")
        st.write(f"**Competitive Advantages:** {', '.join(strategic.get('competitive_advantages', []))}")
        st.write(f"**Areas of Overlap:** {', '.join(strategic.get('areas_of_overlap', []))}")
        st.write(f"**Gaps & Opportunities:** {', '.join(strategic.get('gaps_and_opportunities', []))}")
        st.write(f"**Recommended Differentiators:** {', '.join(strategic.get('recommended_differentiators', []))}")
        st.write(f"**Go-to-Market Strategy:** {strategic.get('go_to_market_strategy', 'Not provided')}")
        st.write(f"**Threat Assessment:** {strategic.get('threat_assessment', 'Not provided')}")
        st.write(f"**Market Size Insights:** {strategic.get('market_size_insights', 'Not provided')}")
        st.write(f"**Next Steps:** {strategic.get('next_steps', 'Not provided')}")
        
    except json.JSONDecodeError:
        st.write(result)
    