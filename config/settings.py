import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(dotenv_path=env_path, override=True)

OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")
