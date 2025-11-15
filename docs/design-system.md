# StudyBuddy Design System

## Genel Bakış
Bu doküman, StudyBuddy uygulamasının görsel tasarım sistemini tanımlar. Tüm UI bileşenleri bu sistemi temel almalıdır.

## Design Tokens (CSS Değişkenleri)

### Renk Paleti
```css
--color-primary: #667eea          /* Ana marka rengi */
--color-primary-dark: #764ba2     /* Koyu varyant */
--color-primary-light: #8a9fff    /* Açık varyant */
--color-primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
```

### Text Renkleri
```css
--color-text-primary: #333333     /* Ana metin */
--color-text-secondary: #666666   /* İkincil metin */
--color-text-muted: #999999       /* Soluk metin */
--color-text-inverse: #ffffff     /* Ters renk (gradient üzerinde) */
```

### Background Renkleri
```css
--color-bg-primary: #ffffff       /* Ana arka plan */
--color-bg-secondary: #f8f9ff     /* İkincil arka plan */
--color-bg-tertiary: #f0f2ff      /* Üçüncül arka plan */
--color-bg-muted: #f8f9fa         /* Nötr arka plan */
```

### Status Renkleri
```css
--color-success: #28a745          /* Başarı */
--color-warning: #ffc107          /* Uyarı */
--color-danger: #dc3545           /* Hata */
--color-info: #17a2b8             /* Bilgi */
```

## Spacing Sistemi (8px Tabanlı)
```css
--spacing-xs: 0.5rem    /* 8px  - İkon boşlukları */
--spacing-sm: 1rem      /* 16px - Küçük padding */
--spacing-md: 1.5rem    /* 24px - Orta padding */
--spacing-lg: 2rem      /* 32px - Büyük padding */
--spacing-xl: 2.5rem    /* 40px - Çok büyük padding */
--spacing-2xl: 3rem     /* 48px - Bölüm içi boşluk */
--spacing-3xl: 4rem     /* 64px - Bölümler arası boşluk */
--spacing-4xl: 5rem     /* 80px - Sayfa bölümleri */
```

## Typography

### Font Sizes
```css
--font-size-xs: 0.75rem     /* 12px - Küçük notlar */
--font-size-sm: 0.875rem    /* 14px - Yardımcı metin */
--font-size-base: 1rem      /* 16px - Ana metin */
--font-size-md: 1.125rem    /* 18px - Vurgu metni */
--font-size-lg: 1.25rem     /* 20px - Küçük başlık */
--font-size-xl: 1.5rem      /* 24px - Alt başlık */
--font-size-2xl: 2rem       /* 32px - Sayfa başlığı */
--font-size-3xl: 2.5rem     /* 40px - Hero başlık */
--font-size-4xl: 3rem       /* 48px - Ana hero başlık */
```

### Font Weights
```css
--font-weight-normal: 400       /* Normal metin */
--font-weight-medium: 500       /* Orta vurgu */
--font-weight-semibold: 600     /* Güçlü vurgu */
--font-weight-bold: 700         /* Başlıklar */
```

### Line Heights
```css
--line-height-tight: 1.25       /* Başlıklar */
--line-height-normal: 1.5       /* Normal metin */
--line-height-relaxed: 1.75     /* Uzun paragraflar */
```

## Border Radius
```css
--radius-sm: 0.375rem    /* 6px  - Küçük elementler */
--radius-md: 0.5rem      /* 8px  - Input alanları */
--radius-lg: 0.75rem     /* 12px - Kartlar */
--radius-xl: 1rem        /* 16px - Büyük kartlar */
--radius-2xl: 1.25rem    /* 20px - Hero kartlar */
--radius-full: 9999px    /* Tam yuvarlak (butonlar) */
```

## Shadows
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)            /* Hafif gölge */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)          /* Orta gölge */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)        /* Büyük gölge */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1)        /* Çok büyük gölge */
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25)     /* Dramatik gölge */
```

## Transitions
```css
--transition-fast: 150ms ease       /* Hızlı animasyon */
--transition-base: 250ms ease       /* Standart animasyon */
--transition-slow: 350ms ease       /* Yavaş animasyon */
```

## Bileşen Kullanımı

### Butonlar

#### Primary Button
```html
<button class="btn-primary-custom">Kayıt Ol</button>
```
- Ana CTA aksiyonları için
- Gradient background
- Hover'da koyu gradient + gölge artışı
- White text (kontrast korunur)

#### Outline Button
```html
<button class="btn-outline-custom">İptal</button>
```
- İkincil aksiyonlar için
- White background + primary border
- Hover'da açık mavi background

#### Hero Button (Landing Page)
```html
<button class="btn-hero btn-hero-primary">Başla</button>
<button class="btn-hero btn-hero-outline">Keşfet</button>
```
- Landing page CTA'ları için
- Daha büyük padding ve font
- Gradient arka plan üzerinde okunabilirlik garantili

### Kartlar

#### Standard Card
```html
<div class="card-custom">
  <div class="card-custom-header">
    <h3 class="card-custom-title">Başlık</h3>
  </div>
  <p>İçerik...</p>
</div>
```

#### Feature Card (Landing)
```html
<div class="feature-card">
  <i class="bi bi-book"></i>
  <h4>Özellik Adı</h4>
  <p>Açıklama...</p>
</div>
```

### Responsive Breakpoints
```css
/* Mobile First Yaklaşımı */
/* Mobil: < 576px (varsayılan) */
@media (max-width: 576px)  { /* Küçük mobil */ }
@media (max-width: 768px)  { /* Tablet */ }
@media (max-width: 992px)  { /* Küçük desktop */ }
@media (max-width: 1200px) { /* Orta desktop */ }
```

## Erişilebilirlik Kuralları

### Kontrast
- Text: En az WCAG AA (4.5:1)
- Büyük text (18px+): En az 3:1
- Hover/focus state'lerinde kontrast korunmalı

### Focus States
- Tüm interaktif elementler `:focus-visible` ile belirginleştirilmeli
- Outline: 3px solid, 2px offset
- Renk: `--color-primary-light` veya beyaz (gradient üzerinde)

### Klavye Navigasyonu
- Tab order mantıklı olmalı
- Skip links gerektiğinde kullanılmalı
- Modal/dropdown'larda focus trap uygulanmalı

## Kullanım Örnekleri

### Sayfa Layout
```html
<section class="page-gradient-bg">
  <div class="container">
    <div class="content-wrapper">
      <!-- İçerik -->
    </div>
  </div>
</section>
```

### Form Alanları
Floating label sistemi kullanılmalı:
```html
<div class="floating-field">
  <div class="floating-input-wrapper">
    <input type="text" class="floating-input" id="name">
    <label class="floating-label" for="name">Ad Soyad</label>
  </div>
  <small class="input-feedback" role="alert"></small>
</div>
```

## İnline CSS Kullanımından Kaçının
❌ **Kullanmayın:**
```html
<div style="padding: 20px; background: white;">...</div>
```

✅ **Kullanın:**
```html
<div class="card-custom">...</div>
```

## Güncellemeler
Bu sistem sürekli geliştirilecektir. Yeni bileşenler eklendiğinde bu dokümana eklenmelidir.

**Son Güncelleme:** 2024

