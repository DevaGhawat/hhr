import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from app.db.database import SessionLocal
from app.db.models import CodingQuestion


QUESTIONS = [
    {
        "title": "Validate Balanced Brackets",
        "description": (
            "Write a Python function that checks whether a string containing brackets "
            "is balanced. The input may contain (), {}, and []. Return True if balanced, otherwise False."
        ),
        "difficulty": "medium",
        "role_type": "developer",
        "expected_concepts": "stack, string parsing, edge cases",
        "test_cases_json": {
            "examples": [
                {"input": "{[()]}", "expected": True},
                {"input": "{[(])}", "expected": False},
                {"input": "", "expected": True}
            ]
        }
    },
    {
        "title": "Find Top K Frequent Words",
        "description": (
            "Given a list of words and an integer k, return the k most frequent words. "
            "If two words have the same frequency, return them in alphabetical order."
        ),
        "difficulty": "medium",
        "role_type": "developer",
        "expected_concepts": "hash map, sorting, frequency counting",
        "test_cases_json": {
            "examples": [
                {
                    "input": "words=['python','ai','python','data','ai','python'], k=2",
                    "expected": ["python", "ai"]
                }
            ]
        }
    },
    {
        "title": "Design a Rate Limiter",
        "description": (
            "Design a simple API rate limiter. Explain the data structures you would use, "
            "how you would handle time windows, and write pseudocode or Python code for the core logic."
        ),
        "difficulty": "hard",
        "role_type": "senior_developer",
        "expected_concepts": "system design, sliding window, token bucket, trade-offs",
        "test_cases_json": {
            "evaluation_focus": [
                "correctness",
                "time complexity",
                "edge cases",
                "design trade-offs"
            ]
        }
    }
]


def seed_questions():
    db = SessionLocal()

    try:
        inserted = 0
        skipped = 0

        for item in QUESTIONS:
            existing = (
                db.query(CodingQuestion)
                .filter(CodingQuestion.title == item["title"])
                .first()
            )

            if existing:
                skipped += 1
                continue

            question = CodingQuestion(**item)
            db.add(question)
            inserted += 1

        db.commit()

        print("Coding questions seeded")
        print(f"Inserted: {inserted}")
        print(f"Skipped existing: {skipped}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_questions()
