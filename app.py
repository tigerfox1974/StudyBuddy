"""
StudyBuddy - Dokümandan Sınav Modu
Flask Web Uygulaması
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import Config
from services.document_reader import DocumentReader
from services.ai_generator import AIGenerator


# Flask uygulamasını oluştur
app = Flask(__name__)
app.config.from_object(Config)

# Upload klasörünün var olduğundan emin ol
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Ana sayfa - dosya yükleme formu"""
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    """
    Dosya yükleme ve işleme route'u
    Dosyayı alır, metin çıkarır ve AI ile içerik üretir
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
    
    try:
        # Dosyayı kaydet
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Dosya uzantısını al
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Dosyadan metin çıkar
        text, error = DocumentReader.extract_text_from_file(file_path, file_extension)
        
        if error:
            # Geçici dosyayı temizle
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Dosya işleme hatası: {error}', 'error')
            return redirect(url_for('index'))
        
        # Metni token limitine göre kısalt
        text = DocumentReader.truncate_text(text)
        
        # AI ile içerik üret
        try:
            Config.validate_config()
            ai_generator = AIGenerator()
            results = ai_generator.generate_all_content(text)
            
            # Geçici dosyayı temizle
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Sonuçları göster
            return render_template('result.html', 
                                   filename=filename,
                                   results=results)
        
        except ValueError as e:
            # API key hatası
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(str(e), 'error')
            return redirect(url_for('index'))
        
        except Exception as e:
            # AI üretim hatası
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'İçerik üretimi sırasında hata oluştu: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        # Genel hata
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

