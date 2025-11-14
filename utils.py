"""
StudyBuddy Utility Functions
Dosya hash, cache kontrol ve diger yardimci fonksiyonlar
"""

import hashlib
import json
import re
import io
import zipfile
import os
from typing import Tuple, Optional
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from models import Document, Result, UsageStats, User, UserUsageStats, Subscription, Payment, db
from config import Config
from flask_mail import Message
from flask import render_template, url_for


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


def check_cache(file_hash, user_level, user_type, user_id=None):
    """
    Cache'de bu dosya var mi kontrol eder
    
    Args:
        file_hash: Dosyanin MD5 hash'i
        user_level: Kullanici seviyesi (elementary, high_school, etc.)
        user_type: Kullanici tipi (student, teacher)
        user_id: Kullanici ID'si (opsiyonel). None ise sadece file_hash, user_level ve user_type ile filtreleme yapilir.
                 None degilse kullanici-spesifik cache kontrolu yapilir.
        
    Returns:
        Result object veya None
        
    Note:
        - user_id None ise: Genel cache kontrolu (kullanici-spesifik degil)
        - user_id belirtilirse: Kullanici-spesifik cache kontrolu
    """
    query = Document.query.filter_by(
        file_hash=file_hash,
        user_level=user_level,
        user_type=user_type
    )
    
    # user_id belirtilmişse, kullanıcı filtresini ekle
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    
    document = query.first()
    
    if document and document.results:
        # Last accessed guncelle
        from datetime import datetime
        document.last_accessed = datetime.utcnow()
        db.session.commit()
        
        return document.results[0]
    
    return None


