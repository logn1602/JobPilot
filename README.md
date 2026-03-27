# 🚀 JobPilot — AI-Powered Job Search Automation Pipeline

**Automate your job search. Stop scrolling. Start interviewing.**

JobPilot is an end-to-end pipeline that scrapes job boards, uses AI to match listings against your resume, generates tailored cover letters, and delivers a daily digest to your inbox and Google Sheets — all on a free-tier stack.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Apify](https://img.shields.io/badge/Apify-Free%20Tier-green?logo=apify)
![Groq](https://img.shields.io/badge/Groq-Free%20AI-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi-Platform Scraping** | LinkedIn, Indeed, Glassdoor, Handshake via Apify |
| **Smart Deduplication** | Never see the same job twice — even across runs and reposts |
| **AI Job Matching** | LLM scores each job 0-100 against your resume with detailed reasoning |
| **Cover Letter Gen** | Auto-generates tailored cover letters for top matches |
| **Google Sheets Tracker** | Live dashboard to track applications, scores, and status |
| **Email Digest** | Beautiful HTML email with top matches, scores, and "Apply" links |
| **Dual AI Support** | Switch between Groq (free) and OpenAI (paid) with one env variable |
| **CLI Flexibility** | Scrape-only, score-only, platform-specific, and reset modes |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        JobPilot Pipeline                     │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│  SCRAPE  │  DEDUP   │ AI MATCH │ COVER    │    NOTIFY       │
│          │          │          │ LETTER   │                 │
│ LinkedIn │ URL-based│ Groq /   │ Auto-gen │ Google Sheets   │
│ Indeed   │ tracking │ OpenAI   │ for top  │ Email Digest    │
│ Glassdoor│ across   │ scoring  │ 5 jobs   │                 │
│ Handshake│ all runs │ 0-100    │          │                 │
└──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/logn1602/JobPilot.git
cd JobPilot
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

| Key | Where to Get It | Cost |
|-----|-----------------|------|
| `APIFY_API_TOKEN` | [console.apify.com](https://console.apify.com) → Settings → API Tokens | Free ($5/mo credits) |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → API Keys | Free |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) | ~$0.01/job |
| `EMAIL_PASSWORD` | [Gmail App Password](https://myaccount.google.com/apppasswords) | Free |

### 3. Set Up Google Sheets (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable **Google Sheets API** and **Google Drive API**
3. Go to **Credentials** → Create **Service Account**
4. Download the JSON key → save as `credentials.json` in the project root
5. Create a Google Sheet named **"JobPilot Tracker"**
6. Share the sheet with the service account email (found in the JSON file)

### 4. Add Your Resume

Edit `data/my_resume.txt` with your full resume text. The AI uses this to match and score jobs.

### 5. Run It!

```bash
# Full pipeline: scrape → deduplicate → AI match → cover letters → notify
python main.py

# Scrape specific platforms only
python main.py --platforms linkedin indeed

# Just scrape, no AI (saves credits for testing)
python main.py --scrape-only

# Re-score jobs from the last scrape
python main.py --score-only

# Clear dedup history (treat all jobs as new)
python main.py --reset
```

---

## 📁 Project Structure

```
JobPilot/
├── main.py                         # Pipeline orchestrator
├── config/
│   └── settings.py                 # Centralized configuration
├── scraper/
│   ├── apify_scraper.py            # Multi-platform Apify scraper
│   └── dedup.py                    # Cross-run deduplication
├── ai/
│   ├── job_matcher.py              # AI resume-job scoring (Groq/OpenAI)
│   └── cover_letter_gen.py         # AI cover letter generation
├── notifications/
│   ├── sheets_updater.py           # Google Sheets integration
│   └── email_alerts.py             # HTML email digest
├── data/
│   ├── my_resume.txt               # Your resume (edit this!)
│   ├── seen_jobs.json              # Dedup tracker (auto-managed)
│   ├── latest_scrape.json          # Raw scrape output
│   └── latest_results.json         # AI-scored results
├── .env.example                    # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 💡 How AI Matching Works

For each job, the LLM receives your resume + the job description and returns:

```json
{
    "match_score": 82,
    "recommendation": "Apply",
    "match_reasons": [
        "Strong Python and SQL skills match requirements",
        "Power BI dashboard experience directly relevant",
        "Prior internship in data pipeline development"
    ],
    "missing_skills": ["Trade compliance knowledge", "Supply chain experience"],
    "summary": "Strong technical fit with relevant data engineering experience."
}
```

Jobs scoring ≥ 60/100 (configurable via `MIN_MATCH_SCORE`) trigger notifications.

---

## 💰 Cost Breakdown (Free Tier)

| Service | Free Tier | Enough For |
|---------|-----------|------------|
| Apify | $5/month credits | ~200-500 job scrapes/month |
| Groq | Free (rate limited) | Unlimited scoring (with delays) |
| Google Sheets | Free | Unlimited |
| Gmail | Free | Unlimited emails |
| **Total** | **$0/month** | **Full pipeline** |

---

## 🛠️ Tech Stack

- **Python 3.9+** — Core language
- **Apify** — Web scraping platform (LinkedIn, Indeed, Glassdoor, Handshake)
- **Groq / OpenAI** — LLM for job matching and cover letter generation
- **Google Sheets API** — Application tracking dashboard
- **SMTP (Gmail)** — Email digest notifications

---

## 📬 Sample Email Digest

The pipeline sends a professional HTML email with:
- Match score (color-coded: 🟢 ≥80, 🟡 ≥60, 🔴 <60)
- Job title, company, location, salary
- AI-generated match reasons
- Skills gaps to brush up on
- Direct "Apply Now" link

---

## 🤝 Contributing

Pull requests welcome! Some ideas:
- Add Telegram/Slack notification channels
- Build a Streamlit dashboard for the tracker
- Add resume parser to auto-extract from PDF
- Implement scheduling with `schedule` or `cron`

---

## 📄 License

MIT License — use it, modify it, land that dream job.

---

**Built by [Shubh Dave](https://github.com/logn1602)** | Northeastern University
