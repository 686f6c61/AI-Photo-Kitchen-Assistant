"""
Utility Functions for AI Kitchen Assistant

This module contains helper functions for file handling, image processing, 
and prompt generation used by the AI Kitchen Assistant application.

Key Functions:
- File handling: save_uploaded_file, clean_temp_files
- Image processing: encode_image_to_base64
- AI Prompt generation: generate_prompt

Dependencies:
- Python standard libraries: os, base64, logging
- Werkzeug: For secure file handling
"""

import os
import base64
import logging
from werkzeug.utils import secure_filename
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """
    Check if the file extension is allowed for upload.
    
    Args:
        filename (str): The name of the file to check
        
    Returns:
        bool: True if the file extension is in ALLOWED_EXTENSIONS, False otherwise
        
    Example:
        >>> allowed_file('image.jpg')
        True
        >>> allowed_file('document.pdf')
        False
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """
    Save the uploaded file to the temporary upload directory.
    
    Args:
        file (FileStorage): The uploaded file object from Flask
        
    Returns:
        str: The full path to the saved file
        
    Raises:
        OSError: If there's an issue creating the directory or saving the file
        
    Example:
        >>> file = request.files['image']
        >>> save_uploaded_file(file)
        'temp_uploads/secure_filename.jpg'
    """
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    logger.info(f"File saved successfully: {filepath}")
    return filepath

def encode_image_to_base64(image_path):
    """
    Encode an image file to base64 string for the OpenAI API.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Base64 encoded string of the image
        
    Raises:
        IOError: If there's an error reading the image file
        
    Example:
        >>> encode_image_to_base64('temp_uploads/image.jpg')
        'iVBORw0KGgoAAAANSUhEUgAA...'
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def clean_temp_files(filepath):
    """
    Remove temporary files after processing to free up disk space.
    
    Args:
        filepath (str): Path to the file to be removed
        
    Note:
        Errors during file removal are caught and logged but not raised.
        
    Example:
        >>> clean_temp_files('temp_uploads/image.jpg')
        # Logs: Temporary file cleaned: temp_uploads/image.jpg
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Temporary file cleaned: {filepath}")
    except Exception as e:
        logger.error(f"Error cleaning temporary file: {e}", exc_info=True)

def generate_prompt(detected_items, allergies='', cuisine_type=''):
    """
    Generate a detailed cooking prompt for the AI model based on available ingredients.
    
    This function creates a structured prompt that guides the AI to generate a recipe
    using the provided ingredients, while considering dietary restrictions and cuisine preferences.
    
    Args:
        detected_items (list): List of ingredients detected in the image
        allergies (str, optional): Food allergies or dietary restrictions (comma-separated)
        cuisine_type (str, optional): Preferred cuisine style (e.g., 'italian', 'mexican')
        
    Returns:
        str: Formatted prompt string ready to be sent to the AI model
        
    Example:
        >>> generate_prompt(['chicken', 'tomatoes', 'garlic'], 'dairy', 'italian')
        'Rol: Eres un chef profesional...'
        
    Note:
        The prompt is designed to work with OpenAI's GPT models and includes
        specific formatting instructions for recipe generation.
    """
    # Limpieza y formateo de ingredientes
    cleaned_items = [item.strip() for item in detected_items if item.strip()]
    logger.info(f"Cleaned ingredients list: {cleaned_items}")
    
    # Construcción del prompt con el rol y las instrucciones detalladas
    prompt = """Rol: Eres un chef profesional con más de 20 años de experiencia en cocina internacional, 
    especializado en crear recetas caseras deliciosas, prácticas y accesibles para cocineros de todos los niveles.

Instrucciones:
1. Recibes como entrada una lista de ingredientes disponibles, un estilo de cocina (opcional) y restricciones por alergias (opcional).
2. Genera UNA receta que:
   - Aproveche al máximo los ingredientes proporcionados.
   - Sea fácil de preparar en cualquier cocina doméstica.
   - Tenga un equilibrio perfecto de sabores y texturas.
   - Sea visualmente atractiva y apetitosa.
   - Incluya consejos profesionales para mejorar el resultado final.

Ingredientes disponibles:
{ingredients_list}

{allergies_text}
{cuisine_text}

Por favor, proporciona la receta con el siguiente formato:

[Receta]

# [NOMBRE DE LA RECETA]
*(Un nombre creativo y apetitoso que refleje la esencia del plato)*

## 🛒 INGREDIENTES
- Lista clara de ingredientes con cantidades específicas (ej: 2 cucharadas, 1 taza, 200g)
- Alternativas posibles para ingredientes que podrían faltar
- Especificar si algún ingrediente es opcional

## ⏱ TIEMPO DE PREPARACIÓN
- Preparación: [X] minutos
- Cocción: [Y] minutos
- Total: [X+Y] minutos

## 🎚 DIFICULTAD
- Nivel: Fácil/Medio/Difícil
- Técnicas requeridas: [listar técnicas]

## 👨‍🍳 PREPARACIÓN
1. Instrucciones claras y secuenciales, numeradas.
2. Incluir tiempos aproximados para cada paso importante.
3. Señalar puntos clave donde el cocinero debe prestar atención.
4. Incluir consejos de presentación.

## 💡 CONSEJOS DEL CHEF
- Trucos profesionales para mejorar el sabor
- Cómo saber cuándo está en su punto
- Posibles variaciones de la receta
- Cómo conservar y recalentar si es necesario

## 🛍 LISTA DE COMPRAS SUGERIDA
*(Solo incluir ingredientes que no estén en la lista original)*
- Ingredientes esenciales para esta receta:
  - [ ] Ingrediente 1 (cantidad)
  - [ ] Ingrediente 2 (cantidad)
- Básicos de despensa recomendados:
  - [ ] Ingrediente básico 1
  - [ ] Ingrediente básico 2

[Nota: La receta debe ser clara, precisa y fácil de seguir incluso para principiantes. Usar un tono cercano y motivador.]
"""
    
    # Construcción de textos condicionales
    ingredients_list = "• " + "\n• ".join(cleaned_items)
    allergies_text = f"\n🚫 RESTRICCIONES ALIMENTARIAS: {allergies}" if allergies else ""
    cuisine_text = f"\n🌍 ESTILO CULINARIO: {cuisine_type.capitalize()}" if cuisine_type else ""
    
    return prompt.format(
        ingredients_list=ingredients_list,
        allergies_text=allergies_text,
        cuisine_text=cuisine_text,
        allergies=allergies
    )
