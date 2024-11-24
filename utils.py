import os
import base64
import logging
from werkzeug.utils import secure_filename
from config import Config

# Configuración del sistema de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """
    Verifica si la extensión del archivo está permitida
    
    Args:
        filename (str): Nombre del archivo a verificar
        
    Returns:
        bool: True si la extensión está permitida, False en caso contrario
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """
    Guarda el archivo subido en el directorio temporal
    
    Args:
        file (FileStorage): Objeto del archivo subido
        
    Returns:
        str: Ruta del archivo guardado
        
    Raises:
        OSError: Si hay problemas creando el directorio o guardando el archivo
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
    Codifica una imagen en base64 para enviarla a la API de OpenAI
    
    Args:
        image_path (str): Ruta al archivo de imagen
        
    Returns:
        str: Imagen codificada en base64
        
    Raises:
        IOError: Si hay problemas leyendo el archivo
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def clean_temp_files(filepath):
    """
    Elimina archivos temporales después de procesarlos
    
    Args:
        filepath (str): Ruta del archivo a eliminar
        
    Raises:
        Exception: Si hay problemas eliminando el archivo
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Temporary file cleaned: {filepath}")
    except Exception as e:
        logger.error(f"Error cleaning temporary file: {e}")

def generate_prompt(detected_items, allergies='', cuisine_type=''):
    """
    Genera el prompt para GPT-4 con los ingredientes detectados y preferencias
    
    Args:
        detected_items (list): Lista de ingredientes detectados en la imagen
        allergies (str, optional): Alergias o restricciones alimentarias
        cuisine_type (str, optional): Tipo de cocina preferida
        
    Returns:
        str: Prompt formateado para enviar a GPT-4
        
    Example:
        >>> generate_prompt(['tomate', 'cebolla'], 'gluten', 'mexicana')
        'Con los siguientes ingredientes encontrados en tu nevera:
         tomate, cebolla
         Por favor, ten en cuenta las siguientes alergias/restricciones: gluten
         Preferencia de cocina: mexicana
         ...'
    """
    # Limpieza y formateo de ingredientes
    cleaned_items = [item.strip() for item in detected_items if item.strip()]
    logger.info(f"Cleaned ingredients list: {cleaned_items}")
    
    # Construcción de textos condicionales
    allergies_text = f"\nPor favor, ten en cuenta las siguientes alergias/restricciones: {allergies}" if allergies else ""
    cuisine_text = f"\nPreferencia de cocina: {cuisine_type}" if cuisine_type else ""
    
    # Construcción del prompt completo
    return f"""
    Con los siguientes ingredientes encontrados en tu nevera:
    {', '.join(cleaned_items)}
    {allergies_text}
    {cuisine_text}
    
    Por favor:
    1. Sugiere una receta casera que:
       - Use la mayoría de estos ingredientes de manera eficiente
       - Sea fácil de preparar y perfecta para cocinar en casa
       - {"Se ajuste al estilo de cocina " + cuisine_type if cuisine_type else "Sea versátil y deliciosa"}
       
    2. Proporciona los siguientes detalles de la receta:
       - Nombre de la receta (algo creativo y apetitoso)
       - Lista de ingredientes con cantidades aproximadas (por ejemplo: "2 tazas", "1 puñado", etc.)
       - Alternativas para ingredientes que podrían faltar o ser sustituidos
       - Pasos de preparación detallados y fáciles de seguir
       - Tiempo estimado de preparación
       - Nivel de dificultad (Fácil/Medio/Difícil)
       - Tips o consejos adicionales para mejorar el resultado
    
    3. Al final de la receta, agrega una sección titulada "LISTA DE COMPRAS SUGERIDA:" que incluya:
       - Lista de ingredientes adicionales recomendados que no están en la nevera pero mejorarían significativamente la receta
       - Ingredientes básicos que podrían faltar para preparaciones futuras
       - Cantidades sugeridas para cada item
    
    {"IMPORTANTE: Asegúrate de NO incluir ningún ingrediente que pueda causar alergias." if allergies else ""}
    
    Por favor, responde en formato claro y estructurado, usando saltos de línea para separar las secciones.
    """
