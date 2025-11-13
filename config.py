"""
StudyBuddy Konfigürasyon Dosyası
OpenAI API ayarları, Flask ayarları ve dosya yükleme konfigürasyonu
"""

import os
from dotenv import load_dotenv

# .env dosyasından ortam değişkenlerini yükle
load_dotenv()


class Config:
    """Temel konfigürasyon sınıfı"""
    
    # Flask ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # OpenAI API ayarları
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or 'gpt-3.5-turbo'
    
    # Demo modu (OpenAI API olmadan test için)
    DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
    
    # Dosya yükleme ayarları
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB maksimum dosya boyutu
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'pptx', 'txt'}
    
    # AI üretim ayarları
    DEFAULT_QUESTION_COUNT = 5
    DEFAULT_FLASHCARD_COUNT = 10
    
    @staticmethod
    def allowed_file(filename):
        """Dosya uzantısının izin verilen listede olup olmadığını kontrol eder"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_config():
        """Gerekli konfigürasyonların ayarlanıp ayarlanmadığını kontrol eder"""
        if Config.DEMO_MODE:
            return True  # Demo modda API key kontrolü yapma
        
        if not Config.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY ortam değişkeni ayarlanmamış! "
                "Lütfen .env dosyasında OPENAI_API_KEY değerini ayarlayın. "
                "Veya test için DEMO_MODE=true ayarlayın."
            )
        return True

