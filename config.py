#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
AI Photo Kitchen Assistant - Configuration Module
================================================================================

Author: 686f6c61 (https://github.com/686f6c61)
Created: 2024-01-15
Updated: 2025-01-24
Version: 2.0.0
License: MIT

Description:
    Configuration management for the AI Kitchen Assistant application.
    Handles environment variables, API credentials, and application settings
    with support for both OpenRouter and OpenAI APIs.

Features:
    - Multi-provider AI support (OpenRouter, OpenAI)
    - Secure credential management via environment variables
    - Automatic validation of required settings
    - Rate limiting configuration
    - Cache configuration support
    - Comprehensive logging setup

Environment Variables:
    Required:
        - OPENROUTER_API_KEY or OPENAI_API_KEY: API authentication
        - FLASK_SECRET_KEY: Flask session security

    Optional:
        - IMAGE_MODEL: Model for image analysis (default: google/gemini-pro-1.5-exp)
        - RECIPE_MODEL: Model for recipe generation (default: anthropic/claude-3.5-sonnet)
        - RATE_LIMIT_PER_MINUTE: API rate limiting (default: 10)
        - CACHE_TYPE: Cache backend (default: simple)
        - LOG_LEVEL: Logging verbosity (default: INFO)

Usage:
    from config import Config

    # Access configuration
    api_key = Config.OPENROUTER_API_KEY
    model = Config.IMAGE_MODEL

    # Validate configuration
    Config.validate_config()

Notes:
    - All sensitive data should be stored in .env file
    - Never commit .env file to version control
    - Use .env.example as template

================================================================================
"""

import os
import logging
import secrets
from typing import Set, Optional

# Configure module logger
logger = logging.getLogger(__name__)


class Config:
    """
    Application configuration class with multi-provider AI support.

    This class loads and validates configuration from environment variables,
    providing support for both OpenRouter (recommended) and OpenAI APIs.

    Attributes:
        Flask Configuration:
            SECRET_KEY (str): Flask session secret key
            FLASK_ENV (str): Application environment (development/production)

        File Upload Settings:
            MAX_CONTENT_LENGTH (int): Maximum file size in bytes (16MB default)
            UPLOAD_FOLDER (str): Directory for temporary uploads
            ALLOWED_EXTENSIONS (Set[str]): Permitted file extensions

        AI Provider Configuration:
            AI_PROVIDER (str): Active provider ('openrouter' or 'openai')
            OPENROUTER_API_KEY (str): OpenRouter API key
            OPENROUTER_BASE_URL (str): OpenRouter API endpoint
            OPENAI_API_KEY (str): OpenAI API key
            IMAGE_MODEL (str): Model for image analysis
            RECIPE_MODEL (str): Model for recipe generation

        Rate Limiting:
            RATE_LIMIT_PER_MINUTE (int): Requests per minute limit
            RATE_LIMIT_PER_HOUR (int): Requests per hour limit

        Caching:
            CACHE_TYPE (str): Cache backend type
            CACHE_REDIS_URL (str): Redis connection URL
            CACHE_DEFAULT_TIMEOUT (int): Default cache TTL in seconds

        Server Configuration:
            HOST (str): Server bind address
            PORT (int): Server port number

        Logging:
            LOG_LEVEL (str): Logging level
            LOG_FILE (str): Log file path
    """

    # =========================================================================
    # Flask Configuration
    # =========================================================================
    SECRET_KEY: str = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)
    FLASK_ENV: str = os.environ.get('FLASK_ENV', 'production')

    # Warn if using default secret key in production
    if FLASK_ENV == 'production' and not os.environ.get('FLASK_SECRET_KEY'):
        logger.warning(
            "⚠️  Using auto-generated SECRET_KEY. Set FLASK_SECRET_KEY in .env "
            "for production to maintain sessions across restarts."
        )

    # =========================================================================
    # File Upload Settings
    # =========================================================================
    try:
        max_content_raw = os.environ.get('MAX_CONTENT_LENGTH')
        if max_content_raw:
            # Extract digits only to handle comments in .env
            max_content_clean = ''.join(c for c in max_content_raw if c.isdigit())
            MAX_CONTENT_LENGTH = int(max_content_clean) if max_content_clean else 16 * 1024 * 1024
        else:
            MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing MAX_CONTENT_LENGTH: {e}. Using default (16MB).")
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    UPLOAD_FOLDER: str = os.environ.get('UPLOAD_FOLDER', 'temp_uploads')
    ALLOWED_EXTENSIONS: Set[str] = {'png', 'jpg', 'jpeg', 'webp'}

    # =========================================================================
    # AI Provider Configuration
    # =========================================================================

    # OpenRouter Configuration (Recommended)
    OPENROUTER_API_KEY: str = os.environ.get('OPENROUTER_API_KEY', '')
    OPENROUTER_BASE_URL: str = os.environ.get(
        'OPENROUTER_BASE_URL',
        'https://openrouter.ai/api/v1'
    )

    # OpenAI Configuration (Alternative/Fallback)
    OPENAI_API_KEY: str = os.environ.get('OPENAI_API_KEY', '')

    # Determine active AI provider
    if OPENROUTER_API_KEY:
        AI_PROVIDER: str = 'openrouter'
        logger.info("✓ Using OpenRouter as AI provider")
    elif OPENAI_API_KEY:
        AI_PROVIDER: str = 'openai'
        logger.info("✓ Using OpenAI as AI provider")
    else:
        AI_PROVIDER: str = 'none'
        logger.error("✗ No AI provider configured! Set OPENROUTER_API_KEY or OPENAI_API_KEY")

    # Model Configuration
    # Default models optimized for quality and cost-efficiency
    IMAGE_MODEL: str = os.environ.get(
        'IMAGE_MODEL',
        'google/gemini-pro-1.5-exp' if AI_PROVIDER == 'openrouter' else 'gpt-4o-mini'
    )
    RECIPE_MODEL: str = os.environ.get(
        'RECIPE_MODEL',
        'anthropic/claude-3.5-sonnet' if AI_PROVIDER == 'openrouter' else 'gpt-4o-mini'
    )

    # =========================================================================
    # Rate Limiting Configuration
    # =========================================================================
    RATE_LIMIT_PER_MINUTE: int = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '10'))
    RATE_LIMIT_PER_HOUR: int = int(os.environ.get('RATE_LIMIT_PER_HOUR', '50'))

    # =========================================================================
    # Caching Configuration
    # =========================================================================
    CACHE_TYPE: str = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_REDIS_URL: str = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT: int = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '3600'))

    # =========================================================================
    # Server Configuration
    # =========================================================================
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    PORT: int = int(os.environ.get('PORT', '5050'))

    # =========================================================================
    # Logging Configuration
    # =========================================================================
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.environ.get('LOG_FILE', 'app.log')

    @classmethod
    def validate_config(cls) -> None:
        """
        Validate the configuration and raise exceptions for missing requirements.

        This method checks:
        - At least one AI provider API key is configured
        - Upload directory exists and is writable
        - All required settings are properly formatted

        Raises:
            ValueError: If required configuration is missing or invalid

        Example:
            >>> Config.validate_config()
            # Logs: Configuration validated successfully
        """
        errors = []

        # Check AI provider configuration
        if not cls.OPENROUTER_API_KEY and not cls.OPENAI_API_KEY:
            errors.append(
                "No AI provider configured. Set either OPENROUTER_API_KEY or OPENAI_API_KEY"
            )

        # Check Flask secret key in production
        if cls.FLASK_ENV == 'production' and not os.environ.get('FLASK_SECRET_KEY'):
            logger.warning(
                "⚠️  No FLASK_SECRET_KEY set in production. Using temporary key."
            )

        # Validate and create upload directory
        if not os.path.exists(cls.UPLOAD_FOLDER):
            try:
                os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
                logger.info(f"✓ Created upload directory: {cls.UPLOAD_FOLDER}")
            except OSError as e:
                errors.append(f"Failed to create upload directory '{cls.UPLOAD_FOLDER}': {e}")

        # Check directory is writable
        if os.path.exists(cls.UPLOAD_FOLDER) and not os.access(cls.UPLOAD_FOLDER, os.W_OK):
            errors.append(f"Upload directory '{cls.UPLOAD_FOLDER}' is not writable")

        # Raise all errors at once
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)

        logger.info("✓ Configuration validated successfully")
        logger.info(f"✓ AI Provider: {cls.AI_PROVIDER.upper()}")
        logger.info(f"✓ Image Model: {cls.IMAGE_MODEL}")
        logger.info(f"✓ Recipe Model: {cls.RECIPE_MODEL}")

    @classmethod
    def get_api_config(cls) -> dict:
        """
        Get the active AI provider configuration.

        Returns:
            dict: Configuration dictionary with keys:
                - provider: 'openrouter' or 'openai'
                - api_key: API key for the active provider
                - base_url: API base URL (OpenRouter only)

        Example:
            >>> config = Config.get_api_config()
            >>> print(config['provider'])
            'openrouter'
        """
        if cls.AI_PROVIDER == 'openrouter':
            return {
                'provider': 'openrouter',
                'api_key': cls.OPENROUTER_API_KEY,
                'base_url': cls.OPENROUTER_BASE_URL
            }
        elif cls.AI_PROVIDER == 'openai':
            return {
                'provider': 'openai',
                'api_key': cls.OPENAI_API_KEY,
                'base_url': 'https://api.openai.com/v1'
            }
        else:
            raise ValueError("No AI provider configured")


# =============================================================================
# Module Initialization
# =============================================================================

# Configure logging with the specified level
log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Config.LOG_FILE)
    ]
)

# Validate configuration on module import
try:
    Config.validate_config()
except Exception as e:
    logger.error(f"❌ Configuration validation failed: {e}")
    raise


# =============================================================================
# Module Exports
# =============================================================================

__all__ = ['Config']
