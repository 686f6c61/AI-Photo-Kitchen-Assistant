# 🍳 Recetas desde tu nevera - AI Kitchen Assistant

Una aplicación web que utiliza inteligencia artificial para analizar el contenido de tu nevera y generar recetas personalizadas. Combina GPT-4o-mini para el reconocimiento de ingredientes y GPT-4 para la generación de recetas creativas y detalladas.
![Fotos Alacena](/img/recetas2.png)
![Recetas](/img/recetas1.png)

## 🌟 Características

- **Análisis de imágenes**: Utiliza GPT-4o-mini para identificar ingredientes en fotos de tu nevera
- **Recetas personalizadas**: Genera hasta 3 recetas basadas en los ingredientes disponibles
- **Preferencias culinarias**: Permite especificar tipo de cocina (mexicana, italiana, española, etc.)
- **Gestión de alergias**: Sistema de etiquetas para indicar restricciones alimentarias
- **Lista de compras**: Sugiere ingredientes adicionales para complementar las recetas
- **Interfaz intuitiva**: 
  - Drag & drop de imágenes
  - Captura directa desde cámara web
  - Sistema de etiquetas para ingredientes principales
- **Copiar al Portapapeles**: Botones para copiar recetas y listas de compra con feedback visual

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
   vision_response = client.chat.completions.create(
       model="gpt-4o-mini",
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

3. **Generación de Recetas con GPT-4**:
   ```python
   recipe_response = client.chat.completions.create(
       model="gpt-4",
       messages=[
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
5. Ejecutar: `python3 app.py`
6. Acceder a `http://localhost:5000`


## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE.md para detalles.
