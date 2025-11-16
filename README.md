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

### 7. Çeviri Kataloglarını Derleyin (İlk Kurulum)

İlk kez projeyi çeken geliştiricilerin çeviri kataloglarını derlemesi gerekir:

```bash
pybabel compile -d translations
```

Bu komut, `.po` dosyalarını `.mo` formatına çevirir ve uygulamanın çevirileri kullanabilmesini sağlar.

### 8. Uygulamayı Çalıştırın

```bash
python app.py
```

veya

```bash
flask run
```

Uygulama varsayılan olarak http://localhost:5000 adresinde çalışacaktır.

## 📊 Veritabanı Migration'ları

### Alembic ile Migration Yönetimi

StudyBuddy, veritabanı şema değişikliklerini yönetmek için **Alembic** kullanır. Alembic, SQLAlchemy tabanlı otomatik migration aracıdır.

#### İlk Kurulum

**⚠️ ÖNEMLİ:** Yeni bir veritabanı kuruyorsanız, `db.create_all()` yerine **mutlaka Alembic migration'larını kullanın**. `db.create_all()` sadece test amaçlı özel bir flag ile çalıştırılır (`USE_DB_CREATE_ALL_FOR_TESTS=true`).

1. **Alembic'i yükleyin** (zaten requirements.txt'de mevcut):

   ```bash
   pip install alembic
   ```

2. **Mevcut migration'ları uygulayın** (ZORUNLU ADIM):

   ```bash
   alembic upgrade head
   ```

   Bu komut, veritabanınızı en son versiyona güncelleyecektir. İlk kurulumda bu adım **mutlaka** çalıştırılmalıdır.

**NOT:** `app.py` içinde `db.create_all()` çağrısı varsayılan olarak devre dışıdır. Veritabanı şeması Alembic migration'ları ile yönetilir. Bu, `db.create_all()` ile Alembic arasındaki çakışma riskini önler.

#### Temel Alembic Komutları

**Migration Durumunu Kontrol Etme:**

```bash
# Mevcut veritabanı versiyonunu görüntüle
alembic current

# Migration geçmişini görüntüle
alembic history --verbose

# Bekleyen migration'ları kontrol et
alembic heads
```

**Migration Uygulama:**

```bash
# Tüm migration'ları uygula (en son versiyona güncelle)
alembic upgrade head

# Belirli bir versiyona güncelle
alembic upgrade <revision_id>

# Bir sonraki migration'ı uygula
alembic upgrade +1

# Migration'ı SQL olarak görüntüle (uygulamadan önce)
alembic upgrade head --sql
```

**Migration Geri Alma:**

```bash
# Bir önceki versiyona geri dön
alembic downgrade -1

# Belirli bir versiyona geri dön
alembic downgrade <revision_id>

# Tüm migration'ları geri al (dikkatli kullanın!)
alembic downgrade base
```

**Yeni Migration Oluşturma:**

```bash
# Manuel migration oluştur
alembic revision -m "aciklama_buraya"

# Otomatik migration oluştur (model değişikliklerini algılar)
alembic revision --autogenerate -m "aciklama_buraya"
```

#### Mevcut Migration'lar

Proje şu migration'ları içerir:

1. **add_user_id_column** - `documents` tablosuna `user_id` kolonu ekler
2. **add_token_system_columns** - `users` tablosuna token sistemi kolonları ekler
3. **add_subscription_models** - `subscriptions` ve `user_usage_stats` tablolarını oluşturur
4. **add_payment_model** - `payments` tablosunu oluşturur

#### Otomatik Migration (Opsiyonel)

Development ortamında, uygulama başlangıcında otomatik migration kontrolü aktif edilebilir:

**.env dosyasına ekleyin:**

```bash
AUTO_MIGRATE_ON_STARTUP=true
```

**⚠️ UYARI:** Production ortamında bu özelliği **ASLA** aktif etmeyin! Production migration'ları manuel olarak uygulanmalıdır.

#### Production Migration Workflow

Production ortamında migration'ları güvenli şekilde uygulamak için:

1. **Veritabanı yedeği alın:**

   ```bash
   cp studybuddy.db studybuddy.db.backup_$(date +%Y%m%d_%H%M%S)
   ```

2. **Migration'ı önce SQL olarak görüntüleyin:**

   ```bash
   alembic upgrade head --sql > migration_preview.sql
   ```

