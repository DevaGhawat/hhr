# Privacy Risk Assessment

## Context

hushHush Recruiter processes public technical profile data for an academic recruitment automation prototype.

Recruitment systems are sensitive because their outputs may affect candidate opportunities. Therefore, the system is designed with privacy, transparency, auditability, and human oversight.

## Main Privacy Risks

| Risk | Description | Mitigation |
|---|---|---|
| Public data misuse | Public GitHub data can still be personal data | Use only minimal public technical signals |
| Unsolicited contact | Automatically contacting real people is ethically risky | Use mock notifications only |
| Fully automated decisions | Automated hiring decisions can be unfair | Human manager makes final decision |
| Token leakage | Invite links could be shared | Store only token hash and expire links |
| GitHub bias | GitHub activity does not represent all developers | Treat score as shortlisting support only |
| Explainability risk | Black-box scoring would be hard to justify | Use transparent rule-based scoring |
| Excessive collection | Collecting unnecessary data increases risk | Avoid private data and email scraping |

## Data Collected

The prototype stores:

- GitHub username
- Public profile URL
- Public repository statistics
- Followers and following count
- Stars and forks
- Recent repository activity
- Top programming languages
- Candidate feature scores
- Candidate ranking scores
- Invite status
- Coding challenge submissions
- Manager evaluation feedback
- Audit logs

## Data Not Collected

The prototype does not intentionally collect:

- Private repositories
- Private messages
- Private email addresses
- Demographic attributes
- Political opinions
- Health information
- Sensitive personal data

## Purpose Limitation

The data is used only for:

1. Academic prototype demonstration
2. Technical profile scoring
3. Candidate challenge workflow simulation
4. Manager evaluation demonstration
5. Privacy and auditability demonstration

The system should not be used for real hiring decisions.

## Storage Limitation

The prototype stores data locally in SQLite.

In a production version, retention rules would be required:

- Raw API data should be deleted after feature extraction
- Invite tokens should expire automatically
- Candidate submissions should be deleted after assessment
- Audit logs should be retained only as long as necessary

## Security Controls

Implemented controls:

- GitHub token stored in `.env`
- `.env` excluded from Git
- Local database excluded from Git
- Invite token hashing
- Expiring invite links
- Mock notification logging
- Audit logs for important actions

## Human Oversight

The system does not make final hiring decisions automatically.

The algorithm supports candidate shortlisting, but the manager reviews submissions and stores the final decision manually.

## Ethical Position

The original project idea involves secretive automated recruitment. That has clear ethical risks.

This implementation reframes the idea as an AI-assisted recruitment workflow where automation supports the process but does not replace human judgement.

## Remaining Limitations

- No formal consent flow is implemented.
- No manager authentication is implemented yet.
- SQLite is not production secure.
- No full fairness audit is implemented.
- Score weights are manually defined.
- StackOverflow integration is planned but not implemented yet.

## Final Recommendation

For academic presentation, this should be described as a privacy-aware AI recruitment prototype, not as a real autonomous hiring system.
