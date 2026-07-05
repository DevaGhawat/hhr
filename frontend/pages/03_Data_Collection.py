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
    GitHubProfile,
    Invite,
    NotificationLog,
)


st.set_page_config(
    page_title="Data Collection",
    page_icon="📥",
    layout="wide"
)

st.markdown(
    """
    <style>
    .page-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .page-subtitle {
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

st.markdown("<div class='page-title'>Data Collection Overview</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='page-subtitle'>Real public GitHub profile signals collected for the academic recruitment prototype.</div>",
    unsafe_allow_html=True
)

db = SessionLocal()

try:
    candidate_count = db.query(Candidate).count()
    github_profile_count = db.query(GitHubProfile).count()
    feature_count = db.query(CandidateFeature).count()
    score_count = db.query(CandidateScore).count()
    invite_count = db.query(Invite).count()
    notification_count = db.query(NotificationLog).count()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Candidates", candidate_count)
    col2.metric("GitHub Profiles", github_profile_count)
    col3.metric("Feature Rows", feature_count)
    col4.metric("Score Rows", score_count)
    col5.metric("Invites", invite_count)
    col6.metric("Notifications", notification_count)

    st.markdown(
        """
        <div class='info-box'>
        <b>Data source note:</b> This prototype uses public GitHub API data only.
        Private repositories, private emails, demographic attributes, and sensitive personal data are not collected.
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_summary, tab_profiles, tab_features, tab_commands = st.tabs(
        [
            "Collection Summary",
            "GitHub Profiles",
            "Feature Signals",
            "Pipeline Commands"
        ]
    )

    with tab_summary:
        st.subheader("Collection Pipeline Status")
        st.markdown(
            "<div class='section-note'>This shows how raw public GitHub data moves into engineered features and candidate scores.</div>",
            unsafe_allow_html=True
        )

        pipeline_data = pd.DataFrame(
            {
                "Stage": [
                    "Candidates",
                    "GitHub Profiles",
                    "Feature Rows",
                    "Score Rows",
                    "Invites"
                ],
                "Count": [
                    candidate_count,
                    github_profile_count,
                    feature_count,
                    score_count,
                    invite_count
                ]
            }
        )

        pipeline_chart = (
            alt.Chart(pipeline_data)
            .mark_bar()
            .encode(
                x=alt.X(
                    "Stage:N",
                    sort=[
                        "Candidates",
                        "GitHub Profiles",
                        "Feature Rows",
                        "Score Rows",
                        "Invites"
                    ],
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

        st.subheader("What Data Is Collected?")

        collected_fields = pd.DataFrame(
            [
                {
                    "Category": "Identity",
                    "Fields": "GitHub username, profile URL",
                    "Purpose": "Candidate profile reference"
                },
                {
                    "Category": "Repository Activity",
                    "Fields": "Public repos, recent push count",
                    "Purpose": "Technical activity signal"
                },
                {
                    "Category": "Repository Quality",
                    "Fields": "Stars, forks, followers",
                    "Purpose": "Public technical visibility signal"
                },
                {
                    "Category": "Skills",
                    "Fields": "Top programming languages",
                    "Purpose": "Skill match estimation"
                },
                {
                    "Category": "Privacy",
                    "Fields": "No private email, no private repos, no demographic attributes",
                    "Purpose": "Data minimisation"
                }
            ]
        )

        st.dataframe(collected_fields, use_container_width=True, hide_index=True)

    with tab_profiles:
        st.subheader("GitHub Profile Records")
        st.markdown(
            "<div class='section-note'>These are public GitHub profile statistics stored in the local SQLite database.</div>",
            unsafe_allow_html=True
        )

        rows = (
            db.query(Candidate, GitHubProfile)
            .join(GitHubProfile, Candidate.id == GitHubProfile.candidate_id)
            .order_by(GitHubProfile.followers.desc())
            .limit(50)
            .all()
        )

        profile_data = []

        for candidate, profile in rows:
            profile_data.append(
                {
                    "Candidate ID": candidate.id,
                    "GitHub": candidate.github_username,
                    "Display Name": candidate.display_name,
                    "Location": candidate.location,
                    "Public Repos": profile.public_repos,
                    "Followers": profile.followers,
                    "Total Stars": profile.total_stars,
                    "Total Forks": profile.total_forks,
                    "Recent Push Count": profile.recent_push_count,
                    "Top Languages": profile.top_languages_json,
                    "Profile URL": candidate.profile_url,
                }
            )

        if profile_data:
            profile_df = pd.DataFrame(profile_data)

            st.dataframe(profile_df, use_container_width=True, hide_index=True)

            st.divider()

            st.subheader("Followers vs Repository Stars")

            scatter_chart = (
                alt.Chart(profile_df)
                .mark_circle(size=90)
                .encode(
                    x=alt.X("Followers:Q", title="Followers"),
                    y=alt.Y("Total Stars:Q", title="Total Stars"),
                    tooltip=[
                        "GitHub",
                        "Followers",
                        "Total Stars",
                        "Public Repos",
                        "Recent Push Count"
                    ]
                )
                .properties(height=360)
            )

            st.altair_chart(scatter_chart, use_container_width=True)

        else:
            st.warning("No GitHub profiles found. Run the GitHub collection script first.")

    with tab_features:
        st.subheader("Engineered Feature Signals")
        st.markdown(
            "<div class='section-note'>Raw GitHub signals are converted into interpretable feature scores used by the ranking model.</div>",
            unsafe_allow_html=True
        )

        feature_rows = (
            db.query(Candidate, CandidateFeature, CandidateScore)
            .join(CandidateFeature, Candidate.id == CandidateFeature.candidate_id)
            .join(CandidateScore, Candidate.id == CandidateScore.candidate_id)
            .order_by(CandidateScore.final_score.desc())
            .limit(50)
            .all()
        )

        feature_data = []

        for candidate, feature, score in feature_rows:
            feature_data.append(
                {
                    "Rank": score.rank_position,
                    "GitHub": candidate.github_username,
                    "GitHub Activity": feature.github_activity_score,
                    "Repository Quality": feature.repository_quality_score,
                    "StackOverflow Score": feature.stackoverflow_score,
                    "Skill Match": feature.skill_match_score,
                    "Profile Completeness": feature.profile_completeness_score,
                    "Overall Feature Score": feature.overall_feature_score,
                    "Final Score": score.final_score,
                }
            )

        if feature_data:
            feature_df = pd.DataFrame(feature_data)

            st.dataframe(feature_df, use_container_width=True, hide_index=True)

            st.divider()

            st.subheader("Average Feature Scores")

            feature_means = pd.DataFrame(
                {
                    "Feature": [
                        "GitHub Activity",
                        "Repository Quality",
                        "StackOverflow Score",
                        "Skill Match",
                        "Profile Completeness"
                    ],
                    "Average Score": [
                        feature_df["GitHub Activity"].mean(),
                        feature_df["Repository Quality"].mean(),
                        feature_df["StackOverflow Score"].mean(),
                        feature_df["Skill Match"].mean(),
                        feature_df["Profile Completeness"].mean()
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
                .properties(height=340)
            )

            st.altair_chart(feature_chart, use_container_width=True)

            st.info(
                "StackOverflow score is currently zero because StackOverflow API integration is planned but not implemented yet."
            )

        else:
            st.warning("No feature records found. Run feature engineering and scoring first.")

    with tab_commands:
        st.subheader("Reproducible Pipeline Commands")
        st.markdown(
            "<div class='section-note'>These commands reproduce the full data collection and scoring pipeline from the terminal.</div>",
            unsafe_allow_html=True
        )

        st.code(
            """
python scripts/create_database.py
python scripts/collect_github_candidates.py --limit 30
python scripts/run_feature_engineering.py
python scripts/run_scoring.py
python scripts/run_selection.py --pool-size 15 --select-count 5 --minimum-score 0.40
python -m app.db.seed_questions
streamlit run frontend/streamlit_app.py
            """,
            language="powershell"
        )

        st.subheader("Current Data Limitation")

        st.warning(
            "GitHub data is only a proxy for technical ability. "
            "Some strong developers work in private repositories or closed-source environments. "
            "Therefore, the score should only support shortlisting and must not be used as a final hiring decision."
        )

finally:
    db.close()