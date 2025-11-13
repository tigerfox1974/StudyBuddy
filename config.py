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
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or 'gpt-4.1-mini'
    
    # Desteklenen modeller
    SUPPORTED_MODELS = ['gpt-4.1-mini', 'gpt-4.1-mini-2025-04-14']
    
    # Demo modu (OpenAI API olmadan test için)
    DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
    
    # SQLite Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///studybuddy.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Seviye bazli soru sayilari ve zorluk dagilimi
    LEVEL_SETTINGS = {
        'elementary': {
            'name': 'İlkokul (1-4. Sınıf)',
            'age_range': '6-10 yaş',
            'questions_per_type': 10,
            'difficulty': {'simple': 80, 'medium': 20, 'advanced': 0, 'academic': 0}
        },
        'middle_school': {
            'name': 'Ortaokul (5-8. Sınıf)',
            'age_range': '11-14 yaş',
            'questions_per_type': 15,
            'difficulty': {'simple': 50, 'medium': 40, 'advanced': 10, 'academic': 0}
        },
        'high_school': {
            'name': 'Lise (9-12. Sınıf)',
            'age_range': '15-18 yaş',
            'questions_per_type': 20,
            'difficulty': {'simple': 30, 'medium': 50, 'advanced': 20, 'academic': 0}
        },
        'university': {
            'name': 'Üniversite',
            'age_range': '18+ yaş',
            'questions_per_type': 25,
            'difficulty': {'simple': 0, 'medium': 20, 'advanced': 60, 'academic': 20}
        },
        'exam_prep': {
            'name': 'Sınav Hazırlığı (YKS, KPSS, vb.)',
            'age_range': '17+ yaş',
            'questions_per_type': 30,
            'difficulty': {'simple': 20, 'medium': 40, 'advanced': 30, 'academic': 10}
        }
    }
    
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

