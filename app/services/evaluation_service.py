from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Session

from app.db.models import (
    AuditLog,
    Invite,
    ManagerEvaluation,
    NotificationLog,
)


def evaluate_candidate_submission(
    db: Session,
    invite_id: int,
    technical_score: float,
    code_quality_score: float,
    communication_score: float,
    final_decision: str,
    feedback: str,
    evaluated_by: str = "Doodle hiring manager"
) -> Dict:
    invite = db.query(Invite).filter(Invite.id == invite_id).first()

    if invite is None:
        return {
            "success": False,
            "message": "Invite not found."
        }

    if invite.status != "submitted":
        return {
            "success": False,
            "message": "This invite has not been submitted yet."
        }

    evaluation = (
        db.query(ManagerEvaluation)
        .filter(ManagerEvaluation.invite_id == invite.id)
        .first()
    )

    if evaluation is None:
        evaluation = ManagerEvaluation(
            candidate_id=invite.candidate_id,
            invite_id=invite.id
        )
        db.add(evaluation)

    evaluation.technical_score = technical_score
    evaluation.code_quality_score = code_quality_score
    evaluation.communication_score = communication_score
    evaluation.final_decision = final_decision
    evaluation.feedback = feedback
    evaluation.evaluated_by = evaluated_by
    evaluation.evaluated_at = datetime.utcnow()

    invite.status = "evaluated"

    notification = NotificationLog(
        candidate_id=invite.candidate_id,
        notification_type="final_result",
        channel="mock_email",
        recipient=invite.candidate.email,
        subject="Doodle coding challenge result",
        message=(
            f"Hello {invite.candidate.display_name or invite.candidate.github_username},\n\n"
            f"Your coding challenge has been reviewed.\n\n"
            f"Final decision: {final_decision}\n\n"
            f"Feedback:\n{feedback}\n\n"
            "This is an academic prototype notification. No real hiring email is sent."
        ),
        status="logged"
    )
    db.add(notification)

    audit_log = AuditLog(
        actor=evaluated_by,
        action="evaluated_candidate_submission",
        entity_type="invite",
        entity_id=invite.id,
        details_json={
            "candidate_id": invite.candidate_id,
            "technical_score": technical_score,
            "code_quality_score": code_quality_score,
            "communication_score": communication_score,
            "final_decision": final_decision
        }
    )
    db.add(audit_log)

    db.commit()

    return {
        "success": True,
        "message": "Candidate evaluation saved successfully.",
        "invite_id": invite.id,
        "candidate_id": invite.candidate_id,
        "final_decision": final_decision
    }