def save_to_cache(file_hash, filename, file_type, file_size, user_level, user_type, 
                  results_data, ai_model, token_used, processing_time, user_id):
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
        user_id: Kullanici ID'si
        
    Returns:
        Result object
    """
    # Once ayni kombinasyon var mi kontrol et
    existing_document = Document.query.filter_by(
        file_hash=file_hash,
        user_level=user_level,
        user_type=user_type,
        user_id=user_id
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
            user_type=user_type,
            user_id=user_id
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


def get_user_documents(user_id, limit=10, user_level=None, user_type=None):
    """
    Kullanicinin daha once isledig dosyalari getirir
    
    Args:
        user_id: Kullanici ID'si (zorunlu)
        limit: Maksimum sonuc sayisi (None ise limit yok, tumunu getirir)
        user_level: Filtre icin seviye (opsiyonel)
        user_type: Filtre icin tip (opsiyonel)
        
    Returns:
        List of Document objects
    """
    query = Document.query.filter_by(user_id=user_id)
    
    if user_level:
        query = query.filter_by(user_level=user_level)
    if user_type:
        query = query.filter_by(user_type=user_type)
    
    query = query.order_by(Document.last_accessed.desc())
    
    # limit None ise limit uygulama
    if limit is not None:
        query = query.limit(limit)
    
    return query.all()


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


def validate_email_address(email):
    """
    Email adresini validate eder ve normalize eder
    
    Args:
        email: Email adresi string
        
    Returns:
        str: Normalize edilmiş email veya None (geçersizse)
    """
    if not email:
        return None
    
    try:
        validated = validate_email(email)
        return validated.email.lower().strip()
    except EmailNotValidError:
        return None


def generate_username_from_email(email):
    """
    Email'den otomatik username oluşturur
    
    Args:
        email: Email adresi
        
    Returns:
        str: Unique username
    """
    from models import User
    
    # Email'in @ öncesi kısmını al
    base_username = email.split('@')[0]
    
    # Özel karakterleri temizle (sadece alphanumeric ve underscore)
    base_username = re.sub(r'[^a-zA-Z0-9_]', '', base_username)
    
    # Uniqueness kontrolü
    username = base_username
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username


def _read_head(content: bytes, n: int) -> bytes:
    """
    Dosya içeriğinin ilk n byte'ını güvenli şekilde okur
    
    Args:
        content: Dosya içeriği (bytes)
        n: Okunacak byte sayısı
        
    Returns:
        bytes: İlk n byte
    """
    return content[:n] if len(content) >= n else content


def _is_pdf(head: bytes) -> bool:
    """
    PDF dosyası olup olmadığını kontrol eder
    
    Args:
        head: Dosyanın ilk 5 byte'ı
        
    Returns:
        bool: PDF ise True
    """
    return head.startswith(b'%PDF-')


def _detect_office_zip(file_content: bytes) -> Optional[str]:
    """
    ZIP dosyasının DOCX mi PPTX mi olduğunu tespit eder
    
    Args:
        file_content: Dosya içeriği (bytes)
        
    Returns:
        str: 'docx', 'pptx' veya None
    """
    try:
        with zipfile.ZipFile(io.BytesIO(file_content), 'r') as zip_file:
            file_list = zip_file.namelist()
            
            # DOCX kontrolü: word/document.xml dosyası var mı?
            if any('word/document.xml' in name for name in file_list):
                return 'docx'
            
            # PPTX kontrolü: ppt/presentation.xml dosyası var mı?
            if any('ppt/presentation.xml' in name for name in file_list):
                return 'pptx'
            
            return None
    except (zipfile.BadZipFile, Exception):
        return None


def validate_file_signature(file_content: bytes, claimed_extension: str) -> Tuple[bool, Optional[str]]:
    """
    Dosya içeriğinin uzantısıyla eşleşip eşleşmediğini kontrol eder (Magic Number Validation)
    
    Args:
        file_content: Dosya içeriği (bytes)
        claimed_extension: Dosya uzantısı (örn: 'pdf', 'docx', 'pptx', 'txt')
        
    Returns:
        Tuple[bool, Optional[str]]: (True, None) geçerliyse, (False, error_message) geçersizse
    """
    if not file_content:
        return False, "Dosya boş veya geçersiz formatta."
    
    claimed_extension = claimed_extension.lower().lstrip('.')
    
    # TXT dosyaları için magic number kontrolü yok
    if claimed_extension == 'txt':
        return True, None
    
    # DOC (legacy) formatını reddet
    if claimed_extension == 'doc':
        return False, "Eski Word formatı (.doc) desteklenmiyor. Lütfen dosyanızı .docx formatına dönüştürün."
    
    # PDF kontrolü
    if claimed_extension == 'pdf':
        head = _read_head(file_content, 5)
        if not _is_pdf(head):
            return False, "Dosya içeriği uzantısıyla eşleşmiyor. PDF dosyası bekleniyor."
        return True, None
    
    # DOCX ve PPTX kontrolü (ZIP dosyaları)
    if claimed_extension in ('docx', 'pptx'):
        head = _read_head(file_content, 4)
        
        # ZIP signature kontrolü
        if not head.startswith(b'PK\x03\x04'):
            if claimed_extension == 'docx':
                return False, "Dosya içeriği uzantısıyla eşleşmiyor. Word belgesi bekleniyor."
            else:  # pptx
                return False, "Dosya içeriği uzantısıyla eşleşmiyor. PowerPoint sunumu bekleniyor."
        
        # ZIP içeriğini kontrol et
        detected_type = _detect_office_zip(file_content)
        
        if detected_type is None:
            return False, "Dosya bozuk veya geçersiz formatta."
        
        if detected_type != claimed_extension:
            if claimed_extension == 'docx':
                return False, "Dosya içeriği uzantısıyla eşleşmiyor. Word belgesi bekleniyor."
            else:  # pptx
                return False, "Dosya içeriği uzantısıyla eşleşmiyor. PowerPoint sunumu bekleniyor."
        
        return True, None
    
    # Desteklenmeyen uzantı
    return False, f"Desteklenmeyen dosya formatı: .{claimed_extension}"


def get_current_month_stats(user_id):
    """Kullanıcının bu ayki kullanım istatistiklerini getir veya oluştur"""
    now = datetime.utcnow()
    year = now.year
    month = now.month
    return UserUsageStats.get_or_create(user_id, year, month)


def increment_user_upload(user_id):
    """Kullanıcının dosya yükleme sayacını artır (cache miss durumunda)"""
    stats = get_current_month_stats(user_id)
    stats.increment_document()


def increment_user_cache_hit(user_id, tokens_saved):
    """Kullanıcının cache hit sayacını artır"""
    stats = get_current_month_stats(user_id)
    stats.increment_cache_hit(tokens_saved)


def check_user_upload_limit(user_id):
    """
    Kullanıcının aylık yükleme limitini kontrol et
    
    Returns:
        Tuple[bool, Optional[str], Optional[dict]]: 
        - (True, None, stats_dict): Limit OK, yükleme yapabilir
        - (False, error_message, stats_dict): Limit aşıldı, hata mesajı
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Kullanıcı bulunamadı", None
    
    plan_type = user.subscription_plan or 'free'
    limit = Config.get_monthly_upload_limit(plan_type)
    
    # Premium plan (sınırsız)
    if limit is None:
        stats = get_current_month_stats(user_id)
        return True, None, {
            'plan': plan_type,
            'limit': None,
            'used': stats.get_total_uploads(),
            'remaining': None
        }
    
    # Limit kontrolü
    stats = get_current_month_stats(user_id)
    current_uploads = stats.get_total_uploads()
    
    if current_uploads >= limit:
        error_msg = f"Aylık dosya yükleme limitinize ulaştınız ({limit} dosya). Bir sonraki ayın 1'inde limit otomatik olarak sıfırlanacaktır."
        return False, error_msg, {
            'plan': plan_type,
            'limit': limit,
            'used': current_uploads,
            'remaining': 0
        }
    
    return True, None, {
        'plan': plan_type,
        'limit': limit,
        'used': current_uploads,
        'remaining': limit - current_uploads
    }


