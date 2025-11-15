"""
StudyBuddy - Dokümandan Sınav Modu
Flask Web Uygulaması
"""

import os
import time
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_file
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.utils import secure_filename
from config import Config
from services.document_reader import DocumentReader
from services.ai_generator import AIGenerator
from models import db, Document, Result, UsageStats, User, Subscription, UserUsageStats, Payment
from utils import (
    get_file_hash, check_cache, save_to_cache, parse_cached_result, estimate_tokens, 
    get_user_documents, validate_email_address, validate_file_signature, 
    check_user_upload_limit, increment_user_upload, increment_user_cache_hit, get_user_stats_summary,
    generate_invoice_pdf, send_payment_confirmation_email, activate_user_subscription, 
    get_user_payment_history, format_currency,
    initialize_user_tokens, is_trial_active, calculate_token_cost, check_user_tokens, 
    deduct_tokens, can_user_export, get_user_token_info,
    generate_export_pdf, generate_export_docx
)
import markdown
import stripe
from decimal import Decimal


# Flask uygulamasını oluştur
app = Flask(__name__)
app.config.from_object(Config)

# SocketIO'yu başlat
socketio = SocketIO(app, cors_allowed_origins="*")

# Database'i başlat
db.init_app(app)

# Flask-Login'i başlat
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Bu sayfayı görüntülemek için giriş yapmalısınız.'
login_manager.login_message_category = 'info'

# Flask-Mail'i başlat
mail = Mail(app)

# Flask-Limiter'i başlat (Flask-Login'den sonra, current_user erişimi için)
def get_user_identifier():
    """Rate limiting için kullanıcı tanımlayıcısı"""
    if current_user.is_authenticated:
        return str(current_user.id)
    return get_remote_address()

limiter = Limiter(
    app=app,
    key_func=get_user_identifier,
    storage_uri=app.config['RATELIMIT_STORAGE_URI'],
    enabled=app.config['RATELIMIT_ENABLED'],
    default_limits=['200/day', '50/hour']
)

# Flask-WTF CSRF Protection'ı başlat
csrf = CSRFProtect(app)

# Upload klasörünün var olduğundan emin ol
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Stripe configuration
if app.config.get('STRIPE_ENABLED', True) and app.config.get('STRIPE_SECRET_KEY'):
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

# Stripe konfigürasyon doğrulaması (startup'ta)
try:
    Config.validate_stripe_config()
except ValueError as e:
    # Unicode-safe error message
    error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
    print(f"WARNING: Stripe configuration validation failed: {error_msg}")
    # Stripe'ı devre dışı bırak veya uygulamayı durdur
    # Burada devre dışı bırakıyoruz, böylece uygulama çalışmaya devam edebilir
    app.config['STRIPE_ENABLED'] = False
    print("Stripe has been disabled. Payment features will not be available.")

