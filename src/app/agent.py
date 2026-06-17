from functools import lru_cache
from typing import Generator

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

from constants import get_llm
from tools import search_competitors, scrape_competitor_page, analyse_competitors

_tools = [search_competitors, scrape_competitor_page, analyse_competitors]

# Human-readable labels for each tool call shown in the UI
_TOOL_LABELS = {
    "search_competitors": "🔎 Searching for competitors...",
    "scrape_competitor_page": "🌐 Scraping {url}...",
    "analyse_competitors": "🧠 Analysing competitors...",
}


@lru_cache(maxsize=1)
def _get_agent():
    return create_react_agent(get_llm(), tools=_tools)


def _build_system_prompt(industry: str, product_summary: str) -> str:
    return (
        f"You are a competitive intelligence analyst. "
        f"Research competitors for a company in the '{industry}' industry. "
        f"Their product: {product_summary}\n\n"
        f"Steps:\n"
        f"1. Call search_competitors to get candidate URLs.\n"
        f"2. For each URL, decide whether it is worth scraping. "
        f"Prefer official company homepages and pricing pages. "
        f"Skip Wikipedia, LinkedIn, aggregator sites (G2, Capterra), and news articles. "
        f"Call scrape_competitor_page once per URL you choose to scrape.\n"
        f"3. Once you have scraped the pages you judge useful, call analyse_competitors "
        f"with the industry, product summary, and the collected scrape results.\n\n"
        f"Return only the JSON output from analyse_competitors."
    )


def run_competitor_analysis(industry: str, product_summary: str) -> str:
    """Run the competitor analysis agent and return the analysis JSON string."""
    result = _get_agent().invoke({
        "messages": [HumanMessage(content=_build_system_prompt(industry, product_summary))]
    })

    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and msg.content:
            return msg.content

    return ""


def stream_competitor_analysis(industry: str, product_summary: str) -> Generator[tuple[str, str], None, str]:
    """Stream agent steps as (label, detail) tuples, then yield the final JSON.

    Yields:
        ("step", "<human-readable description>") for each tool call
        ("result", "<json string>") as the final item
    """
    final_content = ""

    for chunk in _get_agent().stream(
        {"messages": [HumanMessage(content=_build_system_prompt(industry, product_summary))]},
        stream_mode="values",
    ):
        messages = chunk.get("messages", [])
        if not messages:
            continue

        last = messages[-1]

        # Agent is about to call a tool
        if isinstance(last, AIMessage) and last.tool_calls:
            for tc in last.tool_calls:
                name = tc["name"]
                args = tc.get("args", {})
                template = _TOOL_LABELS.get(name, f"⚙️ Calling {name}...")
                # Inject URL into the scrape label if available
                label = template.format(url=args.get("url", "")) if "{url}" in template else template
                detail = ", ".join(f"{k}={v!r}" for k, v in args.items() if k != "competitor_data")
                yield ("step", label, detail)

        # Tool has returned a result
        elif isinstance(last, ToolMessage):
            content_preview = str(last.content)[:120].replace("\n", " ")
            yield ("tool_result", f"✅ Got result from {last.name}", content_preview)

        # Final AI message with the JSON answer
        elif isinstance(last, AIMessage) and last.content and not last.tool_calls:
            final_content = last.content

    yield ("result", final_content, "")
