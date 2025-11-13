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

## Kullanım

1. Tarayıcınızda http://localhost:5000 adresine gidin
2. "Dosyanızı Yükleyin" alanına tıklayın ve ders notlarınızı içeren bir dosya seçin
   - Desteklenen formatlar: PDF, DOCX, PPTX, TXT
   - Maksimum dosya boyutu: 16 MB
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
│   └── js/
│
└── uploads/                    # Yüklenen dosyalar (geçici)
```

## Önemli Notlar

### Dosya Formatları

- **PDF**: Tüm PDF dosyaları desteklenir. Sadece resimlerden oluşan PDF'ler için metin çıkarılamayabilir.
- **DOCX**: Modern Word formatı (.docx) desteklenir.
- **DOC**: Eski Word formatı (.doc) şu anda desteklenmemektedir. Dosyanızı .docx formatına dönüştürün.
- **PPTX**: PowerPoint sunumları desteklenir.
- **TXT**: Düz metin dosyaları (UTF-8, Latin-1, CP1254 encoding'leri)

### Maliyet Yönetimi

- Uygulama OpenAI API kullandığı için her kullanımda token ücreti alınır
- İlk aşamada `gpt-3.5-turbo` modeli kullanılması önerilir (daha ekonomik)
- Uzun dokümanlar otomatik olarak ~12000 token'a kısaltılır
- API kullanımınızı [OpenAI Dashboard](https://platform.openai.com/usage) üzerinden takip edebilirsiniz

### Güvenlik

- `.env` dosyasını asla Git'e eklemeyin (zaten .gitignore'da var)
- OpenAI API anahtarınızı kimseyle paylaşmayın
- Production ortamında güçlü bir SECRET_KEY kullanın

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

## İleride Eklenebilecek Özellikler

- [ ] Kullanıcı kayıt ve giriş sistemi
- [ ] Oluşturulan içerikleri kaydetme ve geçmiş
- [ ] PDF olarak indirme özelliği
- [ ] Yazdırma özelliği
- [ ] Soru sayısını ve zorluk seviyesini ayarlama
- [ ] Çoklu dil desteği
- [ ] DOC formatı desteği
- [ ] OCR desteği (resimlerden metin çıkarma)
- [ ] Abonelik ve ödeme sistemi
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