# Database tablolarını oluştur
# NOT: db.create_all() sadece initial schema oluşturma için kullanılır.
# Mevcut tablolarda değişiklik yapmak için migration script'lerini kullanın (migrations/add_user_id_column.py)
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login için user loader callback"""
    return User.query.get(int(user_id))


def emit_progress(progress, message):
    """SocketIO ile ilerleme gönder"""
    try:
        socketio.emit('progress', {'progress': progress, 'message': message})
        socketio.sleep(0.1)  # Socket'in göndermesi için kısa bekleme
    except:
        pass  # SocketIO hatalarını sessizce geç


def send_reset_email(to_email, reset_link):
    """Şifre sıfırlama email'i gönder"""
    try:
        expiry_hours = Config.RESET_TOKEN_EXPIRY_HOURS
        logo_url = url_for('static', filename='img/studybuddy-owl.png', _external=True)
        
        msg = Message(
            subject='StudyBuddy - Şifre Sıfırlama',
            recipients=[to_email],
            body=render_template('email/reset_password.txt', reset_link=reset_link, expiry_hours=expiry_hours),
            html=render_template('email/reset_password.html', reset_link=reset_link, expiry_hours=expiry_hours, logo_url=logo_url)
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email gönderme hatası: {str(e)}")
        return False


@app.route('/')
def index():
    """Ana sayfa - Landing page (herkes için)"""
    return render_template('index.html', 
                          user=current_user, 
                          config=Config)


@app.route('/upload')
@login_required
def upload():
    """Dosya yükleme sayfası - sadece giriş yapmış kullanıcılar için"""
    limit_info = None
    token_info = None
    _, _, limit_info = check_user_upload_limit(current_user.id)
    token_info = get_user_token_info(current_user)
    
    return render_template('upload.html', 
                          user=current_user, 
                          config=Config,
                          limit_info=limit_info,
                          token_info=token_info)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Kullanıcı kayıt sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Email validation
        validated_email = validate_email_address(email)
        if not validated_email:
            flash('Geçersiz email adresi.', 'error')
            return render_template('register.html')
        
        email = validated_email
        
        # Email uniqueness
        if User.query.filter_by(email=email).first():
            flash('Bu email adresi zaten kullanılıyor.', 'error')
            return render_template('register.html')
        
        # Username validation: non-empty, trimmed, minimum length
        if not username or len(username) < 3:
            if not username:
                # Username boşsa email'den otomatik oluştur
                from utils import generate_username_from_email
                username = generate_username_from_email(email)
            else:
                flash('Kullanıcı adı en az 3 karakter olmalıdır.', 'error')
                return render_template('register.html')
        
        # Username uniqueness (sadece boş değilse kontrol et)
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return render_template('register.html')
        
        # Password validation
        is_valid, errors = Config.validate_password(password)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Password confirmation
        if password != password_confirm:
            flash('Şifreler eşleşmiyor.', 'error')
            return render_template('register.html')
        
        # Create user
        try:
            user = User(email=email, username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # ID'yi almak için
            
            # Yeni kullanıcı için fiş sistemini başlat
            initialize_user_tokens(user)
            
            db.session.commit()
            
            # Auto login
            login_user(user)
            flash('Hesabınız başarıyla oluşturuldu! 7 günlük deneme süreniz başladı!', 'success')
            return redirect(url_for('upload'))
        except Exception as e:
            db.session.rollback()
            flash(f'Kayıt sırasında bir hata oluştu: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı giriş sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # User lookup
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Email veya şifre hatalı.', 'error')
            return render_template('login.html')
        
        # Check if active
        if not user.is_active:
            flash('Hesabınız devre dışı.', 'error')
            return render_template('login.html')
        
        # Login
        login_user(user, remember=remember_me)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        flash(f'Hoş geldiniz, {user.username}!', 'success')
        
        # Redirect to next page or upload
        next_page = request.args.get('next')
        if next_page:
            # Security check: prevent open redirect
            parsed_url = urlparse(next_page)
            if parsed_url.netloc == '':
                return redirect(next_page)
        return redirect(url_for('upload'))
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Kullanıcı çıkış"""
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('index'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Şifre sıfırlama talep sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        user = User.query.filter_by(email=email).first()
        
        # Security: Always show success message (prevent email enumeration)
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            
            reset_link = url_for('reset_password', token=token, _external=True)
            send_reset_email(user.email, reset_link)
        
        flash('Şifre sıfırlama linki email adresinize gönderildi.', 'info')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Şifre sıfırlama sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('Geçersiz veya süresi dolmuş link.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Password validation
        is_valid, errors = Config.validate_password(password)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('reset_password.html', token=token)
        
        # Password confirmation
        if password != password_confirm:
            flash('Şifreler eşleşmiyor.', 'error')
            return render_template('reset_password.html', token=token)
        
        # Update password
        user.set_password(password)
        user.clear_reset_token()
        db.session.commit()
        
        flash('Şifreniz başarıyla güncellendi.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)


@app.route('/profile')
@login_required
def profile():
    """Kullanıcı profil sayfası"""
    stats_summary = get_user_stats_summary(current_user.id)
    payment_history = get_user_payment_history(current_user.id, limit=5)
    token_info = get_user_token_info(current_user)
    plan_type = current_user.subscription_plan or 'free'
    plan_config = Config.SUBSCRIPTION_PLANS.get(plan_type, {})
    
    return render_template('profile.html', 
                          user=current_user, 
                          stats=stats_summary,
                          payment_history=payment_history,
                          config=Config,
                          format_currency=format_currency,
                          token_info=token_info,
                          plan_config=plan_config,
                          plan_type=plan_type)


@app.route('/pricing')
def pricing():
    """Abonelik planları karşılaştırma sayfası"""
    plans = Config.SUBSCRIPTION_PLANS
    
    # Kullanıcı giriş yapmışsa mevcut planını belirle
    current_plan = None
    if current_user.is_authenticated:
        current_plan = current_user.subscription_plan
    
    return render_template('pricing.html', 
                          plans=plans, 
                          current_plan=current_plan,
                          user=current_user)


@app.route('/dashboard')
@login_required
def dashboard():
    """Kullanıcı dashboard'u - kullanım istatistikleri"""
    stats_summary = get_user_stats_summary(current_user.id)
    
    return render_template('dashboard.html',
                          stats=stats_summary,
                          user=current_user,
                          config=Config)


@app.route('/process', methods=['POST'])
@login_required
@limiter.limit(Config.UPLOAD_RATE_LIMIT)
def process():
    """
    Dosya yükleme ve işleme route'u - Cache destekli
    """
    # Dosya kontrolü
    if 'file' not in request.files:
        flash('Dosya seçilmedi', 'error')
        return redirect(url_for('upload'))
    
    file = request.files['file']
    
    # Dosya adı kontrolü
    if file.filename == '':
        flash('Dosya seçilmedi', 'error')
        return redirect(url_for('upload'))
    
    # Dosya uzantısı kontrolü
    if not Config.allowed_file(file.filename):
        flash(f'Desteklenmeyen dosya formatı. Lütfen şu formatlardan birini kullanın: {", ".join(Config.ALLOWED_EXTENSIONS)}', 'error')
        return redirect(url_for('upload'))
    
    # Profil ve seviye bilgilerini al
    user_level = request.form.get('level', 'high_school')
    user_type = request.form.get('user_type', 'student')
    short_settings = Config.LEVEL_SETTINGS.get(user_level, Config.LEVEL_SETTINGS['high_school']).get('short_answer', {})
    short_answer_max_words = short_settings.get('max_words', 4)
    
    try:
        emit_progress(5, 'Dosya yükleniyor...')
        
        # Dosyayı oku
        file_content = file.read()
        file_size = len(file_content)
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        emit_progress(15, 'Dosya kontrol ediliyor...')
        
        # Dosya imza doğrulaması (Magic Number Validation)
        if app.config.get('VALIDATE_FILE_SIGNATURES', True):
            is_valid, error_msg = validate_file_signature(file_content, file_extension)
            if not is_valid:
                flash(error_msg, 'error')
                return redirect(url_for('upload'))
        
        # Dosya hash'ini hesapla
        file_hash = get_file_hash(file_content)
        
        emit_progress(20, 'Önbellek kontrol ediliyor...')
        
        # Cache kontrolü yap
        cached_result = check_cache(file_hash, user_level, user_type, current_user.id)
        
        if cached_result:
            # CACHE HIT - Daha once islenmis!
            print(f"[CACHE HIT] Token saved: ~{cached_result.token_used}")
            
            # İstatistik güncelle
            stats = UsageStats.get_or_create()
            stats.update_cache_hit(cached_result.token_used)
            
            # Kullanıcı bazlı stats güncelle
            increment_user_cache_hit(current_user.id, cached_result.token_used)
            
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
                                   user_type=user_type,
                                   short_answer_max_words=short_answer_max_words,
                                   user=current_user,
                                   result_id=cached_result.id)
        
        # CACHE MISS - Ilk defa isleniyor
        print(f"[CACHE MISS] Isleniyor: {filename}")
        
        # Plan bilgilerini al
        plan_type = current_user.subscription_plan or 'free'
        plan_config = Config.SUBSCRIPTION_PLANS.get(plan_type, {})
        plan_features = plan_config.get('features', {})
        
        # Plan-bazlı dosya boyutu kontrolü
        max_file_size_mb = plan_features.get('max_file_size_mb', 10)
        max_file_size_bytes = max_file_size_mb * 1024 * 1024 if max_file_size_mb else None
        
        if max_file_size_bytes and file_size > max_file_size_bytes:
            error_msg = f'Dosya çok büyük! {plan_config.get("name", plan_type.upper())} için maksimum {max_file_size_mb} MB dosya yükleyebilirsiniz.'
            flash(error_msg, 'error')
            return redirect(url_for('upload'))
        
        # Fiş kontrolü - İşlem için gereken fiş miktarını hesapla
        # Tüm soru türleri için işlem yapılacak
        required_tokens = calculate_token_cost(
            question_types=None,  # Tüm soru türleri
            include_export=False,  # Export yapılmayacak
            user_plan=plan_type
        )
        
        # Kullanıcının yeterli fişi var mı kontrol et
        can_afford, token_error_msg, available_tokens = check_user_tokens(current_user, required_tokens)
        
        if not can_afford:
            flash(token_error_msg, 'error')
            return redirect(url_for('pricing'))
        
        emit_progress(25, 'Dosya kaydediliyor...')
        
        # Geçici dosyayı kaydet
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        emit_progress(30, 'Metin çıkartılıyor...')
        
        # Dosyadan metin çıkar
        text, error = DocumentReader.extract_text_from_file(file_path, file_extension)
        
        if error:
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Dosya işleme hatası: {error}', 'error')
            return redirect(url_for('upload'))
        
        emit_progress(40, 'Metin hazırlanıyor...')
        
        # Metni token limitine göre kısalt
        text = DocumentReader.truncate_text(text)
        estimated_tokens = estimate_tokens(text)
        
        # AI ile içerik üret
        try:
            Config.validate_config()
            
            emit_progress(50, 'Özet oluşturuluyor...')
            start_time = time.time()
            
            ai_generator = AIGenerator()
            
            emit_progress(60, 'Sorular üretiliyor...')
            results = ai_generator.generate_all_content(text, level=user_level, user_type=user_type, user_plan=plan_type)
            
            emit_progress(90, 'Sonuçlar hazırlanıyor...')
            
            processing_time = time.time() - start_time
            
            # Plan bazlı soru limitlerini uygula
            max_questions_per_type = plan_features.get('max_questions_per_type')
            original_counts = {}
            plan_limit_info = {}
            
            if max_questions_per_type is not None:
                # Her soru türü için limit uygula
                question_types = {
                    'multiple_choice': 'Çoktan Seçmeli',
                    'short_answer': 'Kısa Cevap',
                    'fill_blank': 'Boş Doldurma',
                    'true_false': 'Doğru-Yanlış'
                }
                
                for q_type, q_name in question_types.items():
                    if q_type in results:
                        original_count = len(results[q_type])
                        original_counts[q_type] = original_count
                        
                        if original_count > max_questions_per_type:
                            # Limit uygula - sadece ilk N soruyu göster
                            results[q_type] = results[q_type][:max_questions_per_type]
                            plan_limit_info[q_type] = {
                                'name': q_name,
                                'generated': original_count,
                                'displayed': max_questions_per_type,
                                'limit': max_questions_per_type
                            }
            
            # Fiş düş
            deduct_tokens(current_user, required_tokens)
            db.session.commit()  # Fiş düşümünü kaydet
            
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
                processing_time=processing_time,
                user_id=current_user.id
            )
            
            # Kullanıcı bazlı yükleme sayacını artır
            increment_user_upload(current_user.id)
            
            # Özeti markdown'dan HTML'e çevir
            results['summary_html'] = markdown.markdown(results['summary'])
            
            # Token bilgilerini al
            token_info = get_user_token_info(current_user)
            
            # Sonuçları göster
            return render_template('result.html',
                                   filename=filename,
                                   results=results,
                                   from_cache=False,
                                   user_level=user_level,
                                   user_type=user_type,
                                   processing_time=processing_time,
                                   short_answer_max_words=short_answer_max_words,
                                   user=current_user,
                                   user_plan=plan_type,
                                   plan_config=plan_config,
                                   original_counts=original_counts,
                                   plan_limit_info=plan_limit_info,
                                   token_info=token_info,
                                   result_id=result.id)
        
        except ValueError as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(str(e), 'error')
            return redirect(url_for('upload'))
        
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'İçerik üretimi sırasında hata oluştu: {str(e)}', 'error')
            return redirect(url_for('upload'))
    
    except Exception as e:
        flash(f'Bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('upload'))


@app.route('/history')
@login_required
def history():
    """Kullanıcının döküman geçmişi sayfası"""
    # Kullanıcının tüm dökümanlarını getir (limit yok, tümünü göster)
    documents = get_user_documents(user_id=current_user.id, limit=None)
    
    return render_template('history.html', documents=documents, user=current_user)


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """GET: Ödeme önizleme sayfası, POST: Stripe Checkout Session oluştur ve yönlendir"""
    if not app.config.get('STRIPE_ENABLED', True):
        flash('Ödeme sistemi şu anda kullanılamıyor.', 'error')
        return redirect(url_for('pricing'))
    
    if request.method == 'GET':
        # GET: Ödeme önizleme sayfasını göster
        plan_type = request.args.get('plan_type', 'premium')
        
        # Plan kontrolü
        if plan_type not in Config.SUBSCRIPTION_PLANS:
            flash('Geçersiz plan seçimi.', 'error')
            return redirect(url_for('pricing'))
        
        plan = Config.SUBSCRIPTION_PLANS[plan_type]
        
        # Kullanıcı zaten bu planda mı?
        if current_user.subscription_plan == plan_type:
            flash('Zaten bu plandasınız.', 'info')
            return redirect(url_for('pricing'))
        
        # Stripe price ID kontrolü
        stripe_price_id = plan.get('stripe_price_id')
        if not stripe_price_id or stripe_price_id == 'price_your_premium_price_id_here':
            flash('Ödeme sistemi yapılandırılmamış. Lütfen daha sonra tekrar deneyin.', 'error')
            return redirect(url_for('pricing'))
        
        return render_template('checkout.html', 
                             plan=plan, 
                             plan_key=plan_type,
                             user=current_user,
                             config=Config)
    
    # POST: Stripe Checkout Session oluştur
    try:
        # Stripe konfigürasyon kontrolü (runtime'da da kontrol et)
        try:
            Config.validate_stripe_config()
        except ValueError as e:
            flash('Ödeme sistemi yapılandırılmamış. Lütfen daha sonra tekrar deneyin.', 'error')
            return redirect(url_for('pricing'))
        
        plan_type = request.form.get('plan_type', 'premium')
        
        # Plan kontrolü
        if plan_type not in Config.SUBSCRIPTION_PLANS:
            flash('Geçersiz plan seçimi.', 'error')
            return redirect(url_for('pricing'))
        
        plan = Config.SUBSCRIPTION_PLANS[plan_type]
        
        # Kullanıcı zaten bu planda mı?
        if current_user.subscription_plan == plan_type:
            flash('Zaten bu plandasınız.', 'info')
            return redirect(url_for('pricing'))
        
        # Stripe price ID kontrolü
        stripe_price_id = plan.get('stripe_price_id')
        if not stripe_price_id or stripe_price_id == 'price_your_premium_price_id_here':
            flash('Ödeme sistemi yapılandırılmamış. Lütfen daha sonra tekrar deneyin.', 'error')
            return redirect(url_for('pricing'))
        
        # Payment kaydı oluştur (pending) - stripe_session_id başlangıçta None
        payment = Payment(
            user_id=current_user.id,
            amount=Decimal(str(plan['price'])),
            currency=plan.get('currency', 'TRY'),
            status='pending',
            stripe_session_id=None,  # Session oluşturulduktan sonra güncellenecek
            plan_type=plan_type,
            billing_period=plan.get('billing_period', 'monthly')
        )
        db.session.add(payment)
        db.session.flush()
        
        # Stripe Checkout Session oluştur
        try:
            session = stripe.checkout.Session.create(
                mode='subscription' if plan.get('billing_period') == 'monthly' else 'payment',
                line_items=[{
                    'price': stripe_price_id,
                    'quantity': 1,
                }],
                customer_email=current_user.email,
                client_reference_id=str(current_user.id),
                metadata={
                    'user_id': str(current_user.id),
                    'payment_id': str(payment.id),
                    'plan_type': plan_type
                },
                success_url=url_for('checkout_success', session_id='{CHECKOUT_SESSION_ID}', _external=True),
                cancel_url=url_for('checkout_cancel', _external=True),
            )
            
            # Payment kaydına session ID'yi kaydet
            payment.stripe_session_id = session.id
            db.session.commit()
            
            # Stripe'a yönlendir
            return redirect(session.url)
            
        except stripe.error.StripeError as e:
            db.session.rollback()
            flash(f'Ödeme oturumu oluşturulamadı: {str(e)}', 'error')
            return redirect(url_for('pricing'))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('pricing'))