def get_user_stats_summary(user_id):
    """Kullanıcının genel kullanım özetini getir (dashboard için)"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    stats = get_current_month_stats(user_id)
    can_upload, _, limit_info = check_user_upload_limit(user_id)
    
    total_documents = Document.query.filter_by(user_id=user_id).count()
    
    # Limit bilgisi için yüzde hesapla
    percentage = 0
    if limit_info and limit_info['limit']:
        percentage = (limit_info['used'] / limit_info['limit']) * 100
    
    return {
        'current_month': {
            'uploads': stats.documents_processed,
            'cache_hits': stats.cache_hits,
            'tokens_saved': stats.tokens_saved
        },
        'limit_info': {
            'plan': limit_info['plan'] if limit_info else 'free',
            'limit': limit_info['limit'] if limit_info else 5,
            'used': limit_info['used'] if limit_info else 0,
            'remaining': limit_info['remaining'] if limit_info else 5,
            'percentage': percentage
        },
        'total_documents': total_documents
    }


def generate_invoice_pdf(payment, user, subscription_plan):
    """
    PDF fatura oluştur (ReportLab kullanarak)
    
    Args:
        payment: Payment object
        user: User object
        subscription_plan: Plan details dict
        
    Returns:
        str: Oluşturulan PDF dosyasının yolu
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    
    # Invoice storage klasörünü oluştur
    invoice_dir = Config.INVOICE_STORAGE_PATH
    os.makedirs(invoice_dir, exist_ok=True)
    
    # PDF dosya yolu
    pdf_filename = f"{payment.invoice_number}.pdf"
    pdf_path = os.path.join(invoice_dir, pdf_filename)
    
    # PDF dokümanı oluştur
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Özel stiller
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )
    
    # Başlık
    story.append(Paragraph(Config.INVOICE_COMPANY_NAME, title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Fatura bilgileri
    invoice_data = [
        ['Fatura No:', payment.invoice_number],
        ['Tarih:', payment.created_at.strftime('%d %B %Y')],
        ['Durum:', 'Tamamlandı' if payment.status == 'completed' else payment.status]
    ]
    
    invoice_table = Table(invoice_data, colWidths=[4*cm, 10*cm])
    invoice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(invoice_table)
    story.append(Spacer(1, 0.8*cm))
    
    # Müşteri bilgileri
    story.append(Paragraph('Müşteri Bilgileri', heading_style))
    customer_data = [
        ['Ad:', user.username],
        ['Email:', user.email]
    ]
    
    customer_table = Table(customer_data, colWidths=[4*cm, 10*cm])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 0.8*cm))
    
    # Ürün/Hizmet tablosu
    story.append(Paragraph('Fatura Detayları', heading_style))
    
    # Fiyat hesaplamaları
    subtotal = float(payment.amount)
    tax_amount = subtotal * (Config.INVOICE_TAX_RATE / 100)
    total = subtotal + tax_amount
    
    items_data = [
        ['Açıklama', 'Dönem', 'Tutar'],
        [
            subscription_plan.get('name', 'Premium Plan'),
            payment.billing_period,
            f"₺{subtotal:.2f}"
        ]
    ]
    
    items_table = Table(items_data, colWidths=[8*cm, 3*cm, 3*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Toplam tablosu
    if Config.INVOICE_TAX_RATE > 0:
        total_data = [
            ['Ara Toplam:', f"₺{subtotal:.2f}"],
            ['KDV (%{}):'.format(Config.INVOICE_TAX_RATE), f"₺{tax_amount:.2f}"],
            ['TOPLAM:', f"₺{total:.2f}"]
        ]
    else:
        total_data = [
            ['TOPLAM:', f"₺{subtotal:.2f}"]
        ]
    
    total_table = Table(total_data, colWidths=[11*cm, 3*cm])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#667eea')),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 1*cm))
    
    # Ödeme bilgileri
    if payment.payment_method:
        story.append(Paragraph(f'Ödeme Yöntemi: {payment.payment_method}', styles['Normal']))
    if payment.stripe_payment_intent_id:
        story.append(Paragraph(f'İşlem ID: {payment.stripe_payment_intent_id[:20]}...', styles['Normal']))
    
    story.append(Spacer(1, 1*cm))
    
    # Teşekkür mesajı
    thank_you = ParagraphStyle(
        'ThankYou',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceBefore=20
    )
    story.append(Paragraph('Teşekkür ederiz!', thank_you))
    story.append(Paragraph(Config.INVOICE_COMPANY_ADDRESS, thank_you))
    
    # PDF'i oluştur
    doc.build(story)
    
    # Payment kaydına PDF yolunu kaydet (commit yapmaz, çağıran fonksiyon commit edecek)
    payment.invoice_pdf_path = pdf_path
    
    return pdf_path


def send_payment_confirmation_email(user_email, payment, invoice_pdf_path):
    """
    Ödeme onay email'i gönder (fatura PDF'i ile)
    
    Args:
        user_email: Email adresi
        payment: Payment object
        invoice_pdf_path: Invoice PDF dosya yolu
        
    Returns:
        bool: Başarılı ise True
    """
    from app import mail, app
    
    try:
        user = User.query.get(payment.user_id)
        plan = Config.SUBSCRIPTION_PLANS.get(payment.plan_type, {})
        dashboard_link = url_for('dashboard', _external=True)
        
        msg = Message(
            subject='StudyBuddy - Ödeme Onayı ve Fatura',
            recipients=[user_email],
            body=render_template('email/payment_success.txt', 
                               user=user, 
                               payment=payment, 
                               plan=plan,
                               dashboard_link=dashboard_link),
            html=render_template('email/payment_success.html', 
                               user=user, 
                               payment=payment, 
                               plan=plan,
                               dashboard_link=dashboard_link)
        )
        
        # PDF'i ekle
        if os.path.exists(invoice_pdf_path):
            with app.open_resource(invoice_pdf_path) as pdf_file:
                msg.attach(
                    filename=f"{payment.invoice_number}.pdf",
                    content_type="application/pdf",
                    data=pdf_file.read()
                )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email gönderme hatası: {str(e)}")
        return False


def activate_user_subscription(user_id, plan_type, payment_id):
    """
    Kullanıcının premium aboneliğini aktif et
    
    Args:
        user_id: User ID
        plan_type: Plan tipi ('premium')
        payment_id: Payment ID
        
    Returns:
        Tuple[bool, Optional[Subscription], Optional[str]]: (success, subscription, error)
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return False, None, "Kullanıcı bulunamadı"
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return False, None, "Ödeme kaydı bulunamadı"
        
        # Kullanıcının planını güncelle
        user.subscription_plan = plan_type
        db.session.flush()
        
        # Yeni subscription kaydı oluştur
        subscription = Subscription(
            user_id=user_id,
            plan_type=plan_type,
            status='active',
            start_date=datetime.utcnow(),
            end_date=None  # Süresiz (monthly için)
        )
        db.session.add(subscription)
        db.session.flush()
        
        # Payment'ı subscription'a bağla
        payment.subscription_id = subscription.id
        payment.invoice_number = Payment.generate_invoice_number()
        db.session.flush()
        
        # Mevcut ayın usage stats'ını sıfırla (yeni fatura dönemi)
        # Veya mevcut stats'ı koru - burada koruyoruz
        # stats = get_current_month_stats(user_id)
        # stats.documents_processed = 0  # İsteğe bağlı: yeni dönemde sıfırla
        
        # Commit yapmıyoruz - çağıran fonksiyon commit edecek
        return True, subscription, None
        
    except Exception as e:
        # Rollback yapmıyoruz - çağıran fonksiyon rollback edecek
        return False, None, str(e)


def get_user_payment_history(user_id, limit=10):
    """
    Kullanıcının ödeme geçmişini getir
    
    Args:
        user_id: User ID
        limit: Maksimum kayıt sayısı
        
    Returns:
        List[Payment]: Payment nesneleri listesi (tarihe göre azalan)
    """
    return Payment.query.filter_by(user_id=user_id)\
        .order_by(Payment.created_at.desc())\
        .limit(limit)\
        .all()


def format_currency(amount, currency='TRY'):
    """
    Tutarı para birimi sembolü ile formatla
    
    Args:
        amount: Decimal veya float tutar
        currency: Para birimi kodu
        
    Returns:
        str: Formatlanmış tutar (örn: "₺49.99")
    """
    if currency == 'TRY':
        return f"₺{float(amount):.2f}"
    else:
        return f"{currency} {float(amount):.2f}"


