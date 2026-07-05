import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.db.database import SessionLocal
from app.services.scoring_service import get_ranked_candidates, score_all_candidates


def main():
    db = SessionLocal()

    try:
        summary = score_all_candidates(db)

        print("Candidate scoring completed")
        print(f"Candidates with features: {summary['total_candidates_with_features']}")
        print(f"Scored candidates: {summary['scored_candidates']}")
        print("")

        ranked_candidates = get_ranked_candidates(db, limit=10)

        print("Top candidates by final score")
        print("-" * 90)

        for candidate, score in ranked_candidates:
            print(
                f"rank={score.rank_position:>2} | "
                f"id={candidate.id:>3} | "
                f"{candidate.github_username:<25} | "
                f"final_score={score.final_score:.4f}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
