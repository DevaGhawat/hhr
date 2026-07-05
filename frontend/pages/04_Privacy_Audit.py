import sys
from datetime import datetime
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from app.db.database import SessionLocal
from app.db.models import (
    AuditLog,
    Candidate,
    CodingSubmission,
    Invite,
    ManagerEvaluation,
    NotificationLog,
    PrivacyRequest,
)


st.set_page_config(
    page_title="Privacy Audit",
    page_icon="🛡️",
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

    .warning-box {
        padding: 1rem;
        border-radius: 0.7rem;
        border: 1px solid rgba(245, 158, 11, 0.45);
        background-color: rgba(245, 158, 11, 0.10);
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

st.markdown("<div class='page-title'>Privacy Audit</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='page-subtitle'>Governance, privacy controls, auditability, and responsible AI checks for the recruitment prototype.</div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class='warning-box'>
    <b>Important:</b> This is an academic prototype. It uses public GitHub profile signals only,
    logs mock notifications instead of sending real emails, and keeps the final decision with a human manager.
    It must not be used for real hiring decisions without consent, legal review, fairness testing, and stronger security controls.
    </div>
    """,
    unsafe_allow_html=True
)

db = SessionLocal()

try:
    candidate_count = db.query(Candidate).count()
    invite_count = db.query(Invite).count()
    submission_count = db.query(CodingSubmission).count()
    evaluation_count = db.query(ManagerEvaluation).count()
    notification_count = db.query(NotificationLog).count()
    audit_count = db.query(AuditLog).count()
    privacy_request_count = db.query(PrivacyRequest).count()

    expired_invites = (
        db.query(Invite)
        .filter(Invite.expires_at < datetime.utcnow())
        .count()
    )

    active_or_created_invites = (
        db.query(Invite)
        .filter(Invite.status == "created")
        .count()
    )

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Candidates", candidate_count)
    col2.metric("Invites", invite_count)
    col3.metric("Submissions", submission_count)
    col4.metric("Evaluations", evaluation_count)
    col5.metric("Notifications", notification_count)
    col6.metric("Audit Logs", audit_count)

    st.markdown(
        """
        <div class='info-box'>
        <b>Privacy design summary:</b> The system avoids private data collection, stores invite token hashes,
        uses expiring challenge links, logs every important action, and requires human review before any final decision.
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_controls, tab_data, tab_invites, tab_audit, tab_limitations = st.tabs(
        [
            "Privacy Controls",
            "Data Minimisation",
            "Invite Governance",
            "Audit Logs",
            "Limitations"
        ]
    )

    with tab_controls:
        st.subheader("Responsible AI Control Checklist")
        st.markdown(
            "<div class='section-note'>These controls reduce privacy and ethical risk in the recruitment workflow.</div>",
            unsafe_allow_html=True
        )

        controls = pd.DataFrame(
            [
                {
                    "Control": "Public data only",
                    "Status": "Implemented",
                    "Reason": "Uses public GitHub profile statistics, not private repositories."
                },
                {
                    "Control": "No real emails",
                    "Status": "Implemented",
                    "Reason": "Notifications are stored as mock logs only."
                },
                {
                    "Control": "Human final decision",
                    "Status": "Implemented",
                    "Reason": "Manager evaluates submissions manually."
                },
                {
                    "Control": "Token hashing",
                    "Status": "Implemented",
                    "Reason": "Raw invite tokens are not stored."
                },
                {
                    "Control": "Invite expiry",
                    "Status": "Implemented",
                    "Reason": "Challenge links expire after a configured time."
                },
                {
                    "Control": "Audit logging",
                    "Status": "Implemented",
                    "Reason": "Key system actions are logged."
                },
                {
                    "Control": "Manager authentication",
                    "Status": "Planned",
                    "Reason": "Needed for production-level access control."
                },
                {
                    "Control": "Consent workflow",
                    "Status": "Planned",
                    "Reason": "Required before real recruitment use."
                },
                {
                    "Control": "Fairness analysis",
                    "Status": "Planned",
                    "Reason": "Needed before any real-world hiring deployment."
                }
            ]
        )

        st.dataframe(controls, use_container_width=True, hide_index=True)

        status_counts = (
            controls["Status"]
            .value_counts()
            .reset_index()
        )
        status_counts.columns = ["Status", "Count"]

        control_chart = (
            alt.Chart(status_counts)
            .mark_bar()
            .encode(
                x=alt.X("Status:N", title="Control Status"),
                y=alt.Y("Count:Q", title="Count", scale=alt.Scale(domainMin=0)),
                tooltip=["Status", "Count"]
            )
            .properties(height=320)
        )

        st.altair_chart(control_chart, use_container_width=True)

    with tab_data:
        st.subheader("Data Minimisation Table")
        st.markdown(
            "<div class='section-note'>Only fields needed for the academic prototype are stored.</div>",
            unsafe_allow_html=True
        )

        data_minimisation = pd.DataFrame(
            [
                {
                    "Data Field": "GitHub username",
                    "Purpose": "Identify public technical profile",
                    "Risk Level": "Medium",
                    "Mitigation": "Used only for academic prototype and public profile reference."
                },
                {
                    "Data Field": "Profile URL",
                    "Purpose": "Allow manager to inspect public profile",
                    "Risk Level": "Medium",
                    "Mitigation": "Only public URL is stored."
                },
                {
                    "Data Field": "Repository statistics",
                    "Purpose": "Estimate technical activity and repository quality",
                    "Risk Level": "Medium",
                    "Mitigation": "Aggregate statistics only; no private repository data."
                },
                {
                    "Data Field": "Top programming languages",
                    "Purpose": "Estimate skill match",
                    "Risk Level": "Low",
                    "Mitigation": "Stored as aggregate language counts."
                },
                {
                    "Data Field": "Email",
                    "Purpose": "Notification in production",
                    "Risk Level": "High",
                    "Mitigation": "Not collected from GitHub; mock notifications only."
                },
                {
                    "Data Field": "Invite token",
                    "Purpose": "Temporary challenge access",
                    "Risk Level": "Medium",
                    "Mitigation": "Raw token not stored; only hash is stored."
                },
                {
                    "Data Field": "Coding submission",
                    "Purpose": "Manager technical review",
                    "Risk Level": "Medium",
                    "Mitigation": "Manual review only; no automatic execution."
                },
                {
                    "Data Field": "Manager feedback",
                    "Purpose": "Final evaluation record",
                    "Risk Level": "Medium",
                    "Mitigation": "Stored locally for prototype demonstration."
                }
            ]
        )

        st.dataframe(data_minimisation, use_container_width=True, hide_index=True)

        st.divider()

        st.subheader("Data Not Collected")

        not_collected = pd.DataFrame(
            [
                {"Not Collected": "Private repositories"},
                {"Not Collected": "Private email addresses"},
                {"Not Collected": "Private messages"},
                {"Not Collected": "Demographic attributes"},
                {"Not Collected": "Political opinions"},
                {"Not Collected": "Health information"},
                {"Not Collected": "Sensitive personal data"}
            ]
        )

        st.dataframe(not_collected, use_container_width=True, hide_index=True)

    with tab_invites:
        st.subheader("Invite Token Governance")
        st.markdown(
            "<div class='section-note'>Invite links are temporary and access-controlled using token hashes.</div>",
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Created / Active Invites", active_or_created_invites)
        c2.metric("Expired Invites", expired_invites)
        c3.metric("Total Invites", invite_count)

        invite_rows = db.query(Invite).order_by(Invite.id.desc()).all()

        invite_data = []

        for invite in invite_rows:
            is_expired = invite.expires_at < datetime.utcnow()

            invite_data.append(
                {
                    "Invite ID": invite.id,
                    "Candidate ID": invite.candidate_id,
                    "Status": invite.status,
                    "Expired": is_expired,
                    "Expires At": invite.expires_at,
                    "Created At": invite.created_at,
                    "Raw Token Stored": "No"
                }
            )

        if invite_data:
            invite_df = pd.DataFrame(invite_data)
            st.dataframe(invite_df, use_container_width=True, hide_index=True)

            invite_status_counts = invite_df["Status"].value_counts().reset_index()
            invite_status_counts.columns = ["Status", "Count"]

            invite_chart = (
                alt.Chart(invite_status_counts)
                .mark_bar()
                .encode(
                    x=alt.X("Status:N", title="Invite Status"),
                    y=alt.Y("Count:Q", title="Count", scale=alt.Scale(domainMin=0)),
                    tooltip=["Status", "Count"]
                )
                .properties(height=320)
            )

            st.altair_chart(invite_chart, use_container_width=True)
        else:
            st.info("No invites found.")

    with tab_audit:
        st.subheader("Recent Audit Logs")
        st.markdown(
            "<div class='section-note'>Audit logs provide traceability for collection, scoring, selection, submission, and evaluation actions.</div>",
            unsafe_allow_html=True
        )

        logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(50).all()

        audit_data = []

        for log in logs:
            audit_data.append(
                {
                    "ID": log.id,
                    "Actor": log.actor,
                    "Action": log.action,
                    "Entity Type": log.entity_type,
                    "Entity ID": log.entity_id,
                    "Created At": log.created_at,
                    "Details": log.details_json,
                }
            )

        if audit_data:
            audit_df = pd.DataFrame(audit_data)
            st.dataframe(audit_df, use_container_width=True, hide_index=True)

            action_counts = (
                audit_df["Action"]
                .value_counts()
                .reset_index()
            )
            action_counts.columns = ["Action", "Count"]

            st.subheader("Audit Action Frequency")

            audit_chart = (
                alt.Chart(action_counts)
                .mark_bar()
                .encode(
                    x=alt.X("Count:Q", title="Count"),
                    y=alt.Y("Action:N", sort="-x", title="Action"),
                    tooltip=["Action", "Count"]
                )
                .properties(height=420)
            )

            st.altair_chart(audit_chart, use_container_width=True)
        else:
            st.info("No audit logs found.")

    with tab_limitations:
        st.subheader("Known Privacy and Fairness Limitations")

        limitations = pd.DataFrame(
            [
                {
                    "Limitation": "GitHub activity is only a proxy for skill",
                    "Impact": "Strong developers with private work may be underrated",
                    "Future Improvement": "Add consent-based CV, coding test, and interview signals"
                },
                {
                    "Limitation": "No consent workflow",
                    "Impact": "Not suitable for real recruitment use",
                    "Future Improvement": "Add candidate opt-in and data deletion request flow"
                },
                {
                    "Limitation": "No manager authentication",
                    "Impact": "Dashboard is not production secure",
                    "Future Improvement": "Add login and role-based access control"
                },
                {
                    "Limitation": "No full fairness audit",
                    "Impact": "Bias risk is not fully measured",
                    "Future Improvement": "Evaluate selection rates across relevant groups where lawful and consented"
                },
                {
                    "Limitation": "Rule-based score weights",
                    "Impact": "Weights are manually chosen",
                    "Future Improvement": "Calibrate weights with validated hiring data and governance review"
                },
                {
                    "Limitation": "No automatic code sandbox",
                    "Impact": "Candidate code is not automatically tested",
                    "Future Improvement": "Use secure sandboxing with timeouts and resource limits"
                }
            ]
        )

        st.dataframe(limitations, use_container_width=True, hide_index=True)

        st.divider()

        st.subheader("Recommended Presentation Statement")

        st.success(
            "This system is best presented as an AI-assisted recruitment workflow with privacy-aware controls, "
            "not as a fully autonomous hiring system."
        )

finally:
    db.close()