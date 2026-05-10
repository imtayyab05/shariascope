import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
    raise EnvironmentError("OPENAI_API_KEY is missing or empty. Please add it to your .env file in the root directory.")
