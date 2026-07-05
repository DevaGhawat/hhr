import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.db.database import SessionLocal
from app.db.models import Candidate, CandidateFeature
from app.services.feature_engineering import build_features_for_all_candidates


def main():
    db = SessionLocal()

    try:
        summary = build_features_for_all_candidates(db)

        print("Feature engineering completed")
        print(f"Total candidates: {summary['total_candidates']}")
        print(f"Processed: {summary['processed']}")
        print(f"Skipped: {summary['skipped']}")
        print("")

        top_candidates = (
            db.query(Candidate, CandidateFeature)
            .join(CandidateFeature, Candidate.id == CandidateFeature.candidate_id)
            .order_by(CandidateFeature.overall_feature_score.desc())
            .limit(10)
            .all()
        )

        print("Top candidates by feature score")
        print("-" * 80)

        for candidate, features in top_candidates:
            print(
                f"{candidate.id:>3} | "
                f"{candidate.github_username:<25} | "
                f"overall={features.overall_feature_score:.4f} | "
                f"activity={features.github_activity_score:.4f} | "
                f"repo_quality={features.repository_quality_score:.4f} | "
                f"skill={features.skill_match_score:.4f} | "
                f"complete={features.profile_completeness_score:.4f}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
