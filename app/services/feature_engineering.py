import math
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.db.models import (
    AuditLog,
    Candidate,
    CandidateFeature,
    GitHubProfile,
    StackOverflowProfile
)


TARGET_LANGUAGES = {
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "Go",
    "C++",
    "Dockerfile",
    "Shell"
}


FEATURE_VERSION = "github_v1"


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(value, maximum))


def log_scale(value: float, reference_value: float) -> float:
    if value <= 0:
        return 0.0

    return clamp(math.log1p(value) / math.log1p(reference_value))


def calculate_github_activity_score(profile: GitHubProfile) -> float:
    recent_push_score = clamp(profile.recent_push_count / 15)
    repo_score = clamp(profile.public_repos / 30)

    return round(
        0.70 * recent_push_score +
        0.30 * repo_score,
        4
    )


def calculate_repository_quality_score(profile: GitHubProfile) -> float:
    star_score = log_scale(profile.total_stars, 300)
    fork_score = log_scale(profile.total_forks, 100)
    follower_score = log_scale(profile.followers, 500)

    return round(
        0.50 * star_score +
        0.25 * fork_score +
        0.25 * follower_score,
        4
    )


def calculate_skill_match_score(top_languages: Optional[Dict]) -> float:
    if not top_languages:
        return 0.0

    total_language_count = sum(top_languages.values())

    if total_language_count == 0:
        return 0.0

    matched_count = 0

    for language, count in top_languages.items():
        if language in TARGET_LANGUAGES:
            matched_count += count

    return round(clamp(matched_count / total_language_count), 4)


def calculate_profile_completeness_score(candidate: Candidate, github_profile: GitHubProfile) -> float:
    checks = [
        bool(candidate.github_username),
        bool(candidate.profile_url),
        bool(candidate.location),
        github_profile.public_repos > 0,
        bool(github_profile.top_languages_json)
    ]

    return round(sum(checks) / len(checks), 4)


def calculate_stackoverflow_score(profile: Optional[StackOverflowProfile]) -> float:
    if profile is None:
        return 0.0

    reputation_score = log_scale(profile.reputation, 10000)
    answer_score = log_scale(profile.answer_count, 500)
    accepted_score = log_scale(profile.accepted_answer_count, 200)
    badge_score = log_scale(
        profile.gold_badges * 3 + profile.silver_badges * 2 + profile.bronze_badges,
        300
    )

    return round(
        0.45 * reputation_score +
        0.25 * answer_score +
        0.20 * accepted_score +
        0.10 * badge_score,
        4
    )


def calculate_overall_feature_score(
    github_activity_score: float,
    repository_quality_score: float,
    stackoverflow_score: float,
    skill_match_score: float,
    profile_completeness_score: float
) -> float:
    if stackoverflow_score > 0:
        overall_score = (
            0.25 * github_activity_score +
            0.25 * repository_quality_score +
            0.20 * stackoverflow_score +
            0.20 * skill_match_score +
            0.10 * profile_completeness_score
        )
    else:
        overall_score = (
            0.35 * github_activity_score +
            0.35 * repository_quality_score +
            0.20 * skill_match_score +
            0.10 * profile_completeness_score
        )

    return round(clamp(overall_score), 4)


def build_candidate_features(db: Session, candidate: Candidate) -> Optional[CandidateFeature]:
    github_profile = (
        db.query(GitHubProfile)
        .filter(GitHubProfile.candidate_id == candidate.id)
        .first()
    )

    if github_profile is None:
        return None

    stackoverflow_profile = (
        db.query(StackOverflowProfile)
        .filter(StackOverflowProfile.candidate_id == candidate.id)
        .first()
    )

    github_activity_score = calculate_github_activity_score(github_profile)
    repository_quality_score = calculate_repository_quality_score(github_profile)
    stackoverflow_score = calculate_stackoverflow_score(stackoverflow_profile)
    skill_match_score = calculate_skill_match_score(github_profile.top_languages_json)
    profile_completeness_score = calculate_profile_completeness_score(candidate, github_profile)

    overall_feature_score = calculate_overall_feature_score(
        github_activity_score=github_activity_score,
        repository_quality_score=repository_quality_score,
        stackoverflow_score=stackoverflow_score,
        skill_match_score=skill_match_score,
        profile_completeness_score=profile_completeness_score
    )

    feature_record = (
        db.query(CandidateFeature)
        .filter(
            CandidateFeature.candidate_id == candidate.id,
            CandidateFeature.feature_version == FEATURE_VERSION
        )
        .first()
    )

    if feature_record is None:
        feature_record = CandidateFeature(
            candidate_id=candidate.id,
            feature_version=FEATURE_VERSION
        )
        db.add(feature_record)

    feature_record.github_activity_score = github_activity_score
    feature_record.repository_quality_score = repository_quality_score
    feature_record.stackoverflow_score = stackoverflow_score
    feature_record.skill_match_score = skill_match_score
    feature_record.profile_completeness_score = profile_completeness_score
    feature_record.overall_feature_score = overall_feature_score

    audit_log = AuditLog(
        actor="system",
        action="built_candidate_features",
        entity_type="candidate",
        entity_id=candidate.id,
        details_json={
            "feature_version": FEATURE_VERSION,
            "overall_feature_score": overall_feature_score,
            "uses_stackoverflow": stackoverflow_score > 0
        }
    )
    db.add(audit_log)

    return feature_record


def build_features_for_all_candidates(db: Session) -> Dict[str, int]:
    candidates = (
        db.query(Candidate)
        .filter(Candidate.is_active == True)
        .all()
    )

    processed = 0
    skipped = 0

    for candidate in candidates:
        feature_record = build_candidate_features(db, candidate)

        if feature_record is None:
            skipped += 1
        else:
            processed += 1

    db.commit()

    return {
        "total_candidates": len(candidates),
        "processed": processed,
        "skipped": skipped
    }
