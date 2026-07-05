from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from app.db.models import AuditLog, Candidate, CandidateFeature, CandidateScore


SCORING_VERSION = "transparent_rank_score_v1"


def calculate_final_score(features: CandidateFeature) -> Tuple[float, Dict]:
    github_component = 0.30 * features.github_activity_score
    repo_component = 0.30 * features.repository_quality_score
    stackoverflow_component = 0.15 * features.stackoverflow_score
    skill_component = 0.15 * features.skill_match_score
    completeness_component = 0.10 * features.profile_completeness_score

    raw_score = (
        github_component
        + repo_component
        + stackoverflow_component
        + skill_component
        + completeness_component
    )

    missing_stackoverflow_penalty = 0.03 if features.stackoverflow_score == 0 else 0.0
    final_score = max(0.0, min(raw_score - missing_stackoverflow_penalty, 1.0))

    explanation = {
        "scoring_version": SCORING_VERSION,
        "components": {
            "github_activity_component": round(github_component, 4),
            "repository_quality_component": round(repo_component, 4),
            "stackoverflow_component": round(stackoverflow_component, 4),
            "skill_match_component": round(skill_component, 4),
            "profile_completeness_component": round(completeness_component, 4),
            "missing_stackoverflow_penalty": missing_stackoverflow_penalty
        },
        "raw_score": round(raw_score, 4),
        "final_score": round(final_score, 4),
        "interpretation": (
            "This score is a transparent technical ranking score, not an automated hiring decision."
        )
    }

    return round(final_score, 4), explanation


def score_all_candidates(db: Session) -> Dict[str, int]:
    rows: List[Tuple[Candidate, CandidateFeature]] = (
        db.query(Candidate, CandidateFeature)
        .join(CandidateFeature, Candidate.id == CandidateFeature.candidate_id)
        .filter(Candidate.is_active == True)
        .all()
    )

    scored_records = []

    for candidate, features in rows:
        final_score, explanation = calculate_final_score(features)

        score_record = (
            db.query(CandidateScore)
            .filter(
                CandidateScore.candidate_id == candidate.id,
                CandidateScore.scoring_version == SCORING_VERSION
            )
            .first()
        )

        if score_record is None:
            score_record = CandidateScore(
                candidate_id=candidate.id,
                scoring_version=SCORING_VERSION
            )
            db.add(score_record)

        score_record.final_score = final_score
        score_record.selection_probability = 0.0
        score_record.explanation_json = explanation

        scored_records.append(score_record)

    scored_records.sort(key=lambda record: record.final_score, reverse=True)

    for rank_position, score_record in enumerate(scored_records, start=1):
        score_record.rank_position = rank_position

    audit_log = AuditLog(
        actor="system",
        action="scored_all_candidates",
        entity_type="candidate_score",
        entity_id=None,
        details_json={
            "scoring_version": SCORING_VERSION,
            "candidate_count": len(scored_records)
        }
    )
    db.add(audit_log)

    db.commit()

    return {
        "total_candidates_with_features": len(rows),
        "scored_candidates": len(scored_records)
    }


def get_ranked_candidates(db: Session, limit: int = 20):
    return (
        db.query(Candidate, CandidateScore)
        .join(CandidateScore, Candidate.id == CandidateScore.candidate_id)
        .filter(CandidateScore.scoring_version == SCORING_VERSION)
        .order_by(CandidateScore.final_score.desc())
        .limit(limit)
        .all()
    )
