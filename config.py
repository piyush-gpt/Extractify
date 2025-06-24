import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS = "firstwork-463813-a33cf23467fd.json"
    
    # Model settings
    GEMINI_MODEL = "gemini-2.5-flash" 
    MAX_TOKENS = 2000
    
    # Processing settings
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png']
    SUPPORTED_PDF_FORMATS = ['.pdf']
    
    # Output settings
    OUTPUT_DIR = "output"
    
    # OpenAI or Gemini settings
    USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-3.5-turbo"
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        if not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
            raise ValueError(f"Google credentials file not found: {cls.GOOGLE_APPLICATION_CREDENTIALS}")
        
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True) 