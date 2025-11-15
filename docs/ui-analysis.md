# StudyBuddy UI/UX Analiz Raporu

## Tespit Edilen Uyumsuzluklar

### 1. Inline CSS Kullanımı
**Etkilenen Dosyalar:** 11 template (pricing, index, history, dashboard, profile, result, upload, forgot_password, reset_password, success, checkout)

**Sorun:**
- Her sayfa kendi inline `<style>` bloğunda ortak stilleri tekrar tanımlıyor
- Gradient backgrounds, padding değerleri, buton stilleri her sayfada farklı
- Bakım zorluğu ve tutarsızlık riski

**Hedef:** Tüm inline CSS'i `static/css/styles.css` içindeki blueprint sınıflara taşımak

### 2. Buton Stilleri Tutarsızlığı
**Mevcut Durumlar:**
- `.btn-hero`, `.btn-hero-primary`, `.btn-hero-outline` (index.html)
- `.btn-primary-custom`, `.btn-outline-custom` (styles.css)
- Inline buton stilleri (çeşitli sayfalar)
- Bootstrap `.btn-primary` karışımı

**Sorun:**
- Aynı işlevi gören butonlar farklı sınıflar kullanıyor
- Hover renk geçişlerinde kontrast kaybı (kullanıcı geri bildirimi)
- Padding, border-radius, font-size tutarsız

**Hedef:** Tek bir buton hiyerarşisi (primary, secondary, tertiary, danger)

### 3. Kart Bileşenleri Dağınık
**Mevcut Durumlar:**
- `.feature-card` (landing)
- `.pricing-card` (pricing)
- `.question-card` (result)
- `.card-custom` (genel)
- Inline kart stilleri

**Sorun:**
- Her kart türü farklı padding, shadow, border-radius kullanıyor
- Responsive davranış tutarsız
- Gradient arka planlarda okunabilirlik sorunları

**Hedef:** `.card-tier-1`, `.card-tier-2`, `.card-tier-3` gibi hiyerarşik sistem

### 4. Spacing Sistemi Yok
**Mevcut Durumlar:**
- padding: 80px, 60px, 40px, 20px (rasgele)
- margin: 60px, 40px, 20px (rasgele)
- gap: 20px, 30px (rasgele)

**Sorun:**
- Görsel ritim tutarsız
- Mobilde ölçekleme sorunları

**Hedef:** 8px tabanlı spacing sistemi (8, 16, 24, 32, 40, 48, 64, 80)

### 5. Renk Paleti Dağınık
**Mevcut Ana Renkler:**
- Primary: #667eea, #764ba2 (gradient)
- Text: #333 (bazı yerlerde #000, #222)
- Borders: #e0e0e0, #cfd4ff, #8d8d8d (tutarsız)
- Backgrounds: #f8f9ff, #f8f9fa, white

**Sorun:**
- Border ve text renkleri sayfalara göre değişiyor
- Gri tonları standartlaşmamış

**Hedef:** CSS değişkenleri ile standart palet

### 6. Hover/Focus State Sorunları
**Tespit Edilen:**
- Bazı butonlarda hover'da renk değişimi yazıyı okunamaz yapıyor
- Focus outline'ları tutarsız veya yok
- Gradient arka planlarda link hover'ları kontrast kaybediyor

**Hedef:** WCAG AA uyumlu hover/focus state'leri

### 7. Responsive Breakpoint Yok
**Sorun:**
- Mobil padding/spacing inline media query'lerle (dağınık)
- Stack order tanımsız
- Font-size'lar responsive değil

**Hedef:** Standart breakpoint sistemi (576px, 768px, 992px, 1200px)

### 8. Form Tutarsızlığı
**Mevcut:**
- Auth formlar (login/register) yeni floating label sistemine geçti
- Upload formu eski stil
- Diğer formlar (forgot/reset) karışık

**Hedef:** Tüm formları floating label blueprint'ine taşımak

### 9. Typography Dağınık
**Font Sizes:**
- h1: 3.5rem, 2.5rem, 2rem (sayfalara göre)
- Paragraflar: 1.3rem, 1.2rem, 1rem
- Small text: 0.9rem, 0.875rem

**Hedef:** Tutarlı tipografi skalası

### 10. Erişilebilirlik Eksikleri
**Tespit Edilen:**
- Bazı interaktif öğelerde aria-label yok
- Keyboard navigation testi yapılmamış
- Renk körlüğü için alternatif göstergeler eksik

**Hedef:** WCAG 2.1 AA uyumluluk

## Önerilen Öncelik Sırası
1. Design token sistemi (renk, spacing, typography)
2. Buton ve kart blueprint'leri
3. Inline CSS temizliği
4. Form sistemini genişletme
5. Hover/focus kontrast düzeltmeleri
6. Responsive sistem
7. Erişilebilirlik testleri

