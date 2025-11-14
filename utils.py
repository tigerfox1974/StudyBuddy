"""
StudyBuddy Utility Functions
Dosya hash, cache kontrol ve diger yardimci fonksiyonlar
"""

import hashlib
import json
from models import Document, Result, UsageStats, db


def get_file_hash(file_content):
    """
    Dosya iceriginin MD5 hash'ini dondurur
    Ayni icerik = Ayni hash = Cache hit
    
    Args:
        file_content: Binary dosya icerigi
        
    Returns:
        32 karakterlik hex hash
    """
    return hashlib.md5(file_content).hexdigest()


def check_cache(file_hash, user_level, user_type):
    """
    Cache'de bu dosya var mi kontrol eder
    
    Args:
        file_hash: Dosyanin MD5 hash'i
        user_level: Kullanici seviyesi (elementary, high_school, etc.)
        user_type: Kullanici tipi (student, teacher)
        
    Returns:
        Result object veya None
    """
    document = Document.query.filter_by(
        file_hash=file_hash,
        user_level=user_level,
        user_type=user_type
    ).first()
    
    if document and document.results:
        # Last accessed guncelle
        from datetime import datetime
        document.last_accessed = datetime.utcnow()
        db.session.commit()
        
        return document.results[0]
    
    return None


def save_to_cache(file_hash, filename, file_type, file_size, user_level, user_type, 
                  results_data, ai_model, token_used, processing_time):
    """
    Sonuclari cache'e (veritabanina) kaydeder
    
    Args:
        file_hash: Dosya hash'i
        filename: Orijinal dosya adi
        file_type: Dosya tipi (pdf, docx, etc.)
        file_size: Dosya boyutu (byte)
        user_level: Kullanici seviyesi
        user_type: Kullanici tipi
        results_data: Uretilen icerikler (dict)
        ai_model: Kullanilan AI modeli
        token_used: Harcanan token
        processing_time: Islem suresi (saniye)
        
    Returns:
        Result object
    """
    # Once ayni kombinasyon var mi kontrol et
    existing_document = Document.query.filter_by(
        file_hash=file_hash,
        user_level=user_level,
        user_type=user_type
    ).first()
    
    if existing_document:
        # Mevcut document varsa, eski result'u sil ve yenisini olustur
        # (Kullanici ayni dosyayi tekrar yuklerse guncel sonuc almali)
        for old_result in existing_document.results:
            db.session.delete(old_result)
        document = existing_document
        # Son erisim zamanini guncelle
        from datetime import datetime
        document.last_accessed = datetime.utcnow()
    else:
        # Yeni document kaydi olustur
        document = Document(
            file_hash=file_hash,
            original_filename=filename,
            file_type=file_type,
            file_size=file_size,
            user_level=user_level,
            user_type=user_type
        )
        db.session.add(document)
    
    db.session.flush()  # ID'yi al
    
    # Result kaydi olustur
    result = Result(
        document_id=document.id,
        summary=results_data['summary'],
        multiple_choice=json.dumps(results_data['multiple_choice'], ensure_ascii=False),
        short_answer=json.dumps(results_data['short_answer'], ensure_ascii=False),
        fill_blank=json.dumps(results_data['fill_blank'], ensure_ascii=False),
        true_false=json.dumps(results_data['true_false'], ensure_ascii=False),
        flashcards=json.dumps(results_data['flashcards'], ensure_ascii=False),
        ai_model=ai_model,
        token_used=token_used,
        processing_time=processing_time
    )
    db.session.add(result)
    db.session.commit()
    
    # Istatistik guncelle
    stats = UsageStats.get_or_create()
    stats.update_cache_miss()
    
    return result


def parse_cached_result(result):
    """
    Cache'den gelen Result nesnesini parse eder
    
    Args:
        result: Result database nesnesi
        
    Returns:
        dict: Frontend'e gonderilecek format
    """
    return {
        'summary': result.summary,
        'multiple_choice': json.loads(result.multiple_choice),
        'short_answer': json.loads(result.short_answer),
        'fill_blank': json.loads(result.fill_blank),
        'true_false': json.loads(result.true_false),
        'flashcards': json.loads(result.flashcards),
        'from_cache': True,
        'cached_date': result.created_at.strftime('%d %B %Y, %H:%M'),
        'token_used': result.token_used,
        'processing_time': result.processing_time
    }


def estimate_tokens(text):
    """
    Metin icin tahmini token sayisini hesaplar
    Yaklasik: 1 token = 4 karakter (Turkce icin)
    
    Args:
        text: Analiz edilecek metin
        
    Returns:
        int: Tahmini token sayisi
    """
    return len(text) // 4


def get_user_documents(user_level=None, user_type=None, limit=10):
    """
    Kullanicinin daha once isledig dosyalari getirir
    
    Args:
        user_level: Filtre icin seviye (opsiyonel)
        user_type: Filtre icin tip (opsiyonel)
        limit: Maksimum sonuc sayisi
        
    Returns:
        List of Document objects
    """
    query = Document.query
    
    if user_level:
        query = query.filter_by(user_level=user_level)
    if user_type:
        query = query.filter_by(user_type=user_type)
    
    return query.order_by(Document.last_accessed.desc()).limit(limit).all()


def cleanup_old_cache(days=30):
    """
    Belirtilen gun oncesinden eski kayitlari siler
    
    Args:
        days: Kac gun oncesi (varsayilan 30)
        
    Returns:
        int: Silinen kayit sayisi
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    old_documents = Document.query.filter(Document.last_accessed < cutoff_date).all()
    
    count = len(old_documents)
    for doc in old_documents:
        db.session.delete(doc)
    
    db.session.commit()
    return count

