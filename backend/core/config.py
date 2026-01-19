import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the root of the backend directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Required environment variables
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MONGO_URI = os.getenv("MONGO_URI")  # No default - must be set in .env
    
    # Application settings
    DATABASE_NAME = os.getenv("DATABASE_NAME", "IITI_Tutor_DB")
    SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
    GROQ_MODEL = "llama-3.1-8b-instant"
    GROQ_VERSATILE_MODEL = "llama-3.3-70b-versatile"
    
    # Environment detection
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate required environment variables. Returns list of errors."""
        errors = []
        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is not set in environment variables")
        if not cls.MONGO_URI:
            errors.append("MONGO_URI is not set in environment variables")
        return errors
