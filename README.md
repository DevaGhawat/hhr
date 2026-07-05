# hushHush Recruiter

Privacy-aware AI candidate shortlisting and coding challenge management system.

## Project Overview

hushHush Recruiter is an academic prototype for Doodle, a fictional software company that wants to automate parts of its recruitment process.

The system collects public GitHub technical signals, engineers candidate features, scores candidates transparently, selects candidates probabilistically, creates temporary invite links, provides three coding questions, stores candidate submissions, and allows a hiring manager to evaluate the result.

The system does not make fully automated hiring decisions. Final evaluation remains with a human manager.

## Key Features

- Real GitHub API data collection
- Candidate feature engineering
- Transparent technical scoring
- Probabilistic candidate selection
- Time-limited invite token system
- Mock notification logging
- Candidate coding challenge portal
- Three coding questions
- Manager evaluation dashboard
- Privacy audit page
- Audit logs

## Tech Stack

- Python
- Streamlit
- SQLAlchemy
- SQLite
- pandas
- requests
- python-dotenv

## Architecture

GitHub API -> Candidate Collection -> Feature Engineering -> Transparent Scoring -> Probabilistic Selection -> Invite Token + Mock Notification -> Candidate Coding Portal -> Manager Evaluation Dashboard -> Final Result Notification Log

## Setup

Create virtual environment:

python -m venv .venv

Activate environment:

.\.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Create environment file:

copy .env.example .env

Add your GitHub token inside .env.

## Run Pipeline

Create database:

python scripts/create_database.py

Collect GitHub candidates:

python scripts/collect_github_candidates.py --limit 30

Build features:

python scripts/run_feature_engineering.py

Score candidates:

python scripts/run_scoring.py

Select candidates:

python scripts/run_selection.py --pool-size 15 --select-count 5 --minimum-score 0.40

Seed coding questions:

python -m app.db.seed_questions

Run app:

streamlit run frontend/streamlit_app.py

## Current Prototype Results

- Candidates collected: 26
- Scored candidates: 26
- Invites generated: 5
- Coding submissions: 3
- Manager evaluations: 1
- Notification logs: 6
- Audit logs: 65

## Privacy and Ethics

This project handles recruitment-related data, so the design includes privacy controls:

- Uses public GitHub profile data only
- Does not collect private candidate information
- Does not send real emails
- Uses mock notification logs
- Stores invite token hashes instead of raw tokens
- Uses expiring challenge links
- Keeps audit logs
- Requires human manager review
- Does not perform fully automated hiring decisions

## Limitations

- GitHub activity alone is not enough to judge candidate quality.
- Public profile activity may not represent actual skill.
- The scoring model is rule-based and not a validated hiring model.
- No real hiring decision should be made from this prototype.
- StackOverflow integration is planned but not implemented yet.
- Candidate code is manually reviewed for safety.

## Academic Positioning

This project demonstrates an end-to-end AI-assisted recruitment workflow with responsible design choices: transparency, privacy, auditability, and human oversight.
