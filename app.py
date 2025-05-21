"""
AI Kitchen Assistant - Main Application

This module serves as the main entry point for the AI Kitchen Assistant web application.
It provides endpoints for image upload, ingredient analysis, and recipe generation
using OpenAI's GPT-4o models.

Key Components:
- Flask web server setup and configuration
- Image processing and analysis endpoints
- Recipe generation using AI
- Error handling and logging

Dependencies:
- Flask: Web framework
- OpenAI: AI model integration
- Python-dotenv: Environment variable management
"""

import os
import logging
import time
import re
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from openai import OpenAI, OpenAIError
from config import Config
from utils import allowed_file, save_uploaded_file, encode_image_to_base64, clean_temp_files, generate_prompt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask application and load configuration
app = Flask(__name__)
app.config.from_object(Config)

# Initialize OpenAI client with API key from environment variables
try:
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    raise

def make_openai_request_with_retry(request_fn, max_retries=3, initial_delay=1):
    """
    Sistema de reintentos para llamadas a la API de OpenAI con backoff exponencial
    
    Args:
        request_fn: Función que realiza la llamada a la API
        max_retries: Número máximo de reintentos
        initial_delay: Tiempo inicial entre reintentos en segundos
    
    Returns:
        Response de OpenAI o None si fallan todos los intentos
    """
    for attempt in range(max_retries):
        try:
            return request_fn()
        except OpenAIError as e:
            logger.error(f'OpenAI API error (attempt {attempt + 1}/{max_retries}): {str(e)}')
            if attempt < max_retries - 1 and (
                'rate_limit' in str(e).lower() or 
                'server_error' in str(e).lower() or 
                'timeout' in str(e).lower()
            ):
                delay = initial_delay * (2 ** attempt)
                logger.info(f'Retrying in {delay} seconds...')
                time.sleep(delay)
                continue
            raise
        except Exception as e:
            logger.error(f'Unexpected error (attempt {attempt + 1}/{max_retries}): {str(e)}')
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                logger.info(f'Retrying in {delay} seconds...')
                time.sleep(delay)
            else:
                raise
    return None

def clean_recipe_text(recipe_text, ingredients):
    """
    Procesa y formatea el texto de la receta en HTML estructurado
    
    Args:
        recipe_text: Texto de la receta generado por GPT-4
        ingredients: Lista de ingredientes disponibles
    
    Returns:
        str: HTML formateado de la receta con elementos interactivos
    """
    # Limpieza de formato markdown
    recipe_text = recipe_text.replace('**', '').replace('*', '')
    recipe_text = recipe_text.replace('###', '').replace('##', '').replace('#', '')
    
    # Procesamiento del texto en secciones
    lines = recipe_text.split('\n')
    title = ''
    content = []
    shopping_list = []
    in_shopping_list = False
    
    # Extracción de título y contenido
    for line in lines:
        line = line.strip()
        if not title and (
            'nombre de la receta' in line.lower() or 
            line.startswith('"') or 
            line.endswith('"') or
            ':' in line and len(line.split(':')[0]) < 50
        ):
            title = line.replace('Nombre de la receta:', '').replace('"', '').strip()
            continue
            
        if 'LISTA DE COMPRAS SUGERIDA:' in line.upper():
            in_shopping_list = True
            continue
            
        if in_shopping_list and line.strip():
            shopping_list.append(line)
        elif not in_shopping_list:
            content.append(line)
    
    # Procesamiento del título y contenido
    if not title and content:
        title = content[0].strip()
        content = content[1:]
    
    content_text = '\n'.join(content).replace('\n', '<br>')
    content_text = re.sub(r'(\d+\.)|\-', '•', content_text)
    
    # Generación del HTML para la lista de compras
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
            item = item.strip('• -').strip()
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
    
    # Construcción del HTML de la receta
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
    
    # Resaltado de ingredientes disponibles en el texto
    for ingredient in ingredients:
        ingredient = ingredient.strip('.')
        pattern = f'(?i){re.escape(ingredient)}'
        recipe_html = re.sub(pattern, 
                           f'<span class="available-ingredient">{ingredient}</span>', 
                           recipe_html)
    
    return recipe_html

