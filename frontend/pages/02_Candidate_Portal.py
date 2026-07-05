import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from app.db.database import SessionLocal
from app.services.challenge_service import (
    get_active_questions,
    submit_candidate_solutions,
    validate_invite_token
)


st.set_page_config(
    page_title="Candidate Portal",
    page_icon="??",
    layout="wide"
)

st.title("Candidate Coding Challenge Portal")

token = st.query_params.get("token", "")

if isinstance(token, list):
    token = token[0] if token else ""

if not token:
    st.error("Missing invite token. Open this page using the invite link.")
    st.stop()

db = SessionLocal()

try:
    invite, error = validate_invite_token(db, token)

    if error:
        st.error(error)
        st.stop()

    candidate = invite.candidate

    st.success("Invite verified.")
    st.markdown(f"**Candidate ID:** {candidate.id}")
    st.markdown(f"**Candidate:** {candidate.display_name or candidate.github_username}")
    st.markdown(f"**GitHub:** `{candidate.github_username}`")
    st.markdown(f"**Expires at:** {invite.expires_at}")

    questions = get_active_questions(db, limit=3)

    if len(questions) < 3:
        st.error("Challenge setup error: three active questions are required.")
        st.stop()

    st.divider()
    st.subheader("Coding Questions")

    with st.form("candidate_submission_form"):
        answers = {}

        for index, question in enumerate(questions, start=1):
            st.markdown(f"### Question {index}: {question.title}")
            st.markdown(f"**Difficulty:** {question.difficulty}")
            st.write(question.description)

            if question.expected_concepts:
                st.caption(f"Expected concepts: {question.expected_concepts}")

            answers[question.id] = st.text_area(
                label=f"Your answer for question {index}",
                height=220,
                key=f"answer_{question.id}"
            )

            st.divider()

        language = st.selectbox(
            "Submission language",
            options=["python", "pseudocode", "java", "javascript", "other"],
            index=0
        )

        submitted = st.form_submit_button("Submit challenge")

    if submitted:
        result = submit_candidate_solutions(
            db=db,
            token=token,
            answers_by_question_id=answers,
            language=language
        )

        if result["success"]:
            st.success(result["message"])
            st.info("Your submission has been stored for manager review.")
        else:
            st.error(result["message"])

finally:
    db.close()
