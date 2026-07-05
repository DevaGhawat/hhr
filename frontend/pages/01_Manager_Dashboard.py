import sys
from pathlib import Path

import altair as alt
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
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    .dashboard-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        font-size: 1rem;
        color: #9ca3af;
        margin-bottom: 1.2rem;
    }

    .info-box {
        padding: 1rem;
        border-radius: 0.7rem;
        border: 1px solid rgba(156, 163, 175, 0.35);
        background-color: rgba(156, 163, 175, 0.08);
        margin-bottom: 1.2rem;
    }

    .section-note {
        color: #9ca3af;
        font-size: 0.92rem;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='dashboard-title'>Manager Dashboard</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='dashboard-subtitle'>Human-in-the-loop review for shortlisted candidates, coding submissions, and final decisions.</div>",
    unsafe_allow_html=True
)

db = SessionLocal()

try:
    total_candidates = db.query(Candidate).count()
    total_scores = db.query(CandidateScore).count()
    total_invites = db.query(Invite).count()
    submitted_invites = db.query(Invite).filter(Invite.status == "submitted").count()
    evaluated_invites = db.query(Invite).filter(Invite.status == "evaluated").count()
    total_submissions = db.query(CodingSubmission).count()
    total_notifications = db.query(NotificationLog).count()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Candidates", total_candidates)
    col2.metric("Scored", total_scores)
    col3.metric("Invites", total_invites)
    col4.metric("Submitted", submitted_invites)
    col5.metric("Evaluated", evaluated_invites)
    col6.metric("Notifications", total_notifications)

    st.markdown(
        """
        <div class='info-box'>
        <b>Responsible AI note:</b> Candidate scores are used only for shortlisting support.
        Final decisions are made by a human manager. Notifications are logged as mock emails,
        not sent to real candidates.
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_overview, tab_ranked, tab_review, tab_evaluations = st.tabs(
        [
            "Overview",
            "Ranked Candidates",
            "Review Submissions",
            "Completed Evaluations"
        ]
    )

    with tab_overview:
        st.subheader("Recruitment Pipeline Status")
        st.markdown(
            "<div class='section-note'>This overview shows how many candidates moved through each stage of the prototype workflow.</div>",
            unsafe_allow_html=True
        )

        pipeline_data = pd.DataFrame(
            {
                "Stage": [
                    "Collected",
                    "Scored",
                    "Invited",
                    "Submitted",
                    "Evaluated"
                ],
                "Count": [
                    total_candidates,
                    total_scores,
                    total_invites,
                    submitted_invites,
                    evaluated_invites
                ]
            }
        )

        pipeline_chart = (
            alt.Chart(pipeline_data)
            .mark_bar()
            .encode(
                x=alt.X(
                    "Stage:N",
                    sort=["Collected", "Scored", "Invited", "Submitted", "Evaluated"],
                    title="Pipeline Stage"
                ),
                y=alt.Y(
                    "Count:Q",
                    title="Count",
                    scale=alt.Scale(domainMin=0)
                ),
                tooltip=["Stage", "Count"]
            )
            .properties(height=340)
        )

        st.altair_chart(pipeline_chart, use_container_width=True)

        st.divider()

        st.subheader("Top Candidate Score Distribution")
        st.markdown(
            "<div class='section-note'>This chart shows the highest ranked candidates based on the transparent technical score.</div>",
            unsafe_allow_html=True
        )

        score_rows = (
            db.query(Candidate, CandidateScore)
            .join(CandidateScore, Candidate.id == CandidateScore.candidate_id)
            .order_by(CandidateScore.final_score.desc())
            .limit(15)
            .all()
        )

        score_data = []

        for candidate, score in score_rows:
            score_data.append(
                {
                    "GitHub": candidate.github_username,
                    "Final Score": score.final_score,
                    "Selection Probability": score.selection_probability,
                    "Rank": score.rank_position
                }
            )

        if score_data:
            score_df = pd.DataFrame(score_data)

            score_chart = (
                alt.Chart(score_df)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "GitHub:N",
                        sort="-y",
                        title="GitHub Username"
                    ),
                    y=alt.Y(
                        "Final Score:Q",
                        title="Final Score",
                        scale=alt.Scale(domainMin=0)
                    ),
                    tooltip=[
                        "Rank",
                        "GitHub",
                        "Final Score",
                        "Selection Probability"
                    ]
                )
                .properties(height=360)
            )

            st.altair_chart(score_chart, use_container_width=True)
            st.dataframe(score_df, use_container_width=True, hide_index=True)
        else:
            st.info("No score data found. Run feature engineering and scoring first.")

    with tab_ranked:
        st.subheader("Ranked Candidates")
        st.markdown(
            "<div class='section-note'>Candidates are ranked using transparent technical feature scores. This is not a final hiring decision.</div>",
            unsafe_allow_html=True
        )

        ranked_rows = (
            db.query(Candidate, CandidateScore, CandidateFeature)
            .join(CandidateScore, Candidate.id == CandidateScore.candidate_id)
            .join(CandidateFeature, Candidate.id == CandidateFeature.candidate_id)
            .order_by(CandidateScore.final_score.desc())
            .limit(30)
            .all()
        )

        ranked_data = []

        for candidate, score, feature in ranked_rows:
            ranked_data.append(
                {
                    "Rank": score.rank_position,
                    "Candidate ID": candidate.id,
                    "GitHub": candidate.github_username,
                    "Location": candidate.location,
                    "Final Score": score.final_score,
                    "Selection Probability": score.selection_probability,
                    "GitHub Activity": feature.github_activity_score,
                    "Repository Quality": feature.repository_quality_score,
                    "Skill Match": feature.skill_match_score,
                    "Profile Completeness": feature.profile_completeness_score,
                    "Profile URL": candidate.profile_url,
                }
            )

        if ranked_data:
            ranked_df = pd.DataFrame(ranked_data)

            st.dataframe(
                ranked_df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("Average Feature Contribution")

            feature_means = pd.DataFrame(
                {
                    "Feature": [
                        "GitHub Activity",
                        "Repository Quality",
                        "Skill Match",
                        "Profile Completeness"
                    ],
                    "Average Score": [
                        ranked_df["GitHub Activity"].mean(),
                        ranked_df["Repository Quality"].mean(),
                        ranked_df["Skill Match"].mean(),
                        ranked_df["Profile Completeness"].mean()
                    ]
                }
            )

            feature_chart = (
                alt.Chart(feature_means)
                .mark_bar()
                .encode(
                    x=alt.X("Feature:N", title="Feature"),
                    y=alt.Y(
                        "Average Score:Q",
                        title="Average Score",
                        scale=alt.Scale(domainMin=0)
                    ),
                    tooltip=["Feature", "Average Score"]
                )
                .properties(height=320)
            )

            st.altair_chart(feature_chart, use_container_width=True)

        else:
            st.warning("No ranked candidates found. Run feature engineering and scoring first.")

    with tab_review:
        st.subheader("Submitted Challenges Waiting for Review")
        st.markdown(
            "<div class='section-note'>The manager reviews submitted code manually and stores the final decision.</div>",
            unsafe_allow_html=True
        )

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

            selected_invite = (
                db.query(Invite)
                .filter(Invite.id == selected_invite_id)
                .first()
            )

            selected_candidate = selected_invite.candidate

            st.markdown("### Candidate Summary")

            c1, c2, c3 = st.columns(3)
            c1.metric("Candidate ID", selected_candidate.id)
            c2.metric("Invite ID", selected_invite.id)
            c3.metric("Status", selected_invite.status)

            st.markdown(f"**Candidate:** {selected_candidate.display_name or selected_candidate.github_username}")
            st.markdown(f"**GitHub:** `{selected_candidate.github_username}`")
            st.markdown(f"**Profile:** {selected_candidate.profile_url}")

            submissions = (
                db.query(CodingSubmission)
                .filter(CodingSubmission.invite_id == selected_invite_id)
                .order_by(CodingSubmission.question_id.asc())
                .all()
            )

            st.markdown("### Submitted Answers")

            for submission in submissions:
                with st.expander(f"Question {submission.question_id} answer", expanded=False):
                    st.markdown(f"**Language:** {submission.language}")
                    st.markdown(f"**Submitted at:** {submission.submitted_at}")
                    st.code(
                        submission.submitted_code,
                        language=submission.language if submission.language == "python" else None
                    )

            st.markdown("### Manager Evaluation")

            with st.form("manager_evaluation_form"):
                technical_score = st.slider(
                    "Technical correctness score",
                    min_value=0.0,
                    max_value=10.0,
                    value=7.0,
                    step=0.5
                )

                code_quality_score = st.slider(
                    "Code quality score",
                    min_value=0.0,
                    max_value=10.0,
                    value=7.0,
                    step=0.5
                )

                communication_score = st.slider(
                    "Explanation / communication score",
                    min_value=0.0,
                    max_value=10.0,
                    value=7.0,
                    step=0.5
                )

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

    with tab_evaluations:
        st.subheader("Completed Manager Evaluations")

        evaluation_rows = (
            db.query(ManagerEvaluation, Candidate)
            .join(Candidate, ManagerEvaluation.candidate_id == Candidate.id)
            .order_by(ManagerEvaluation.evaluated_at.desc())
            .all()
        )

        evaluation_data = []

        for evaluation, candidate in evaluation_rows:
            evaluation_data.append(
                {
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
                }
            )

        if evaluation_data:
            evaluation_df = pd.DataFrame(evaluation_data)
            st.dataframe(
                evaluation_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No completed manager evaluations yet.")

finally:
    db.close()