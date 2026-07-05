# Architecture Documentation

## Project Name

hushHush Recruiter: Privacy-Aware AI Candidate Shortlisting and Challenge Management System

## System Goal

The system automates the early recruitment workflow for a fictional company called Doodle.

It collects public technical profile signals, creates interpretable candidate features, ranks candidates, selects candidates probabilistically, creates temporary challenge links, stores coding submissions, and allows a human hiring manager to evaluate the result.

This is an academic prototype, not a production hiring system.

## High-Level Pipeline

GitHub API
-> Candidate Collection
-> SQLite Database
-> Feature Engineering
-> Transparent Scoring
-> Probabilistic Selection
-> Invite Token + Mock Notification
-> Candidate Coding Portal
-> Manager Evaluation Dashboard
-> Audit Logs + Privacy Audit

## Main Components

### 1. Candidate Collection

The system collects public GitHub profile data using the GitHub API.

Collected signals include public repositories, followers, forks, stars, recent activity, top languages, profile URL, and location if available.

### 2. Feature Engineering

Raw GitHub data is converted into numerical feature scores:

- GitHub activity score
- Repository quality score
- Skill match score
- Profile completeness score
- StackOverflow score placeholder

### 3. Transparent Scoring

The system uses a transparent rule-based scoring model.

This is better than fake supervised learning because the project does not have real hiring labels.

### 4. Probabilistic Selection

Candidates are not selected only by deterministic top-N ranking.

The system uses weighted probability, so higher-scoring candidates are more likely to be selected, but the output is not always exactly the same.

### 5. Invite Token System

Selected candidates receive a temporary challenge link.

The raw token is not stored. Only the token hash is stored in the database.

The link expires after a configured time.

### 6. Candidate Portal

The candidate portal validates the token and shows three coding questions.

Candidates can submit their answers through the portal.

### 7. Manager Dashboard

The manager dashboard allows a human manager to review submissions, score answers, provide feedback, and store the final decision.

### 8. Privacy Audit

The privacy audit page explains data minimisation, mock notifications, invite expiry, and audit logs.

## Database Tables

Important tables:

- candidates
- github_profiles
- stackoverflow_profiles
- candidate_features
- candidate_scores
- invites
- coding_questions
- coding_submissions
- manager_evaluations
- notification_logs
- audit_logs
- privacy_requests

## Responsible Design Choices

The system includes these controls:

- Public technical data only
- Mock notifications instead of real emails
- Expiring invite tokens
- Token hashes instead of raw tokens
- Transparent scoring
- Human final decision
- Audit logs
- Privacy audit page
- No automatic execution of candidate code

## Current Prototype Status

Implemented:

- GitHub data collection
- Feature engineering
- Candidate scoring
- Probabilistic selection
- Invite generation
- Candidate portal
- Three coding questions
- Candidate submission
- Manager evaluation
- Notification logs
- Privacy audit

## Future Improvements

- StackOverflow API integration
- Role-specific coding challenges
- Fairness analysis
- Authentication for manager dashboard
- PostgreSQL instead of SQLite
- Deployment with secure environment variables
