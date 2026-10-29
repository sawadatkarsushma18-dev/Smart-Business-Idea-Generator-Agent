"""
config.py – Centralised application configuration.
Loads credentials from environment variables or .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── IBM WatsonX credentials ─────────────────────────────────────────────────
IBM_API_KEY: str = os.getenv("IBM_API_KEY", "cLaqQ1kpqBJWfzva-HJwIzBK22qvCElWWytjLahcIUoo")
IBM_PROJECT_ID: str = os.getenv("IBM_PROJECT_ID", "e5329855-dcb6-470a-beef-412fdd2efc43")
IBM_URL: str = os.getenv("IBM_URL", "https://au-syd.ml.cloud.ibm.com")

# ── Model configuration ─────────────────────────────────────────────────────
MODEL_ID: str = "meta-llama/llama-3-3-70b-instruct"

# Keep alias so existing imports don't break
GRANITE_MODEL_ID: str = MODEL_ID

# Generation parameters
GENERATION_PARAMS: dict = {
    "max_new_tokens": 3000,
    "min_new_tokens": 100,
    "temperature": 0.75,
    "top_p": 0.9,
    "top_k": 50,
    "repetition_penalty": 1.1,
}

# ── Application settings ────────────────────────────────────────────────────
APP_DEBUG: bool = os.getenv("APP_DEBUG", "False").lower() == "true"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
APP_TITLE: str = "Smart Business Idea Generator Agent"
APP_VERSION: str = "1.0.0"

# ── Disclaimer ──────────────────────────────────────────────────────────────
DISCLAIMER: str = (
    "⚠️ **Disclaimer:** AI-generated business ideas, market assessments, and financial "
    "estimates are informational suggestions only. They do not guarantee business success, "
    "profitability, or investment returns. All cost figures, revenue projections, and market "
    "statistics are AI-generated estimates unless explicitly marked as verified. Always consult "
    "qualified professionals before making business or financial decisions."
)
