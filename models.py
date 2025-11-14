"""
StudyBuddy Database Models
SQLite veritabani icin model tanimlari
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from config import Config

db = SQLAlchemy()


class Document(db.Model):
    """Yuklenen dokumanlar"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    file_hash = db.Column(db.String(32), nullable=False, index=True)  # UNIQUE constraint yok - ayni dosya tekrar yuklenebilir
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    user_level = db.Column(db.String(20), nullable=False, index=True)  # elementary, middle_school, high_school, university
    user_type = db.Column(db.String(20), nullable=False, index=True)   # student, teacher
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    results = db.relationship('Result', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'


class Result(db.Model):
    """Uretilen icerikler (ozet, sorular, flashcards)"""
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    multiple_choice = db.Column(db.Text, nullable=False)  # JSON string
    short_answer = db.Column(db.Text, nullable=False)     # JSON string
    fill_blank = db.Column(db.Text, nullable=False)       # JSON string
    true_false = db.Column(db.Text, nullable=False)       # JSON string
    flashcards = db.Column(db.Text, nullable=False)       # JSON string
    ai_model = db.Column(db.String(50), nullable=False)
    token_used = db.Column(db.Integer, default=0)
    processing_time = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Result for Document {self.document_id}>'


class User(UserMixin, db.Model):
    """Kullanıcı hesapları"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    subscription_plan = db.Column(db.String(20), default='free', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    # Token sistemi için yeni kolonlar
    tokens_remaining = db.Column(db.Integer, default=0, nullable=False)  # Kalan fiş sayısı
    trial_ends_at = db.Column(db.DateTime, nullable=True)  # 7 günlük deneme bitiş tarihi
    last_token_refresh = db.Column(db.DateTime, nullable=True)  # Son fiş yenileme tarihi
    
    # Relationships
    documents = db.relationship('Document', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Şifreyi hash'leyip kaydet"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Şifreyi doğrula"""
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Şifre sıfırlama token'ı oluştur"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=Config.RESET_TOKEN_EXPIRY_HOURS)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Token'ı ve expiry'yi kontrol et"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expiry:
            return False
        return True
    
    def clear_reset_token(self):
        """Token field'larını temizle"""
        self.reset_token = None
        self.reset_token_expiry = None
    
    def __repr__(self):
        return f'<User {self.email}>'


class Subscription(db.Model):
    """Abonelik geçmişi"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    plan_type = db.Column(db.String(20), nullable=False)  # 'free', 'premium'
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active', 'cancelled', 'expired'
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)  # None = süresiz
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='subscriptions')
    
    def is_active(self):
        """Aboneliğin aktif olup olmadığını kontrol et"""
        if self.status != 'active':
            return False
        if self.end_date is None:
            return True
        return self.end_date > datetime.utcnow()
    
    def __repr__(self):
        return f'<Subscription {self.plan_type} for User {self.user_id}>'


class UsageStats(db.Model):
    """Kullanim istatistikleri"""
    __tablename__ = 'usage_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    total_documents = db.Column(db.Integer, default=0)
    cache_hits = db.Column(db.Integer, default=0)
    cache_misses = db.Column(db.Integer, default=0)
    total_tokens_saved = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_or_create(cls):
        """Tek bir stats kaydi tutar"""
        stats = cls.query.first()
        if not stats:
            stats = cls()
            db.session.add(stats)
            db.session.commit()
        return stats
    
    def update_cache_hit(self, tokens_saved):
        """Cache hit kaydi"""
        self.cache_hits += 1
        self.total_tokens_saved += tokens_saved
        self.last_updated = datetime.utcnow()
        db.session.commit()
    
    def update_cache_miss(self):
        """Cache miss kaydi"""
        self.cache_misses += 1
        self.total_documents += 1
        self.last_updated = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<UsageStats hits={self.cache_hits} misses={self.cache_misses}>'


class UserUsageStats(db.Model):
    """Kullanıcı bazlı aylık kullanım istatistikleri"""
    __tablename__ = 'user_usage_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False, index=True)  # 1-12
    documents_processed = db.Column(db.Integer, default=0)  # Yeni yüklenen dosya sayısı (cache hit hariç)
    cache_hits = db.Column(db.Integer, default=0)
    cache_misses = db.Column(db.Integer, default=0)
    tokens_saved = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: Her kullanıcı için ay bazında tek kayıt
    __table_args__ = (db.UniqueConstraint('user_id', 'year', 'month', name='_user_year_month_uc'),)
    
    # Relationships
    user = db.relationship('User', backref='usage_stats')
    
    @classmethod
    def get_or_create(cls, user_id, year=None, month=None):
        """Belirtilen ay için stats kaydı getir veya oluştur"""
        if year is None or month is None:
            now = datetime.utcnow()
            year = now.year
            month = now.month
        
        stats = cls.query.filter_by(user_id=user_id, year=year, month=month).first()
        if not stats:
            stats = cls(user_id=user_id, year=year, month=month)
            db.session.add(stats)
            db.session.commit()
        return stats
    
    def increment_document(self):
        """Dosya yükleme sayacını artır (cache miss durumunda)"""
        self.documents_processed += 1
        self.cache_misses += 1
        self.last_updated = datetime.utcnow()
        db.session.commit()
    
    def increment_cache_hit(self, tokens_saved):
        """Cache hit sayacını artır"""
        self.cache_hits += 1
        self.tokens_saved += tokens_saved
        self.last_updated = datetime.utcnow()
        db.session.commit()
    
    def get_total_uploads(self):
        """Toplam yükleme sayısını döndür"""
        return self.documents_processed
    
    def __repr__(self):
        return f'<UserUsageStats User {self.user_id} - {self.year}/{self.month}>'


class Payment(db.Model):
    """Ödeme işlemleri"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='TRY', nullable=False)
    status = db.Column(db.String(20), nullable=False, index=True)  # 'pending', 'completed', 'failed', 'refunded'
    stripe_session_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    plan_type = db.Column(db.String(20), nullable=False)  # 'premium'
    billing_period = db.Column(db.String(20), default='monthly', nullable=False)
    payment_method = db.Column(db.String(50), nullable=True)  # 'card', 'bank_transfer', etc.
    invoice_number = db.Column(db.String(50), unique=True, nullable=True)
    invoice_pdf_path = db.Column(db.String(255), nullable=True)
    payment_metadata = db.Column(db.Text, nullable=True)  # JSON string for additional Stripe metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='payments')
    subscription = db.relationship('Subscription', backref='payments')
    
    @classmethod
    def generate_invoice_number(cls):
        """Sıralı fatura numarası oluştur (format: INV-YYYY-NNNNN)"""
        now = datetime.utcnow()
        year = now.year
        
        # Bu yıl için en son fatura numarasını bul
        last_payment = cls.query.filter(
            cls.invoice_number.like(f'INV-{year}-%')
        ).order_by(cls.invoice_number.desc()).first()
        
        if last_payment and last_payment.invoice_number:
            # Son numaradan devam et
            try:
                last_num = int(last_payment.invoice_number.split('-')[-1])
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1
        
        return f'INV-{year}-{next_num:05d}'
    
    def mark_completed(self, payment_intent_id, payment_method=None):
        """Ödemeyi tamamlandı olarak işaretle (commit yapmaz, sadece field'ları günceller)"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.stripe_payment_intent_id = payment_intent_id
        if payment_method:
            self.payment_method = payment_method
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self, reason=None):
        """Ödemeyi başarısız olarak işaretle (commit yapmaz, sadece field'ları günceller)"""
        self.status = 'failed'
        self.updated_at = datetime.utcnow()
        if reason:
            import json
            metadata_dict = {}
            if self.payment_metadata:
                try:
                    metadata_dict = json.loads(self.payment_metadata)
                except:
                    pass
            metadata_dict['failure_reason'] = reason
            self.payment_metadata = json.dumps(metadata_dict, ensure_ascii=False)
    
    def to_dict(self):
        """Payment verilerini dict olarak döndür (API yanıtları için)"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status,
            'plan_type': self.plan_type,
            'invoice_number': self.invoice_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<Payment {self.invoice_number or self.id} - {self.status}>'


class TokenPurchase(db.Model):
    """Fiş satın alma geçmişi"""
    __tablename__ = 'token_purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    package_type = db.Column(db.String(20), nullable=False)  # 'small', 'medium', 'large', 'xlarge'
    tokens = db.Column(db.Integer, nullable=False)  # Satın alınan fiş sayısı
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Ödenen tutar
    currency = db.Column(db.String(3), default='TL', nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)  # İlgili ödeme kaydı
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='token_purchases')
    payment = db.relationship('Payment', backref='token_purchases')
    
    def __repr__(self):
        return f'<TokenPurchase {self.tokens} tokens for User {self.user_id}>'
