"""
Configuration Settings for AI Kitchen Assistant

This module contains all the configuration settings for the application,
including environment variables, file upload settings, and API configurations.

Environment Variables:
    FLASK_SECRET_KEY: Secret key for Flask session management
    FLASK_ENV: Environment (development/production)
    MAX_CONTENT_LENGTH: Maximum file upload size (default: 16MB)
    UPLOAD_FOLDER: Directory for temporary file uploads
    OPENAI_API_KEY: API key for OpenAI services
    IMAGE_MODEL: OpenAI model for image analysis
    RECIPE_MODEL: OpenAI model for recipe generation
"""

import os
import logging
from typing import Dict, Set, Optional, Any, Union

logger = logging.getLogger(__name__)

class Config:
    """
    Application configuration class.
    
    Loads settings from environment variables with sensible defaults.
    All sensitive configurations should be set via environment variables.
    
    Environment Variables:
        FLASK_SECRET_KEY: Secret key for Flask session management
        FLASK_ENV: Application environment (development/production)
        MAX_CONTENT_LENGTH: Maximum file upload size in bytes (default: 16MB)
        UPLOAD_FOLDER: Directory for temporary file uploads
        OPENAI_API_KEY: OpenAI API key (required)
        IMAGE_MODEL: Model for image analysis (default: gpt-4o-mini)
        RECIPE_MODEL: Model for recipe generation (default: gpt-4o-mini)
    """
    
    # Flask Configuration
    # -----------------
    SECRET_KEY: str = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    FLASK_ENV: str = os.environ.get('FLASK_ENV', 'production')
    
    # File Upload Settings
    # -------------------
    # Default to 16MB if MAX_CONTENT_LENGTH is not set or invalid
    try:
        # First, try to get the environment variable
        max_content_raw = os.environ.get('MAX_CONTENT_LENGTH')
        # If it exists, clean up the value (remove any comments or extra spaces)
        if max_content_raw:
            # Extract only the digits
            max_content_clean = ''.join(c for c in max_content_raw if c.isdigit())
            MAX_CONTENT_LENGTH = int(max_content_clean) if max_content_clean else 16 * 1024 * 1024
        else:
            MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing MAX_CONTENT_LENGTH: {e}. Using default value.")
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        
    UPLOAD_FOLDER: str = os.environ.get('UPLOAD_FOLDER', 'temp_uploads')
    ALLOWED_EXTENSIONS: Set[str] = {'png', 'jpg', 'jpeg'}
    
    # OpenAI API Configuration
    # -----------------------
    OPENAI_API_KEY: str = os.environ.get('OPENAI_API_KEY', '')
    
    # Model Configuration
    # ------------------
    # Note: These should be set in .env file or environment variables
    IMAGE_MODEL: str = os.environ.get('IMAGE_MODEL', 'gpt-4o-mini')
    RECIPE_MODEL: str = os.environ.get('RECIPE_MODEL', 'gpt-4o-mini')
    
    @classmethod
    def validate_config(cls) -> None:
        """
        Validate the configuration and raise exceptions for required settings.
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        required_vars = {
            'OPENAI_API_KEY': cls.OPENAI_API_KEY,
        }
        
        missing = [name for name, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Validate file upload directory exists and is writable
        if not os.path.exists(cls.UPLOAD_FOLDER):
            try:
                os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
                logger.info(f"Created upload directory: {cls.UPLOAD_FOLDER}")
            except OSError as e:
                raise ValueError(f"Failed to create upload directory '{cls.UPLOAD_FOLDER}': {e}")
        
        if not os.access(cls.UPLOAD_FOLDER, os.W_OK):
            raise ValueError(f"Upload directory '{cls.UPLOAD_FOLDER}' is not writable")
        
        logger.info("Configuration validated successfully")

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    # Validate configuration when the module is imported
    Config.validate_config()
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")
    # Re-raise the exception to halt the application
    raise
