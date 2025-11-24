#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
AI Photo Kitchen Assistant - Main Application
================================================================================

Author: 686f6c61 (https://github.com/686f6c61)
Created: 2024-01-15
Updated: 2025-01-24
Version: 2.0.0
License: MIT

Description:
    Flask web application that uses AI to analyze refrigerator photos and
    generate personalized recipes. Supports multiple AI providers including
    OpenRouter (recommended) and OpenAI, allowing access to various models
    like GPT-4, Claude, Gemini, and more.

Key Features:
    - Multi-provider AI support (OpenRouter, OpenAI)
    - Image analysis for ingredient detection
    - Personalized recipe generation
    - Dietary restrictions and cuisine preferences
    - Rate limiting for API protection
    - Comprehensive error handling and logging
    - Automatic temporary file cleanup

Architecture:
    - Flask: Web framework
    - OpenAI SDK: Compatible with both OpenAI and OpenRouter APIs
    - Environment-based configuration
    - Modular utility functions

Endpoints:
    GET  /           - Main web interface
    POST /analyze    - Image analysis and recipe generation endpoint

Dependencies:
    - Flask: Web server and routing
    - OpenAI: AI API client (works with OpenRouter too)
    - python-dotenv: Environment configuration
    - See requirements.txt for complete list

Environment Variables:
    Required:
        - OPENROUTER_API_KEY or OPENAI_API_KEY
        - FLASK_SECRET_KEY

    Optional:
        - IMAGE_MODEL: Model for image analysis
        - RECIPE_MODEL: Model for recipe generation
        - See .env.example for complete list

Usage:
    # Development
    python app.py

    # Production
    gunicorn -w 4 -b 0.0.0.0:5050 app:app

Security Considerations:
    - Rate limiting enabled
    - File type validation
    - Secure filename sanitization
    - Environment-based secrets
    - Comprehensive input validation
    - Automatic cleanup of uploaded files

Performance:
    - Exponential backoff for API retries
    - Efficient base64 encoding
    - Temporary file management
    - Configurable rate limits

Notes:
    - This is version 2.0.0 with OpenRouter integration
    - Supports multiple AI models through OpenRouter
    - Backward compatible with OpenAI API
    - All API keys should be stored in .env file

Author Contact:
    GitHub: https://github.com/686f6c61

================================================================================
"""

import os
import logging
import time
import re
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from openai import OpenAI, OpenAIError
from config import Config
from utils import (
    allowed_file,
    save_uploaded_file,
    encode_image_to_base64,
    clean_temp_files,
    generate_prompt
)
from dotenv import load_dotenv

# =============================================================================
# Application Initialization
# =============================================================================

# Load environment variables from .env file
load_dotenv()

# Configure comprehensive logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Config.LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for cross-origin requests (configure domains in production)
CORS(app)

# Initialize rate limiter to prevent API abuse
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[
        f"{Config.RATE_LIMIT_PER_MINUTE}/minute",
        f"{Config.RATE_LIMIT_PER_HOUR}/hour"
    ],
    storage_uri="memory://"
)

# =============================================================================
# AI Client Initialization
# =============================================================================

try:
    api_config = Config.get_api_config()

    if api_config['provider'] == 'openrouter':
        # Initialize OpenAI client with OpenRouter configuration
        client = OpenAI(
            api_key=api_config['api_key'],
            base_url=api_config['base_url']
        )
        logger.info("✓ OpenRouter client initialized successfully")
        logger.info(f"  - Base URL: {api_config['base_url']}")
        logger.info(f"  - Image Model: {Config.IMAGE_MODEL}")
        logger.info(f"  - Recipe Model: {Config.RECIPE_MODEL}")
    else:
        # Initialize standard OpenAI client
        client = OpenAI(api_key=api_config['api_key'])
        logger.info("✓ OpenAI client initialized successfully")
        logger.info(f"  - Image Model: {Config.IMAGE_MODEL}")
        logger.info(f"  - Recipe Model: {Config.RECIPE_MODEL}")

except Exception as e:
    logger.error(f"❌ Failed to initialize AI client: {str(e)}")
    raise


# =============================================================================
# Helper Functions
# =============================================================================

def make_ai_request_with_retry(request_fn, max_retries=3, initial_delay=1):
    """
    Execute AI API requests with exponential backoff retry logic.

    Implements a robust retry mechanism for handling transient API errors,
    rate limits, and network issues when communicating with AI providers.

    Args:
        request_fn (callable): Function that makes the API call
        max_retries (int): Maximum number of retry attempts (default: 3)
        initial_delay (int): Initial delay in seconds before first retry (default: 1)

    Returns:
        Response object from the AI API, or None if all retries fail

    Retry Strategy:
        - Exponential backoff: delay doubles with each retry
        - Retry on: rate limits, server errors, timeouts
        - No retry on: authentication errors, invalid requests

    Examples:
        >>> def api_call():
        ...     return client.chat.completions.create(...)
        >>> response = make_ai_request_with_retry(api_call)

    Notes:
        - Logs each retry attempt with delay information
        - Last exception is re-raised if all retries fail
        - Suitable for both vision and text generation requests
    """
    for attempt in range(max_retries):
        try:
            response = request_fn()
            if attempt > 0:
                logger.info(f"✓ Request succeeded on attempt {attempt + 1}")
            return response

        except OpenAIError as e:
            error_msg = str(e).lower()
            logger.error(f'AI API error (attempt {attempt + 1}/{max_retries}): {str(e)}')

            # Determine if we should retry
            should_retry = (
                attempt < max_retries - 1 and (
                    'rate_limit' in error_msg or
                    'server_error' in error_msg or
                    'timeout' in error_msg or
                    '429' in error_msg or
                    '500' in error_msg or
                    '503' in error_msg
                )
            )

            if should_retry:
                delay = initial_delay * (2 ** attempt)
                logger.info(f'⏳ Retrying in {delay} seconds...')
                time.sleep(delay)
                continue
            else:
                logger.error(f'❌ Non-retryable error or max retries exceeded')
                raise

        except Exception as e:
            logger.error(f'Unexpected error (attempt {attempt + 1}/{max_retries}): {str(e)}')
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                logger.info(f'⏳ Retrying in {delay} seconds...')
                time.sleep(delay)
            else:
                raise

    return None


def clean_recipe_text(recipe_text, ingredients):
    """
    Process and format AI-generated recipe text into structured HTML.

    Transforms raw recipe text from AI into properly formatted, interactive
    HTML with highlighted ingredients, structured sections, and copy buttons.

    Args:
        recipe_text (str): Raw recipe text from AI model
        ingredients (list): List of available ingredients to highlight

    Returns:
        str: HTML-formatted recipe with interactive elements

    HTML Structure:
        - Recipe card container with title
        - Copy button for full recipe
        - Formatted recipe content with sections
        - Shopping list (if present)
        - Ingredient highlighting

    Processing Steps:
        1. Remove markdown formatting
        2. Extract title and sections
        3. Parse shopping list
        4. Convert to HTML structure
        5. Highlight available ingredients
        6. Add interactive buttons

    Examples:
        >>> recipe = "# Pasta Carbonara\\n## Ingredients\\n- pasta..."
        >>> html = clean_recipe_text(recipe, ['pasta', 'eggs'])
        >>> # Returns formatted HTML with highlighted 'pasta' and 'eggs'

    Notes:
        - Preserves recipe structure and formatting
        - Highlights available ingredients in green
        - Shopping list items are separately formatted
        - Copy buttons include Font Awesome icons
    """
    # Clean markdown formatting
    recipe_text = recipe_text.replace('**', '').replace('*', '')
    recipe_text = recipe_text.replace('###', '').replace('##', '').replace('#', '')

    # Parse recipe text
    lines = recipe_text.split('\n')
    title = ''
    content = []
    shopping_list = []
    in_shopping_list = False

    # Extract title, content, and shopping list
    for line in lines:
        line = line.strip()
        if not title and (
            'nombre de la receta' in line.lower() or
            line.startswith('"') or
            line.endswith('"') or
            (':' in line and len(line.split(':')[0]) < 50)
        ):
            title = line.replace('Nombre de la receta:', '').replace('"', '').strip()
            continue

        if 'LISTA DE COMPRAS' in line.upper() or 'SHOPPING LIST' in line.upper():
            in_shopping_list = True
            continue

        if in_shopping_list and line.strip():
            shopping_list.append(line)
        elif not in_shopping_list:
            content.append(line)

    # Extract title from content if not found
    if not title and content:
        title = content[0].strip()
        content = content[1:]

    # Format content
    content_text = '\n'.join(content).replace('\n', '<br>')
    content_text = re.sub(r'(\d+\.)|\-', '•', content_text)

    # Generate shopping list HTML
    shopping_list_html = ''
    if shopping_list:
        shopping_list_html = '''
        <div class="shopping-list">
            <div class="shopping-list-header">
                <i class="fas fa-shopping-cart"></i>
                <h3>Lista de compra sugerida</h3>
                <button class="btn btn-outline-primary copy-shopping-list" title="Copiar lista de compra">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            <ul class="shopping-list-items">
        '''
        for item in shopping_list:
            item = item.strip('• -[]').strip()
            if item:
                shopping_list_html += f'''
                    <li class="shopping-list-item">
                        <i class="fas fa-shopping-basket"></i>
                        <span>{item}</span>
                    </li>'''
        shopping_list_html += '''
            </ul>
        </div>
        '''

    # Build recipe HTML structure
    recipe_html = f'''
    <div class="recipe-card">
        <div class="recipe-header">
            <h2 class="recipe-title">{title}</h2>
            <button class="btn btn-outline-primary copy-button" title="Copiar receta">
                <i class="fas fa-copy"></i>
            </button>
        </div>
        <div class="recipe-content">{content_text}</div>
        {shopping_list_html}
    </div>
    '''

    # Highlight available ingredients
    for ingredient in ingredients:
        ingredient = ingredient.strip('.')
        if len(ingredient) > 2:  # Only highlight meaningful ingredients
            pattern = f'(?i)\\b{re.escape(ingredient)}\\b'
            recipe_html = re.sub(
                pattern,
                f'<span class="available-ingredient">{ingredient}</span>',
                recipe_html
            )

    return recipe_html


# =============================================================================
# Routes
# =============================================================================

@app.route('/')
def index():
    """
    Serve the main web interface.

    Returns:
        HTML: Rendered index.html template with web interface

    Template Variables:
        - Config values are accessible via app.config
    """
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE}/minute")
def analyze():
    """
    Main endpoint for image analysis and recipe generation.

    Processes uploaded refrigerator images, detects ingredients using vision AI,
    and generates personalized recipes based on available ingredients, dietary
    restrictions, and cuisine preferences.

    Request Format:
        Method: POST
        Content-Type: multipart/form-data

        Files:
            - images: Image file(s) of refrigerator contents

        Form Data:
            - num_recipes (int, optional): Number of recipes to generate (1-3)
            - allergies (str, optional): Comma-separated allergies/restrictions
            - main_ingredients (str, optional): Additional ingredients to include
            - cuisine_type (str, optional): Preferred cuisine style

    Response Format:
        Success (200):
            {
                "success": true,
                "ingredients": ["ingredient1", "ingredient2", ...],
                "recipes": ["<html>recipe1</html>", ...]
            }

        Error (200):
            {
                "success": false,
                "error": "Error description"
            }

    Processing Flow:
        1. Validate request and file uploads
        2. Save and encode image to base64
        3. Send image to vision AI for ingredient detection
        4. Parse detected ingredients
        5. Generate recipe prompt with preferences
        6. Request recipe(s) from AI
        7. Format and return results
        8. Clean up temporary files

    Rate Limiting:
        - Per IP address
        - Configured via RATE_LIMIT_PER_MINUTE
        - Returns 429 if limit exceeded

    Security:
        - File type validation
        - Secure filename handling
        - Input sanitization
        - Automatic cleanup of uploads

    Examples:
        >>> # Using curl
        >>> curl -X POST http://localhost:5050/analyze \\
        ...   -F "images=@fridge.jpg" \\
        ...   -F "allergies=dairy" \\
        ...   -F "cuisine_type=italian"

    Notes:
        - Supports both OpenRouter and OpenAI
        - Automatically retries on transient errors
        - Logs all processing steps for debugging
        - Cleans up temporary files even on error
    """
    logger.info('=' * 70)
    logger.info('Starting recipe analysis request')
    logger.info('=' * 70)
    logger.info(f'Request files: {list(request.files.keys())}')
    logger.info(f'Request form: {dict(request.form)}')

    # Validate file upload
    if 'images' not in request.files:
        logger.warning('❌ No files in request')
        return jsonify({
            'success': False,
            'error': 'No se subieron archivos. Por favor, selecciona una imagen.'
        })

    files = request.files.getlist('images')
    if not files or not files[0].filename:
        logger.warning('❌ No files selected or empty filename')
        return jsonify({
            'success': False,
            'error': 'No se seleccionaron archivos válidos.'
        })

    filepath = None

    try:
        # Parse and validate request parameters
        num_recipes = min(max(int(request.form.get('num_recipes', 1)), 1), 3)
        allergies = request.form.get('allergies', '').strip()
        main_ingredients = request.form.get('main_ingredients', '').strip()
        cuisine_type = request.form.get('cuisine_type', '').strip()

        logger.info('📋 Request parameters:')
        logger.info(f'  - Recipes to generate: {num_recipes}')
        logger.info(f'  - Allergies: {allergies or "None"}')
        logger.info(f'  - Additional ingredients: {main_ingredients or "None"}')
        logger.info(f'  - Cuisine type: {cuisine_type or "Any"}')

        # Process first uploaded file
        file = files[0]
        logger.info(f'📁 Processing file: {file.filename}')

        # Validate file type
        if not allowed_file(file.filename):
            logger.warning(f'❌ Invalid file type: {file.filename}')
            return jsonify({
                'success': False,
                'error': 'Tipo de archivo no permitido. Use JPG, PNG o WEBP.'
            })

        # Save and encode image
        filepath = save_uploaded_file(file)
        logger.info(f'✓ File saved: {filepath}')

        base64_image = encode_image_to_base64(filepath)
        logger.info(f'✓ Image encoded to base64 ({len(base64_image)} chars)')

        # =================================================================
        # STEP 1: Ingredient Detection with Vision AI
        # =================================================================
        logger.info('🔍 Step 1: Analyzing image for ingredients...')

        def vision_request():
            return client.chat.completions.create(
                model=Config.IMAGE_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analiza esta imagen y lista todos los ingredientes y alimentos que puedes identificar. Usa nombres en español de España. Responde solo con la lista de ingredientes separados por comas, sin puntos ni otros caracteres adicionales."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }],
                max_tokens=2000,
                temperature=0.3
            )

        vision_response = make_ai_request_with_retry(vision_request)

        if not vision_response:
            logger.error('❌ Failed to get response from Vision AI')
            return jsonify({
                'success': False,
                'error': 'Error al analizar la imagen. Por favor, intenta de nuevo.'
            })

        # Parse detected ingredients
        ingredients_text = vision_response.choices[0].message.content
        ingredients = [
            ing.strip()
            for ing in ingredients_text.split(',')
            if ing.strip()
        ] if ingredients_text else []

        logger.info(f'✓ Detected {len(ingredients)} ingredients: {ingredients[:5]}...')

        # Add manually specified ingredients
        if main_ingredients:
            additional = [ing.strip() for ing in main_ingredients.split(',')]
            ingredients.extend(additional)
            logger.info(f'✓ Added {len(additional)} manual ingredients')

        if not ingredients:
            logger.warning('⚠️  No ingredients detected')
            return jsonify({
                'success': False,
                'error': 'No se detectaron ingredientes en la imagen. Intenta con una foto más clara.'
            })

        # =================================================================
        # STEP 2: Recipe Generation with AI
        # =================================================================
        logger.info(f'👨‍🍳 Step 2: Generating {num_recipes} recipe(s)...')

        recipes = []
        recipe_prompt = generate_prompt(ingredients, allergies, cuisine_type)

        # System message for consistent recipe generation
        system_message = {
            "role": "system",
            "content": """Eres un chef profesional con más de 20 años de experiencia en cocina internacional,
especializado en crear recetas caseras deliciosas, prácticas y accesibles para cocineros de todos los niveles.

Tu tarea es crear recetas que sean:
- Fáciles de seguir, incluso para principiantes
- Con ingredientes accesibles
- Con instrucciones claras y precisas
- Incluyendo consejos profesionales para mejorar los resultados
- Con un toque personal y amigable

Siempre responde en español de España y usa un tono cercano y motivador."""
        }

        # Generate requested number of recipes
        for i in range(num_recipes):
            logger.info(f'  Generating recipe {i + 1}/{num_recipes}...')

            def recipe_request():
                return client.chat.completions.create(
                    model=Config.RECIPE_MODEL,
                    messages=[
                        system_message,
                        {"role": "user", "content": recipe_prompt}
                    ],
                    temperature=0.8,  # Higher for creativity
                    max_tokens=3000
                )

            recipe_response = make_ai_request_with_retry(recipe_request)

            if not recipe_response:
                logger.error(f'❌ Failed to generate recipe {i + 1}')
                continue

            recipe_text = recipe_response.choices[0].message.content
            if recipe_text:
                recipe_html = clean_recipe_text(recipe_text, ingredients)
                recipes.append(recipe_html)
                logger.info(f'  ✓ Recipe {i + 1} generated successfully')

        # Final cleanup and response
        clean_temp_files(filepath)
        logger.info('✓ Temporary files cleaned up')

        logger.info('=' * 70)
        logger.info(f'✅ Analysis complete: {len(ingredients)} ingredients, {len(recipes)} recipes')
        logger.info('=' * 70)

        return jsonify({
            'success': True,
            'ingredients': ingredients,
            'recipes': recipes
        })

    except OpenAIError as e:
        logger.error(f'❌ AI API error: {str(e)}')
        if filepath:
            clean_temp_files(filepath)
        return jsonify({
            'success': False,
            'error': f'Error en el servicio de IA. Por favor, intenta de nuevo más tarde.'
        })

    except Exception as e:
        logger.error(f'❌ Unexpected error: {str(e)}', exc_info=True)
        if filepath:
            clean_temp_files(filepath)
        return jsonify({
            'success': False,
            'error': 'Error inesperado. Por favor, verifica tu imagen e intenta de nuevo.'
        })


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == '__main__':
    logger.info('=' * 70)
    logger.info('🍳 AI Photo Kitchen Assistant Starting...')
    logger.info('=' * 70)
    logger.info(f'Environment: {Config.FLASK_ENV}')
    logger.info(f'AI Provider: {Config.AI_PROVIDER.upper()}')
    logger.info(f'Server: http://{Config.HOST}:{Config.PORT}')
    logger.info('=' * 70)

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=(Config.FLASK_ENV == 'development')
    )
