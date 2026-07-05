import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from app.db.database import SessionLocal
from app.db.models import (
    Candidate,
    CandidateFeature,
    CandidateScore,
    CodingSubmission,
    Invite,
    ManagerEvaluation,
    NotificationLog,
)
from app.services.evaluation_service import evaluate_candidate_submission


st.set_page_config(
    page_title="Manager Dashboard",
    page_icon="??",
    layout="wide"
)

st.title("Manager Dashboard")
st.caption("Human review layer for shortlisted candidates and coding submissions.")

db = SessionLocal()

try:
    total_candidates = db.query(Candidate).count()
    total_scores = db.query(CandidateScore).count()
    total_invites = db.query(Invite).count()
    submitted_invites = db.query(Invite).filter(Invite.status == "submitted").count()
    evaluated_invites = db.query(Invite).filter(Invite.status == "evaluated").count()
    total_submissions = db.query(CodingSubmission).count()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Candidates", total_candidates)
    col2.metric("Scored", total_scores)
    col3.metric("Invites", total_invites)
    col4.metric("Submitted", submitted_invites)
    col5.metric("Evaluated", evaluated_invites)
    col6.metric("Submissions", total_submissions)

    st.divider()

    st.subheader("Top Ranked Candidates")

    ranked_rows = (
        db.query(Candidate, CandidateScore, CandidateFeature)
        .join(CandidateScore, Candidate.id == CandidateScore.candidate_id)
        .join(CandidateFeature, Candidate.id == CandidateFeature.candidate_id)
        .order_by(CandidateScore.final_score.desc())
        .limit(20)
        .all()
    )

    ranked_data = []

    for candidate, score, feature in ranked_rows:
        ranked_data.append({
            "Rank": score.rank_position,
            "Candidate ID": candidate.id,
            "GitHub": candidate.github_username,
            "Location": candidate.location,
            "Final Score": score.final_score,
            "Selection Probability": score.selection_probability,
            "GitHub Activity": feature.github_activity_score,
            "Repo Quality": feature.repository_quality_score,
            "Skill Match": feature.skill_match_score,
            "Profile Complete": feature.profile_completeness_score,
            "Profile URL": candidate.profile_url,
        })

    if ranked_data:
        st.dataframe(pd.DataFrame(ranked_data), use_container_width=True)
    else:
        st.warning("No scored candidates found.")

    st.divider()

    st.subheader("Submitted Challenges Waiting for Manager Review")

    submitted_rows = (
        db.query(Invite, Candidate)
        .join(Candidate, Invite.candidate_id == Candidate.id)
        .filter(Invite.status == "submitted")
        .order_by(Invite.id.desc())
        .all()
    )

    if not submitted_rows:
        st.info("No submitted challenges waiting for review.")
    else:
        invite_options = {
            f"Invite {invite.id} | {candidate.github_username} | Candidate ID {candidate.id}": invite.id
            for invite, candidate in submitted_rows
        }

        selected_label = st.selectbox(
            "Select submitted challenge",
            options=list(invite_options.keys())
        )

        selected_invite_id = invite_options[selected_label]

        selected_invite = db.query(Invite).filter(Invite.id == selected_invite_id).first()
        selected_candidate = selected_invite.candidate

        st.markdown(f"**Candidate:** {selected_candidate.display_name or selected_candidate.github_username}")
        st.markdown(f"**GitHub:** `{selected_candidate.github_username}`")
        st.markdown(f"**Invite ID:** {selected_invite.id}")

        submissions = (
            db.query(CodingSubmission)
            .filter(CodingSubmission.invite_id == selected_invite_id)
            .order_by(CodingSubmission.question_id.asc())
            .all()
        )

        st.markdown("### Submitted Answers")

        for submission in submissions:
            with st.expander(f"Question {submission.question_id} answer"):
                st.markdown(f"**Language:** {submission.language}")
                st.markdown(f"**Submitted at:** {submission.submitted_at}")
                st.code(
                    submission.submitted_code,
                    language=submission.language if submission.language == "python" else None
                )

        st.markdown("### Manager Evaluation")

        with st.form("manager_evaluation_form"):
            technical_score = st.slider("Technical correctness score", 0.0, 10.0, 7.0, 0.5)
            code_quality_score = st.slider("Code quality score", 0.0, 10.0, 7.0, 0.5)
            communication_score = st.slider("Explanation / communication score", 0.0, 10.0, 7.0, 0.5)

            final_decision = st.selectbox(
                "Final decision",
                options=[
                    "selected_for_interview",
                    "needs_manual_follow_up",
                    "rejected"
                ]
            )

            feedback = st.text_area(
                "Manager feedback",
                height=160,
                placeholder="Write clear feedback for the candidate."
            )

            evaluated_by = st.text_input(
                "Evaluated by",
                value="Doodle hiring manager"
            )

            submitted = st.form_submit_button("Save evaluation and log result notification")

        if submitted:
            if not feedback.strip():
                st.error("Feedback is required.")
            else:
                result = evaluate_candidate_submission(
                    db=db,
                    invite_id=selected_invite_id,
                    technical_score=technical_score,
                    code_quality_score=code_quality_score,
                    communication_score=communication_score,
                    final_decision=final_decision,
                    feedback=feedback,
                    evaluated_by=evaluated_by
                )

                if result["success"]:
                    st.success(result["message"])
                    st.info("Mock result notification has been logged.")
                    st.rerun()
                else:
                    st.error(result["message"])

    st.divider()

    st.subheader("Completed Evaluations")

    evaluation_rows = (
        db.query(ManagerEvaluation, Candidate)
        .join(Candidate, ManagerEvaluation.candidate_id == Candidate.id)
        .order_by(ManagerEvaluation.evaluated_at.desc())
        .all()
    )

    evaluation_data = []

    for evaluation, candidate in evaluation_rows:
        evaluation_data.append({
            "Evaluation ID": evaluation.id,
            "Candidate ID": candidate.id,
            "GitHub": candidate.github_username,
            "Invite ID": evaluation.invite_id,
            "Technical": evaluation.technical_score,
            "Code Quality": evaluation.code_quality_score,
            "Communication": evaluation.communication_score,
            "Decision": evaluation.final_decision,
            "Evaluated By": evaluation.evaluated_by,
            "Evaluated At": evaluation.evaluated_at,
            "Feedback": evaluation.feedback,
        })

    if evaluation_data:
        st.dataframe(pd.DataFrame(evaluation_data), use_container_width=True)
    else:
        st.info("No completed manager evaluations yet.")

finally:
    db.close()
