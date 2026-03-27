"""
JobPilot — AI Cover Letter Generator
Auto-generates a tailored cover letter for high-match jobs.
Supports: Groq (free) and OpenAI (paid)
"""

import json
from typing import Dict, Optional
from config.settings import (
    AI_PROVIDER, GROQ_API_KEY, OPENAI_API_KEY,
    GROQ_MODEL, OPENAI_MODEL, RESUME_FILE,
)


def _load_resume() -> str:
    try:
        with open(RESUME_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def _get_client():
    if AI_PROVIDER == "groq":
        from groq import Groq
        return Groq(api_key=GROQ_API_KEY), GROQ_MODEL
    elif AI_PROVIDER == "openai":
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY), OPENAI_MODEL
    else:
        raise ValueError(f"Unknown AI_PROVIDER: {AI_PROVIDER}")


def generate_cover_letter(job: Dict, resume_text: Optional[str] = None) -> str:
    """
    Generate a tailored cover letter for a specific job.

    Args:
        job: Normalized job dict with title, company, description, etc.
        resume_text: Optional override; defaults to data/my_resume.txt

    Returns:
        Cover letter as a string.
    """
    if resume_text is None:
        resume_text = _load_resume()

    client, model = _get_client()

    prompt = f"""You are an expert career writer. Write a concise, personalized cover letter for this job application.

CANDIDATE RESUME:
{resume_text[:4000]}

JOB DETAILS:
Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'N/A')}
Location: {job.get('location', 'N/A')}
Description: {job.get('description', 'N/A')[:2500]}

INSTRUCTIONS:
- Write a 3-4 paragraph cover letter (250-350 words)
- Open with genuine interest in the specific role and company
- Highlight 2-3 specific experiences from the resume that match the job requirements
- Reference specific projects or technical skills that are relevant
- Close with enthusiasm and availability
- Keep it professional but warm — not generic or robotic
- Do NOT include placeholder brackets like [Your Name] — use info from the resume
- Do NOT include addresses or headers — just the letter body

Return ONLY the cover letter text, no extra formatting.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer. Write compelling, specific, non-generic cover letters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[Cover letter generation failed: {e}]"
