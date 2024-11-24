import os

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'una-clave-secreta-segura')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'temp_uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
