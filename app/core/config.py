import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./hushhush_recruiter.db")
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.stackexchange_key = os.getenv("STACKEXCHANGE_KEY", "")
        self.app_secret_key = os.getenv("APP_SECRET_KEY", "change-this-secret-key")
        self.invite_expiry_hours = int(os.getenv("INVITE_EXPIRY_HOURS", "72"))
        self.data_collection_limit = int(os.getenv("DATA_COLLECTION_LIMIT", "100"))


settings = Settings()
