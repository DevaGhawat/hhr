from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Boolean
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    display_name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)

    github_username = Column(String(100), unique=True, nullable=True, index=True)
    stackoverflow_user_id = Column(String(100), unique=True, nullable=True, index=True)

    profile_url = Column(String(500), nullable=True)
    location = Column(String(200), nullable=True)

    source = Column(String(100), default="public_api")
    privacy_basis = Column(String(200), default="public professional data for academic prototype")

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    github_profile = relationship("GitHubProfile", back_populates="candidate", uselist=False)
    stackoverflow_profile = relationship("StackOverflowProfile", back_populates="candidate", uselist=False)
    features = relationship("CandidateFeature", back_populates="candidate")
    scores = relationship("CandidateScore", back_populates="candidate")
    invites = relationship("Invite", back_populates="candidate")


class GitHubProfile(Base):
    __tablename__ = "github_profiles"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), unique=True, nullable=False)

    public_repos = Column(Integer, default=0)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)

    total_stars = Column(Integer, default=0)
    total_forks = Column(Integer, default=0)
    recent_push_count = Column(Integer, default=0)

    account_age_days = Column(Integer, default=0)
    top_languages_json = Column(JSON, nullable=True)
    raw_profile_json = Column(JSON, nullable=True)

    collected_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="github_profile")


class StackOverflowProfile(Base):
    __tablename__ = "stackoverflow_profiles"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), unique=True, nullable=False)

    reputation = Column(Integer, default=0)
    gold_badges = Column(Integer, default=0)
    silver_badges = Column(Integer, default=0)
    bronze_badges = Column(Integer, default=0)

    answer_count = Column(Integer, default=0)
    question_count = Column(Integer, default=0)
    accepted_answer_count = Column(Integer, default=0)

    top_tags_json = Column(JSON, nullable=True)
    raw_profile_json = Column(JSON, nullable=True)

    collected_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="stackoverflow_profile")


class CandidateFeature(Base):
    __tablename__ = "candidate_features"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    github_activity_score = Column(Float, default=0.0)
    repository_quality_score = Column(Float, default=0.0)
    stackoverflow_score = Column(Float, default=0.0)
    skill_match_score = Column(Float, default=0.0)
    profile_completeness_score = Column(Float, default=0.0)

    overall_feature_score = Column(Float, default=0.0)
    feature_version = Column(String(50), default="v1")

    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="features")


class CandidateScore(Base):
    __tablename__ = "candidate_scores"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    final_score = Column(Float, default=0.0)
    selection_probability = Column(Float, default=0.0)
    rank_position = Column(Integer, nullable=True)

    scoring_version = Column(String(50), default="rule_based_v1")
    explanation_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="scores")


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    token_hash = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    status = Column(String(50), default="created")
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="invites")
    submissions = relationship("CodingSubmission", back_populates="invite")


class CodingQuestion(Base):
    __tablename__ = "coding_questions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(50), default="medium")
    role_type = Column(String(100), default="developer")

    expected_concepts = Column(Text, nullable=True)
    test_cases_json = Column(JSON, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id = Column(Integer, primary_key=True, index=True)

    invite_id = Column(Integer, ForeignKey("invites.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("coding_questions.id"), nullable=False)

    submitted_code = Column(Text, nullable=False)
    language = Column(String(50), default="python")

    submitted_at = Column(DateTime, default=datetime.utcnow)

    manager_score = Column(Float, nullable=True)
    manager_feedback = Column(Text, nullable=True)

    invite = relationship("Invite", back_populates="submissions")
    question = relationship("CodingQuestion")


class ManagerEvaluation(Base):
    __tablename__ = "manager_evaluations"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    invite_id = Column(Integer, ForeignKey("invites.id"), nullable=False)

    technical_score = Column(Float, nullable=True)
    code_quality_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)

    final_decision = Column(String(50), default="pending")
    feedback = Column(Text, nullable=True)

    evaluated_by = Column(String(200), nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow)


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    notification_type = Column(String(100), nullable=False)
    channel = Column(String(50), default="mock_email")
    recipient = Column(String(255), nullable=True)

    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)

    status = Column(String(50), default="logged")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    actor = Column(String(100), default="system")
    action = Column(String(200), nullable=False)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)

    details_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class PrivacyRequest(Base):
    __tablename__ = "privacy_requests"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True)

    request_type = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")

    request_details = Column(Text, nullable=True)
    handled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
