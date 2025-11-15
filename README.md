# 🎓 StudyBuddy - Dokümandan Sınav Modu

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**StudyBuddy**, öğrencilerin PDF, Word, PowerPoint ve metin dosyalarındaki ders notlarını yükleyerek **otomatik olarak özet, test soruları ve flashcard'lar üretmesini sağlayan** AI destekli bir web uygulamasıdır.

🌟 **Demo modu ile API anahtarı olmadan test edebilirsiniz!**

---

## 📸 Özellikler

- 📄 **Çoklu Dosya Desteği**: PDF, DOCX, PPTX, TXT formatlarını destekler
- 📝 **Konu Özeti**: Yüklenen dokümanlardan otomatik özet çıkarır
- ❓ **Çoktan Seçmeli Sorular**: 4 şıklı test soruları üretir (doğru cevap ve açıklama ile)
- ✍️ **Kısa Cevap Soruları**: Açık uçlu sorular ve örnek cevaplar
- 📋 **Boş Doldurma Soruları**: Cümlelerdeki boşlukları doldurma soruları
- ✅ **Doğru-Yanlış Soruları**: İfadelerin doğruluğunu test eden sorular
- 🗃️ **Flashcard Çalışma Kartları**: Soru-cevap çiftleri (ön yüz/arka yüz formatı)
- 🎨 **Modern Arayüz**: Bootstrap 5 ile responsive ve kullanıcı dostu tasarım
- 🔄 **Interaktif Flashcard**: Tıklayarak çevrilebilen çalışma kartları
- 🧪 **Demo Modu**: OpenAI API olmadan test edebilme (sahte verilerle)
- ✅ **Abonelik Yönetimi:** Free, Standart ve Premium plan desteği
- ✅ **Token (Fiş) Sistemi:** Kullanım bazlı fiş sistemi ile esnek ödeme
- ✅ **7 Günlük Deneme:** Yeni kullanıcılar için 10 fiş deneme süresi
- ✅ **Kullanım Limitleri:** Plan bazlı dosya boyutu ve soru limitleri
- ✅ **Kullanım İstatistikleri:** Detaylı dashboard ve raporlama
- ✅ **Cache Sistemi:** Token tasarrufu ve hızlı erişim
- ♿ **Erişilebilirlik:** WCAG 2.1 AA uyumlu, keyboard navigation desteği
- 🎨 **Design System:** Tutarlı renk paleti, spacing ve typography
- 🔍 **Gelişmiş Form UX:** Floating label, password strength göstergesi, autofill desteği

## Teknoloji Yığını

- **Backend**: Python 3 + Flask
- **AI**: OpenAI API (GPT-3.5-turbo / GPT-4)
- **Doküman İşleme**:
  - PDF: pypdf
  - Word: python-docx
  - PowerPoint: python-pptx
- **Arayüz**: HTML + Bootstrap 5
- **Ortam Yönetimi**: python-dotenv

## Gereksinimler

- Python 3.10 veya üzeri
- OpenAI API anahtarı
- Windows işletim sistemi (veya Linux/macOS)

## Kurulum Adımları

### 1. Python Kurulumu

Python 3.10 veya üzeri bir sürümün kurulu olduğundan emin olun. Kontrol etmek için:

```bash
python --version
```

### 2. Projeyi İndirin

```bash
git clone <repository-url>
cd StudyBuddy
```

### 3. Sanal Ortam Oluşturun

Windows için:

```bash
python -m venv .venv
```

### 4. Sanal Ortamı Aktif Edin

Windows PowerShell:

```bash
.\.venv\Scripts\activate
```

Windows CMD:

```bash
.venv\Scripts\activate.bat
```

### 5. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

**Yeni Bağımlılıklar:**
- `Flask-Limiter`: Rate limiting için (dosya yükleme limitleri)
- `Flask-WTF`: CSRF protection için (form güvenliği)
- `stripe`: Stripe ödeme entegrasyonu için
- `reportlab`: PDF fatura oluşturma için