3. **SQL dosyasını inceleyin ve onaylayın**

4. **Migration'ı uygulayın:**

   ```bash
   alembic upgrade head
   ```

5. **Uygulamayı test edin**

6. **Sorun varsa geri alın:**

   ```bash
   alembic downgrade -1
   # Veya yedekten geri yükleyin:
   cp studybuddy.db.backup_YYYYMMDD_HHMMSS studybuddy.db
   ```

#### Docker ile Migration

Docker container içinde migration çalıştırmak için:

```bash
# Container içinde komut çalıştır
docker-compose exec app alembic upgrade head

# Veya container başlatmadan önce
docker-compose run --rm app alembic upgrade head
```

#### Sorun Giderme

**"Can't locate revision identified by 'head'" hatası:**

```bash
# Migration geçmişini sıfırlayın
alembic stamp head
```

**"Target database is not up to date" hatası:**

```bash
# Mevcut durumu kontrol edin
alembic current
alembic history

# Gerekirse manuel stamp yapın
alembic stamp <revision_id>
```

**Migration çakışması:**

```bash
# Çakışan migration'ları birleştirin
alembic merge <rev1> <rev2> -m "merge_aciklamasi"
```

#### Legacy Migration Script'leri

Eski manuel migration script'leri `migrations/legacy/` klasöründe yedek olarak saklanmıştır. Bu script'ler artık kullanılmamaktadır, ancak referans için korunmuştur.

**⚠️ ÖNEMLİ:** Yeni bir veritabanı kuruyorsanız, legacy script'leri çalıştırmayın. Bunun yerine `alembic upgrade head` komutunu kullanın.

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

## 🌍 Çok Dilli Destek (i18n)

StudyBuddy, Flask-Babel kullanarak çok dilli destek sunmaktadır. Uygulama şu anda **Türkçe (tr)** ve **İngilizce (en)** dillerini desteklemektedir.

### Desteklenen Diller

- **Türkçe (tr)**: Varsayılan dil)
- **İngilizce (en)**

### Dil Seçimi

Kullanıcılar navbar'daki dil seçici ile istedikleri dili seçebilir. Dil tercihi session ve cookie'de saklanır, böylece sonraki ziyaretlerde de tercih edilen dil kullanılır.

### Geliştiriciler İçin

#### Yeni Çevrilebilir String Ekleme

Template'lerde çevrilebilir string eklemek için `_()` fonksiyonunu kullanın:

```html
<h1>{{ _('Hoş Geldiniz') }}</h1>
<p>{{ _('StudyBuddy\'ye hoş geldiniz!') }}</p>
```

Python kodunda çevrilebilir string eklemek için `gettext()` fonksiyonunu kullanın:

```python
from flask_babel import gettext

flash(gettext('Kayıt başarılı!'), 'success')
```

#### Çeviri Kataloglarını Güncelleme

1. **Tüm çevrilebilir string'leri extract edin:**
   ```bash
   pybabel extract -F babel.cfg -o messages.pot .
   ```

2. **Mevcut çeviri dosyalarını güncelleyin:**
   ```bash
   pybabel update -i messages.pot -d translations
   ```

3. **Çevirileri derleyin:**
   ```bash
   pybabel compile -d translations
   ```

#### Yeni Dil Ekleme

Örnek olarak Almanca (de) eklemek için:

1. **Yeni dil için çeviri dosyası oluşturun:**
   ```bash
   pybabel init -i messages.pot -d translations -l de
   ```

2. **`config.py` dosyasında `SUPPORTED_LANGUAGES`'e yeni dili ekleyin:**
   ```python
   SUPPORTED_LANGUAGES = {
       'tr': 'Türkçe',
       'en': 'English',
       'de': 'Deutsch'  # Yeni dil
   }
   ```

3. **`translations/de/LC_MESSAGES/messages.po` dosyasını düzenleyerek çevirileri ekleyin**

4. **Çevirileri derleyin:**
   ```bash
   pybabel compile -d translations
   ```

#### İlk Kurulumda Çeviri Kataloglarını Derleme

Projeyi ilk kez çeken geliştiricilerin, çeviri kataloglarını derlemesi gerekir:

```bash
pybabel compile -d translations
```

Bu komut, `.po` dosyalarını `.mo` formatına çevirir ve uygulamanın çevirileri kullanabilmesini sağlar.

### Babel Komutları Referansı