@app.route('/checkout/success')
@login_required
def checkout_success():
    """Ödeme başarılı sayfası"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Geçersiz oturum.', 'error')
        return redirect(url_for('pricing'))
    
    try:
        # Stripe session'ı al
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Payment kaydını bul
        payment = Payment.query.filter_by(stripe_session_id=session_id).first()
        
        if not payment:
            flash('Ödeme kaydı bulunamadı.', 'error')
            return redirect(url_for('pricing'))
        
        # Payment durumunu kontrol et
        if payment.status == 'completed':
            # Başarılı - abonelik aktif
            plan = Config.SUBSCRIPTION_PLANS.get(payment.plan_type, {})
            return render_template('success.html', 
                                 payment=payment, 
                                 plan=plan,
                                 user=current_user,
                                 format_currency=format_currency)
        else:
            # Hala işleniyor
            return render_template('success.html', 
                                 payment=payment, 
                                 plan=Config.SUBSCRIPTION_PLANS.get(payment.plan_type, {}),
                                 user=current_user,
                                 processing=True,
                                 format_currency=format_currency)
            
    except stripe.error.StripeError as e:
        flash(f'Ödeme bilgileri alınamadı: {str(e)}', 'error')
        return redirect(url_for('pricing'))
    except Exception as e:
        flash(f'Bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('pricing'))


@app.route('/checkout/cancel')
@login_required
def checkout_cancel():
    """Ödeme iptal sayfası"""
    flash('Ödeme işlemi iptal edildi.', 'info')
    return redirect(url_for('pricing'))


@app.route('/invoice/<int:payment_id>')
@login_required
def download_invoice(payment_id):
    """Fatura PDF'ini indir"""
    payment = Payment.query.get_or_404(payment_id)
    
    # Yetkilendirme kontrolü
    if payment.user_id != current_user.id:
        abort(403)
    
    if not payment.invoice_pdf_path or not os.path.exists(payment.invoice_pdf_path):
        flash('Fatura bulunamadı.', 'error')
        return redirect(url_for('profile'))
    
    return send_file(
        payment.invoice_pdf_path,
        as_attachment=True,
        download_name=f"{payment.invoice_number}.pdf",
        mimetype='application/pdf'
    )


