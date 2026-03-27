"""
JobPilot — AI Job Matcher
Scores each job against your resume using LLM.
Supports: Groq (free) and OpenAI (paid)
"""

import json
from typing import Dict, Optional
from config.settings import (
    AI_PROVIDER, GROQ_API_KEY, OPENAI_API_KEY,
    GROQ_MODEL, OPENAI_MODEL, RESUME_FILE, MIN_MATCH_SCORE,
)


def _load_resume() -> str:
    """Load resume text from file."""
    try:
        with open(RESUME_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("  ⚠️  Resume file not found at data/my_resume.txt — using empty resume")
        return ""


def _get_client():
    """Get the appropriate AI client based on config."""
    if AI_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set! Get one free at https://console.groq.com")
        from groq import Groq
        return Groq(api_key=GROQ_API_KEY), GROQ_MODEL
    elif AI_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set!")
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY), OPENAI_MODEL
    else:
        raise ValueError(f"Unknown AI_PROVIDER: {AI_PROVIDER}. Use 'groq' or 'openai'.")


def score_job(job: Dict, resume_text: Optional[str] = None) -> Dict:
    """
    Score a job against the resume using AI.

    Returns the job dict enriched with:
        - match_score (0-100)
        - match_reasons (list of why it's a good fit)
        - missing_skills (list of skills you'd need)
        - recommendation ("Apply", "Maybe", "Skip")
    """
    if resume_text is None:
        resume_text = _load_resume()

    client, model = _get_client()

    prompt = f"""You are a career advisor AI. Analyze how well this job matches the candidate's resume.

CANDIDATE RESUME:
{resume_text[:4000]}

JOB POSTING:
Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'N/A')}
Location: {job.get('location', 'N/A')}
Type: {job.get('job_type', 'N/A')}
Salary: {job.get('salary', 'N/A')}
Description: {job.get('description', 'N/A')[:2500]}

Respond ONLY with a valid JSON object (no markdown, no backticks, no extra text):
{{
    "match_score": <integer 0-100>,
    "recommendation": "<Apply | Maybe | Skip>",
    "match_reasons": ["<reason 1>", "<reason 2>", "<reason 3>"],
    "missing_skills": ["<skill 1>", "<skill 2>"],
    "summary": "<1-2 sentence summary of fit>"
}}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise career matching AI. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
        )

        text = response.choices[0].message.content.strip()
        # Clean potential markdown fences
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)

        job["match_score"] = result.get("match_score", 0)
        job["recommendation"] = result.get("recommendation", "Skip")
        job["match_reasons"] = result.get("match_reasons", [])
        job["missing_skills"] = result.get("missing_skills", [])
        job["ai_summary"] = result.get("summary", "")

    except json.JSONDecodeError:
        print(f"    ⚠️  AI returned invalid JSON for: {job.get('title')}")
        job["match_score"] = 0
        job["recommendation"] = "Error"
        job["match_reasons"] = []
        job["missing_skills"] = []
        job["ai_summary"] = "AI analysis failed"
    except Exception as e:
        print(f"    ⚠️  AI scoring error for {job.get('title')}: {e}")
        job["match_score"] = 0
        job["recommendation"] = "Error"
        job["match_reasons"] = []
        job["missing_skills"] = []
        job["ai_summary"] = str(e)

    return job


def score_jobs(jobs: list, resume_text: Optional[str] = None) -> list:
    """Score a batch of jobs, return sorted by match_score descending."""
    if resume_text is None:
        resume_text = _load_resume()

    scored = []
    for i, job in enumerate(jobs):
        print(f"    🤖 Scoring job {i+1}/{len(jobs)}: {job.get('title', '?')} @ {job.get('company', '?')}")
        scored_job = score_job(job, resume_text)
        scored.append(scored_job)

    # Sort by match score (highest first)
    scored.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return scored


def filter_top_matches(scored_jobs: list) -> list:
    """Return only jobs meeting the minimum match score threshold."""
    return [j for j in scored_jobs if j.get("match_score", 0) >= MIN_MATCH_SCORE]
