import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.db.database import Base, engine
from app.db import models


def create_database():
    Base.metadata.create_all(bind=engine)
    print("Database created successfully: hushhush_recruiter.db")


if __name__ == "__main__":
    create_database()
