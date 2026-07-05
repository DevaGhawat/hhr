import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_invite_token, hash_token
from app.db.models import AuditLog, Candidate, CandidateScore, Invite
from app.services.notification_service import log_invite_notification
from app.services.scoring_service import SCORING_VERSION


def weighted_sample_without_replacement(
    items: List[Dict],
    sample_size: int,
    seed: Optional[int] = None
) -> List[Dict]:
    rng = random.Random(seed)
    available_items = items.copy()
    selected_items = []

    while available_items and len(selected_items) < sample_size:
        total_weight = sum(item["weight"] for item in available_items)

        if total_weight <= 0:
            break

        pick = rng.uniform(0, total_weight)
        cumulative = 0.0

        for index, item in enumerate(available_items):
            cumulative += item["weight"]

            if cumulative >= pick:
                selected_items.append(item)
                available_items.pop(index)
                break

    return selected_items


def select_candidates_for_challenge(
    db: Session,
    pool_size: int = 15,
    select_count: int = 5,
    minimum_score: float = 0.40,
    seed: Optional[int] = None
) -> Dict:
    ranked_rows = (
        db.query(Candidate, CandidateScore)
        .join(CandidateScore, Candidate.id == CandidateScore.candidate_id)
        .filter(CandidateScore.scoring_version == SCORING_VERSION)
        .filter(CandidateScore.final_score >= minimum_score)
        .order_by(CandidateScore.final_score.desc())
        .limit(pool_size)
        .all()
    )

    if not ranked_rows:
        return {
            "candidate_pool_size": 0,
            "selected_count": 0,
            "selected": []
        }

    pool_items = []

    for candidate, score in ranked_rows:
        pool_items.append({
            "candidate": candidate,
            "score_record": score,
            "weight": max(score.final_score, 0.001)
        })

    total_weight = sum(item["weight"] for item in pool_items)

    for item in pool_items:
        probability = item["weight"] / total_weight
        item["score_record"].selection_probability = round(probability, 4)

    selected_items = weighted_sample_without_replacement(
        items=pool_items,
        sample_size=select_count,
        seed=seed
    )

    selected_output = []

    for item in selected_items:
        candidate = item["candidate"]
        score_record = item["score_record"]

        token = generate_invite_token()
        token_hash = hash_token(token)
        expires_at = datetime.utcnow() + timedelta(hours=settings.invite_expiry_hours)

        invite = Invite(
            candidate_id=candidate.id,
            token_hash=token_hash,
            expires_at=expires_at,
            status="created"
        )
        db.add(invite)
        db.flush()

        invite_link = f"http://localhost:8501/Candidate_Portal?token={token}"

        log_invite_notification(
            db=db,
            candidate=candidate,
            invite_link=invite_link
        )

        audit_log = AuditLog(
            actor="system",
            action="selected_candidate_for_challenge",
            entity_type="candidate",
            entity_id=candidate.id,
            details_json={
                "candidate_id": candidate.id,
                "github_username": candidate.github_username,
                "final_score": score_record.final_score,
                "selection_probability": score_record.selection_probability,
                "invite_id": invite.id,
                "expires_at": expires_at.isoformat(),
                "selection_method": "weighted_probability_without_replacement"
            }
        )
        db.add(audit_log)

        selected_output.append({
            "candidate_id": candidate.id,
            "github_username": candidate.github_username,
            "final_score": score_record.final_score,
            "selection_probability": score_record.selection_probability,
            "invite_id": invite.id,
            "invite_link": invite_link,
            "expires_at": expires_at.isoformat()
        })

    db.commit()

    return {
        "candidate_pool_size": len(pool_items),
        "selected_count": len(selected_output),
        "selected": selected_output
    }
