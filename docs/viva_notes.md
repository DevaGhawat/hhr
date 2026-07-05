# Viva Notes

## One-Minute Project Explanation

hushHush Recruiter is a privacy-aware recruitment automation prototype.

It collects public GitHub technical signals, converts them into interpretable candidate features, scores candidates using a transparent ranking model, selects candidates probabilistically, creates temporary invite links, gives selected candidates three coding questions, stores their submissions, and allows a hiring manager to evaluate the final result.

The system does not make final hiring decisions automatically. It supports shortlisting and challenge management, but the final decision remains with a human manager.

## Why GitHub Data?

GitHub provides public technical signals such as repositories, languages, stars, forks, followers, and recent activity.

These signals are relevant for a software recruitment prototype.

However, GitHub data is not a complete measure of skill. Some strong developers work mostly on private repositories or closed-source projects.

Therefore, GitHub is used only as one technical signal, not as the final hiring decision.

## Why Rule-Based Scoring?

A supervised ML model needs reliable labels such as hired/not hired, interview performance, coding challenge result, or later job performance.

This project does not have real hiring labels.

Using fake labels would create misleading accuracy.

So I used a transparent rule-based scoring model. It is easier to explain, audit, and justify.

## Why Probabilistic Selection?

The project requirement says the selection algorithm should not be deterministic.

Instead of random selection, I used weighted probabilistic selection.

Higher-scoring candidates have a higher chance of being selected, but the selected set is not always exactly the same.

This balances technical quality and non-determinism.

## Why Mock Notifications?

Sending real emails to people collected from public GitHub profiles would create privacy and ethical issues.

So the prototype logs notifications instead of sending them.

This demonstrates the workflow without contacting real people.

## Why Token-Based Candidate Portal?

The project requires the challenge interface to be temporary.

The system generates a secure token, stores only its hash, and validates it when the candidate opens the portal.

If the token is missing, invalid, expired, or already submitted, access is blocked.

## Why No Automatic Code Execution?

Running candidate code automatically is risky.

Submitted code could be malicious or resource-intensive.

A production system would need sandboxing, timeout limits, container isolation, and security controls.

For this academic prototype, manual manager evaluation is safer and sufficient.

## Main Database Tables

- candidates
- github_profiles
- candidate_features
- candidate_scores
- invites
- coding_questions
- coding_submissions
- manager_evaluations
- notification_logs
- audit_logs
- privacy_requests

## Responsible AI Elements

- Public technical data only
- Transparent scoring
- Human final decision
- Mock notifications
- Expiring invite links
- Token hashing
- Audit logs
- Privacy audit page
- Clear limitations
- No fully automated hiring

## Main Limitation

The biggest limitation is that GitHub activity is only a proxy signal.

It can favour people who work publicly and penalise people who work in private companies or closed-source projects.

Therefore, this prototype should not be used for real hiring without consent, fairness testing, stronger governance, and better data.

## If Professor Asks: Is This Fair?

Answer:

No, not fully. GitHub data alone is not enough for fair hiring. It can favour visible open-source developers. I reduced risk by using transparent scoring, avoiding real emails, adding audit logs, using temporary tokens, and requiring human manager review.

## If Professor Asks: Where Is AI?

Answer:

The AI part is the decision-support pipeline: feature engineering from public technical signals, transparent candidate scoring, probabilistic selection, and human-in-the-loop evaluation. I intentionally avoided a black-box classifier because there are no reliable hiring labels.

## If Professor Asks: Why Not Deep Learning?

Answer:

Deep learning would be unnecessary and misleading here. The dataset is small, there are no reliable labels, and the task requires explainability. A transparent scoring model is more appropriate.

## If Professor Asks: What Would You Improve?

I would add:

1. Consent-based candidate onboarding
2. StackOverflow integration
3. Role-specific scoring
4. Fairness analysis
5. Manager authentication
6. PostgreSQL instead of SQLite
7. Data deletion workflow
8. Secure sandbox for automatic code testing
