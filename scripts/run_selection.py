import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.db.database import SessionLocal
from app.services.selection_service import select_candidates_for_challenge


def parse_args():
    parser = argparse.ArgumentParser(description="Probabilistically select candidates for challenge.")
    parser.add_argument("--pool-size", type=int, default=15)
    parser.add_argument("--select-count", type=int, default=5)
    parser.add_argument("--minimum-score", type=float, default=0.40)
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    db = SessionLocal()

    try:
        result = select_candidates_for_challenge(
            db=db,
            pool_size=args.pool_size,
            select_count=args.select_count,
            minimum_score=args.minimum_score,
            seed=args.seed
        )

        print("Probabilistic candidate selection completed")
        print(f"Candidate pool size: {result['candidate_pool_size']}")
        print(f"Selected count: {result['selected_count']}")
        print("")

        for item in result["selected"]:
            print(
                f"id={item['candidate_id']:>3} | "
                f"{item['github_username']:<25} | "
                f"score={item['final_score']:.4f} | "
                f"prob={item['selection_probability']:.4f} | "
                f"invite_id={item['invite_id']}"
            )
            print(f"link={item['invite_link']}")
            print(f"expires_at={item['expires_at']}")
            print("-" * 90)

    finally:
        db.close()


if __name__ == "__main__":
    main()
