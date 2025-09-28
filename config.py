# config.py - Configuration settings for ISTVON Engine
import os
from typing import Dict, Any

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, try to load .env manually
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

class Config:
    """Configuration settings for the ISTVON Prompt Enhancement Engine"""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCebaAOXEowAnJfZ5urzIsyx5FmBrrYvMo')
    DEFAULT_MODEL = "gemini-2.0-flash"
    
    # ISTVON Schema Definition
    ISTVON_SCHEMA = {
        "I": {
            "type": "array",
            "required": True,
            "description": "Instructions - Array of instruction strings"
        },
        "S": {
            "type": "object",
            "required": False,
            "description": "Sources - Object containing documents, URLs, and data points"
        },
        "T": {
            "type": "array",
            "required": False,
            "description": "Tools - Array of tool strings"
        },
        "V": {
            "type": "object",
            "required": False,
            "description": "Variables - Object containing tone, format, complexity, etc."
        },
        "O": {
            "type": "object",
            "required": True,
            "description": "Outcome - Object containing format, delivery, success criteria"
        },
        "N": {
            "type": "object",
            "required": False,
            "description": "Notifications - Object containing milestones and completion notices"
        }
    }
    
    # Database Configuration
    DATABASE_TYPE = "Oracle"
    DATABASE_DSN = "localhost:1521/XEPDB1"
    DATABASE_USERNAME = "heman"
    DATABASE_PASSWORD = "password"
    DATABASE_TABLE = "prompt_log"
    
    # UI Configuration
    PAGE_TITLE = "ISTVON Prompt Enhancement Engine"
    PAGE_ICON = "🚀"
    LAYOUT = "wide"
    
    # Processing Configuration
    MAX_PROMPT_LENGTH = 5000
    DEFAULT_TIMEOUT = 30
    
    # Domain-specific configurations
    DOMAIN_CONFIGS = {
        "technical": {
            "default_tools": ["Code formatting", "Documentation standards", "Technical writing"],
            "default_variables": {"complexity": "Technical", "format": "Markdown/Code"},
            "success_criteria": ["Technically accurate", "Well-structured code/documentation"]
        },
        "business": {
            "default_tools": ["Business frameworks", "Professional templates", "Industry standards"],
            "default_variables": {"tone": "Professional", "length": "Comprehensive"},
            "success_criteria": ["Professionally formatted", "Actionable recommendations"]
        },
        "creative": {
            "default_tools": ["Creative writing techniques", "Style guides", "Literary devices"],
            "default_variables": {"tone": "Engaging", "format": "Narrative"},
            "success_criteria": ["Engaging content", "Appropriate style and tone"]
        },
        "academic": {
            "default_tools": ["Academic standards", "Citation formats", "Research methodologies"],
            "default_variables": {"tone": "Formal", "complexity": "Detailed"},
            "success_criteria": ["Academic rigor", "Proper citations and references"]
        },
        "communication": {
            "default_tools": ["Communication templates", "Professional etiquette", "Format guidelines"],
            "default_variables": {"tone": "Appropriate", "length": "Concise"},
            "success_criteria": ["Clear communication", "Appropriate tone"]
        }
    }
    
    @classmethod
    def get_domain_config(cls, domain: str) -> Dict[str, Any]:
        """Get configuration for a specific domain"""
        return cls.DOMAIN_CONFIGS.get(domain, cls.DOMAIN_CONFIGS["business"])
    
    @classmethod
    def is_api_configured(cls) -> bool:
        """Check if API is properly configured"""
        return cls.GEMINI_API_KEY and cls.GEMINI_API_KEY != 'your-gemini-api-key-here'