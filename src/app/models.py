import os
from langchain_groq import ChatGroq

# Fast model (Llama 3.1 8B Instant)
llm_fast = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.2,
    max_tokens=2048,
    api_key=os.getenv("GROQ_API_KEY")
)

# High-quality model (Llama 3.3 70B Versatile)
llm_smart = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.2,
    max_tokens=4096,
    api_key=os.getenv("GROQ_API_KEY")
)