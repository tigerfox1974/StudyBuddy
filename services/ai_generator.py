"""
AI Üretim Servisi
OpenAI API ile özet, sorular ve flashcard üretme fonksiyonları
"""

import json
from typing import Dict, List, Any
from openai import OpenAI
from config import Config


class AIGenerator:
    """OpenAI API kullanarak eğitim içeriği üreten sınıf"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        AIGenerator başlatıcı
        
        Args:
            api_key: OpenAI API anahtarı (opsiyonel, config'den alınır)
            model: Kullanılacak model (opsiyonel, config'den alınır)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        self.demo_mode = Config.DEMO_MODE
        
        if not self.demo_mode:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None  # Demo modda client gerekmiyor
    
    def _call_openai(self, prompt: str, temperature: float = 0.7) -> str:
        """
        OpenAI API'ye çağrı yapar (veya demo modda sahte veri döndürür)
        
        Args:
            prompt: Gönderilecek prompt
            temperature: Yaratıcılık seviyesi (0-1)
            
        Returns:
            API yanıtı veya demo verisi
        """
        if self.demo_mode:
            # Demo mode: Gerçek API çağrısı yapmadan sahte veri döndür
            return self._get_demo_response(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sen bir eğitim asistanısın. Verilen metinlerden kaliteli özet, sorular ve flashcard'lar üretiyorsun. Yanıtlarını her zaman Türkçe ver."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API hatası: {str(e)}")
    
    def _get_demo_response(self, prompt: str) -> str:
        """
        Demo modu için sahte yanıt döndürür
        
        Args:
            prompt: Gönderilen prompt
            
        Returns:
            Prompt tipine göre sahte veri
        """
        # Prompt içeriğine göre uygun demo veri döndür
        if "özet" in prompt.lower():
            return """Bu doküman şu ana konuları içermektedir:

• Birinci ana konu: Giriş ve temel kavramlar
• İkinci ana konu: Detaylı açıklamalar ve örnekler
• Üçüncü ana konu: Pratik uygulamalar
• Dördüncü ana konu: Sonuç ve öneriler

