"""
StudyBuddy - Dokümandan Sınav Modu
Flask Web Uygulaması
"""

import os
import time
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import Config
from services.document_reader import DocumentReader
from services.ai_generator import AIGenerator
from models import db, Document, Result, UsageStats
from utils import get_file_hash, check_cache, save_to_cache, parse_cached_result, estimate_tokens, get_user_documents
import markdown


# Flask uygulamasını oluştur
app = Flask(__name__)
app.config.from_object(Config)

# Database'i başlat
db.init_app(app)

# Upload klasörünün var olduğundan emin ol
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database tablolarını oluştur
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """Ana sayfa - dosya yükleme formu"""
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    """
    Dosya yükleme ve işleme route'u - Cache destekli
    """
    # Dosya kontrolü
    if 'file' not in request.files:
        flash('Dosya seçilmedi', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # Dosya adı kontrolü
    if file.filename == '':
        flash('Dosya seçilmedi', 'error')
        return redirect(url_for('index'))
    
    # Dosya uzantısı kontrolü
    if not Config.allowed_file(file.filename):
        flash(f'Desteklenmeyen dosya formatı. Lütfen şu formatlardan birini kullanın: {", ".join(Config.ALLOWED_EXTENSIONS)}', 'error')
        return redirect(url_for('index'))
    
    # Profil ve seviye bilgilerini al
    user_level = request.form.get('level', 'high_school')
    user_type = request.form.get('user_type', 'student')
    
    try:
        # Dosyayı oku
        file_content = file.read()
        file_size = len(file_content)
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Dosya hash'ini hesapla
        file_hash = get_file_hash(file_content)
        
        # Cache kontrolü yap
        cached_result = check_cache(file_hash, user_level, user_type)
        
        if cached_result:
            # ✅ CACHE HIT - Daha önce işlenmiş!
            print(f"✅ Cache hit! Token saved: ~{cached_result.token_used}")
            
            # İstatistik güncelle
            stats = UsageStats.get_or_create()
            stats.update_cache_hit(cached_result.token_used)
            
            # Kayıtlı sonuçları parse et
            results_data = parse_cached_result(cached_result)
            
            # Özeti markdown'dan HTML'e çevir
            results_data['summary_html'] = markdown.markdown(results_data['summary'])
            
            flash(f'Bu dosya daha önce işlenmişti! Kayıtlı sonuçlar gösteriliyor. (Token tasarrufu: ~{cached_result.token_used})', 'success')
            
            return render_template('result.html',
                                   filename=filename,
                                   results=results_data,
                                   from_cache=True,
                                   user_level=user_level,
                                   user_type=user_type)
        
        # ❌ CACHE MISS - İlk defa işleniyor
        print(f"❌ Cache miss - İşleniyor: {filename}")
        
        # Geçici dosyayı kaydet
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Dosyadan metin çıkar
        text, error = DocumentReader.extract_text_from_file(file_path, file_extension)
        
        if error:
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Dosya işleme hatası: {error}', 'error')
            return redirect(url_for('index'))
        
        # Metni token limitine göre kısalt
        text = DocumentReader.truncate_text(text)
        estimated_tokens = estimate_tokens(text)
        
        # AI ile içerik üret
        try:
            Config.validate_config()
            start_time = time.time()
            
            ai_generator = AIGenerator()
            results = ai_generator.generate_all_content(text, level=user_level, user_type=user_type)
            
            processing_time = time.time() - start_time
            
            # Geçici dosyayı temizle
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Cache'e kaydet
            save_to_cache(
                file_hash=file_hash,
                filename=filename,
                file_type=file_extension,
                file_size=file_size,
                user_level=user_level,
                user_type=user_type,
                results_data=results,
                ai_model=Config.OPENAI_MODEL,
                token_used=estimated_tokens,
                processing_time=processing_time
            )
            
            # Özeti markdown'dan HTML'e çevir
            results['summary_html'] = markdown.markdown(results['summary'])
            
            # Sonuçları göster
            return render_template('result.html',
                                   filename=filename,
                                   results=results,
                                   from_cache=False,
                                   user_level=user_level,
                                   user_type=user_type,
                                   processing_time=processing_time)
        
        except ValueError as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(str(e), 'error')
            return redirect(url_for('index'))
        
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'İçerik üretimi sırasında hata oluştu: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.errorhandler(413)
def too_large(e):
    """Dosya çok büyük hatası"""
    flash('Dosya çok büyük! Maksimum 16 MB dosya yükleyebilirsiniz.', 'error')
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(e):
    """Sunucu hatası"""
    flash('Sunucu hatası oluştu. Lütfen tekrar deneyin.', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Geliştirme sunucusunu başlat
    app.run(debug=True, host='0.0.0.0', port=5000)