- `pybabel extract -F babel.cfg -o messages.pot .`: Tüm çevrilebilir string'leri extract eder
- `pybabel init -i messages.pot -d translations -l <lang>`: Yeni dil için çeviri dosyası oluşturur
- `pybabel update -i messages.pot -d translations`: Mevcut çeviri dosyalarını günceller
- `pybabel compile -d translations`: Çevirileri derler (`.po` → `.mo`)

## İleride Eklenebilecek Özellikler

- [x] Kullanıcı kayıt ve giriş sistemi
- [x] Abonelik ve ödeme sistemi (temel yapı hazır, ödeme entegrasyonu bekleniyor)
- [x] Çoklu dil desteği
- [ ] Email doğrulama
- [ ] Oluşturulan içerikleri kaydetme ve geçmiş
- [ ] PDF olarak indirme özelliği
- [ ] Yazdırma özelliği
- [ ] Soru sayısını ve zorluk seviyesini ayarlama
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

## Testing

### Test Suite Kurulumu

1. Test bağımlılıklarını yükleyin:

```bash
pip install -r requirements.txt
```

2. Test veritabanını oluşturun (otomatik olarak in-memory SQLite kullanılır)

### Testleri Çalıştırma

**Tüm testleri çalıştır:**

```bash
pytest
```

**Verbose mode ile çalıştır:**

```bash
pytest -v
```

**Belirli bir test dosyasını çalıştır:**

```bash
pytest tests/test_document_reader.py
```

**Belirli bir test fonksiyonunu çalıştır:**

```bash
pytest tests/test_document_reader.py::test_extract_text_from_pdf
```

**Coverage raporu ile çalıştır:**

```bash
pytest --cov=. --cov-report=html
```

HTML raporu `htmlcov/index.html` dosyasında oluşur.

**Sadece unit testleri çalıştır:**

```bash
pytest -m unit
```

**Sadece integration testleri çalıştır:**

```bash
pytest -m integration
```

### Test Yapısı

- `tests/test_document_reader.py`: Dosya okuma testleri
- `tests/test_ai_generator.py`: AI içerik üretimi testleri
- `tests/test_routes.py`: Flask route testleri
- `tests/test_utils.py`: Utility fonksiyon testleri
- `tests/conftest.py`: Merkezi fixture'lar
- `tests/data/`: Test dosyaları (PDF, DOCX, PPTX, TXT)

### Test Konfigürasyonu

Testler otomatik olarak:

- In-memory SQLite database kullanır
- Demo mode'da çalışır (OpenAI API gerektirmez)
- CSRF ve rate limiting'i devre dışı bırakır
- Mock'lanmış email ve payment servisleri kullanır

## 🚀 Deployment (Production)

### Docker ile Deployment

StudyBuddy'yi production ortamında çalıştırmak için Docker ve Docker Compose kullanılır.

**Gereksinimler:**
- Docker 20.10+ 
- Docker Compose 2.0+ (veya Docker Desktop ile birlikte gelen Docker Compose V2)

**Docker Kurulumu:**
- Windows için: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) indirip kurun
- Docker Desktop kurulduktan sonra PowerShell'de `docker --version` ve `docker compose version` komutları ile kontrol edin

**Hızlı Başlangıç:**

1. `.env.production.example` dosyasını `.env` olarak kopyalayın:
   ```bash
   cp .env.production.example .env
   ```

2. `.env` dosyasını düzenleyin ve gerekli değerleri doldurun:
   - `SECRET_KEY`: Güçlü random string oluşturun: `python -c "import secrets; print(secrets.token_hex(32))"`
   - `OPENAI_API_KEY`: Production API key
   - `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`: Production keys
   - `MAIL_USERNAME`, `MAIL_PASSWORD`: SMTP ayarları
   - Diğer zorunlu değişkenler

3. Docker Compose ile servisleri başlatın:
   ```bash
   docker compose up -d
   ```
   **Not:** Docker Compose V2 kullanılıyorsa `docker compose` (tire olmadan) komutunu kullanın. Eski versiyon için `docker-compose` kullanılabilir.

4. Logları izleyin:
   ```bash
   docker compose logs -f app
   ```

5. Servisleri durdurmak için:
   ```bash
   docker compose down
   ```

### Environment Variables (Production)

Production deployment için kritik environment variables:

