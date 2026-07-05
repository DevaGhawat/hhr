import streamlit as st

st.set_page_config(
    page_title="hushHush Recruiter",
    page_icon="???",
    layout="wide"
)

st.title("hushHush Recruiter")
st.subheader("Privacy-Aware AI Candidate Shortlisting and Challenge System")

st.markdown(
    """
    This academic prototype demonstrates an end-to-end recruitment automation pipeline:

    1. Collect public technical profile signals.
    2. Engineer interpretable candidate features.
    3. Score and rank candidates transparently.
    4. Select candidates probabilistically.
    5. Issue temporary coding challenge links.
    6. Allow manager review and final decision.

    The system uses mock notifications and requires human manager evaluation.
    It does not perform fully automated hiring.
    """
)

st.info("Use the sidebar pages to open the Manager Dashboard, Candidate Portal, Data Collection, and Privacy Audit.")
