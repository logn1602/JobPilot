"""
JobPilot — Deduplication Tracker
Ensures the same job is never processed twice across runs.
Uses job URL as the unique identifier.
"""

import json
import os
from typing import List, Dict
from config.settings import SEEN_JOBS_FILE


class DedupTracker:
    """Tracks seen job URLs across scraping runs to avoid duplicates."""

    def __init__(self):
        self.seen_urls = self._load()

    def _load(self) -> set:
        """Load previously seen job URLs from disk."""
        if os.path.exists(SEEN_JOBS_FILE):
            try:
                with open(SEEN_JOBS_FILE, "r") as f:
                    data = json.load(f)
                    return set(data)
            except (json.JSONDecodeError, TypeError):
                return set()
        return set()

    def _save(self):
        """Persist seen URLs to disk."""
        os.makedirs(os.path.dirname(SEEN_JOBS_FILE), exist_ok=True)
        with open(SEEN_JOBS_FILE, "w") as f:
            json.dump(list(self.seen_urls), f, indent=2)

    def filter_new(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filter a list of jobs, returning only those not seen before.
        Automatically marks returned jobs as seen.
        """
        new_jobs = []
        for job in jobs:
            url = job.get("url", "").strip()
            if not url:
                continue

            # Also create a secondary key from title + company for URL-less matches
            fallback_key = f"{job.get('title', '')}|{job.get('company', '')}".lower().strip()

            if url not in self.seen_urls and fallback_key not in self.seen_urls:
                new_jobs.append(job)
                self.seen_urls.add(url)
                if fallback_key:
                    self.seen_urls.add(fallback_key)

        self._save()
        return new_jobs

    def get_stats(self) -> dict:
        """Return dedup stats."""
        return {
            "total_seen": len(self.seen_urls),
        }

    def reset(self):
        """Clear all seen jobs (start fresh)."""
        self.seen_urls = set()
        self._save()
        print("🔄 Dedup tracker reset — all jobs will be treated as new.")
