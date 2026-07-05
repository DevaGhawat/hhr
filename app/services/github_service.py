from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import requests

from app.core.config import settings


GITHUB_API_BASE = "https://api.github.com"


def _github_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "hushhush-recruiter-academic-prototype"
    }

    if settings.github_token and "your_github" not in settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    return headers


def github_get(url: str, params: Optional[Dict] = None) -> Dict:
    response = requests.get(
        url,
        headers=_github_headers(),
        params=params,
        timeout=30
    )

    if response.status_code == 403:
        remaining = response.headers.get("X-RateLimit-Remaining", "unknown")
        reset_time = response.headers.get("X-RateLimit-Reset", "unknown")
        raise RuntimeError(
            f"GitHub API limit or access issue. Remaining={remaining}, Reset={reset_time}"
        )

    if response.status_code >= 400:
        raise RuntimeError(
            f"GitHub API error {response.status_code}: {response.text[:300]}"
        )

    return response.json()


def search_github_users(query: str, max_users: int = 20) -> List[str]:
    usernames = []
    page = 1
    per_page = min(max_users, 30)

    while len(usernames) < max_users:
        data = github_get(
            f"{GITHUB_API_BASE}/search/users",
            params={
                "q": query,
                "per_page": per_page,
                "page": page
            }
        )

        items = data.get("items", [])

        if not items:
            break

        for item in items:
            username = item.get("login")
            if username and username not in usernames:
                usernames.append(username)

            if len(usernames) >= max_users:
                break

        page += 1

    return usernames


def fetch_github_user_profile(username: str) -> Dict:
    return github_get(f"{GITHUB_API_BASE}/users/{username}")


def fetch_github_repositories(username: str, max_repos: int = 100) -> List[Dict]:
    repos = github_get(
        f"{GITHUB_API_BASE}/users/{username}/repos",
        params={
            "per_page": min(max_repos, 100),
            "sort": "pushed",
            "direction": "desc"
        }
    )

    if isinstance(repos, list):
        return repos

    return []


def _parse_github_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def summarize_github_profile(profile: Dict, repos: List[Dict]) -> Dict:
    now = datetime.now(timezone.utc)
    created_at = _parse_github_datetime(profile.get("created_at"))

    if created_at:
        account_age_days = max((now - created_at).days, 0)
    else:
        account_age_days = 0

    recent_cutoff = now - timedelta(days=90)

    total_stars = 0
    total_forks = 0
    recent_push_count = 0
    language_counts = {}

    for repo in repos:
        total_stars += int(repo.get("stargazers_count") or 0)
        total_forks += int(repo.get("forks_count") or 0)

        language = repo.get("language")
        if language:
            language_counts[language] = language_counts.get(language, 0) + 1

        pushed_at = _parse_github_datetime(repo.get("pushed_at"))
        if pushed_at and pushed_at >= recent_cutoff:
            recent_push_count += 1

    top_languages = sorted(
        language_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )

    sanitized_profile = {
        "github_id": profile.get("id"),
        "login": profile.get("login"),
        "html_url": profile.get("html_url"),
        "type": profile.get("type"),
        "created_at": profile.get("created_at"),
        "public_repos": profile.get("public_repos"),
        "followers": profile.get("followers"),
        "following": profile.get("following"),
        "location": profile.get("location")
    }

    return {
        "display_name": profile.get("name") or profile.get("login"),
        "github_username": profile.get("login"),
        "profile_url": profile.get("html_url"),
        "location": profile.get("location"),
        "public_repos": int(profile.get("public_repos") or 0),
        "followers": int(profile.get("followers") or 0),
        "following": int(profile.get("following") or 0),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "recent_push_count": recent_push_count,
        "account_age_days": account_age_days,
        "top_languages_json": dict(top_languages[:10]),
        "raw_profile_json": sanitized_profile
    }