Dokümanda ele alınan konular, öğrencilerin konuyu anlaması için gerekli temel bilgileri kapsamaktadır."""
        
        elif "çoktan seçmeli" in prompt.lower():
            return """[
  {
    "question": "Bu demo sorusunda hangi kavram açıklanmaktadır?",
    "options": ["Demo Kavramı A", "Demo Kavramı B", "Demo Kavramı C", "Demo Kavramı D"],
    "correct_answer": 0,
    "explanation": "Demo modda çalışıyorsunuz. Gerçek sorular için OpenAI API anahtarı ekleyin."
  },
  {
    "question": "Aşağıdakilerden hangisi doğrudur?",
    "options": ["İlk seçenek", "İkinci seçenek", "Üçüncü seçenek", "Dördüncü seçenek"],
    "correct_answer": 2,
    "explanation": "Bu demo veridir."
  },
  {
    "question": "Test sorusu 3: Hangi ifade en doğru açıklamayı yapar?",
    "options": ["Açıklama A", "Açıklama B", "Açıklama C", "Açıklama D"],
    "correct_answer": 1,
    "explanation": "Demo modu aktif."
  },
  {
    "question": "Aşağıdakilerden hangisi örnek bir soru başlığıdır?",
    "options": ["Örnek A", "Örnek B", "Örnek C", "Örnek D"],
    "correct_answer": 3,
    "explanation": "Bu sahte veridir."
  },
  {
    "question": "Son demo sorusu: Hangi yanıt doğrudur?",
    "options": ["Yanıt 1", "Yanıt 2", "Yanıt 3", "Yanıt 4"],
    "correct_answer": 0,
    "explanation": "OpenAI API ile gerçek sorular üretebilirsiniz."
  }
]"""
        
        elif "kısa cevap" in prompt.lower():
            return """[
  {
    "question": "Bu dokümanın ana konusu nedir?",
    "answer": "Dokümanın ana konusu, demo modu test içeriğidir."
  },
  {
    "question": "Hangi kavramlar ele alınmıştır?",
    "answer": "Demo modu, test verisi ve örnek içerik kavramları ele alınmıştır."
  },
  {
    "question": "Bu konunun önemi nedir?",
    "answer": "Bu demo verisidir. Gerçek cevaplar için OpenAI API gereklidir."
  },
  {
    "question": "Öğrenilen bilgiler nasıl uygulanabilir?",
    "answer": "Demo modda çalıştığınız için bu sahte bir cevaptır."
  },
  {
    "question": "Konunun özeti nasıl yapılabilir?",
    "answer": "Demo veri: Özet yapabilmek için önce içerik analiz edilmeli."
  }
]"""
        
        elif "boş doldurma" in prompt.lower() or "boş yerleri doldurma" in prompt.lower():
            return """[
  {
    "question": "Bu doküman _____ hakkında bilgi vermektedir.",
    "answer": "demo modu",
    "options": ["demo modu", "gerçek veri", "test içeriği", "örnek metin"]
  },
  {
    "question": "Öğrenciler bu konuyu _____ için kullanabilir.",
    "answer": "test etmek",
    "options": ["test etmek", "öğrenmek", "çalışmak", "anlamak"]
  },
  {
    "question": "Demo modu _____ olmadan çalışır.",
    "answer": "API anahtarı",
    "options": ["API anahtarı", "internet", "dosya", "bilgisayar"]
  },
  {
    "question": "Gerçek içerik için _____ gereklidir.",
    "answer": "OpenAI API",
    "options": ["OpenAI API", "demo modu", "test verisi", "örnek dosya"]
  },
  {
    "question": "Bu sistem _____ üretebilir.",
    "answer": "sorular",
    "options": ["sorular", "cevaplar", "özetler", "hepsi"]
  }
]"""
        
        elif "doğru" in prompt.lower() and "yanlış" in prompt.lower():
            return """[
  {
    "statement": "Bu demo modu, OpenAI API olmadan çalışır.",
    "is_true": true,
    "explanation": "Doğru. Demo modu özellikle API olmadan test için tasarlanmıştır."
  },
  {
    "statement": "Demo modda üretilen sorular gerçek AI tarafından oluşturulur.",
    "is_true": false,
    "explanation": "Yanlış. Demo modda önceden hazırlanmış sahte veriler kullanılır."
  },
  {
    "statement": "Gerçek içerik üretmek için OpenAI API anahtarı gereklidir.",
    "is_true": true,
    "explanation": "Doğru. Gerçek AI üretimi için OpenAI API anahtarı zorunludur."
  },
  {
    "statement": "Bu sistem sadece PDF dosyalarını destekler.",
    "is_true": false,
    "explanation": "Yanlış. Sistem PDF, DOCX, PPTX ve TXT formatlarını destekler."
  },
  {
    "statement": "Demo modu test ve geliştirme amaçlıdır.",
    "is_true": true,
    "explanation": "Doğru. Demo modu, uygulamayı API olmadan test etmek içindir."
  }
]"""
        
        elif "flashcard" in prompt.lower():
            return """[
  {
    "front": "Demo Modu Nedir?",
    "back": "OpenAI API olmadan uygulamayı test etmeyi sağlayan moddur."
  },
  {
    "front": "API Anahtarı Ne İşe Yarar?",
    "back": "OpenAI servislerine erişim için gerekli olan kimlik doğrulama anahtarıdır."
  },
  {
    "front": "StudyBuddy Ne Yapar?",
    "back": "Dokümanlardan otomatik özet, soru ve flashcard üreten bir eğitim uygulamasıdır."
  },
  {
    "front": "Hangi Dosya Formatları Desteklenir?",
    "back": "PDF, DOCX, PPTX ve TXT formatları desteklenir."
  },
  {
    "front": "Çoktan Seçmeli Soru Nedir?",
    "back": "Birden fazla seçenek arasından doğru cevabın seçildiği soru tipidir."
  },
  {
    "front": "Flashcard Nasıl Kullanılır?",
    "back": "Önde soru/terim, arkada cevap/açıklama bulunan çalışma kartlarıdır."
  },
  {
    "front": "Kısa Cevap Sorusu Nedir?",
    "back": "Açık uçlu, öğrencinin kendi cümlesi ile cevapladığı sorulardır."
  },
  {
    "front": "Boş Doldurma Sorusu Nedir?",
    "back": "Cümledeki eksik kısmın tamamlanması gereken soru tipidir."
  },
  {
    "front": "Doğru-Yanlış Sorusu Nedir?",
    "back": "Verilen ifadenin doğru veya yanlış olduğunu belirleme sorusudur."
  },
  {
    "front": "GPT-3.5-turbo Nedir?",
    "back": "OpenAI'ın ekonomik ve hızlı dil modelidir."
  }
]"""
        
        else:
            return "Bu demo modu için hazırlanmış sahte içeriktir. Gerçek AI üretimi için OpenAI API anahtarı gereklidir."
    
    def generate_summary(self, text: str, level: str = 'high_school', user_type: str = 'student') -> str:
        """
        Metinden seviyeye uygun özet üretir
        
        Args:
            text: Özetlenecek metin
            level: Kullanıcı seviyesi
            user_type: Kullanıcı tipi
            
        Returns:
            Markdown formatında özet
        """
        level_config = Config.LEVEL_SETTINGS.get(level, Config.LEVEL_SETTINGS['high_school'])
        age_desc = level_config['age_range']
        level_name = level_config['name']
        
        prompt = f"""Aşağıdaki metni {level_name} ({age_desc}) seviyesindeki {"öğrenciler" if user_type == "student" else "öğretmenin sınıfı"} için anlaşılır ve kapsamlı bir şekilde özetle.

