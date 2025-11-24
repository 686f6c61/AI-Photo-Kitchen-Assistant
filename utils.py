#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
AI Photo Kitchen Assistant - Utility Functions
================================================================================

Author: 686f6c61 (https://github.com/686f6c61)
Created: 2024-01-15
Updated: 2025-01-24
Version: 2.0.0
License: MIT

Description:
    Collection of utility functions for file handling, image processing,
    and AI prompt generation used throughout the AI Kitchen Assistant.

Functions:
    File Operations:
        - allowed_file(filename): Validate file extensions
        - save_uploaded_file(file): Securely save uploaded files
        - clean_temp_files(filepath): Remove temporary files

    Image Processing:
        - encode_image_to_base64(image_path): Convert images to base64

    AI Prompt Generation:
        - generate_prompt(ingredients, allergies, cuisine_type): Create AI prompts
        - format_ingredients_list(ingredients): Format ingredient lists

Security Considerations:
    - All filenames are sanitized using secure_filename()
    - File extensions are validated against whitelist
    - Temporary files are cleaned up after processing
    - Error handling prevents information disclosure

Usage:
    from utils import save_uploaded_file, encode_image_to_base64, generate_prompt

    # Save uploaded file
    filepath = save_uploaded_file(request.files['image'])

    # Convert to base64
    image_data = encode_image_to_base64(filepath)

    # Generate AI prompt
    prompt = generate_prompt(['chicken', 'rice'], 'gluten', 'italian')

Notes:
    - All functions include comprehensive error handling
    - Logging is enabled for debugging and monitoring
    - Type hints are provided for better IDE support

================================================================================
"""

import os
import base64
import logging
from typing import List, Optional
from werkzeug.utils import secure_filename
from config import Config

# Configure module logger
logger = logging.getLogger(__name__)


def allowed_file(filename: str) -> bool:
    """
    Validate if a file extension is permitted for upload.

    Checks the file extension against a whitelist of allowed image formats
    defined in the application configuration. This is a critical security
    function to prevent upload of malicious files.

    Args:
        filename (str): The name of the file to validate

    Returns:
        bool: True if the file extension is in ALLOWED_EXTENSIONS, False otherwise

    Security:
        - Case-insensitive comparison
        - Only validates extension, not content (MIME type validation recommended)
        - Prevents path traversal attacks via filename sanitization

    Examples:
        >>> allowed_file('vacation.jpg')
        True
        >>> allowed_file('document.pdf')
        False
        >>> allowed_file('photo.PNG')
        True
        >>> allowed_file('malicious.exe')
        False

    See Also:
        - Config.ALLOWED_EXTENSIONS: Set of permitted file extensions
        - save_uploaded_file(): Uses this function for validation
    """
    has_extension = '.' in filename
    if not has_extension:
        return False

    extension = filename.rsplit('.', 1)[1].lower()
    is_allowed = extension in Config.ALLOWED_EXTENSIONS

    if not is_allowed:
        logger.warning(f"Rejected file with disallowed extension: {filename}")

    return is_allowed


def save_uploaded_file(file) -> str:
    """
    Securely save an uploaded file to the temporary upload directory.

    Creates the upload directory if it doesn't exist and saves the file
    with a sanitized filename to prevent security vulnerabilities.

    Args:
        file (FileStorage): The uploaded file object from Flask request

    Returns:
        str: The full absolute path to the saved file

    Raises:
        OSError: If directory creation or file saving fails
        ValueError: If filename is invalid after sanitization

    Security:
        - Filename is sanitized using Werkzeug's secure_filename()
        - Directory creation is protected against race conditions
        - Full path validation prevents directory traversal

    Examples:
        >>> from flask import request
        >>> file = request.files['image']
        >>> path = save_uploaded_file(file)
        >>> print(path)
        '/app/temp_uploads/user_photo_abc123.jpg'

    Notes:
        - Original filename is preserved but sanitized
        - Upload directory is configurable via Config.UPLOAD_FOLDER
        - Files should be cleaned up using clean_temp_files() after processing

    See Also:
        - Config.UPLOAD_FOLDER: Upload directory path
        - secure_filename(): Werkzeug sanitization function
        - clean_temp_files(): Cleanup function
    """
    # Ensure upload directory exists
    if not os.path.exists(Config.UPLOAD_FOLDER):
        try:
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            logger.info(f"Created upload directory: {Config.UPLOAD_FOLDER}")
        except OSError as e:
            logger.error(f"Failed to create upload directory: {e}")
            raise

    # Sanitize filename to prevent security issues
    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError("Invalid filename after sanitization")

    # Generate full path and save file
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    try:
        file.save(filepath)
        logger.info(f"File saved successfully: {filepath} ({os.path.getsize(filepath)} bytes)")
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise

    return filepath


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string for API transmission.

    Reads an image file from disk and converts it to a base64-encoded string
    suitable for sending to AI APIs like OpenAI, OpenRouter, or Anthropic.

    Args:
        image_path (str): Absolute path to the image file

    Returns:
        str: Base64-encoded string representation of the image

    Raises:
        FileNotFoundError: If the image file doesn't exist
        IOError: If there's an error reading the image file
        PermissionError: If the file cannot be accessed

    Examples:
        >>> base64_img = encode_image_to_base64('/tmp/photo.jpg')
        >>> print(base64_img[:50])
        '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBw...'

        >>> # Use with OpenAI API
        >>> image_url = f"data:image/jpeg;base64,{base64_img}"

    Performance:
        - Efficient for images up to 16MB (configured limit)
        - No image compression or optimization performed
        - Memory usage equals file size during encoding

    Notes:
        - Returned string does not include data URI prefix
        - Add appropriate prefix for API usage (e.g., "data:image/jpeg;base64,")
        - Consider image size limits for specific APIs

    See Also:
        - Config.MAX_CONTENT_LENGTH: Maximum file size limit
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            logger.debug(f"Image encoded to base64: {len(encoded)} characters")
            return encoded
    except FileNotFoundError:
        logger.error(f"Image file not found: {image_path}")
        raise
    except Exception as e:
        logger.error(f"Error encoding image to base64: {e}")
        raise


def clean_temp_files(filepath: str) -> None:
    """
    Remove temporary files after processing to free disk space.

    Safely deletes a file from the filesystem, typically used to clean up
    uploaded images after they've been processed by the AI.

    Args:
        filepath (str): Path to the file to be removed

    Returns:
        None

    Raises:
        None: All exceptions are caught and logged

    Examples:
        >>> filepath = '/tmp/uploads/photo.jpg'
        >>> clean_temp_files(filepath)
        # File is removed if it exists

        >>> clean_temp_files('/nonexistent/file.jpg')
        # No error raised, warning logged

    Notes:
        - Errors during file removal are caught and logged but not raised
        - Safe to call on non-existent files
        - Should be called in finally blocks or after processing completion

    Best Practices:
        - Always call after processing uploaded files
        - Use in conjunction with try/finally blocks
        - Monitor logs for repeated failures (may indicate permissions issues)

    See Also:
        - save_uploaded_file(): Creates files that need cleanup
    """
    try:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            os.remove(filepath)
            logger.info(f"Cleaned temporary file: {filepath} ({file_size} bytes freed)")
        else:
            logger.debug(f"File doesn't exist, skipping cleanup: {filepath}")
    except PermissionError as e:
        logger.error(f"Permission denied when cleaning file {filepath}: {e}")
    except Exception as e:
        logger.error(f"Error cleaning temporary file {filepath}: {e}", exc_info=True)


def format_ingredients_list(ingredients: List[str]) -> str:
    """
    Format a list of ingredients into a structured string for AI prompts.

    Cleans and formats ingredient names, removing empty entries and
    creating a bulleted list suitable for inclusion in AI prompts.

    Args:
        ingredients (List[str]): List of ingredient names

    Returns:
        str: Formatted string with bullet points

    Examples:
        >>> ingredients = ['chicken', 'rice', '', 'tomatoes']
        >>> print(format_ingredients_list(ingredients))
        • chicken
        • rice
        • tomatoes

    See Also:
        - generate_prompt(): Uses this function for formatting
    """
    cleaned = [item.strip() for item in ingredients if item.strip()]
    if not cleaned:
        return "• (sin ingredientes especificados)"

    return "• " + "\n• ".join(cleaned)


def generate_prompt(
    detected_items: List[str],
    allergies: str = '',
    cuisine_type: str = ''
) -> str:
    """
    Generate a comprehensive cooking prompt for AI recipe generation.

    Creates a structured, detailed prompt that guides AI models to generate
    professional, practical recipes based on available ingredients, dietary
    restrictions, and cuisine preferences.

    Args:
        detected_items (List[str]): List of available ingredients
        allergies (str, optional): Comma-separated food allergies or restrictions
        cuisine_type (str, optional): Preferred cuisine style (e.g., 'italian', 'mexican')

    Returns:
        str: Formatted prompt string ready for AI model consumption

    Prompt Structure:
        1. Chef role definition with expertise context
        2. Task instructions with clear objectives
        3. Available ingredients list
        4. Dietary restrictions (if provided)
        5. Cuisine preference (if provided)
        6. Output format specifications
        7. Quality guidelines

    Examples:
        >>> ingredients = ['chicken breast', 'tomatoes', 'garlic', 'olive oil']
        >>> prompt = generate_prompt(ingredients, 'dairy', 'italian')
        >>> # Returns detailed prompt for Italian dairy-free chicken recipe

        >>> prompt = generate_prompt(['eggs', 'flour', 'milk'])
        >>> # Returns prompt for any cuisine style recipe

    Prompt Engineering Features:
        - Role-based prompting for better AI responses
        - Structured output format specification
        - Professional tone and terminology
        - Safety guidelines for allergens
        - Flexibility for missing ingredients

    Output Format Specification:
        The generated prompt requests recipes in the following format:
        - Recipe name
        - Ingredients list with quantities
        - Preparation and cooking times
        - Difficulty level
        - Step-by-step instructions
        - Professional tips
        - Shopping list for missing ingredients

    Notes:
        - Optimized for models like GPT-4, Claude, and Gemini
        - Supports Spanish language output
        - Encourages creative yet practical recipes
        - Includes safety considerations for allergies

    See Also:
        - format_ingredients_list(): Helper for ingredient formatting
        - app.py analyze(): Uses this function for recipe generation
    """
    # Clean and format ingredients
    cleaned_items = [item.strip() for item in detected_items if item.strip()]

    if not cleaned_items:
        logger.warning("No ingredients provided for prompt generation")
        cleaned_items = ["ingredientes variados"]

    logger.info(f"Generating prompt with {len(cleaned_items)} ingredients")
    logger.debug(f"Ingredients: {cleaned_items}")

    # Build conditional text blocks
    ingredients_list = format_ingredients_list(cleaned_items)
    allergies_text = f"\n🚫 **RESTRICCIONES ALIMENTARIAS**: {allergies}" if allergies else ""
    cuisine_text = f"\n🌍 **ESTILO CULINARIO PREFERIDO**: {cuisine_type.capitalize()}" if cuisine_type else ""

    # Log dietary restrictions if present
    if allergies:
        logger.info(f"Dietary restrictions: {allergies}")
    if cuisine_type:
        logger.info(f"Cuisine type: {cuisine_type}")

    # Construct comprehensive prompt
    prompt = f"""Rol: Eres un chef profesional con más de 20 años de experiencia en cocina internacional,
especializado en crear recetas caseras deliciosas, prácticas y accesibles para cocineros de todos los niveles.

Tu experiencia abarca desde cocina tradicional hasta técnicas modernas, y tienes un don especial
para crear platos que maximizan el sabor con ingredientes simples y cotidianos.

Instrucciones:
1. Recibes como entrada una lista de ingredientes disponibles, restricciones alimentarias (opcional)
   y preferencia de estilo culinario (opcional).

2. Genera UNA receta completa y detallada que:
   - Aproveche al máximo los ingredientes proporcionados
   - Sea fácil de preparar en cualquier cocina doméstica
   - Tenga un equilibrio perfecto de sabores y texturas
   - Sea visualmente atractiva y apetitosa
   - Incluya consejos profesionales para mejorar el resultado final
   - Respete estrictamente las restricciones alimentarias indicadas

3. La receta debe ser práctica pero inspiradora, mostrando cómo ingredientes comunes
   pueden transformarse en platos extraordinarios.

📦 **INGREDIENTES DISPONIBLES**:
{ingredients_list}
{allergies_text}
{cuisine_text}

Por favor, proporciona la receta con el siguiente formato estructurado:

═══════════════════════════════════════════════════════════════════

# [NOMBRE CREATIVO DE LA RECETA]
*(Un nombre apetitoso que capture la esencia del plato)*

## 🛒 INGREDIENTES

**Ingredientes Principales:**
- Lista clara de ingredientes con cantidades específicas (ej: 2 cucharadas, 1 taza, 200g)
- Marca con ✓ los ingredientes ya disponibles
- Indica alternativas posibles para mayor flexibilidad

**Condimentos y Básicos:**
- Sal, pimienta, aceite y otros básicos necesarios
- Especificar cantidades cuando sea importante

## ⏱ TIEMPO

- ⏲ Preparación: [X] minutos
- 🔥 Cocción: [Y] minutos
- ⌛ Total: [X+Y] minutos
- 👥 Porciones: [N] personas

## 🎚 NIVEL DE DIFICULTAD

- **Nivel**: Fácil / Medio / Difícil
- **Técnicas requeridas**: [listar técnicas culinarias específicas]
- **Utensilios especiales**: [si aplica]

## 👨‍🍳 PREPARACIÓN

### Preparación previa:
1. [Pasos de mise en place, lavado, corte, etc.]

### Cocción:
1. [Instrucciones claras, numeradas y secuenciales]
2. [Incluir temperaturas específicas cuando sea relevante]
3. [Indicar tiempos aproximados para cada paso crítico]
4. [Señalar puntos de control: "cuando esté dorado", "hasta que hierva", etc.]

### Finalización y emplatado:
- [Últimos toques y presentación]
- [Sugerencias de decoración]

## 💡 CONSEJOS DEL CHEF

- **Secreto del sabor**: [Trucos profesionales para potenciar sabores]
- **Punto perfecto**: [Cómo saber cuándo está listo]
- **Variaciones**: [Alternativas o modificaciones posibles]
- **Maridaje**: [Bebidas o acompañamientos recomendados]
- **Conservación**: [Cómo almacenar y recalentar si es necesario]
- **Trucos de tiempo**: [Cómo optimizar la preparación]

## 🍽 VALOR NUTRICIONAL (Aproximado por porción)

- Calorías: ~[X] kcal
- Proteínas: ~[X]g
- Carbohidratos: ~[X]g
- Grasas: ~[X]g

## 🛍 LISTA DE COMPRAS SUGERIDA

*(Solo incluir ingredientes que NO están en la lista original de disponibles)*

**Esenciales para esta receta:**
- [ ] Ingrediente 1 (cantidad aproximada)
- [ ] Ingrediente 2 (cantidad aproximada)

**Opcionales pero recomendados:**
- [ ] Ingrediente opcional 1
- [ ] Ingrediente opcional 2

═══════════════════════════════════════════════════════════════════

**IMPORTANTE**:
- La receta debe ser clara, precisa y fácil de seguir incluso para cocineros principiantes
- Usa un tono cercano, motivador y educativo
- Incluye contexto cultural si el plato tiene origen específico
- Si hay restricciones alimentarias, verifica dos veces que la receta las respeta completamente
- Prioriza ingredientes ya disponibles, sugiere compras solo cuando sea necesario
"""

    logger.debug(f"Prompt generated: {len(prompt)} characters")
    return prompt


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    'allowed_file',
    'save_uploaded_file',
    'encode_image_to_base64',
    'clean_temp_files',
    'format_ingredients_list',
    'generate_prompt'
]
