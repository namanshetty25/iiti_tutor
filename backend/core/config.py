import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the root of the backend directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ankush_10010:hl9B_iFzL%5DBH%3BK2%3F@iititutor.rhtimwk.mongodb.net/?retryWrites=true&w=majority&appName=IITITutor")
    DATABASE_NAME = "IITI_Tutor_DB"
    SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
    GROQ_MODEL = "llama-3.1-8b-instant"
    GROQ_VERSATILE_MODEL = "llama-3.3-70b-versatile"
