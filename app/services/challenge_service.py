from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.security import hash_token
from app.db.models import AuditLog, CodingQuestion, CodingSubmission, Invite


def validate_invite_token(db: Session, token: str) -> Tuple[Optional[Invite], Optional[str]]:
    if not token:
        return None, "Missing invite token."

    token_hash = hash_token(token)

    invite = (
        db.query(Invite)
        .filter(Invite.token_hash == token_hash)
        .first()
    )

    if invite is None:
        return None, "Invalid invite token."

    if invite.expires_at < datetime.utcnow():
        invite.status = "expired"
        db.commit()
        return None, "This invite link has expired."

    if invite.status == "submitted":
        return None, "This challenge has already been submitted."

    return invite, None


def get_active_questions(db: Session, limit: int = 3) -> List[CodingQuestion]:
    return (
        db.query(CodingQuestion)
        .filter(CodingQuestion.is_active == True)
        .order_by(CodingQuestion.id.asc())
        .limit(limit)
        .all()
    )


def submit_candidate_solutions(
    db: Session,
    token: str,
    answers_by_question_id: Dict[int, str],
    language: str = "python"
) -> Dict:
    invite, error = validate_invite_token(db, token)

    if error:
        return {
            "success": False,
            "message": error
        }

    questions = get_active_questions(db, limit=3)

    if len(questions) < 3:
        return {
            "success": False,
            "message": "Challenge is not configured correctly. Three active questions are required."
        }

    missing_answers = []

    for question in questions:
        answer = answers_by_question_id.get(question.id, "").strip()
        if not answer:
            missing_answers.append(question.id)

    if missing_answers:
        return {
            "success": False,
            "message": f"Please answer all questions. Missing question IDs: {missing_answers}"
        }

    for question in questions:
        submission = CodingSubmission(
            invite_id=invite.id,
            question_id=question.id,
            submitted_code=answers_by_question_id[question.id].strip(),
            language=language
        )
        db.add(submission)

    invite.status = "submitted"

    audit_log = AuditLog(
        actor="candidate",
        action="submitted_coding_challenge",
        entity_type="invite",
        entity_id=invite.id,
        details_json={
            "candidate_id": invite.candidate_id,
            "question_count": len(questions),
            "language": language
        }
    )
    db.add(audit_log)

    db.commit()

    return {
        "success": True,
        "message": "Challenge submitted successfully.",
        "invite_id": invite.id,
        "candidate_id": invite.candidate_id
    }
