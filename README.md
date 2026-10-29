# 💡 Smart Business Idea Generator Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red?logo=streamlit)
![IBM WatsonX](https://img.shields.io/badge/IBM-WatsonX%20AI-0530AD?logo=ibm)
![Llama 3.3](https://img.shields.io/badge/LLM-Llama%203.3%2070B-purple)
![License](https://img.shields.io/badge/License-MIT-green)

**An intelligent agentic AI application that transforms your interests, skills, and real-world problems into creative, feasible, and actionable business opportunities — powered by Meta Llama 3.3 70B Instruct via IBM WatsonX AI.**

[Features](#-features) · [Demo](#-demo) · [Quick Start](#-quick-start) · [Architecture](#-architecture) · [Usage](#-usage) · [Deployment](#-deployment)

</div>

---

## ⚠️ Disclaimer

> AI-generated business ideas, market assessments, and financial estimates are **informational suggestions only**. They do **not** guarantee business success, profitability, or investment returns. All cost figures, revenue projections, and market statistics are AI-generated estimates unless explicitly marked as verified. Always consult qualified professionals before making business or financial decisions.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Agentic AI Workflow** | Four modular agents: Idea Generation → Market Analysis → Feasibility Evaluation → Recommendation |
| 💡 **3–5 Unique Ideas** | Personalised business ideas based on skills, budget, location, and goals |
| 📊 **Scoring & Ranking** | Transparent weighted scoring across 7 dimensions with radar charts |
| 🗺️ **Full Business Plan** | Roadmap, MVP plan, tools, marketing, risks, and next steps |
| ⚖️ **Idea Comparison** | Side-by-side comparison tables and grouped bar charts |
| 💬 **Follow-up Chat** | Refine ideas, ask questions, and explore alternatives interactively |
| 📥 **PDF / Text Export** | Download a complete report of all generated ideas and the business plan |
| 🛡️ **Responsible AI** | Input sanitisation, prompt injection guards, no fabricated statistics |

---

## 🖥️ Demo

```
User fills in profile  →  Agentic pipeline runs (5 steps)  →  Dashboard unlocks

  🏠 Home        – Profile form & pipeline trigger
  💡 Ideas       – Expandable idea cards with radar charts & feasibility verdicts
  📊 Compare     – Bar chart + table comparing all ideas; deep two-idea comparison
  📋 Plan        – Full business plan (Roadmap · MVP · Tools · Marketing · Risks)
  💬 Chat        – Open-ended follow-up queries answered by Llama 3.3
```

---

## 🗂️ Project Structure

```
Smart-Business-Idea-Generator-Agent/
│
├── app.py                        # Main Streamlit application entry point
├── config.py                     # Centralised configuration & credentials
├── llm_client.py                 # WatsonX AI / Llama 3.3 client (singleton)
├── models.py                     # Typed dataclasses for all data structures
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
│
├── agents/
│   ├── prompts.py                # All 6 LLM prompt templates
│   ├── idea_agent.py             # Agent 1 – Generates 3–5 business ideas
│   ├── market_agent.py           # Agent 2 – Market size, trends, competitors
│   ├── feasibility_agent.py      # Agent 3 – Technical/financial/operational check
│   ├── recommendation_agent.py   # Agent 4 – Weighted ranking + business plan
│   └── orchestrator.py           # Master pipeline coordinator
│
├── ui/
│   └── components.py             # Reusable Streamlit UI components
│
├── utils/
│   ├── logger.py                 # Safe application logging
│   ├── validators.py             # Input sanitisation & validation
│   ├── parsers.py                # LLM response → typed Python objects
│   └── pdf_exporter.py           # PDF / text report generator
│
└── tests/
    ├── test_validators.py        # 16 validator unit tests
    ├── test_parsers.py           # 18 parser unit tests
    └── test_recommendation_agent.py  # 9 ranking logic unit tests
```

---

## 🚀 Quick Start

### Prerequisites

- Python **3.10** or higher
- An **IBM WatsonX AI** account with an API key and a project ID
- `pip` (Python package manager)

### 1 – Clone the repository

```bash
git clone https://github.com/sawadatkarsushma18-dev/Smart-Business-Idea-Generator-Agent.git
cd Smart-Business-Idea-Generator-Agent
```

### 2 – Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3 – Install dependencies

```bash
pip install -r requirements.txt
```

### 4 – Configure credentials

Copy the template and fill in your IBM WatsonX credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
IBM_API_KEY=your_ibm_watsonx_api_key
IBM_PROJECT_ID=your_watsonx_project_id
IBM_URL=https://au-syd.ml.cloud.ibm.com
```

> **Security note:** Never commit your `.env` file. It is listed in `.gitignore`.

### 5 – Run the app

```bash
# Standard Python installation
streamlit run app.py

# Windows Store / Microsoft Store Python (PATH not set)
python -m streamlit run app.py
```

Open **`http://localhost:8501`** in your browser.

---

## 🤖 Architecture

### Agentic Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     User Profile Input                       │
│  (interest · skills · budget · location · goals · audience) │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   IdeaGenerationAgent  │  Step 1
              │  Llama 3.3 70B prompt  │  Generate 3–5 tailored ideas
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │  MarketAnalysisAgent   │  Step 2
              │  (per idea)            │  Market size · trends · competitors
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   FeasibilityAgent     │  Step 3
              │  (per idea)            │  Technical · financial · operational
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │  RecommendationAgent   │  Step 4 + 5
              │  Weighted ranking      │  Rank all ideas
              │  Business plan         │  Full plan for top pick
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   Streamlit Dashboard  │
              │  Ideas · Compare · Plan│
              │  Chat · PDF Export     │
              └────────────────────────┘
```

### Scoring Dimensions (weighted composite)

| Dimension | Weight | Description |
|---|---|---|
| Feasibility | **20%** | Can it be built with available resources? |
| Market Demand | **20%** | Is there a real need in the market? |
| Affordability | **15%** | Does it fit within the stated budget? |
| Profitability | **15%** | Can it generate sustainable revenue? |
| Innovation | **10%** | How unique and novel is the idea? |
| Social Impact | **10%** | Does it benefit society or community? |
| Scalability | **10%** | Can it grow beyond the initial market? |

---

## 💬 Usage Examples

### Supported follow-up queries (Chat page)

```
Suggest business ideas under $1,000
Generate AI-based startup ideas for students
Find innovative solutions for local food waste
Compare Idea 1 and Idea 3
Suggest low-investment business opportunities
Create a business plan for the top idea
How can I market this idea on social media?
What are the biggest risks for my selected idea?
Improve my existing business idea
```

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| LLM | **Meta Llama 3.3 70B Instruct** via IBM WatsonX AI |
| Backend | Python 3.10+ |
| Web Framework | Streamlit |
| IBM SDK | `ibm-watsonx-ai` |
| Visualisation | Plotly |
| Data | Pandas |
| PDF Export | `fpdf2` |
| Testing | `pytest` |

---

## 🧪 Running Tests

```bash
# Run all 43 tests (no API key required)
pytest tests/ -v

# Individual test files
pytest tests/test_validators.py -v
pytest tests/test_parsers.py -v
pytest tests/test_recommendation_agent.py -v
```

All tests for validators, parsers, and ranking logic run **offline** — no IBM API connection needed.

---

## 🔧 Environment Variables

| Variable | Required | Description | Default |
|---|---|---|---|
| `IBM_API_KEY` | ✅ | WatsonX AI API key | – |
| `IBM_PROJECT_ID` | ✅ | WatsonX project ID | – |
| `IBM_URL` | ❌ | WatsonX endpoint URL | `https://au-syd.ml.cloud.ibm.com` |
| `APP_DEBUG` | ❌ | Enable debug mode | `False` |
| `LOG_LEVEL` | ❌ | Logging verbosity | `INFO` |

---

## 📦 Deployment

### Streamlit Community Cloud (free)

1. Fork this repository to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your fork → set main file to `app.py`.
4. Under **Advanced settings → Secrets**, add:
   ```toml
   IBM_API_KEY = "your_api_key"
   IBM_PROJECT_ID = "your_project_id"
   IBM_URL = "https://au-syd.ml.cloud.ibm.com"
   ```
5. Click **Deploy**.

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build & run
docker build -t business-idea-generator .
docker run -p 8501:8501 \
  -e IBM_API_KEY=your_key \
  -e IBM_PROJECT_ID=your_project_id \
  business-idea-generator
```

### Local (development)

```bash
python -m streamlit run app.py
```

---

## 🛡️ Responsible AI Practices

- **Input Sanitisation:** All user inputs are sanitised to prevent prompt injection attacks.
- **No Fabricated Statistics:** Every prompt explicitly instructs the model to label all financial and market figures as AI-estimated.
- **No Success Guarantees:** The application never guarantees profits, success, or investment returns.
- **Inclusive Language:** All prompts enforce a helpful, respectful, and inclusive tone.
- **Data Privacy:** No user data is stored, logged in identifiable form, or sent to any third party other than IBM WatsonX AI for inference.

---

## 📝 Sample Output

```
💡 EduBot AI — Personalised AI tutoring for every student  •  8.2/10  •  🟡 Medium

🎯 Problem:   Students in rural areas lack access to quality tutors.
💡 Solution:  An AI-powered chatbot providing 24/7 personalised tutoring.
💰 Cost:      $3,000–$8,000 (AI-estimated)
📈 Revenue:   Freemium subscription
⭐ USP:       Affordable, offline-capable, multilingual tutoring bot

Innovation 8 | Feasibility 7 | Market Demand 9 | Affordability 8
Social Impact 9 | Scalability 9 | Overall 8/10
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is released under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ using **Meta Llama 3.3 70B** · **IBM WatsonX AI** · **Streamlit**

*AI-generated outputs are suggestions only — not financial or business advice.*

</div>