**Not:** Production ortamında rate limiting için Redis kullanmak istiyorsanız:
- Redis'i kurun: https://redis.io/docs/getting-started/
- `.env` dosyasında `RATELIMIT_STORAGE_URI=redis://localhost:6379` ayarlayın

### 6. Ortam Değişkenlerini Ayarlayın

Proje kök dizininde `.env` adlı bir dosya oluşturun ve aşağıdaki içeriği ekleyin:

#### Demo Modu (OpenAI API olmadan test için):
```env
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
SECRET_KEY=dev-secret-key-studybuddy-2024
DEMO_MODE=true
```

#### Gerçek AI Kullanımı için:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo
SECRET_KEY=your-secret-key-here
DEMO_MODE=false
```

**Önemli**: 
- **DEMO_MODE=true**: OpenAI API olmadan çalışır, sahte veriler gösterir (test için ideal)
- **DEMO_MODE=false**: Gerçek OpenAI API kullanır (API anahtarı gerekli)
- `OPENAI_API_KEY` değerini [OpenAI Platform](https://platform.openai.com/api-keys) üzerinden aldığınız API anahtarı ile değiştirin.
- `SECRET_KEY` değerini güvenli, rastgele bir string ile değiştirin.
- İlk aşamada maliyet için `gpt-3.5-turbo` önerilir. Daha iyi kalite için `gpt-4` kullanabilirsiniz.

### 7. Uygulamayı Çalıştırın

```bash
python app.py
```

veya

```bash
flask run
```

Uygulama varsayılan olarak http://localhost:5000 adresinde çalışacaktır.

## Database Migration

Yeni abonelik sistemi için migration çalıştırın:

```bash
python migrations/add_subscription_models.py
```

Bu migration:
- `subscription` tablosunu oluşturur
- `user_usage_stats` tablosunu oluşturur
- Mevcut kullanıcılar için default subscription kayıtları oluşturur

Ödeme sistemi için migration çalıştırın:

```bash
python migrations/add_payment_model.py
```

Bu migration:
- `payments` tablosunu oluşturur
- `invoices/` klasörünü oluşturur

Token sistemi için migration çalıştırın:

```bash
python migrations/add_token_system_columns.py -y
```

Bu migration:
- `users` tablosuna `tokens_remaining`, `trial_ends_at`, `last_token_refresh` kolonlarını ekler
- `token_purchases` tablosunu oluşturur
- Mevcut kullanıcılar için varsayılan değerleri ayarlar

## Kullanım

1. Tarayıcınızda http://localhost:5000 adresine gidin
2. "Dosyanızı Yükleyin" alanına tıklayın ve ders notlarınızı içeren bir dosya seçin
   - Desteklenen formatlar: PDF, DOCX, PPTX, TXT
   - Maksimum dosya boyutu: Plan bazlı (Ücretsiz: 10 MB, Standart: 16 MB, Premium: 24 MB)
   - Fiş sistemi: Her dosya işleme için fiş harcanır (temel işleme: 1 fiş, her soru türü: +0.5 fiş)
3. "İçerik Üret" butonuna tıklayın
4. İşlem tamamlandığında sonuç sayfasında aşağıdaki içerikler görüntülenecektir:
   - **Özet**: Dokümanın ana konularını içeren özet
   - **Çoktan Seçmeli**: Test soruları ve doğru cevaplar
   - **Kısa Cevap**: Açık uçlu sorular ve örnek cevaplar
   - **Boş Doldurma**: Cümlelerdeki boşlukları doldurma soruları
   - **Doğru-Yanlış**: İfadelerin doğruluğunu test eden sorular
   - **Flashcards**: Üzerine tıklayarak çevrilebilen çalışma kartları

## Proje Yapısı

```
StudyBuddy/
├── app.py                      # Flask uygulaması ve route tanımları
├── config.py                   # Konfigürasyon ayarları
├── requirements.txt            # Python bağımlılıkları
├── .env                        # Ortam değişkenleri (oluşturulacak)
├── .gitignore                  # Git ignore kuralları
├── README.md                   # Bu dosya
│
├── services/                   # İş mantığı servisleri
│   ├── __init__.py
│   ├── document_reader.py      # Doküman okuma fonksiyonları
│   └── ai_generator.py         # OpenAI API entegrasyonu
│
├── templates/                  # HTML şablonları
│   ├── index.html              # Ana sayfa (dosya yükleme formu)
│   └── result.html             # Sonuç sayfası (üretilen içerik)
│
├── static/                     # Statik dosyalar
│   ├── css/
│   │   └── styles.css           # Ana CSS dosyası (Design System)
│   ├── js/
│   └── img/
│
├── docs/                       # Dokümantasyon
│   ├── design-system.md         # UI/UX tasarım sistem rehberi
│   ├── ui-analysis.md           # UI/UX analiz raporu
│   └── ui-qa-checklist.md       # Kalite kontrol listesi
│
└── uploads/                    # Yüklenen dosyalar (geçici)
```

## UI/UX Design System 🎨

StudyBuddy, tutarlı ve erişilebilir bir kullanıcı deneyimi sunmak için kapsamlı bir **Design System** kullanır.

### Temel Özellikler
- **Design Tokens:** CSS değişkenleri ile merkezi renk, spacing, typography yönetimi
- **8px Tabanlı Spacing:** Tutarlı boşluk sistemi
- **WCAG 2.1 AA Uyumlu:** Erişilebilirlik standartlarına uygun kontrast ve focus state'leri
- **Responsive:** 576px ve 768px breakpoint'leri ile mobil uyumlu
- **Floating Label Forms:** Modern form deneyimi, autofill desteği
- **Password Strength Indicator:** Gerçek zamanlı şifre gücü göstergesi
- **Keyboard Navigation:** Tam klavye desteği

### Dokümantasyon
- **`docs/design-system.md`**: Tasarım sistem rehberi, bileşen kullanımı, renk paleti
- **`docs/ui-analysis.md`**: İyileştirme öncesi analiz raporu
- **`docs/ui-qa-checklist.md`**: Kalite kontrol listesi ve test önerileri

### Blueprint Sınıfları
```html
<!-- Butonlar -->
<button class="btn-primary-custom">Kayıt Ol</button>
<button class="btn-outline-custom">İptal</button>
<button class="btn-hero btn-hero-primary">Başla</button>