**Zorunlu Değişkenler:**
- `SECRET_KEY`: Güçlü random string (32+ karakter)
- `SESSION_COOKIE_SECURE=true`: HTTPS zorunlu
- `OPENAI_API_KEY`: Production API key
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`: Production keys
- `MAIL_USERNAME`, `MAIL_PASSWORD`: SMTP credentials
- `RATELIMIT_STORAGE_URI=redis://redis:6379`: Redis kullanımı önerilir

**Önemli Notlar:**
- `.env.production.example` dosyasını referans olarak kullanın
- `.env` dosyasını ASLA commit etmeyin (secrets içerir)
- Tüm production keys kullanılmalı (test keys değil)

### Redis Setup (Optional but Recommended)

Redis, rate limiting için önerilir. Memory-based rate limiting tek container için yeterli ama restart'ta sıfırlanır.

**Redis Kurulumu:**

1. Redis servisini devreye almak için `--profile redis` kullanın:
   ```bash
   docker compose --profile redis up -d
   ```
2. `.env` dosyasında `RATELIMIT_STORAGE_URI=redis://redis:6379` ayarlayın
3. Redis kullanılmadığında uygulama `RATELIMIT_STORAGE_URI=memory://` ile çalışabilir (tek container için yeterli, restart'ta sıfırlanır)
4. Redis health check:
   ```bash
   docker compose exec redis redis-cli ping
   ```
   `PONG` dönmeli

**Not:** Redis servisi varsayılan olarak başlatılmaz. Sadece `--profile redis` ile başlatıldığında çalışır ve sadece internal network üzerinden erişilebilir (port mapping yoktur).

### Database Migration (Production)

**SQLite vs PostgreSQL:**
- SQLite: Başlangıç için yeterli, düşük trafik için uygun
- PostgreSQL: Yüksek trafik ve production için önerilir

**Migration Komutları:**

Container içinde migration script'lerini çalıştırın:

```bash
# Subscription models
docker compose exec app python migrations/add_subscription_models.py

# Payment model
docker compose exec app python migrations/add_payment_model.py

# Token system columns
docker compose exec app python migrations/add_token_system_columns.py -y

# User ID column
docker compose exec app python migrations/add_user_id_column.py
```

**PostgreSQL Kullanımı (Optional):**

1. `docker-compose.yml`'ye postgres service ekleyin
2. `.env` dosyasında `DATABASE_URL=postgresql://user:password@postgres:5432/studybuddy` ayarlayın

### SSL/TLS Setup (HTTPS)

Production'da HTTPS zorunludur (`SESSION_COOKIE_SECURE=true`).

**Reverse Proxy Önerilir:**
- Nginx veya Caddy kullanılabilir
- Let's Encrypt ile ücretsiz SSL sertifikası

**Nginx Örnek Konfigürasyonu (Basic):**

```nginx
upstream studybuddy {
    server localhost:5000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://studybuddy;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for SocketIO
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Health Checks and Monitoring

**Docker Health Check:**
```bash
docker compose ps
```
Container health status görüntülenir.

**Application Health:**
- `GET /` endpoint'i 200 OK dönmeli
- Health check (container içinde curl mevcut):
  ```bash
  docker compose exec app curl -f http://localhost:5000/
  ```

**Logs:**
```bash
# Real-time logs
docker compose logs -f app

# Last 100 lines
docker compose logs --tail=100 app
```

Gunicorn logs stdout/stderr'a yazılır, Docker logs ile görüntülenir.

## Güvenlik İyileştirmeleri (Yeni)

- SECRET_KEY production doğrulaması eklendi (fallback kabul edilmez).
- Open redirect koruması güçlendirildi (`is_safe_url`).
- Token düşümü ve cache yazımı tek transaction mantığına yakınlaştırıldı; hata durumunda rollback.
- Webhook logging iyileştirildi; hatalar detaylı loglanır, idempotent tekrarlar sessizce atlanır.
- Merkezi logging altyapısı eklendi (`logging_config.py`).

Production kontrol listesi:

- [ ] FLASK_ENV=production ve FLASK_DEBUG=false
- [ ] Güçlü ve unique SECRET_KEY
- [ ] Stripe production anahtarları ve doğru Price ID'ler
- [ ] AUTO_MIGRATE_ON_STARTUP=false
- [ ] LOG_LEVEL=INFO veya WARNING

## Logging Konfigürasyonu

Uygulama Python `logging` ile log yazar. Varsayılan olarak console handler aktiftir. İsteğe bağlı olarak dönen dosya log'u açabilirsiniz:

- LOG_LEVEL: DEBUG/INFO/WARNING/ERROR/CRITICAL (default: INFO)
- LOG_FILE: logs/studybuddy.log (varsa dosyaya yazar)
- LOG_MAX_BYTES: rotation için maksimum boyut (default: 10MB)
- LOG_BACKUP_COUNT: yedek dosya sayısı (default: 5)

Docker'da log görüntüleme:

```bash
docker logs studybuddy
docker logs -f studybuddy
```

## Sorun Giderme (Yeni)

- "SECRET_KEY must be set in production": `.env` dosyanızda güçlü bir SECRET_KEY ayarlayın.
- "Invalid Stripe Price ID": Stripe dashboard'dan gerçek Price ID'yi kopyalayın (format: `price_...`).
- "Token deduction failed": `logs/` klasöründeki uygulama loglarını kontrol edin.
- "Webhook signature verification failed": `STRIPE_WEBHOOK_SECRET` doğru mu kontrol edin; saat senkronizasyonuna dikkat edin.

## Migration Notları

Webhook idempotency için ek kolonlar önerildi ancak mevcut sürümde opsiyonel tutuldu. İleride ihtiyaç halinde Alembic ile migration oluşturabilirsiniz:

```bash
alembic revision --autogenerate -m "Add webhook idempotency fields"
alembic upgrade head
```

### Backup and Persistence

**Volumes (Persistent Data):**
- `./uploads`: Kullanıcı dosyaları
- `./exports`: Export dosyaları
- `./invoices`: Fatura PDF'leri
- `./studybuddy.db`: SQLite database
- `redis-data`: Redis data (named volume)

**Backup Stratejisi:**

1. **Database Backup:**
   ```bash
   docker compose exec app sqlite3 studybuddy.db .dump > backup.sql
   ```

2. **Volume Backup:**
   ```bash
   # Uploads
   docker cp studybuddy-app:/app/uploads ./backups/uploads-$(date +%Y%m%d)
   
   # Exports
   docker cp studybuddy-app:/app/exports ./backups/exports-$(date +%Y%m%d)
   ```

3. **Otomatik Backup:**
   - Cron job veya backup service kullanılabilir
   - Günlük/haftalık backup stratejisi önerilir

### Scaling and Performance

**Gunicorn Workers:**
- `GUNICORN_WORKERS` environment variable ile ayarlanır
- Default: `cpu_count * 2 + 1`
- Worker class: `gevent` (SocketIO için zorunlu, async)

**Horizontal Scaling:**
- Load balancer + multiple containers
- Sticky sessions gerekli (SocketIO için)
- Database: PostgreSQL + connection pooling önerilir

**Cache:**
- Redis + application-level caching
- Rate limiting için Redis kullanımı önerilir

### Troubleshooting (Production)

**Container Başlamıyor:**
- Logs kontrol edin: `docker compose logs app`
- Environment variables eksik mi: `.env` dosyasını kontrol edin
- Port conflict: 5000 portu kullanımda mı kontrol edin

**SocketIO Çalışmıyor:**
- Gunicorn worker class: `gevent` olmalı (`gunicorn.conf.py` kontrol edin)
- Reverse proxy: WebSocket headers doğru mu (Nginx config)

**Redis Bağlantı Hatası:**
- Redis container çalışıyor mu: `docker compose ps redis`
- `.env` dosyasında `RATELIMIT_STORAGE_URI=redis://redis:6379` doğru mu

**Database Migration Hatası:**
- Migration script'leri sırayla çalıştırıldı mı
- Database file permissions: container user'ın yazma yetkisi var mı

**Stripe Webhook Çalışmıyor:**
- Webhook URL doğru mu: `https://yourdomain.com/stripe/webhook`
- Webhook secret doğru mu: `.env` dosyasında `STRIPE_WEBHOOK_SECRET`
- Stripe Dashboard'da webhook events aktif mi

### Security Checklist (Production)

Production deployment öncesi kontrol listesi:

- ✅ `SECRET_KEY`: Güçlü, unique, 32+ karakter
- ✅ `SESSION_COOKIE_SECURE=true`: HTTPS zorunlu
- ✅ `WTF_CSRF_ENABLED=true`: CSRF protection aktif
- ✅ `RATELIMIT_ENABLED=true`: Rate limiting aktif
- ✅ `VALIDATE_FILE_SIGNATURES=true`: File validation aktif
- ✅ `.env` dosyası `.gitignore`'da: Secrets commit edilmemeli
- ✅ Stripe production keys: Test keys kullanılmamalı
- ✅ HTTPS: SSL/TLS sertifikası aktif
- ✅ Firewall: Sadece 80/443 portları açık (5000 portu external'e kapalı)
- ✅ Database backups: Otomatik backup stratejisi

### Quick Commands Reference

**Build ve Start:**
```bash
# Build image
docker compose build

# Start services
docker compose up -d

# Start with rebuild
docker compose up -d --build
```

**Management:**
```bash
# Stop services
docker compose down

# View logs
docker compose logs -f app

# Restart app
docker compose restart app

# Execute command in container
docker compose exec app <command>

# Shell access
docker compose exec app bash
```

**Database:**
```bash
# Migration
docker compose exec app python migrations/<script>.py

# SQLite shell
docker compose exec app sqlite3 studybuddy.db
```

**Cleanup:**
```bash
# Remove containers and volumes (DİKKAT: Tüm data silinir)
docker compose down -v

# Remove images
docker compose down --rmi all
```

### Health Check Endpoint

**Mevcut Durum:**
- Health check şu an `/` endpoint'ini kullanıyor
- Public erişim, authentication gerektirmiyor
- Rate limiting'e tabi olabilir

**Önerilen İyileştirme (Optional):**

Dedicated `/health` veya `/healthz` endpoint'i oluşturulabilir:
- Authentication gerektirmez
- Rate limiting'den muaf
- Minimal response (örn: `{"status": "healthy"}`)
- Database bağlantısı kontrolü (optional)
- Redis bağlantısı kontrolü (optional)

**Örnek Implementation:**
```python
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}), 200
```

**Docker Health Check Güncelleme:**
- Dockerfile: `CMD curl -f http://localhost:5000/health || exit 1`
- docker-compose.yml: `test: ["CMD", "curl", "-f", "http://localhost:5000/health"]`

## Logging Konfigürasyonu (Genişletilmiş)

Uygulama Python `logging` modülü ile merkezi log yönetimi kullanır (`logging_config.py`).

**Environment Variables:**

| Değişken | Açıklama | Default | Production Önerisi |
|----------|----------|---------|--------------------|
| LOG_LEVEL | Log seviyesi | INFO | INFO veya WARNING |
| LOG_FILE | Log dosya yolu | None (sadece console) | /app/logs/studybuddy.log |
| LOG_MAX_BYTES | Rotation max boyut | 10MB | 10MB - 50MB |
| LOG_BACKUP_COUNT | Yedek dosya sayısı | 5 | 5 - 10 |
| LOG_ERROR_FILE | Sadece error logları | None | /app/logs/errors.log |

**Production Logging Stratejisi:**

1. **Console Logging (Zorunlu):**
   - Gunicorn stdout/stderr'a yazar
   - Docker logs ile erişilir: `docker compose logs -f app`
   - Container orchestration (Kubernetes) ile entegre

2. **File Logging (Optional):**
   - Persistent volume mount: `./logs:/app/logs`
   - Rotation ile disk dolmasını engelle
   - Log aggregation için kullanılabilir

3. **Log Levels:**
   - DEBUG: Development only (çok verbose)
   - INFO: Production default (önemli olaylar)
   - WARNING: Production minimal (sadece uyarılar ve hatalar)
   - ERROR: Sadece hatalar (önerilmez, WARNING kullanın)

**Docker'da Log Görüntüleme:**
```bash
# Real-time logs
docker compose logs -f app

# Son 100 satır
docker compose logs --tail=100 app

# Belirli zaman aralığı
docker compose logs --since 1h app

# Sadece error logları (grep ile)
docker compose logs app | grep ERROR
```

**Log Rotation ve Cleanup:**
```bash
# Manuel cleanup (disk doluysa)
docker compose exec app find /app/logs -name "*.log.*" -mtime +30 -delete

# Otomatik cleanup için cron job (host'ta)
0 2 * * * find /path/to/logs -name "*.log.*" -mtime +30 -delete
```

## PostgreSQL'e Geçiş Adımları (Detaylı)

1. **PostgreSQL Service'i Aktif Et:**
   ```bash
   # docker-compose.yml'de postgres service yorumunu kaldır
   docker compose --profile postgres up -d
   ```

2. **Environment Variables Ayarla:**
   ```bash
   # .env dosyasında:
   DATABASE_URL=postgresql://studybuddy:your_password@postgres:5432/studybuddy
   POSTGRES_PASSWORD=your_strong_password
   ```

3. **SQLite'dan PostgreSQL'e Veri Taşıma (Optional):**
   ```bash
   # SQLite dump al
   docker compose exec app sqlite3 instance/studybuddy.db .dump > sqlite_dump.sql
   
   # PostgreSQL'e import et (manuel düzenleme gerekebilir)
   # SQLite ve PostgreSQL syntax farklılıkları için:
   # - AUTOINCREMENT → SERIAL
   # - DATETIME → TIMESTAMP
   # - Boolean değerler
   ```

4. **Migration'ları Çalıştır:**
   ```bash
   docker compose exec app alembic upgrade head
   ```

5. **Test Et:**
   ```bash
   # Uygulama loglarını kontrol et
   docker compose logs -f app
   
   # PostgreSQL bağlantısını test et
   docker compose exec postgres psql -U studybuddy -d studybuddy -c "\dt"
   ```

## Environment Variables (Güncellenmiş)

**Logging Değişkenleri:**
- `LOG_LEVEL=INFO`: Production log seviyesi
- `LOG_FILE=/app/logs/studybuddy.log`: Optional file logging
- `LOG_MAX_BYTES=10485760`: Log rotation boyutu (10MB)
- `LOG_BACKUP_COUNT=5`: Yedek log dosya sayısı

**Gunicorn Değişkenleri:**
- `GUNICORN_WORKERS=4`: Worker sayısı (CPU'ya göre ayarla)
- `GUNICORN_BIND=0.0.0.0:5000`: Bind address
- `GUNICORN_TIMEOUT=120`: Worker timeout (AI işlemleri için)
- `GUNICORN_LOG_LEVEL=info`: Gunicorn log seviyesi

## 🚀 Quick Commands (Production)

### Docker Management
```bash
# Build ve başlat
docker compose up -d --build

# Sadece başlat (build olmadan)
docker compose up -d

# Durdur
docker compose down

# Durdur ve volume'ları sil (DİKKAT: Veri kaybı!)
docker compose down -v

# Restart
docker compose restart app

# Logs
docker compose logs -f app
docker compose logs --tail=100 app

# Container shell
docker compose exec app /bin/bash

# Health check
docker compose ps
curl http://localhost:5000/
```

### Database Management
```bash
# Alembic migration
docker compose exec app alembic upgrade head
docker compose exec app alembic current
docker compose exec app alembic history

# SQLite shell
docker compose exec app sqlite3 instance/studybuddy.db

# PostgreSQL shell
docker compose exec postgres psql -U studybuddy -d studybuddy

# Database backup
docker compose exec app sqlite3 instance/studybuddy.db .dump > backup_$(date +%Y%m%d).sql
```

### Cleanup
```bash
# Container'ları temizle
docker compose down
docker system prune -f

# Volume'ları temizle (DİKKAT: Veri kaybı!)
docker volume prune -f

# Image'ları temizle
docker image prune -a -f

# Tümünü temizle (DİKKAT: Tüm Docker kaynakları silinir!)
docker system prune -a --volumes -f
```

## Production Checklist (Genişletildi)

- [ ] FLASK_ENV=production ve FLASK_DEBUG=false
- [ ] Güçlü ve unique SECRET_KEY (32+ karakter)
- [ ] Stripe production anahtarları ve doğru Price ID'ler
- [ ] AUTO_MIGRATE_ON_STARTUP=false
- [ ] LOG_LEVEL=INFO veya WARNING (DEBUG değil)
- [ ] SESSION_COOKIE_SECURE=true (HTTPS zorunlu)
- [ ] VALIDATE_FILE_SIGNATURES=true
- [ ] WTF_CSRF_ENABLED=true
- [ ] RATELIMIT_ENABLED=true (production'da aktif olmalı)
- [ ] Rate limiting backend: Redis kullan (RATELIMIT_STORAGE_URI=redis://redis:6379)
- [ ] Veritabanı ve volume yedekleme stratejisi belirlendi ve belgelendi
- [ ] Monitoring ve alerting kuruldu (container health, Gunicorn, app logs)
- [ ] Daha yüksek trafik için PostgreSQL’e geçiş değerlendirildi (DATABASE_URL=postgresql://...)

