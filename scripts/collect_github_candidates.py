import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import AuditLog, Candidate, GitHubProfile
from app.services.github_service import (
    fetch_github_repositories,
    fetch_github_user_profile,
    search_github_users,
    summarize_github_profile
)


DEFAULT_QUERY = "language:python location:Germany followers:>5 repos:>3"


def save_github_candidate(db, summary):
    username = summary["github_username"]

    candidate = (
        db.query(Candidate)
        .filter(Candidate.github_username == username)
        .first()
    )

    if candidate is None:
        candidate = Candidate(
            display_name=summary["display_name"],
            email=None,
            github_username=username,
            profile_url=summary["profile_url"],
            location=summary["location"],
            source="github_api",
            privacy_basis="public GitHub profile data for academic prototype"
        )
        db.add(candidate)
        db.flush()
        action = "created_github_candidate"
    else:
        candidate.display_name = summary["display_name"]
        candidate.profile_url = summary["profile_url"]
        candidate.location = summary["location"]
        action = "updated_github_candidate"

    github_profile = (
        db.query(GitHubProfile)
        .filter(GitHubProfile.candidate_id == candidate.id)
        .first()
    )

    if github_profile is None:
        github_profile = GitHubProfile(candidate_id=candidate.id)
        db.add(github_profile)

    github_profile.public_repos = summary["public_repos"]
    github_profile.followers = summary["followers"]
    github_profile.following = summary["following"]
    github_profile.total_stars = summary["total_stars"]
    github_profile.total_forks = summary["total_forks"]
    github_profile.recent_push_count = summary["recent_push_count"]
    github_profile.account_age_days = summary["account_age_days"]
    github_profile.top_languages_json = summary["top_languages_json"]
    github_profile.raw_profile_json = summary["raw_profile_json"]

    audit_log = AuditLog(
        actor="system",
        action=action,
        entity_type="candidate",
        entity_id=candidate.id,
        details_json={
            "source": "github_api",
            "github_username": username,
            "stored_email": False
        }
    )
    db.add(audit_log)

    return candidate.id


def collect_candidates(query: str, limit: int):
    print(f"Searching GitHub users with query: {query}")
    print(f"Collection limit: {limit}")

    usernames = search_github_users(query=query, max_users=limit)

    print(f"Found {len(usernames)} GitHub usernames")

    db = SessionLocal()

    inserted_or_updated = 0
    skipped = 0

    try:
        for username in usernames:
            try:
                print(f"Collecting: {username}")

                profile = fetch_github_user_profile(username)

                if profile.get("type") != "User":
                    print(f"Skipped {username}: not a user profile")
                    skipped += 1
                    continue

                repos = fetch_github_repositories(username)
                summary = summarize_github_profile(profile, repos)

                candidate_id = save_github_candidate(db, summary)
                db.commit()

                inserted_or_updated += 1
                print(f"Saved candidate_id={candidate_id}")

            except Exception as exc:
                db.rollback()
                skipped += 1
                print(f"Skipped {username}: {exc}")

    except SQLAlchemyError as exc:
        db.rollback()
        raise exc

    finally:
        db.close()

    print("")
    print("GitHub collection completed")
    print(f"Inserted/updated: {inserted_or_updated}")
    print(f"Skipped: {skipped}")


def parse_args():
    parser = argparse.ArgumentParser(description="Collect public GitHub candidate profiles.")
    parser.add_argument(
        "--query",
        type=str,
        default=DEFAULT_QUERY,
        help="GitHub user search query."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=settings.data_collection_limit,
        help="Maximum number of GitHub users to collect."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    collect_candidates(query=args.query, limit=args.limit)
