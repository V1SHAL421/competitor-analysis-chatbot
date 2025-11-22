import streamlit as st
from constants import categories
from utils import analyse_competitors

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
    analyse_competitors(industry, product_summary)
    