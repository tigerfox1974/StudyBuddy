"""
StudyBuddy Database Models
SQLite veritabani icin model tanimlari
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Document(db.Model):
    """Yuklenen dokumanlar"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    file_hash = db.Column(db.String(32), unique=True, nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    user_level = db.Column(db.String(20), nullable=False)  # elementary, middle_school, high_school, university
    user_type = db.Column(db.String(20), nullable=False)   # student, teacher
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
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

