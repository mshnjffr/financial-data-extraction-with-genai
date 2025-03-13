import os
from dataclasses import dataclass
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

@dataclass
class AppConfig:
    """Application configuration."""
    access_token: str
    models_endpoint: str
    chat_completions_endpoint: str
    x_requested_with: Optional[str] = None    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        access_token = os.getenv("SG_ACCESS_TOKEN")
        models_endpoint = os.getenv("SG_MODELS_ENDPOINT")
        chat_completions_endpoint = os.getenv("SG_CHAT_COMPLETIONS_ENDPOINT") 
        x_requested_with = os.getenv("X_Requested_With")
        
        return cls(
            access_token=access_token,
            models_endpoint=models_endpoint,
            chat_completions_endpoint=chat_completions_endpoint,
            x_requested_with=x_requested_with
        )
    
    def validate(self):
        """Validate configuration"""
        if not self.access_token or not self.models_endpoint or not self.chat_completions_endpoint:
            return False
        return True