<!-- Kartlar -->
<div class="card-custom">...</div>
<div class="feature-card">...</div>
<div class="pricing-card pricing-card-premium">...</div>

<!-- Formlar -->
<div class="floating-field">
  <div class="floating-input-wrapper">
    <input type="text" class="floating-input" id="name">
    <label class="floating-label" for="name">İsim</label>
  </div>
</div>
```

### Hover Kontrast Garantisi ✅
Tüm interaktif elementlerde (buton, link, nav item) hover state'lerinde metin okunabilirliği garanti edilmiştir. Gradient arka planlarda hover'da daha koyu tonlar veya arka plan rengi değişimi ile kontrast korunur.

---

## Önemli Notlar

### Dosya Formatları

- **PDF**: Tüm PDF dosyaları desteklenir. Sadece resimlerden oluşan PDF'ler için metin çıkarılamayabilir.
- **DOCX**: Modern Word formatı (.docx) desteklenir.
- **DOC**: Eski Word formatı (.doc) desteklenmemektedir. `.doc` dosyaları yükleme aşamasında reddedilir. Dosyanızı .docx formatına dönüştürün.
- **PPTX**: PowerPoint sunumları desteklenir.
- **TXT**: Düz metin dosyaları (UTF-8, Latin-1, CP1254 encoding'leri)

### Maliyet Yönetimi

- Uygulama OpenAI API kullandığı için her kullanımda token ücreti alınır
- İlk aşamada `gpt-3.5-turbo` modeli kullanılması önerilir (daha ekonomik)
- Uzun dokümanlar otomatik olarak ~12000 token'a kısaltılır
- API kullanımınızı [OpenAI Dashboard](https://platform.openai.com/usage) üzerinden takip edebilirsiniz

### Güvenlik Özellikleri

StudyBuddy aşağıdaki güvenlik özellikleri ile korunmaktadır:

- **Rate Limiting**: Kullanıcı başına saatte 10 dosya yükleme limiti (spam ve kötüye kullanımı önler)
- **CSRF Protection**: Tüm formlarda CSRF token koruması (cross-site request forgery saldırılarına karşı)
- **File Signature Validation**: Dosya içeriğinin uzantısıyla eşleşip eşleşmediğini kontrol eden magic number doğrulaması
- **Session Security**: HttpOnly ve SameSite cookie ayarları ile güvenli oturum yönetimi
- **Password Policy**: Güçlü şifre gereksinimleri (minimum 8 karakter, büyük/küçük harf, rakam)

#### Güvenlik Ayarları

- `.env` dosyasını asla Git'e eklemeyin (zaten .gitignore'da var)
- OpenAI API anahtarınızı kimseyle paylaşmayın
- Production ortamında güçlü bir SECRET_KEY kullanın
- Production'da `SESSION_COOKIE_SECURE=true` yapın (HTTPS gerekli)
- Production'da Redis kullanarak rate limiting'i yapılandırın: `RATELIMIT_STORAGE_URI=redis://localhost:6379`
- `WTF_CSRF_ENABLED=true` olarak tutun (production için zorunlu)

