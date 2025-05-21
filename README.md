# 🍳 Recetas desde tu nevera - AI Kitchen Assistant

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)

## 🔍 Descripción

Una aplicación web **Proof of Concept (POC)** que utiliza inteligencia artificial para analizar el contenido de tu nevera y generar recetas personalizadas. Combina GPT-4o-mini para el reconocimiento de ingredientes y la generación de recetas creativas y detalladas.

> **Nota**: Este proyecto es un Proof of Concept (POC) diseñado para demostrar las capacidades de la IA en la generación de recetas a partir de imágenes. No está pensado para uso en producción sin mejoras adicionales.

![Fotos Alacena](/img/recetas2.png)
![Recetas](/img/recetas1.png)

## 🌟 Características

- **Análisis de imágenes**: Utiliza GPT-4o-mini para identificar ingredientes en fotos de tu nevera
- **Recetas personalizadas**: Genera recetas basadas en los ingredientes disponibles
- **Preferencias culinarias**: Permite especificar tipo de cocina (mexicana, italiana, española, etc.)
- **Gestión de alergias**: Sistema para indicar restricciones alimentarias
- **Salida profesional**: Recetas con formato de chef profesional, incluyendo:
  - Lista de ingredientes con cantidades
  - Pasos detallados de preparación
  - Tiempos de cocción
  - Nivel de dificultad
  - Consejos del chef
- **Interfaz intuitiva**: Drag & drop de imágenes para fácil uso
  - Captura directa desde cámara web
  - Sistema de etiquetas para ingredientes principales
- **Copiar al Portapapeles**: Botones para copiar recetas y listas de compra con feedback visual

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- Cuenta de OpenAI con API key
- Git

### Obtener una API key de OpenAI