@app.route('/stripe/webhook', methods=['POST'])
@csrf.exempt
def stripe_webhook():
    """Stripe webhook endpoint - ödeme olaylarını işle"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    if not app.config.get('STRIPE_WEBHOOK_SECRET'):
        return {'error': 'Webhook secret not configured'}, 400
    
    try:
        # Webhook signature'ı doğrula
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError as e:
        # Invalid payload
        print(f"Invalid payload: {str(e)}")
        return {'error': 'Invalid payload'}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Invalid signature: {str(e)}")
        return {'error': 'Invalid signature'}, 400
    
    # Event tipine göre işle
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        try:
            # Payment kaydını bul
            payment = Payment.query.filter_by(stripe_session_id=session['id']).first()
            
            if not payment:
                print(f"Payment not found for session: {session['id']}")
                return {'error': 'Payment not found'}, 404
            
            # Zaten işlenmiş mi kontrol et (idempotency)
            if payment.status == 'completed':
                print(f"Payment already processed: {payment.id}")
                return {'status': 'already_processed'}, 200
            
            # Payment Intent ID'yi al
            payment_intent_id = session.get('payment_intent')
            if not payment_intent_id:
                # Subscription için payment_intent yok, subscription ID olabilir
                subscription_id = session.get('subscription')
                if subscription_id:
                    # Subscription'dan invoice'u al, invoice'dan payment intent'i al
                    try:
                        subscription = stripe.Subscription.retrieve(subscription_id)
                        if subscription.latest_invoice:
                            invoice = stripe.Invoice.retrieve(subscription.latest_invoice)
                            payment_intent_id = invoice.payment_intent
                    except Exception as e:
                        print(f"Error retrieving payment intent from subscription: {str(e)}")
                        # Fallback: session ID kullanılacak
            
            # Ödemeyi tamamlandı olarak işaretle (henüz commit yok)
            payment_method = 'card'  # Default
            if payment_intent_id:
                try:
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                    payment_method = payment_intent.payment_method_types[0] if payment_intent.payment_method_types else 'card'
                except Exception as e:
                    print(f"Error retrieving payment intent details: {str(e)}")
                    # Fallback: default payment_method kullanılacak
            
            # Tüm database işlemlerini tek transaction içinde yap
            payment.mark_completed(payment_intent_id or session.get('id'), payment_method)
            
            # Aboneliği aktif et (commit yapmaz)
            success, subscription, error = activate_user_subscription(
                payment.user_id, 
                payment.plan_type, 
                payment.id
            )
            
            if not success:
                raise Exception(f"Failed to activate subscription: {error}")
            
            # Fatura PDF'i oluştur (içinde commit yapıyor, ama hata olursa rollback edilecek)
            user = User.query.get(payment.user_id)
            plan = Config.SUBSCRIPTION_PLANS.get(payment.plan_type, {})
            invoice_pdf_path = generate_invoice_pdf(payment, user, plan)
            
            # Tüm işlemler başarılı oldu, tek seferde commit et
            db.session.commit()
            
            # Onay email'i gönder (commit sonrası, hata olsa bile rollback edilmez)
            try:
                send_payment_confirmation_email(user.email, payment, invoice_pdf_path)
            except Exception as e:
                print(f"Error sending confirmation email: {str(e)}")
                # Email hatası transaction'ı etkilemez
            
            print(f"Payment processed successfully: {payment.id}")
            return {'status': 'success'}, 200
            
        except Exception as e:
            print(f"Error processing webhook: {str(e)}")
            db.session.rollback()
            return {'error': str(e)}, 500
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        
        try:
            # Payment kaydını bul (metadata'dan veya session'dan)
            # Bu durumda session_id'yi metadata'dan alabiliriz
            payment = Payment.query.filter_by(
                stripe_payment_intent_id=payment_intent['id']
            ).first()
            
            if payment:
                payment.mark_failed(payment_intent.get('last_payment_error', {}).get('message', 'Payment failed'))
                db.session.commit()
                print(f"Payment marked as failed: {payment.id}")
            
            return {'status': 'processed'}, 200
            
        except Exception as e:
            print(f"Error processing failed payment: {str(e)}")
            db.session.rollback()
            return {'error': str(e)}, 500
    
    # Diğer event'ler için 200 döndür (Stripe tekrar göndermesin)
    return {'status': 'received'}, 200


@app.route('/result/<int:result_id>')
@login_required
def view_result(result_id):
    """Önceki sonuçları görüntüleme sayfası"""
    # Result'u getir
    result = Result.query.get_or_404(result_id)
    
    # Yetkilendirme kontrolü - kullanıcı sadece kendi dökümanlarının sonuçlarını görebilir
    # Legacy veriler için: user_id None olabilir, bu durumda erişim engellenir
    document_user_id = result.document.user_id
    if document_user_id is None:
        # Legacy veri: user_id yok, erişim engellenir
        flash('Bu sonuç eski bir kayıttan geliyor ve artık erişilebilir değil.', 'error')
        abort(403)
    
    if document_user_id != current_user.id:
        abort(403)
    
    # Sonuçları parse et
    results_data = parse_cached_result(result)
    
    # Özeti markdown'dan HTML'e çevir
    results_data['summary_html'] = markdown.markdown(results_data['summary'])
    
    # Kısa cevap max kelime sayısını al
    short_settings = Config.LEVEL_SETTINGS.get(result.document.user_level, Config.LEVEL_SETTINGS['high_school']).get('short_answer', {})
    short_answer_max_words = short_settings.get('max_words', 4)
    
    return render_template('result.html',
                          filename=result.document.original_filename,
                          results=results_data,
                          from_cache=True,
                          user_level=result.document.user_level,
                          user_type=result.document.user_type,
                          short_answer_max_words=short_answer_max_words,
                          user=current_user,
                          result_id=result_id)


@app.route('/export/<int:result_id>')
@login_required
def export(result_id):
    """Result'u PDF veya DOCX formatında export et"""
    # Result'u getir
    result = Result.query.get_or_404(result_id)
    
    # Yetkilendirme kontrolü - kullanıcı sadece kendi dökümanlarının sonuçlarını export edebilir
    # Legacy veriler için: user_id None olabilir, bu durumda erişim engellenir
    document_user_id = result.document.user_id
    if document_user_id is None:
        # Legacy veri: user_id yok, erişim engellenir
        flash('Bu sonuç eski bir kayıttan geliyor ve artık erişilebilir değil.', 'error')
        abort(403)
    
    if document_user_id != current_user.id:
        abort(403)
    
    # Format validasyonu
    format_param = request.args.get('format', 'pdf').lower()
    if format_param not in Config.EXPORT_FORMATS:
        flash(f'Geçersiz export formatı. Desteklenen formatlar: {", ".join(Config.EXPORT_FORMATS)}', 'error')
        return redirect(url_for('view_result', result_id=result_id))
    
    # Format type parametresi (full, questions_only, summary_only)
    type_param = request.args.get('type', 'full').lower()
    if type_param not in ['full', 'questions_only', 'summary_only']:
        type_param = 'full'
    
    # Plan ve fiş kontrolü
    can_export, error_msg, required_tokens = can_user_export(current_user)
    if not can_export:
        flash(error_msg, 'error')
        return redirect(url_for('view_result', result_id=result_id))
    
    # Export dosyası oluşturma
    try:
        if format_param == 'pdf':
            file_path = generate_export_pdf(result, current_user, format_type=type_param)
            mimetype = 'application/pdf'
        elif format_param == 'docx':
            file_path = generate_export_docx(result, current_user, format_type=type_param)
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            flash('Desteklenmeyen export formatı.', 'error')
            return redirect(url_for('view_result', result_id=result_id))
    except ImportError as e:
        flash(f'Export için gerekli kütüphane yüklü değil: {str(e)}', 'error')
        return redirect(url_for('view_result', result_id=result_id))
    except Exception as e:
        flash(f'Export oluşturulurken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('view_result', result_id=result_id))
    
    # Token düşme (sadece required_tokens > 0 ise)
    if required_tokens > 0:
        deduct_tokens(current_user, required_tokens)
        db.session.commit()
    
    # Dosya indirme
    download_name = f"{result.document.original_filename.rsplit('.', 1)[0]}_export.{format_param}"
    return send_file(file_path, as_attachment=True, download_name=download_name, mimetype=mimetype)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """CSRF token hatası"""
    flash('Güvenlik hatası: CSRF token eksik veya geçersiz. Lütfen sayfayı yenileyip tekrar deneyin.', 'error')
    referrer = request.referrer or url_for('index')
    return redirect(referrer)


@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit aşıldı hatası"""
    flash(Config.UPLOAD_RATE_LIMIT_MESSAGE, 'error')
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    return redirect(url_for('index'))


@app.errorhandler(413)
def too_large(e):
    """Dosya çok büyük hatası"""
    # Plan-bazlı limit mesajı göster
    if current_user.is_authenticated:
        plan_type = current_user.subscription_plan or 'free'
        max_file_size_mb = Config.get_plan_limit(plan_type, 'max_file_size_mb')
        error_msg = f'Dosya çok büyük! {plan_type.upper()} planı için maksimum {max_file_size_mb} MB dosya yükleyebilirsiniz.'
    else:
        # Giriş yapmamış kullanıcılar için varsayılan free plan limiti
        max_file_size_mb = Config.get_plan_limit('free', 'max_file_size_mb')
        error_msg = f'Dosya çok büyük! Maksimum {max_file_size_mb} MB dosya yükleyebilirsiniz.'
    flash(error_msg, 'error')
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(e):
    """Sunucu hatası"""
    flash('Sunucu hatası oluştu. Lütfen tekrar deneyin.', 'error')
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    return redirect(url_for('index'))


# Stripe error handler - sadece Stripe aktifse ekle
if app.config.get('STRIPE_ENABLED', True):
    @app.errorhandler(stripe.error.StripeError)
    def handle_stripe_error(e):
        """Stripe hatalarını yakala"""
        flash(f'Ödeme hatası: {str(e)}', 'error')
        return redirect(url_for('pricing'))


if __name__ == '__main__':
    # Geliştirme sunucusunu başlat (SocketIO ile)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

