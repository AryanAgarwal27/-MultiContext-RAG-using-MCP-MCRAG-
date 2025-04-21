import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Search Configuration
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

# Validate required API keys
required_keys = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "TAVILY_API_KEY": TAVILY_API_KEY,
    "FIRECRAWL_API_KEY": FIRECRAWL_API_KEY,
    "EXA_API_KEY": EXA_API_KEY
}

missing_keys = [key for key, value in required_keys.items() if not value]
if missing_keys:
    raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")

# Model Configuration
TEMPERATURE = 0

# Search Tool Configuration
MAX_TOKENS = 4000 