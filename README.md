# Competitor Analysis Chatbot

An AI-powered competitor analysis tool built with LangGraph, Streamlit, and Groq. Enter your industry and a short product description, and the agent automatically searches the web, scrapes competitor pages, and returns a structured analysis with a downloadable PDF report.

Full documentation: https://deepwiki.com/V1SHAL421/competitor-analysis-chatbot

---

## How It Works

1. Select an industry and describe your product (up to 300 characters).
2. The LangGraph ReAct agent uses **Tavily** to search for competitors, **Firecrawl** to scrape their websites, and **Groq (Llama 3.3 70B)** to produce a structured analysis.
3. Results are displayed in the UI and can be downloaded as a PDF or sent via email.

---

## Prerequisites

- Python 3.10+
- API keys for the following services:

| Key | Where to get it |
|-----|----------------|
| `GROQ_API_KEY` | https://console.groq.com |
| `TAVILY_API_KEY` | https://app.tavily.com |
| `FIRECRAWL_API_KEY` | https://www.firecrawl.dev |
| `EMAIL_SENDER` | Your sender email address |
| `EMAIL_PASSWORD` | App password for the sender account |
| `SMTP_SERVER` | e.g. `smtp.gmail.com` |
| `SMTP_PORT` | e.g. `587` |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/V1SHAL421/competitor-analysis-chatbot.git
cd competitor-analysis-chatbot
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Optional — only needed for the email feature
EMAIL_SENDER=you@example.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

> **Gmail users:** generate an [App Password](https://myaccount.google.com/apppasswords) instead of using your account password.

---

## Running the App

```bash
streamlit run src/app/main.py
```

Streamlit will print a local URL (usually `http://localhost:8501`). Open it in your browser.

---

## Project Structure

```
src/app/
├── main.py          # Streamlit UI
├── agent.py         # LangGraph ReAct agent
├── tools.py         # search_competitors, scrape_competitor_page, analyse_competitors
├── models.py        # Pydantic response schema
├── constants.py     # LLM setup and industry categories
├── pdf.py           # PDF report generation
└── email_sender.py  # Email delivery via SMTP
```
