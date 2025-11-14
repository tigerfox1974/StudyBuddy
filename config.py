"""
StudyBuddy Konfigürasyon Dosyası
OpenAI API ayarları, Flask ayarları ve dosya yükleme konfigürasyonu
"""

import os
import re
from datetime import timedelta
from dotenv import load_dotenv

# .env dosyasından ortam değişkenlerini yükle
load_dotenv()


class Config:
    """Temel konfigürasyon sınıfı"""
    
    # Flask ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session ve Security ayarları
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
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
            'difficulty': {'simple': 80, 'medium': 20, 'advanced': 0, 'academic': 0},
            'short_answer': {'max_words': 3}
        },
        'middle_school': {
            'name': 'Ortaokul (5-8. Sınıf)',
            'age_range': '11-14 yaş',
            'questions_per_type': 15,
            'difficulty': {'simple': 50, 'medium': 40, 'advanced': 10, 'academic': 0},
            'short_answer': {'max_words': 4}
        },
        'high_school': {
            'name': 'Lise (9-12. Sınıf)',
            'age_range': '15-18 yaş',
            'questions_per_type': 20,
            'difficulty': {'simple': 30, 'medium': 50, 'advanced': 20, 'academic': 0},
            'short_answer': {'max_words': 5}
        },
        'university': {
            'name': 'Üniversite',
            'age_range': '18+ yaş',
            'questions_per_type': 25,
            'difficulty': {'simple': 0, 'medium': 20, 'advanced': 60, 'academic': 20},
            'short_answer': {'max_words': 7}
        },
        'exam_prep': {
            'name': 'Sınav Hazırlığı (YKS, KPSS, vb.)',
            'age_range': '17+ yaş',
            'questions_per_type': 30,
            'difficulty': {'simple': 20, 'medium': 40, 'advanced': 30, 'academic': 10},
            'short_answer': {'max_words': 7}
        }
    }
    
    # Abonelik planları ve limitleri
    SUBSCRIPTION_PLANS = {
        'free': {
            'name': 'Ücretsiz Plan',
            'price': 0,
            'currency': 'TRY',
            'billing_period': 'monthly',
            'stripe_price_id': None,  # Free plan için Stripe price ID yok
            'stripe_product_id': None,
            'features': {
                'monthly_upload_limit': 5,  # Aylık maksimum dosya yükleme sayısı
                'max_file_size_mb': 16,
                'supported_formats': ['pdf', 'docx', 'pptx', 'txt'],
                'cache_enabled': True,
                'priority_support': False,
                'export_formats': ['web'],  # Gelecek için: pdf, docx export
                'history_retention_days': 30
            },
            'description': 'Başlangıç için ideal',
            'highlights': [
                '5 dosya/ay yükleme',
                'Tüm soru tipleri',
                'Özet ve flashcard',
                '30 gün geçmiş'
            ]
        },
        'premium': {
            'name': 'Premium Plan',
            'price': 49.99,  # Aylık fiyat (TRY)
            'currency': 'TRY',
            'billing_period': 'monthly',
            'stripe_price_id': os.environ.get('STRIPE_PREMIUM_PRICE_ID') or 'price_your_premium_price_id_here',
            'stripe_product_id': os.environ.get('STRIPE_PREMIUM_PRODUCT_ID'),
            'features': {
                'monthly_upload_limit': None,  # None = sınırsız
                'max_file_size_mb': 32,
                'supported_formats': ['pdf', 'docx', 'pptx', 'txt'],
                'cache_enabled': True,
                'priority_support': True,
                'export_formats': ['web', 'pdf', 'docx'],  # Gelecek için
                'history_retention_days': None  # None = sınırsız
            },
            'description': 'Sınırsız öğrenme deneyimi',
            'highlights': [
                'Sınırsız dosya yükleme',
                'Öncelikli destek',
                'Gelişmiş export seçenekleri',
                'Sınırsız geçmiş'
            ]
        }
    }
    
    # Dosya yükleme ayarları
    # Not: Plan-bazlı limitler /process route'unda kontrol edilir
    # Bu global limit premium plan için yeterli olacak şekilde ayarlanmıştır
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB maksimum dosya boyutu (premium plan için)
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt'}
    
    # AI üretim ayarları
    DEFAULT_QUESTION_COUNT = 5
    DEFAULT_FLASHCARD_COUNT = 10
    
    # Flask-Mail SMTP ayarları
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    MAIL_MAX_EMAILS = None
    
    # Password Policy
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_PASSWORD_UPPERCASE = True
    REQUIRE_PASSWORD_LOWERCASE = True
    REQUIRE_PASSWORD_DIGIT = True
    REQUIRE_PASSWORD_SPECIAL = False
    
    # Token ayarları
    RESET_TOKEN_EXPIRY_HOURS = 1
    
    # CSRF Protection Ayarları
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'true').lower() in ('true', '1', 'yes')
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT')) if os.environ.get('WTF_CSRF_TIME_LIMIT') and os.environ.get('WTF_CSRF_TIME_LIMIT').lower() != 'none' else None
    
    # Rate Limiting Ayarları
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'true').lower() in ('true', '1', 'yes')
    UPLOAD_RATE_LIMIT = '10/hour'
    UPLOAD_RATE_LIMIT_MESSAGE = 'Çok fazla dosya yükleme isteği. Lütfen bir süre bekleyip tekrar deneyin.'
    
    # File Validation Ayarları
    VALIDATE_FILE_SIGNATURES = os.environ.get('VALIDATE_FILE_SIGNATURES', 'true').lower() in ('true', '1', 'yes')
    ALLOWED_FILE_SIGNATURES = {
        'pdf': b'%PDF-',
        'docx': b'PK\x03\x04',  # ZIP signature (DOCX is a ZIP file)
        'pptx': b'PK\x03\x04',  # ZIP signature (PPTX is a ZIP file)
        'txt': None  # No magic number for text files
    }
    
    # Stripe Payment Ayarları
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    STRIPE_ENABLED = os.environ.get('STRIPE_ENABLED', 'true').lower() in ('true', '1', 'yes')
    STRIPE_CURRENCY = os.environ.get('STRIPE_CURRENCY', 'TRY')
    STRIPE_SUCCESS_URL = os.environ.get('STRIPE_SUCCESS_URL') or '/checkout/success?session_id={CHECKOUT_SESSION_ID}'
    STRIPE_CANCEL_URL = os.environ.get('STRIPE_CANCEL_URL') or '/checkout/cancel'
    
    # Invoice Ayarları
    INVOICE_PREFIX = 'INV'
    INVOICE_COMPANY_NAME = os.environ.get('INVOICE_COMPANY_NAME', 'StudyBuddy')
    INVOICE_COMPANY_ADDRESS = os.environ.get('INVOICE_COMPANY_ADDRESS', 'Adres bilgisi buraya')
    INVOICE_TAX_RATE = float(os.environ.get('INVOICE_TAX_RATE', '0'))
    INVOICE_STORAGE_PATH = os.environ.get('INVOICE_STORAGE_PATH', 'invoices')
    
    @staticmethod
    def allowed_file(filename):
        """Dosya uzantısının izin verilen listede olup olmadığını kontrol eder"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_password(password):
        """Şifrenin policy'ye uygun olup olmadığını kontrol et"""
        errors = []
        
        if len(password) < Config.MIN_PASSWORD_LENGTH:
            errors.append(f"Şifre en az {Config.MIN_PASSWORD_LENGTH} karakter olmalıdır.")
        
        if Config.REQUIRE_PASSWORD_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Şifre en az bir büyük harf içermelidir.")
        
        if Config.REQUIRE_PASSWORD_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Şifre en az bir küçük harf içermelidir.")
        
        if Config.REQUIRE_PASSWORD_DIGIT and not re.search(r'\d', password):
            errors.append("Şifre en az bir rakam içermelidir.")
        
        if Config.REQUIRE_PASSWORD_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Şifre en az bir özel karakter içermelidir.")
        
        if errors:
            return False, errors
        return True, []
    
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
    
    @staticmethod
    def get_plan_limit(plan_type, feature_key):
        """Belirtilen plan için özellik değerini döndür"""
        plan = Config.SUBSCRIPTION_PLANS.get(plan_type)
        if not plan:
            plan = Config.SUBSCRIPTION_PLANS.get('free')  # Default olarak free plan
        return plan['features'].get(feature_key)
    
    @staticmethod
    def get_monthly_upload_limit(plan_type):
        """Kısayol metod: Aylık yükleme limitini döndür"""
        return Config.get_plan_limit(plan_type, 'monthly_upload_limit')
    
    @staticmethod
    def is_unlimited_plan(plan_type):
        """Plan sınırsız mı kontrol et"""
        return Config.get_monthly_upload_limit(plan_type) is None
    
    @staticmethod
    def validate_stripe_config():
        """Stripe anahtarlarının ayarlanıp ayarlanmadığını kontrol eder"""
        if not Config.STRIPE_ENABLED:
            return True  # Stripe devre dışıysa kontrol yapma
        
        if not Config.STRIPE_SECRET_KEY:
            raise ValueError(
                "STRIPE_SECRET_KEY ortam değişkeni ayarlanmamış! "
                "Lütfen .env dosyasında STRIPE_SECRET_KEY değerini ayarlayın. "
                "Veya Stripe'ı devre dışı bırakmak için STRIPE_ENABLED=false ayarlayın."
            )
        if not Config.STRIPE_PUBLISHABLE_KEY:
            raise ValueError(
                "STRIPE_PUBLISHABLE_KEY ortam değişkeni ayarlanmamış! "
                "Lütfen .env dosyasında STRIPE_PUBLISHABLE_KEY değerini ayarlayın."
            )
        return True
    
    @staticmethod
    def get_stripe_price_id(plan_type):
        """Belirtilen plan için Stripe Price ID döndür"""
        plan = Config.SUBSCRIPTION_PLANS.get(plan_type)
        if not plan:
            return None
        return plan.get('stripe_price_id')
    
    @staticmethod
    def get_plan_by_stripe_price_id(price_id):
        """Stripe Price ID'ye göre plan bul (reverse lookup)"""
        for plan_key, plan in Config.SUBSCRIPTION_PLANS.items():
            if plan.get('stripe_price_id') == price_id:
                return plan_key, plan
        return None, None