1. Regístrate o inicia sesión en [OpenAI](https://platform.openai.com/signup)
2. Ve a la sección [API Keys](https://platform.openai.com/api-keys)
3. Haz clic en "Create new secret key"
4. Copia la clave generada (asegúrate de guardarla en un lugar seguro, ya que no podrás verla de nuevo)

### Pasos de Instalación

1. Clona este repositorio
   ```bash
   git clone https://github.com/tu-usuario/AI-Photo-Kitchen-Assistant.git
   cd AI-Photo-Kitchen-Assistant
   ```

2. Copia el archivo de configuración de ejemplo
   ```bash
   cp .env.example .env
   ```

3. Edita el archivo `.env` y añade tu API key de OpenAI
   ```
   OPENAI_API_KEY=tu-api-key-aquí
   ```

4. Ejecuta el script de instalación y configuración
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

## 💻 Uso

1. Inicia la aplicación (si no está ya ejecutándose)
   ```bash
   ./run.sh
   ```

2. Abre tu navegador y ve a `http://localhost:5050`

3. Sube una foto de los ingredientes disponibles en tu nevera o alacena

4. Añade información adicional (opcional):
   - Alergias o restricciones alimentarias
   - Tipo de cocina preferida

5. Haz clic en "Generar Recetas" y espera a que la IA procese la información

## ⚙️ Configuración

El proyecto utiliza variables de entorno para su configuración. Puedes personalizar los siguientes parámetros en el archivo `.env`:

```
# OpenAI API Key (required)
OPENAI_API_KEY=tu-api-key-aqui

# Flask configuration (optional)
FLASK_SECRET_KEY=una-clave-secreta-segura
FLASK_ENV=development

# Application settings
MAX_CONTENT_LENGTH=16777216  # 16MB max file size
UPLOAD_FOLDER=temp_uploads

# Model configurations
IMAGE_MODEL=gpt-4o-mini
RECIPE_MODEL=gpt-4o-mini
```

### Configuración de Puertos

Por defecto, la aplicación se ejecuta en el puerto 5050. Si necesitas cambiar esto, puedes modificar el script `run.sh`.

## 🛠️ Tecnologías

- **Frontend**: 
  - HTML5, CSS3, JavaScript
  - Bootstrap 5 para el diseño responsivo
  - Bootstrap Tags Input para gestión de etiquetas
  - Font Awesome para iconografía
- **Backend**: 
  - Flask (Python)
  - Sistema de logging detallado
  - Manejo de archivos temporales
- **IA**: 
  - GPT-4o-mini para análisis de imágenes
  - GPT-4 para generación de recetas
- **Dependencias**: Ver `requirements.txt`

## 🔄 Flujo de trabajo

1. **Captura y procesamiento de imagen**:
   ```python
   # app.py
   def analyze():
       file = request.files['image']
       filepath = save_uploaded_file(file)
       base64_image = encode_image_to_base64(filepath)
   ```

2. **Análisis de ingredientes con GPT-4o-mini**:
   ```python
   # Solicitud de análisis de imagen desde app.py
   vision_response = client.chat.completions.create(
       model=Config.IMAGE_MODEL,  # gpt-4o-mini desde config.py
       messages=[{
           "role": "user",
           "content": [
               {"type": "text", "text": "Analiza esta imagen de una nevera y lista los ingredientes que puedes identificar con nombre de España. Responde solo con la lista de ingredientes separados por comas, sin puntos ni otros caracteres adicionales."},
               {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
           ]
       }],
       max_tokens=2000
   )
   ```

3. **Generación de Recetas con prompt personalizado**:
   ```python
   # Función de generación de prompt desde utils.py
   def generate_prompt(detected_items, allergies='', cuisine_type=''):
       # Construcción del prompt con rol e instrucciones detalladas
       prompt = """Rol: Eres un chef profesional con más de 20 años de experiencia en cocina internacional, 
       especializado en crear recetas caseras deliciosas, prácticas y accesibles para cocineros de todos los niveles.

   Instrucciones:
   1. Recibes como entrada una lista de ingredientes disponibles, un estilo de cocina (opcional) y restricciones por alergias (opcional).
   2. Genera UNA receta que:
      - Aproveche al máximo los ingredientes proporcionados.
      - Sea fácil de preparar en cualquier cocina doméstica.
      - Tenga un equilibrio perfecto de sabores y texturas.
      - Incluya consejos profesionales para mejorar el resultado final.
   """
       
   # Envío a la API desde app.py 
   recipe_response = client.chat.completions.create(
       model=Config.RECIPE_MODEL,  # gpt-4o-mini desde config.py
       messages=[
           {"role": "system", "content": "Eres un chef profesional con más de 20 años de experiencia..."},
           {"role": "user", "content": recipe_prompt}
       ],
       temperature=0.8,
       max_tokens=2500
   )
   ```

4. **Sistema de notificaciones y feedback**:
   ```javascript
   function showNotification(message) {
       const notification = document.createElement('div');
       notification.className = 'alert alert-success notification';
       notification.textContent = message;
       document.body.appendChild(notification);
       
       setTimeout(() => {
           notification.remove();
       }, 2000);
   }
   ```

## 🚀 Características técnicas destacadas

- **Manejo de Errores**:
  ```python
  def make_openai_request_with_retry(request_fn, max_retries=3, initial_delay=1):
      """Implementa retry exponencial para llamadas a la API"""
      for attempt in range(max_retries):
          try:
              return request_fn()
          except OpenAIError as e:
              if attempt < max_retries - 1:
                  delay = initial_delay * (2 ** attempt)
                  time.sleep(delay)
                  continue
              raise
  ```

- **Optimización de recursos**:
  ```python
  # Límites y restricciones
  MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
  ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
  
  # Limpieza automática de archivos temporales
  def clean_temp_files(filepath):
      if os.path.exists(filepath):
          os.remove(filepath)
  ```

- **Sistema de logging detallado**:
  ```python
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )
  ```

## 📝 Variables de entorno requeridas

```bash
OPENAI_API_KEY=tu_api_key
FLASK_SECRET_KEY=tu_clave_secreta
```

## 🛠️ Instalación

1. Clonar el repositorio
2. Crear y activar entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instalar dependencias: `pip install -r requirements.txt`
4. Crear archivo `.env` con las variables de entorno
5. Ejecutar: `./run.sh`
6. Acceder a `http://localhost:5050`

## ❗ Solución de Problemas

### Puerto ocupado

Si encuentras el error "Address already in use" al iniciar la aplicación:

```
Address already in use
Port 5050 is in use by another program.
```

Puedes cambiar el puerto en el script `run.sh` o detener el proceso que está usando ese puerto:

```bash
# Buscar el proceso que usa el puerto 5050
lsof -i :5050

# Terminar el proceso (reemplaza PID con el ID del proceso)
kill -9 PID
```

### Errores de API

Si recibes errores relacionados con la API de OpenAI:

1. Verifica que tu clave API sea válida y esté correctamente configurada en `.env`
2. Asegúrate de tener crédito disponible en tu cuenta de OpenAI
3. Comprueba el estado del servicio de OpenAI en [status.openai.com](https://status.openai.com)

## 🚧 Limitaciones

Al ser un Proof of Concept (POC), este proyecto tiene algunas limitaciones:

- Puede tener dificultades para reconocer ciertos ingredientes o alimentos poco comunes
- El tiempo de respuesta depende del servicio de OpenAI y puede variar
- No está optimizado para imágenes de baja calidad o con mala iluminación
- Los costos de API aumentarán con el uso frecuente o a gran escala

## 👥 Contribución

Las contribuciones son bienvenidas. Si deseas contribuir a este proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y documéntalos
4. Asegúrate de que los test pasen
5. Envía un pull request

Ideas para contribuciones:
- Mejorar el reconocimiento de ingredientes
- Añadir soporte para más idiomas
- Implementar un historial de recetas generadas
- Mejorar la interfaz de usuario

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE.md para detalles.