@app.route('/')
def index():
    """Ruta principal que renderiza la interfaz de usuario"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint principal que procesa las imágenes y genera recetas
    
    Flujo:
    1. Validación de entrada y parámetros
    2. Procesamiento de imagen
    3. Detección de ingredientes (nombre de España) con GPT-4o-mini
    4. Generación de recetas con GPT-4
    5. Formateo y respuesta
    """
    logger.info('=== Starting analyze endpoint ===')
    logger.info(f'Request files: {request.files}')
    logger.info(f'Request form data: {dict(request.form)}')
    
    # Validación inicial
    if 'images' not in request.files:
        logger.warning('No files uploaded in request')
        return jsonify({'success': False, 'error': 'No se subieron archivos'})

    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        logger.warning('No files selected or empty filename')
        return jsonify({'success': False, 'error': 'No se seleccionaron archivos'})

    try:
        # Procesamiento de parámetros de entrada
        num_recipes = min(int(request.form.get('num_recipes', 1)), 3)
        allergies = request.form.get('allergies', '').strip()
        main_ingredients = request.form.get('main_ingredients', '').strip()
        cuisine_type = request.form.get('cuisine_type', '').strip()
        
        logger.info(f'Processing parameters:')
        logger.info(f'- Number of recipes: {num_recipes}')
        logger.info(f'- Allergies: {allergies}')
        logger.info(f'- Main ingredients: {main_ingredients}')
        logger.info(f'- Cuisine type: {cuisine_type}')
        
        # Función para la llamada al modelo de visión
        def vision_request():
            return client.chat.completions.create(
                model=app.config['IMAGE_MODEL'],
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analiza esta imagen de una nevera y lista los ingredientes que puedes identificar con nombre de España. Responde solo con la lista de ingredientes separados por comas, sin puntos ni otros caracteres adicionales."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                max_tokens=2000
            )

        # Procesamiento de imagen
        file = files[0]
        logger.info(f'Processing file: {file.filename}')
        
        if not allowed_file(file.filename):
            logger.warning(f'Invalid file type: {file.filename}')
            return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'})

        filepath = save_uploaded_file(file)
        logger.info(f'File saved successfully at: {filepath}')
        
        base64_image = encode_image_to_base64(filepath)
        logger.info('Image encoded successfully to base64')

        # Análisis de imagen con IA
        logger.info('Sending request to OpenAI Vision API for ingredient detection')
        vision_response = make_openai_request_with_retry(vision_request)

        if not vision_response:
            logger.error('Failed to get response from Vision API after retries')
            return jsonify({
                'success': False,
                'error': 'Error al analizar la imagen. Por favor, intenta de nuevo.'
            })

        # Procesamiento de ingredientes detectados
        ingredients_text = vision_response.choices[0].message.content
        ingredients = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()] if ingredients_text else []
        logger.info(f'Detected ingredients: {ingredients}')

        # Incorporación de ingredientes adicionales
        if main_ingredients:
            additional_ingredients = [ing.strip() for ing in main_ingredients.split(',')]
            ingredients.extend(additional_ingredients)
            
        # Generación de recetas
        recipes = []
        recipe_prompt = generate_prompt(ingredients, allergies, cuisine_type)

        # System message with chef's role and instructions
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
            
            Siempre responde en español y usa un tono cercano y motivador."""
        }
        
        for i in range(num_recipes):
            def recipe_request():
                return client.chat.completions.create(
                    model=app.config['RECIPE_MODEL'],
                    messages=[
                        system_message,
                        {"role": "user", "content": recipe_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=2500
                )

            logger.info(f'Sending request to OpenAI API for recipe generation #{i+1}')
            recipe_response = make_openai_request_with_retry(recipe_request)

            if not recipe_response:
                logger.error(f'Failed to get response from GPT-4 API after retries for recipe #{i+1}')
                continue
            
            recipe_text = recipe_response.choices[0].message.content
            if recipe_text:
                recipe_html = clean_recipe_text(recipe_text, ingredients)
                recipes.append(recipe_html)
        
        # Limpieza y respuesta
        clean_temp_files(filepath)
        logger.info('Temporary files cleaned up')

        return jsonify({
            'success': True,
            'ingredients': ingredients,
            'recipes': recipes
        })

    except OpenAIError as e:
        logger.error(f'OpenAI API error: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Error en el servicio de OpenAI: {str(e)}'
        })
    except Exception as e:
        logger.error(f'Unexpected error during processing: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Error inesperado. Por favor, intenta de nuevo.'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
