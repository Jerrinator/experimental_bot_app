import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Config:
    # OpenAI Configuration
    openai_api_key: str
    chat_model: str = "gpt-4"
    
    # Web Scraper Configuration
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    scraping_delay: float = 1.0

def get_config() -> Config:
    """Get configuration from environment variables."""
    config = Config(
        # OpenAI Configuration
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        chat_model=os.getenv("CHAT_MODEL", "gpt-4"),
        
        # Web Scraper Configuration
        user_agent=os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
        scraping_delay=float(os.getenv("SCRAPING_DELAY", "1.0"))
    )
    
    return config
