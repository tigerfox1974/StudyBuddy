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
    # Flask DEBUG modu (production'da kapalı olmalıdır)
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1', 'yes')
    _SECRET_FALLBACK = 'dev-secret-key-change-in-production'
    
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
    
    # Demo modu uyarı metinleri
    DEMO_MODE_WARNING_TEXT = {
        'banner': 'Demo Modu Aktif: Bu içerikler yapay zeka tarafından üretilmemiş sahte verilerdir. Gerçek AI üretimi için OpenAI API anahtarı gereklidir.',
        'navbar': 'DEMO MODU',
        'card_note': 'Bu demo veridir'
    }
    
    # Internationalization (i18n) ayarları
    BABEL_DEFAULT_LOCALE = 'tr'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Istanbul'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    SUPPORTED_LANGUAGES = {
        'tr': {'name': 'Türkçe', 'flag': '🇹🇷'},
        'en': {'name': 'English', 'flag': '🇬🇧'}
    }
    DEFAULT_LANGUAGE = 'tr'
    
    # SQLite Database
    # Flask SQLAlchemy instance klasöründe veritabanı oluşturur
    # instance klasörünün varlığını kontrol et ve oluştur
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(instance_path, "studybuddy.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Alembic Migration Ayarları
    # AUTO_MIGRATE_ON_STARTUP: Uygulama başlangıcında otomatik migration kontrolü
    # Production'da 'false' olmalı, development'ta 'true' olabilir
    # Manuel kontrol için: alembic upgrade head
    AUTO_MIGRATE_ON_STARTUP = os.environ.get('AUTO_MIGRATE_ON_STARTUP', 'false').lower() in ('true', '1', 'yes')
    ALEMBIC_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'alembic.ini')
    
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
            'currency': 'TL',
            'billing_period': 'monthly',
            'stripe_price_id': None,  # Free plan için Stripe price ID yok
            'stripe_product_id': None,
            'features': {
                'monthly_tokens': 3,  # Aylık 3 fiş (otomatik yenilenir)
                'trial_tokens': 10,  # İlk 7 gün için 10 fiş
                'trial_days': 7,  # 7 günlük deneme süresi
                'max_file_size_mb': 10,
                'max_questions_per_type': 5,  # Her soru türünde maksimum 5 soru
                'supported_formats': ['pdf', 'docx', 'pptx', 'txt'],
                'cache_enabled': True,
                'priority_support': False,
                'export_formats': ['web'],  # Export yok (sadece web görüntüleme)
                'export_cost_tokens': 2,  # Export için 2 fiş gerektirir
                'history_retention_days': 30
            },
            'description': 'Başlangıç için ideal',
            'highlights': [
                'Aylık 3 fiş (otomatik yenilenir)',
                '10 MB dosya boyutu limiti',
                'Çoktan Seçmeli: 5 soru',
                'Kısa Cevap: 5 soru',
                'Boş Doldurma: 5 soru',
                'Doğru-Yanlış: 5 soru',
                'Özet ve flashcard',
                '30 gün geçmiş',
                'Export (Dışa Aktarım) yok'
            ]
        },
        'standard': {
            'name': 'Standart Plan',
            'price': 24.99,
            'currency': 'TL',
            'billing_period': 'monthly',
            'stripe_price_id': os.environ.get('STRIPE_STANDARD_PRICE_ID') or 'price_your_standard_price_id_here',
            'stripe_product_id': os.environ.get('STRIPE_STANDARD_PRODUCT_ID'),
            'features': {
                'monthly_tokens': 25,  # Aylık 25 fiş (otomatik yenilenir)
                'max_file_size_mb': 16,
                'max_questions_per_type': 30,  # Her soru türünde maksimum 30 soru
                'supported_formats': ['pdf', 'docx', 'pptx', 'txt'],
                'cache_enabled': True,
                'priority_support': False,
                'export_formats': ['web'],  # Export var ama fiş gerektirir
                'export_cost_tokens': 2,  # Export için 2 fiş gerektirir
                'history_retention_days': 90
            },
            'description': 'Daha fazla içerik için ideal',
            'highlights': [
                'Aylık 25 fiş (otomatik yenilenir)',
                '16 MB dosya boyutu limiti',
                'Çoktan Seçmeli: 30 soru',
                'Kısa Cevap: 30 soru',
                'Boş Doldurma: 30 soru',
                'Doğru-Yanlış: 30 soru',
                'Özet ve flashcard',
                '90 gün geçmiş',
                'Export (Dışa Aktarım): 2 fiş'
            ]
        },
        'premium': {
            'name': 'Premium Plan',
            'price': 49.99,
            'currency': 'TL',
            'billing_period': 'monthly',
            'stripe_price_id': os.environ.get('STRIPE_PREMIUM_PRICE_ID') or 'price_your_premium_price_id_here',
            'stripe_product_id': os.environ.get('STRIPE_PREMIUM_PRODUCT_ID'),
            'features': {
                'monthly_tokens': 60,  # Aylık 60 fiş (otomatik yenilenir)
                'max_file_size_mb': 24,
                'max_questions_per_type': None,  # None = sınırsız
                'supported_formats': ['pdf', 'docx', 'pptx', 'txt'],
                'cache_enabled': True,
                'priority_support': True,
                'export_formats': ['web', 'pdf', 'docx'],  # Export ücretsiz
                'export_cost_tokens': 0,  # Export ücretsiz (0 fiş)
                'history_retention_days': None  # None = sınırsız
            },
            'description': 'Profesyonel öğrenme deneyimi',
            'highlights': [
                'Aylık 60 fiş (otomatik yenilenir)',
                '24 MB dosya boyutu limiti',
                'Çoktan Seçmeli: Sınırsız',
                'Kısa Cevap: Sınırsız',
                'Boş Doldurma: Sınırsız',
                'Doğru-Yanlış: Sınırsız',
                'Özet ve flashcard',
                'Export (Dışa Aktarım veya Soru Kağıdı Oluşturma): ÜCRETSİZ',
                'Sınırsız geçmiş',
                'Öncelikli destek'
            ]
        }
    }
    
    # Fiş paketleri (Token packages)
    TOKEN_PACKAGES = {
        'small': {
            'name': '10 Fiş Paketi',
            'tokens': 10,
            'price': 14.99,
            'currency': 'TL',
            'price_per_token': 1.50,
            'discount_percent': 0
        },
        'medium': {
            'name': '25 Fiş Paketi',
            'tokens': 25,
            'price': 29.99,
            'currency': 'TL',
            'price_per_token': 1.20,
            'discount_percent': 20,
            'popular': True
        },
        'large': {
            'name': '50 Fiş Paketi',
            'tokens': 50,
            'price': 49.99,
            'currency': 'TL',
            'price_per_token': 1.00,
            'discount_percent': 33
        },
        'xlarge': {
            'name': '100 Fiş Paketi',
            'tokens': 100,
            'price': 89.99,
            'currency': 'TL',
            'price_per_token': 0.90,
            'discount_percent': 40
        }
    }
    
    # Fiş harcama maliyetleri (Token costs)
    TOKEN_COSTS = {
        'base_processing': 1,  # Temel işleme (özet + flashcard): 1 fiş
        'question_type': 0.5,  # Her soru türü için: 0.5 fiş
        'export': 2  # Export için: 2 fiş (premium'da 0)
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
    
    # Export Ayarları
    EXPORT_STORAGE_PATH = os.environ.get('EXPORT_STORAGE_PATH', 'exports')
    EXPORT_FILENAME_FORMAT = 'export_{result_id}_{timestamp}'
    EXPORT_INCLUDE_ANSWER_KEY = True
    EXPORT_FORMATS = ['pdf', 'docx']

    # Logging Ayarları (Environment üzerinden yapılandırılabilir)
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE')  # Örn: logs/studybuddy.log (optional)
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    LOG_ERROR_FILE = os.environ.get('LOG_ERROR_FILE')  # Sadece error logları için (optional)

    # Gunicorn Ayarları (Environment üzerinden yapılandırılabilir)
    GUNICORN_BIND = os.environ.get('GUNICORN_BIND', '0.0.0.0:5000')
    GUNICORN_WORKERS = int(os.environ.get('GUNICORN_WORKERS', (os.cpu_count() or 1) * 2 + 1))
    GUNICORN_LOG_LEVEL = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
    GUNICORN_TIMEOUT = int(os.environ.get('GUNICORN_TIMEOUT', 120))
    
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
        # Production ortamında SECRET_KEY fallback kullanımı engellenir
        if Config.is_production():
            if not Config.SECRET_KEY or Config.SECRET_KEY == Config._SECRET_FALLBACK:
                raise ValueError(
                    "SECRET_KEY must be set in production and cannot use fallback value."
                )
            # Production'da DEBUG kesinlikle kapalı olmalı
            if Config.DEBUG:
                raise ValueError("DEBUG mode must be disabled in production (FLASK_DEBUG=false)")
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
    def is_production():
        """Production ortamını belirle (FLASK_ENV/FLASK_DEBUG)"""
        env = (os.environ.get('FLASK_ENV') or '').lower()
        debug_raw = os.environ.get('FLASK_DEBUG')
        debug_on = False if debug_raw is None else str(debug_raw).lower() in ('true', '1', 'yes')
        # FLASK_DEBUG açıksa asla production değildir
        if debug_on:
            return False
        # Debug kapalıysa yalnızca FLASK_ENV explicit 'production' ise prod
        return env == 'production'
    
    @staticmethod
    def get_plan_limit(plan_type, feature_key):
        """Belirtilen plan için özellik değerini döndür"""
        plan = Config.SUBSCRIPTION_PLANS.get(plan_type)
        if not plan:
            plan = Config.SUBSCRIPTION_PLANS.get('free')  # Default olarak free plan
        return plan['features'].get(feature_key)
    
    @staticmethod
    def get_monthly_tokens(plan_type):
        """Kısayol metod: Aylık fiş sayısını döndür"""
        return Config.get_plan_limit(plan_type, 'monthly_tokens')
    
    @staticmethod
    def get_monthly_upload_limit(plan_type):
        """Kısayol metod: Aylık yükleme limitini döndür (geriye uyumluluk için)"""
        # Eski sistem için: monthly_upload_limit yoksa None döndür
        return Config.get_plan_limit(plan_type, 'monthly_upload_limit')
    
    @staticmethod
    def is_unlimited_plan(plan_type):
        """Plan sınırsız mı kontrol et (dosya yükleme açısından)"""
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
        # Price ID doğrulaması (free plan hariç)
        for plan_key, plan in Config.SUBSCRIPTION_PLANS.items():
            price_id = plan.get('stripe_price_id')
            if price_id:
                Config.validate_stripe_price_id(price_id)
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

    @staticmethod
    def validate_stripe_price_id(price_id: str):
        """
        Stripe Price ID formatını doğrula ve placeholder değerleri reddet.
        Beklenen format: price_XXXX...
        """
        if not isinstance(price_id, str):
            raise ValueError("Invalid Stripe Price ID: not a string")
        placeholder_patterns = [
            r'^price_your_.*_price_id_here$',
            r'^price_test_.*$',
        ]
        for patt in placeholder_patterns:
            if re.match(patt, price_id):
                raise ValueError(f"Invalid Stripe Price ID (placeholder not allowed): {price_id}")
        if not re.match(r'^price_[A-Za-z0-9_]+$', price_id):
            raise ValueError(f"Invalid Stripe Price ID format: {price_id}")

    @staticmethod
    def validate_production_config():
        """
        Production için genişletilmiş doğrulama:
        - SECRET_KEY, DEBUG, Stripe (enabled ise), Mail ayarları
        - Logging seviyesi önerisi
        """
        if not Config.is_production():
            return True
        # SECRET_KEY ve DEBUG kontrolü zaten validate_config içinde var
        Config.validate_config()
        # Stripe (enabled ise) doğrula
        if Config.STRIPE_ENABLED:
            Config.validate_stripe_config()
        # Mail ayarları (basic check)
        if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
            # Prod'da e-posta reset/notification planlanıyorsa zorunlu olabilir; uyarı amaçlı istisna fırlat
            # Operasyonel bilinç için ValueError tercih edildi
            raise ValueError("MAIL_USERNAME ve MAIL_PASSWORD production ortamında ayarlanmalıdır.")
        # Logging seviyesi önerisi
        lvl = (Config.LOG_LEVEL or '').upper()
        if lvl == 'DEBUG':
            raise ValueError("Production ortamında LOG_LEVEL DEBUG olamaz. INFO veya WARNING kullanın.")
        return True