ÖNEMLI KURALLAR:
1. Dili seviyeye uygun tut ({"basit ve anlaşılır" if level in ["elementary", "middle_school"] else "akademik ve detaylı"})
2. Ana konuları, önemli kavramları ve kilit noktaları içer
3. Başlıklar ve alt başlıklar kullan
4. Markdown formatında yaz (## başlıklar, - madde işaretleri)
5. Önemli terimleri **kalın** yap
6. Konular arasında boşluk bırak

Metin:
{text}

Lütfen özetini yapılandırılmış Markdown formatında ver."""

        return self._call_openai(prompt, temperature=0.5)
    
    def generate_multiple_choice(self, text: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Çoktan seçmeli sorular üretir
        
        Args:
            text: Soru üretilecek metin
            count: Üretilecek soru sayısı
            
        Returns:
            Soru listesi [{"question": "...", "options": ["A", "B", "C", "D"], "correct": 0}]
        """
        prompt = f"""Aşağıdaki metinden {count} adet çoktan seçmeli soru üret.
Her soru için 4 seçenek (A, B, C, D) ver ve doğru cevabı belirt.
Sorular metindeki önemli kavramları ve bilgileri test etmeli.

Yanıtını JSON formatında ver:
[
  {{
    "question": "Soru metni?",
    "options": ["A seçeneği", "B seçeneği", "C seçeneği", "D seçeneği"],
    "correct_answer": 0,
    "explanation": "Doğru cevabın kısa açıklaması"
  }}
]

Metin:
{text}

Lütfen sadece JSON formatında yanıt ver, başka açıklama ekleme."""

        response = self._call_openai(prompt, temperature=0.7)
        
        try:
            # JSON parse et
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.startswith('```'):
                response_clean = response_clean[3:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            questions = json.loads(response_clean.strip())
            return questions
        except json.JSONDecodeError:
            # JSON parse edilemezse, basit format döndür
            return [{
                "question": "Soru üretimi sırasında bir hata oluştu",
                "options": ["Tekrar deneyin", "", "", ""],
                "correct_answer": 0,
                "explanation": response
            }]
    
    def generate_short_answer(self, text: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Kısa cevap soruları üretir
        
        Args:
            text: Soru üretilecek metin
            count: Üretilecek soru sayısı
            
        Returns:
            Soru listesi [{"question": "...", "answer": "..."}]
        """
        prompt = f"""Aşağıdaki metinden {count} adet kısa cevap sorusu üret.
Her soru açık uçlu olmalı ve öğrencinin konuyu anladığını test etmeli.
Örnek cevapları da ver.

Yanıtını JSON formatında ver:
[
  {{
    "question": "Soru metni?",
    "answer": "Örnek cevap"
  }}
]

Metin:
{text}

Lütfen sadece JSON formatında yanıt ver, başka açıklama ekleme."""

        response = self._call_openai(prompt, temperature=0.7)
        
        try:
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.startswith('```'):
                response_clean = response_clean[3:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            questions = json.loads(response_clean.strip())
            return questions
        except json.JSONDecodeError:
            return [{
                "question": "Soru üretimi sırasında bir hata oluştu",
                "answer": response
            }]
    
    def generate_fill_blank(self, text: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Boş doldurma soruları üretir
        
        Args:
            text: Soru üretilecek metin
            count: Üretilecek soru sayısı
            
        Returns:
            Soru listesi [{"question": "... ___ ...", "answer": "cevap", "options": [...]}]
        """
        prompt = f"""Aşağıdaki metinden {count} adet boş doldurma sorusu üret.
Her soruda önemli bir kelime veya kavram boş bırakılmalı (_____ ile gösterilmeli).
Her soru için doğru cevabı ve 3 yanlış seçenek daha ver (toplam 4 seçenek).

Yanıtını JSON formatında ver:
[
  {{
    "question": "Cümle metni _____ devam eder.",
    "answer": "doğru kelime",
    "options": ["doğru kelime", "yanlış1", "yanlış2", "yanlış3"]
  }}
]

Metin:
{text}

Lütfen sadece JSON formatında yanıt ver, başka açıklama ekleme."""

        response = self._call_openai(prompt, temperature=0.7)
        
        try:
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.startswith('```'):
                response_clean = response_clean[3:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            questions = json.loads(response_clean.strip())
            return questions
        except json.JSONDecodeError:
            return [{
                "question": "Soru üretimi sırasında bir hata oluştu _____",
                "answer": "hata",
                "options": ["hata", "tekrar", "dene", "lütfen"]
            }]
    
    def generate_true_false(self, text: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Doğru-Yanlış soruları üretir
        
        Args:
            text: Soru üretilecek metin
            count: Üretilecek soru sayısı
            
        Returns:
            Soru listesi [{"statement": "...", "is_true": true/false, "explanation": "..."}]
        """
        prompt = f"""Aşağıdaki metinden {count} adet doğru-yanlış sorusu üret.
Her ifade metindeki bilgilere dayanmalı.
Hem doğru hem yanlış ifadeler olmalı.

Yanıtını JSON formatında ver:
[
  {{
    "statement": "İfade metni",
    "is_true": true,
    "explanation": "Neden doğru/yanlış olduğunun açıklaması"
  }}
]

Metin:
{text}

Lütfen sadece JSON formatında yanıt ver, başka açıklama ekleme."""

        response = self._call_openai(prompt, temperature=0.7)
        
        try:
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.startswith('```'):
                response_clean = response_clean[3:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            questions = json.loads(response_clean.strip())
            return questions
        except json.JSONDecodeError:
            return [{
                "statement": "Soru üretimi sırasında bir hata oluştu",
                "is_true": False,
                "explanation": response
            }]
    
    def generate_flashcards(self, text: str, count: int = 10) -> List[Dict[str, str]]:
        """
        Flashcard'lar (çift yönlü kartlar) üretir
        
        Args:
            text: Flashcard üretilecek metin
            count: Üretilecek flashcard sayısı
            
        Returns:
            Flashcard listesi [{"front": "soru/terim", "back": "cevap/açıklama"}]
        """
        prompt = f"""Aşağıdaki metinden {count} adet flashcard (çalışma kartı) üret.
Her kartın ön yüzünde bir soru veya terim, arka yüzünde cevap veya açıklama olmalı.
Flashcard'lar önemli kavramları, terimleri ve bilgileri içermeli.

Yanıtını JSON formatında ver:
[
  {{
    "front": "Soru veya terim",
    "back": "Cevap veya açıklama"
  }}
]

Metin:
{text}

Lütfen sadece JSON formatında yanıt ver, başka açıklama ekleme."""

        response = self._call_openai(prompt, temperature=0.6)
        
        try:
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.startswith('```'):
                response_clean = response_clean[3:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            flashcards = json.loads(response_clean.strip())
            return flashcards
        except json.JSONDecodeError:
            return [{
                "front": "Flashcard üretimi sırasında bir hata oluştu",
                "back": response
            }]
    
    def generate_all_content(self, text: str, level: str = 'high_school', user_type: str = 'student') -> Dict[str, Any]:
        """
        Tüm içerikleri seviyeye göre tek seferde üretir
        
        Args:
            text: İçerik üretilecek metin
            level: Kullanıcı seviyesi (elementary, middle_school, high_school, university, exam_prep)
            user_type: Kullanıcı tipi (student, teacher)
            
        Returns:
            Tüm içerikleri içeren dict
        """
        # Seviye ayarlarini al
        level_config = Config.LEVEL_SETTINGS.get(level, Config.LEVEL_SETTINGS['high_school'])
        question_count = level_config['questions_per_type']
        flashcard_count = question_count * 2  # Flashcard sayisi daha fazla
        
        return {
            "summary": self.generate_summary(text, level, user_type),
            "multiple_choice": self.generate_multiple_choice(text, question_count, level, user_type),
            "short_answer": self.generate_short_answer(text, question_count, level, user_type),
            "fill_blank": self.generate_fill_blank(text, question_count, level, user_type),
            "true_false": self.generate_true_false(text, question_count, level, user_type),
            "flashcards": self.generate_flashcards(text, flashcard_count, level, user_type)
        }

