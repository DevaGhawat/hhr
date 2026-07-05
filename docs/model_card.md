# Model Card: Transparent Candidate Scoring

## Model Name

Transparent Rank Score v1

## Model Type

Rule-based transparent scoring model.

This is not a supervised machine learning classifier.

## Intended Use

The model ranks technical candidates for an academic recruitment automation prototype.

It helps identify candidates who may be invited to a coding challenge.

It is not intended to make final hiring decisions.

## Input Data

The current version uses public GitHub profile signals:

- Public repository count
- Followers
- Following
- Total stars
- Total forks
- Recent repository activity
- Top programming languages
- Profile completeness

## Output

The model outputs:

- Final candidate score between 0 and 1
- Rank position
- Selection probability
- Explanation JSON

## Why Rule-Based Instead of Supervised ML?

A supervised hiring model needs reliable labels such as hired/not hired, interview results, or job performance.

This project does not have real validated hiring labels.

Using fake labels would make model accuracy misleading.

Therefore, a transparent rule-based scoring model is more honest and defensible.

## Probabilistic Selection

The system does not select only the top candidates deterministically.

Candidates above a minimum score enter a candidate pool. Selection is then performed using weighted probability.

Higher-scoring candidates have higher probability, but selection is not fully deterministic.

## Explainability

Each candidate score contains component-level explanations.

This helps the manager understand why a candidate was ranked highly.

## Evaluation

Current evaluation is system-level, not predictive ML evaluation.

The system is evaluated by checking whether:

- Candidates are collected
- Features are generated
- Scores are created
- Selection probabilities are assigned
- Invite links are generated
- Candidate submissions are stored
- Manager evaluations are saved
- Audit logs are created

## Limitations

- GitHub activity is an incomplete proxy for technical ability.
- Developers without public GitHub activity may be disadvantaged.
- Stars and followers can reflect popularity, not only skill.
- Score weights are manually selected.
- The model is not validated against real hiring outcomes.
- It should not be used for real hiring decisions.

## Ethical Controls

The prototype includes:

- Transparent scoring
- Human manager review
- Mock notifications
- Expiring invite links
- Privacy audit page
- Audit logs
- No fully automated final decision

## Presentation Wording

Use this phrase:

"Transparent technical ranking model for academic shortlisting simulation."

Avoid saying:

"AI model that decides who should be hired."
