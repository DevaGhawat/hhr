from sqlalchemy.orm import Session

from app.db.models import Candidate, NotificationLog


def log_invite_notification(
    db: Session,
    candidate: Candidate,
    invite_link: str
) -> NotificationLog:
    subject = "Doodle coding challenge invitation"

    message = (
        f"Hello {candidate.display_name or candidate.github_username},\n\n"
        "You have been shortlisted for a Doodle technical coding challenge.\n"
        "Please use the temporary link below to access your coding questions:\n\n"
        f"{invite_link}\n\n"
        "This is an academic prototype notification. "
        "No real hiring email is sent from this system."
    )

    notification = NotificationLog(
        candidate_id=candidate.id,
        notification_type="coding_challenge_invite",
        channel="mock_email",
        recipient=candidate.email,
        subject=subject,
        message=message,
        status="logged"
    )

    db.add(notification)
    return notification