## Demo Modu Kullanımı

### OpenAI API Olmadan Test Etme

Eğer OpenAI API anahtarınız yoksa veya önce uygulamayı test etmek istiyorsanız:

1. `.env` dosyasında `DEMO_MODE=true` olarak ayarlayın
2. Uygulamayı normal şekilde çalıştırın
3. **Sahte/demo veriler gösterilecektir** (gerçek AI üretimi olmaz)
4. Arayüzü, dosya yükleme akışını ve sonuç sayfasını test edebilirsiniz

### Gerçek AI'ya Geçiş

1. [OpenAI Platform](https://platform.openai.com/api-keys) üzerinden API anahtarı alın
2. `.env` dosyasında:
   - `OPENAI_API_KEY=sk-proj-...` (gerçek anahtarınızı yazın)
   - `DEMO_MODE=false` yapın
3. Uygulamayı yeniden başlatın

## Sorun Giderme

### "CSRF token missing" Hatası

- **Çözüm:** Formlar otomatik olarak CSRF token içerir. Eğer bu hata alıyorsanız:
  - Tarayıcı cache'ini temizleyin
  - Sayfayı yenileyin (F5)
  - `.env` dosyasında `WTF_CSRF_ENABLED=true` olduğundan emin olun

### "Rate limit exceeded" Hatası

- **Çözüm:** Kullanıcı başına saatte 10 dosya yükleme limiti vardır. Limit aşıldıysa:
  - Bir saat bekleyin
  - Veya `.env` dosyasında `RATELIMIT_ENABLED=false` yaparak test edebilirsiniz (sadece development için)

### "File validation failed" Hatası

- **Çözüm:** Dosya içeriği uzantısıyla eşleşmiyor. Örneğin:
  - `.pdf` uzantılı bir dosya gerçekte PDF değilse reddedilir
  - Dosyanın doğru formatta olduğundan emin olun
  - `.env` dosyasında `VALIDATE_FILE_SIGNATURES=false` yaparak kontrolü devre dışı bırakabilirsiniz (sadece test için, güvenlik riski)

### "OPENAI_API_KEY ortam değişkeni ayarlanmamış" Hatası

- **Çözüm 1 (Test için):** `.env` dosyasında `DEMO_MODE=true` yapın
- **Çözüm 2 (Gerçek kullanım):** `.env` dosyasını oluşturduğunuzdan ve doğru API anahtarını girdiğinizden emin olun.

### "Dosyadan yeterli metin çıkarılamadı" Hatası

- Dosyanın boş olmadığından emin olun
- PDF dosyası sadece resimlerden oluşuyorsa, OCR (optik karakter tanıma) gerekir
- Dosyanın şifreli veya korumalı olmadığından emin olun

### Modül Bulunamadı Hatası

Sanal ortamın aktif olduğundan ve tüm bağımlılıkların yüklendiğinden emin olun:

```bash
pip install -r requirements.txt
```

### Bağlantı Noktası Kullanımda Hatası

5000 portu başka bir uygulama tarafından kullanılıyorsa, farklı bir port kullanın:

```bash
flask run --port 5001
```

## Kimlik Doğrulama Sistemi

StudyBuddy artık kullanıcı kayıt ve giriş sistemi ile geliyor! Dosya yükleme ve işleme için giriş yapmanız gerekmektedir.

### Kurulum Adımları

1. **Yeni bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **`.env.example` dosyasını `.env` olarak kopyalayın:**
   ```bash
   cp .env.example .env
   ```
   Windows PowerShell:
   ```powershell
   Copy-Item .env.example .env
   ```

3. **`.env` dosyasını düzenleyin:**
   - `SECRET_KEY`: Güçlü random string oluşturun:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - **Email ayarları**: SMTP server bilgilerini girin (şifre sıfırlama için gerekli)
   - Gmail kullanıyorsanız: 2FA aktif edin ve App Password oluşturun
     - Google Account > Security > App Passwords
     - `MAIL_SERVER=smtp.gmail.com`, `MAIL_PORT=587`
     - `MAIL_USERNAME`: Gmail adresiniz
     - `MAIL_PASSWORD`: Oluşturduğunuz App Password

4. **Database migration**: İlk çalıştırmada otomatik oluşacak (User tablosu eklenecek)

5. **Uygulamayı başlatın:**
   ```bash
   python app.py
   ```

### Email Konfigürasyonu

#### Gmail için:
- 2FA aktif edin
- App Password oluşturun: Google Account > Security > App Passwords
- `.env` dosyasında:
  ```
  MAIL_SERVER=smtp.gmail.com
  MAIL_PORT=587
  MAIL_USERNAME=your-email@gmail.com
  MAIL_PASSWORD=your-app-password
  ```

#### SendGrid için:
- API key alın, SMTP credentials kullanın
- `.env` dosyasında SendGrid SMTP bilgilerini girin

#### Mailgun için:
- SMTP credentials alın
- `.env` dosyasında Mailgun SMTP bilgilerini girin

### Özellikler

- ✅ **Kullanıcı kayıt ve giriş**: Email ve şifre ile kayıt olun
- ✅ **Güvenli şifre hash'leme**: Bcrypt ile şifreler güvenli şekilde saklanır
- ✅ **"Beni hatırla" özelliği**: 30 gün boyunca oturum açık kalır
- ✅ **Email bazlı şifre sıfırlama**: Şifrenizi unuttuysanız email ile sıfırlayın
- ✅ **Kullanıcı profil sayfası**: Hesap bilgilerinizi görüntüleyin
- ✅ **Session yönetimi**: Güvenli oturum yönetimi

### Güvenlik

- **Şifre policy**: 
  - Minimum 8 karakter
  - En az bir büyük harf
  - En az bir küçük harf
  - En az bir rakam
- **Session cookie güvenliği**: HttpOnly, SameSite koruması
- **CSRF koruması**: ✅ Tüm formlarda aktif (Flask-WTF)
- **Rate limiting**: ✅ Kullanıcı başına 10 upload/saat (Flask-Limiter)
- **File signature validation**: ✅ Dosya içeriği doğrulaması (Magic Number)

### Kullanım

1. Ana sayfada "Kayıt Ol" butonuna tıklayın
2. Email, kullanıcı adı ve şifre ile kayıt olun
3. Otomatik olarak giriş yapılacak
4. Dosya yükleme için giriş gerekli
5. Şifrenizi unuttuysanız "Şifremi Unuttum" linkini kullanın

### Troubleshooting

- **Email gönderilmiyor**: SMTP ayarlarını kontrol edin, firewall/antivirus kontrol edin
- **Login olmuyor**: Database'i sil ve yeniden oluşturun (`rm studybuddy.db` veya `del studybuddy.db`)
- **Session sorunları**: Browser cache'i temizleyin, cookies'i silin

### Geliştirme Notları

- Production'da `SESSION_COOKIE_SECURE=true` yapın (HTTPS gerekli)
- `SECRET_KEY`'i asla paylaşmayın veya commit etmeyin
- Production'da Redis kullanarak rate limiting'i yapılandırın
- `WTF_CSRF_ENABLED=true` olarak tutun (production için zorunlu)
- Email verification sonraki fazda eklenecek

### API Endpoints

- `GET /`: Ana sayfa (anonim erişim)
- `GET /register`: Kayıt sayfası
- `POST /register`: Kayıt işlemi
- `GET /login`: Giriş sayfası
- `POST /login`: Giriş işlemi
- `GET /logout`: Çıkış işlemi (login required)
- `GET /profile`: Profil sayfası (login required)
- `POST /process`: Dosya işleme (login required)
- `GET /forgot-password`: Şifre sıfırlama talebi
- `POST /forgot-password`: Email gönderimi
- `GET /reset-password/<token>`: Şifre sıfırlama sayfası
- `POST /reset-password/<token>`: Şifre güncelleme

### Database Schema

User tablosu eklendi:
- `id`: Primary key
- `email`: Unique, indexed
- `username`: Unique
- `password_hash`: Bcrypt hash
- `is_active`: Hesap aktif mi
- `is_verified`: Email doğrulandı mı
- `subscription_plan`: Abonelik planı (free/premium)
- `created_at`: Kayıt tarihi
- `last_login`: Son giriş zamanı
- `reset_token`: Şifre sıfırlama token'ı
- `reset_token_expiry`: Token son kullanma tarihi

## 📊 Abonelik Planları ve Limitler

### Planlar

StudyBuddy iki farklı abonelik planı sunar:

#### 🆓 Ücretsiz Plan

- **Aylık Limit:** 5 dosya yükleme
- **Dosya Boyutu:** Maksimum 16 MB
- **Özellikler:**
  - Tüm soru tipleri (çoktan seçmeli, kısa cevap, boş doldurma, doğru-yanlış)
  - Özet ve flashcard üretimi
  - 30 gün geçmiş saklama
  - Cache sistemi (token tasarrufu)

#### ⭐ Premium Plan

- **Aylık Limit:** Sınırsız dosya yükleme
- **Dosya Boyutu:** Maksimum 32 MB
- **Özellikler:**
  - Tüm ücretsiz plan özellikleri
  - Sınırsız dosya yükleme
  - Öncelikli destek
  - Sınırsız geçmiş saklama
  - Gelişmiş export seçenekleri (yakında)

### Kullanım Takibi

Sistem, her kullanıcının aylık kullanımını otomatik olarak takip eder:

- **Aylık Limit:** Her ayın 1'inde otomatik sıfırlanır
- **Cache Hit:** Daha önce işlenmiş dosyalar limite sayılmaz
- **Dashboard:** Kullanım istatistiklerinizi `/dashboard` sayfasından görüntüleyin
- **Profil:** Kalan yükleme hakkınızı profil sayfanızda görebilirsiniz

### Limit Aşımı

Ücretsiz plandaki kullanıcılar aylık 5 dosya limitine ulaştığında:

1. Ana sayfada uyarı mesajı görüntülenir
2. Dosya yükleme butonu devre dışı kalır
3. Premium plana geçiş önerisi sunulur
4. Bir sonraki ayın 1'inde limit otomatik sıfırlanır

### Plan Değiştirme

StudyBuddy artık Stripe ödeme entegrasyonu ile Premium plana geçiş yapabilirsiniz!

## 💳 Payment Integration (Stripe)

StudyBuddy uses Stripe for secure payment processing.

### Setup Stripe

1. **Create Stripe Account**
   - Sign up at https://stripe.com
   - Complete account verification

2. **Get API Keys**
   - Go to Stripe Dashboard > Developers > API Keys
   - Copy Publishable Key (pk_test_...)
   - Copy Secret Key (sk_test_...)
   - Add to `.env` file:
     ```
     STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
     STRIPE_SECRET_KEY=sk_test_your_key_here
     ```

3. **Create Products and Prices**
   - Go to Stripe Dashboard > Products
   - **Standart Plan için:**
     - Create product: "StudyBuddy Standart"
     - Add price: ₺24.99 TRY, recurring monthly
     - Copy Price ID (price_xxxxx) and Product ID (prod_xxxxx)
     - Add to `.env`:
       ```
       STRIPE_STANDARD_PRICE_ID=price_xxxxx
       STRIPE_STANDARD_PRODUCT_ID=prod_xxxxx
       ```
   - **Premium Plan için:**
   - Create product: "StudyBuddy Premium"
   - Add price: ₺49.99 TRY, recurring monthly
     - Copy Price ID (price_xxxxx) and Product ID (prod_xxxxx)
     - Add to `.env`:
     ```
     STRIPE_PREMIUM_PRICE_ID=price_xxxxx
       STRIPE_PREMIUM_PRODUCT_ID=prod_xxxxx
     ```

4. **Set Up Webhook**
   - Go to Stripe Dashboard > Developers > Webhooks
   - Click "Add endpoint"
   - Endpoint URL: `https://yourdomain.com/stripe/webhook`
   - Events to listen:
     - `checkout.session.completed`
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
   - Copy Webhook Secret (whsec_xxxxx)
   - Add to `.env`:
     ```
     STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
     ```

5. **Test with Stripe CLI** (Development)
   - Install Stripe CLI: https://stripe.com/docs/stripe-cli
   - Login: `stripe login`
   - Forward webhooks: `stripe listen --forward-to localhost:5000/stripe/webhook`
   - Use test cards: https://stripe.com/docs/testing

### Testing Payment Flow

1. Register a new user
2. Go to Pricing page
3. Click "Planı Seç" for Premium
4. Use test card: `4242 4242 4242 4242`
5. Complete checkout on Stripe
6. Verify:
   - Redirected to success page
   - Email received with invoice
   - Subscription activated (check profile)
   - Payment recorded in database

### Invoice Generation

Invoices are automatically generated as PDFs using ReportLab and emailed to users after successful payment. PDFs are stored temporarily in `invoices/` directory.

### Database Migration

Run the payment migration to create the Payment table:

```bash
python migrations/add_payment_model.py
```

This migration:
- Creates `payments` table
- Creates `invoices/` directory for PDF storage

### Troubleshooting

- **Webhook not receiving events**: Check Stripe CLI is running or webhook URL is correct
- **Payment not activating subscription**: Check webhook signature verification
- **Invoice not generated**: Check ReportLab installation and `invoices/` directory permissions
- **Email not sent**: Verify SMTP settings in `.env`

## İleride Eklenebilecek Özellikler

- [x] Kullanıcı kayıt ve giriş sistemi
- [x] Abonelik ve ödeme sistemi (temel yapı hazır, ödeme entegrasyonu bekleniyor)
- [ ] Email doğrulama
- [ ] Oluşturulan içerikleri kaydetme ve geçmiş
- [ ] PDF olarak indirme özelliği
- [ ] Yazdırma özelliği
- [ ] Soru sayısını ve zorluk seviyesini ayarlama
- [ ] Çoklu dil desteği
- [ ] DOC formatı desteği
- [ ] OCR desteği (resimlerden metin çıkarma)
- [ ] Mobil uygulama

## 🤝 Katkıda Bulunma

Bu proje açık kaynak bir projedir. Katkılarınızı bekliyoruz!

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/YeniOzellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. Detaylar için LICENSE dosyasına bakın.

## 📧 İletişim

- GitHub: [@tigerfox1974](https://github.com/tigerfox1974)
- Sorularınız veya önerileriniz için [GitHub Issues](https://github.com/tigerfox1974/StudyBuddy/issues) kullanabilirsiniz

## ⭐ Yıldız Vermeyi Unutmayın!

Eğer bu proje işinize yaradıysa, lütfen ⭐ vererek destekleyin!

---

**Not**: Bu uygulama OpenAI API kullanmaktadır. Kullanım ücretleri [OpenAI fiyatlandırma sayfasında](https://openai.com/pricing) belirtilmiştir.

