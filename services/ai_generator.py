"""
AI Üretim Servisi
OpenAI API ile özet, sorular ve flashcard üretme fonksiyonları
"""

import json
import random
from typing import Dict, List, Any
from openai import OpenAI
from config import Config

# Türkçe prompt şablonları
TR_PROMPTS = {
    'system': 'Sen bir eğitim asistanısın. Verilen metinlerden kaliteli özet, sorular ve flashcard\'lar üretiyorsun. Yanıtlarını her zaman Türkçe ver.',
    'summary_intro': 'Aşağıdaki metni {level_name} ({age_range}) seviyesindeki {user_type_desc} için anlaşılır ve kapsamlı bir şekilde özetle.',
    'summary_full': '{intro}\n\nÖNEMLİ KURALLAR:\n1. Dili seviyeye uygun tut ({level_style})\n2. Ana konuları, önemli kavramları ve kilit noktaları içer\n3. Başlıklar ve alt başlıklar kullan\n4. Markdown formatında yaz (## başlıklar, - madde işaretleri)\n5. Önemli terimleri **kalın** yap\n6. Konular arasında boşluk bırak\n\nMetin:\n{text}\n\nLütfen özetini yapılandırılmış Markdown formatında ver.',
    'mcq_intro': 'Aşağıdaki metinden {level_name} seviyesine uygun {count} adet çoktan seçmeli soru üret.',
    'mcq_full': '{intro}\n\nHEDEF KİTLE: {level_name}\nKULLANICI TİPİ: {user_type_desc}\n\nZORLUK DAĞILIMI (mutlaka uyulmalı):\n{difficulty_dist}\n\nÖNEMLİ KURALLAR:\n1. Metindeki BAŞLIKLARI, ÜNİTELERİ ve KONU BAŞLIKLARINI tespit et\n2. Her önemli konudan MUTLAKA sorular sor\n3. Sorular içeriği ÖĞRETİR nitelikte olmalı, sadece ezber değil\n4. Yanlış şıklar mantıklı ama yanlış olmalı (çeldirici olmalı)\n5. Dili seviyeye uygun tut\n6. Her soruya detaylı açıklama ekle\n\nYanıtını JSON formatında ver:\n[\n  {{\n    "question": "Soru metni",\n    "options": ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"],\n    "correct_answer": 0,\n    "difficulty": "simple",\n    "topic": "Konu başlığı",\n    "explanation": "Detaylı açıklama: Neden bu cevap doğru, diğerleri neden yanlış"\n  }}\n]\n\nMetin:\n{text}\n\nLütfen sadece JSON formatında yanıt ver.',
    'short_answer_intro': 'Aşağıdaki metinden {level_name} seviyesine uygun {count} adet kısa cevap sorusu üret.',
    'short_answer_full': '{intro}\n\nHEDEF KİTLE: {level_name}\nKULLANICI TİPİ: {user_type_desc}\n\nÖNEMLİ KURALLAR:\n1. Metindeki BAŞLIKLARI, ÜNİTELERİ ve KONU BAŞLIKLARINI tespit et\n2. Her önemli konudan MUTLAKA sorular sor\n3. Sorular içeriği ÖĞRETİR nitelikte olmalı, sadece ezber değil\n4. Dili seviyeye uygun tut\n5. Her cevabı en fazla {max_words} kelime olacak şekilde kısa, noktasız ifadeler halinde ver\n6. Her soru için aynı anlama gelebilecek en fazla 2 alternatif kısa ifade daha ekle (accepted_answers alanında listelenmiş halde)\n\nYanıtını JSON formatında ver:\n[\n  {{\n    "question": "Soru metni?",\n    "answer": "3-4 kelimelik kısa ifade",\n    "accepted_answers": ["alternatif 1", "alternatif 2"],\n    "topic": "Konu başlığı"\n  }}\n]\n\nMetin:\n{text}\n\nLütfen sadece JSON formatında yanıt ver.',
    'fill_blank_intro': 'Aşağıdaki metinden {level_name} seviyesine uygun {count} adet boş doldurma sorusu üret.',
    'fill_blank_full': '{intro}\n\nHEDEF KİTLE: {level_name}\nKULLANICI TİPİ: {user_type_desc}\n\nÖNEMLİ KURALLAR:\n1. Metindeki BAŞLIKLARI, ÜNİTELERİ ve KONU BAŞLIKLARINI tespit et\n2. Her önemli konudan MUTLAKA sorular sor\n3. Boş bırakılan yer önemli bir KAVRAM olmalı (sadece kelime değil)\n4. Yanlış şıklar mantıklı ama yanlış olmalı (çeldirici)\n5. Dili seviyeye uygun tut\n\nHer soruda önemli bir kelime veya kavram boş bırakılmalı (_____ ile gösterilmeli).\nHer soru için doğru cevabı ve 3 yanlış seçenek daha ver (toplam 4 seçenek).\n\nYanıtını JSON formatında ver:\n[\n  {{\n    "question": "Cümle metni _____ devam eder.",\n    "answer": "doğru kelime/kavram",\n    "options": ["doğru kelime/kavram", "yanlış1", "yanlış2", "yanlış3"],\n    "topic": "Konu başlığı"\n  }}\n]\n\nMetin:\n{text}\n\nLütfen sadece JSON formatında yanıt ver.',
    'true_false_intro': 'Aşağıdaki metinden {level_name} seviyesine uygun {count} adet doğru-yanlış sorusu üret.',
    'true_false_full': '{intro}\n\nHEDEF KİTLE: {level_name}\nKULLANICI TİPİ: {user_type_desc}\n\nÖNEMLİ KURALLAR:\n1. Metindeki BAŞLIKLARI, ÜNİTELERİ ve KONU BAŞLIKLARINI tespit et\n2. Her önemli konudan MUTLAKA sorular sor\n3. Hem doğru hem yanlış ifadeler olmalı (yaklaşık %50-%50)\n4. Yanlış ifadeler mantıklı ama yanlış olmalı (çeldirici)\n5. Dili seviyeye uygun tut\n6. Her ifadeye detaylı açıklama ekle\n\nYanıtını JSON formatında ver:\n[\n  {{\n    "statement": "İfade metni",\n    "is_true": true,\n    "explanation": "Detaylı açıklama: Neden doğru/yanlış olduğu",\n    "topic": "Konu başlığı"\n  }}\n]\n\nMetin:\n{text}\n\nLütfen sadece JSON formatında yanıt ver.',
    'flashcard_intro': 'Aşağıdaki metinden {level_name} seviyesine uygun {count} adet flashcard (çalışma kartı) üret.',
    'flashcard_full': '{intro}\n\nHEDEF KİTLE: {level_name}\n\nÇOK ÖNEMLİ KURALLAR:\n1. Metindeki BAŞLIKLARI, ÜNİTELERİ ve KONU BAŞLIKLARINI tespit et\n2. Her flashcard belirli bir KONU/KAVRAM hakkında olmalı\n3. Ön yüz: Konuyu anlatan SORU (sadece terim değil!)\n4. Arka yüz: Detaylı, öğretici AÇIKLAMA (sadece tanım değil!)\n5. Flashcard\'lar konunun ÖZÜNÜ öğretmeli\n6. Sadece dokümandaki kelimeleri sorma, KAVRAMI öğret\n\nYANLIŞ ÖRNEK (yapma!):\nFront: "Fotosentez nedir?"\nBack: "Bitkilerin ışıkla besin üretmesidir."\n\nDOĞRU ÖRNEK (yap!):\nFront: "Fotosentez sırasında bitki hücresinde hangi dönüşümler gerçekleşir ve bu sürecin canlılar için önemi nedir?"\nBack: "Klorofil molekülleri ışık enerjisini yakalar ve bu enerjiyle su molekülleri parçalanır. CO2 ve sudan glikoz sentezlenir. Bu süreç atmosfere oksijen salar ve besin zincirinin temelidir. Tüm canlılar doğrudan veya dolaylı olarak fotosenteze bağımlıdır."\n\nYanıtını JSON formatında ver:\n[\n  {{\n    "front": "Derinlemesine öğretici soru",\n    "back": "Detaylı, kavramsal açıklama",\n    "topic": "Konu başlığı"\n  }}\n]\n\nMetin:\n{text}\n\nLütfen sadece JSON formatında yanıt ver.'
}

# İngilizce prompt şablonları
EN_PROMPTS = {
    'system': 'You are an educational assistant. You generate quality summaries, questions, and flashcards from given texts. Always respond in English.',
    'summary_intro': 'Summarize the following text for {user_type_desc} at {level_name} level ({age_range}) in a clear and comprehensive way.',
    'summary_full': '{intro}\n\nIMPORTANT RULES:\n1. Keep language appropriate for the level ({level_style})\n2. Include main topics, important concepts, and key points\n3. Use headings and subheadings\n4. Write in Markdown format (## headings, - bullet points)\n5. Make important terms **bold**\n6. Leave space between topics\n\nText:\n{text}\n\nPlease provide the summary in structured Markdown format.',
    'mcq_intro': 'Generate {count} multiple-choice questions suitable for {level_name} level from the following text.',
    'mcq_full': '{intro}\n\nTARGET AUDIENCE: {level_name}\nUSER TYPE: {user_type_desc}\n\nDIFFICULTY DISTRIBUTION (must be followed):\n{difficulty_dist}\n\nIMPORTANT RULES:\n1. Identify HEADINGS, UNITS, and TOPIC HEADINGS in the text\n2. Ask questions from EVERY important topic\n3. Questions should TEACH the content, not just test memorization\n4. Wrong options should be plausible but incorrect (distractors)\n5. Keep language appropriate for the level\n6. Add detailed explanation to each question\n\nRespond in JSON format:\n[\n  {{\n    "question": "Question text",\n    "options": ["Option A", "Option B", "Option C", "Option D"],\n    "correct_answer": 0,\n    "difficulty": "simple",\n    "topic": "Topic heading",\n    "explanation": "Detailed explanation: Why this answer is correct, why others are wrong"\n  }}\n]\n\nText:\n{text}\n\nPlease respond only in JSON format.',
    'short_answer_intro': 'Generate {count} short-answer questions suitable for {level_name} level from the following text.',
    'short_answer_full': '{intro}\n\nTARGET AUDIENCE: {level_name}\nUSER TYPE: {user_type_desc}\n\nIMPORTANT RULES:\n1. Identify HEADINGS, UNITS, and TOPIC HEADINGS in the text\n2. Ask questions from EVERY important topic\n3. Questions should TEACH the content, not just test memorization\n4. Keep language appropriate for the level\n5. Provide each answer as a short phrase, maximum {max_words} words, without punctuation\n6. Add up to 2 alternative short phrases with the same meaning for each question (listed in accepted_answers field)\n\nRespond in JSON format:\n[\n  {{\n    "question": "Question text?",\n    "answer": "3-4 word short phrase",\n    "accepted_answers": ["alternative 1", "alternative 2"],\n    "topic": "Topic heading"\n  }}\n]\n\nText:\n{text}\n\nPlease respond only in JSON format.',
    'fill_blank_intro': 'Generate {count} fill-in-the-blank questions suitable for {level_name} level from the following text.',
    'fill_blank_full': '{intro}\n\nTARGET AUDIENCE: {level_name}\nUSER TYPE: {user_type_desc}\n\nIMPORTANT RULES:\n1. Identify HEADINGS, UNITS, and TOPIC HEADINGS in the text\n2. Ask questions from EVERY important topic\n3. The blank should be an important CONCEPT (not just a word)\n4. Wrong options should be plausible but incorrect (distractors)\n5. Keep language appropriate for the level\n\nEach question should have an important word or concept left blank (shown with _____).\nFor each question, provide the correct answer and 3 wrong options (4 options total).\n\nRespond in JSON format:\n[\n  {{\n    "question": "Sentence text _____ continues.",\n    "answer": "correct word/concept",\n    "options": ["correct word/concept", "wrong1", "wrong2", "wrong3"],\n    "topic": "Topic heading"\n  }}\n]\n\nText:\n{text}\n\nPlease respond only in JSON format.',
    'true_false_intro': 'Generate {count} true-false questions suitable for {level_name} level from the following text.',
    'true_false_full': '{intro}\n\nTARGET AUDIENCE: {level_name}\nUSER TYPE: {user_type_desc}\n\nIMPORTANT RULES:\n1. Identify HEADINGS, UNITS, and TOPIC HEADINGS in the text\n2. Ask questions from EVERY important topic\n3. Both true and false statements should be included (approximately 50%-50%)\n4. False statements should be plausible but incorrect (distractors)\n5. Keep language appropriate for the level\n6. Add detailed explanation to each statement\n\nRespond in JSON format:\n[\n  {{\n    "statement": "Statement text",\n    "is_true": true,\n    "explanation": "Detailed explanation: Why it is true/false",\n    "topic": "Topic heading"\n  }}\n]\n\nText:\n{text}\n\nPlease respond only in JSON format.',
    'flashcard_intro': 'Generate {count} flashcards suitable for {level_name} level from the following text.',
    'flashcard_full': '{intro}\n\nTARGET AUDIENCE: {level_name}\n\nVERY IMPORTANT RULES:\n1. Identify HEADINGS, UNITS, and TOPIC HEADINGS in the text\n2. Each flashcard should be about a specific TOPIC/CONCEPT\n3. Front: A QUESTION that explains the topic (not just a term!)\n4. Back: Detailed, educational EXPLANATION (not just a definition!)\n5. Flashcards should teach the ESSENCE of the topic\n6. Don\'t just ask about words in the document, teach the CONCEPT\n\nWRONG EXAMPLE (don\'t do!):\nFront: "What is photosynthesis?"\nBack: "Plants producing food with light."\n\nCORRECT EXAMPLE (do!):\nFront: "What transformations occur in plant cells during photosynthesis and what is the importance of this process for living organisms?"\nBack: "Chlorophyll molecules capture light energy and use it to split water molecules. Glucose is synthesized from CO2 and water. This process releases oxygen into the atmosphere and is the foundation of the food chain. All living organisms depend directly or indirectly on photosynthesis."\n\nRespond in JSON format:\n[\n  {{\n    "front": "In-depth educational question",\n    "back": "Detailed, conceptual explanation",\n    "topic": "Topic heading"\n  }}\n]\n\nText:\n{text}\n\nPlease respond only in JSON format.'
}

PROMPT_TEMPLATES = {
    'tr': TR_PROMPTS,
    'en': EN_PROMPTS
}

class AIGenerator:
    """OpenAI API kullanarak eğitim içeriği üreten sınıf"""
    
    def __init__(self, api_key: str = None, model: str = None, language: str = 'tr'):
        """
        AIGenerator başlatıcı
        
        Args:
            api_key: OpenAI API anahtarı (opsiyonel, config'den alınır)
            model: Kullanılacak model (opsiyonel, config'den alınır)
            language: Dil kodu ('tr' veya 'en')
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        self.demo_mode = Config.DEMO_MODE
        self.language = language if language in ['tr', 'en'] else 'tr'
        self.prompts = PROMPT_TEMPLATES.get(self.language, TR_PROMPTS)
        
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
            return self._get_demo_response(prompt, self.language)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompts['system']},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API hatası: {str(e)}")
    
    def _get_demo_response(self, prompt: str, language: str = 'tr') -> str:
        """
        Demo modu için sahte yanıt döndürür
        
        Args:
            prompt: Gönderilen prompt
            language: Dil kodu ('tr' veya 'en')
            
        Returns:
            Prompt tipine göre sahte veri
        """
        # Prompt içeriğine göre uygun demo veri döndür
        prompt_lower = prompt.lower()
        
        # Özet kontrolü (hem Türkçe hem İngilizce)
        if "özet" in prompt_lower or "summary" in prompt_lower:
            if language == 'en':
                return """This document covers the following main topics:

• First main topic: Introduction and basic concepts
• Second main topic: Detailed explanations and examples
• Third main topic: Practical applications
• Fourth main topic: Conclusion and recommendations

The topics covered in the document include the essential information needed for students to understand the subject."""
            else:  # tr
                return """Bu doküman şu ana konuları içermektedir:

• Birinci ana konu: Giriş ve temel kavramlar
• İkinci ana konu: Detaylı açıklamalar ve örnekler
• Üçüncü ana konu: Pratik uygulamalar
• Dördüncü ana konu: Sonuç ve öneriler

Dokümanda ele alınan konular, öğrencilerin konuyu anlaması için gerekli temel bilgileri kapsamaktadır."""
        
        # Çoktan seçmeli kontrolü
        elif "çoktan seçmeli" in prompt_lower or "multiple-choice" in prompt_lower or "multiple choice" in prompt_lower:
            if language == 'en':
                return """[
  {
    "question": "Which concept is explained in this demo question?",
    "options": ["Demo Concept A", "Demo Concept B", "Demo Concept C", "Demo Concept D"],
    "correct_answer": 0,
    "explanation": "You are working in demo mode. Add OpenAI API key for real questions."
  },
  {
    "question": "Which of the following is correct?",
    "options": ["First option", "Second option", "Third option", "Fourth option"],
    "correct_answer": 2,
    "explanation": "This is demo data."
  },
  {
    "question": "Test question 3: Which statement provides the most accurate explanation?",
    "options": ["Explanation A", "Explanation B", "Explanation C", "Explanation D"],
    "correct_answer": 1,
    "explanation": "Demo mode is active."
  },
  {
    "question": "Which of the following is an example question title?",
    "options": ["Example A", "Example B", "Example C", "Example D"],
    "correct_answer": 3,
    "explanation": "This is fake data."
  },
  {
    "question": "Final demo question: Which answer is correct?",
    "options": ["Answer 1", "Answer 2", "Answer 3", "Answer 4"],
    "correct_answer": 0,
    "explanation": "You can generate real questions with OpenAI API."
  }
]"""
            else:  # tr
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
        
        # Kısa cevap kontrolü
        elif "kısa cevap" in prompt_lower or "short-answer" in prompt_lower or "short answer" in prompt_lower:
            if language == 'en':
                return """[
  {
    "question": "What is the main topic of this document?",
    "answer": "demo mode test content"
  },
  {
    "question": "What concepts are covered?",
    "answer": "demo mode test data"
  },
  {
    "question": "What is the importance of this topic?",
    "answer": "demo data OpenAI API"
  },
  {
    "question": "How can learned information be applied?",
    "answer": "fake answer demo mode"
  },
  {
    "question": "How can the topic be summarized?",
    "answer": "content analysis required"
  }
]"""
            else:  # tr
                return """[
  {
    "question": "Bu dokümanın ana konusu nedir?",
    "answer": "demo modu test içeriği"
  },
  {
    "question": "Hangi kavramlar ele alınmıştır?",
    "answer": "demo modu test verisi"
  },
  {
    "question": "Bu konunun önemi nedir?",
    "answer": "demo verisi OpenAI API"
  },
  {
    "question": "Öğrenilen bilgiler nasıl uygulanabilir?",
    "answer": "sahte cevap demo modu"
  },
  {
    "question": "Konunun özeti nasıl yapılabilir?",
    "answer": "içerik analiz edilmeli"
  }
]"""
        
        # Boş doldurma kontrolü
        elif "boş doldurma" in prompt_lower or "boş yerleri doldurma" in prompt_lower or "fill-in-the-blank" in prompt_lower or "fill in the blank" in prompt_lower:
            if language == 'en':
                return """[
  {
    "question": "This document provides information about _____.",
    "answer": "demo mode",
    "options": ["demo mode", "real data", "test content", "sample text"]
  },
  {
    "question": "Students can use this topic to _____.",
    "answer": "test",
    "options": ["test", "learn", "study", "understand"]
  },
  {
    "question": "Demo mode works without _____.",
    "answer": "API key",
    "options": ["API key", "internet", "file", "computer"]
  },
  {
    "question": "For real content, _____ is required.",
    "answer": "OpenAI API",
    "options": ["OpenAI API", "demo mode", "test data", "sample file"]
  },
  {
    "question": "This system can generate _____.",
    "answer": "questions",
    "options": ["questions", "answers", "summaries", "all"]
  }
]"""
            else:  # tr
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
        
        # Doğru-yanlış kontrolü
        elif ("doğru" in prompt_lower and "yanlış" in prompt_lower) or ("true" in prompt_lower and "false" in prompt_lower):
            if language == 'en':
                return """[
  {
    "statement": "This demo mode works without OpenAI API.",
    "is_true": true,
    "explanation": "True. Demo mode is specifically designed for testing without API."
  },
  {
    "statement": "Questions generated in demo mode are created by real AI.",
    "is_true": false,
    "explanation": "False. Demo mode uses pre-prepared fake data."
  },
  {
    "statement": "OpenAI API key is required to generate real content.",
    "is_true": true,
    "explanation": "True. OpenAI API key is mandatory for real AI generation."
  },
  {
    "statement": "This system only supports PDF files.",
    "is_true": false,
    "explanation": "False. The system supports PDF, DOCX, PPTX, and TXT formats."
  },
  {
    "statement": "Demo mode is for testing and development purposes.",
    "is_true": true,
    "explanation": "True. Demo mode is for testing the application without API."
  }
]"""
            else:  # tr
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
        
        # Flashcard kontrolü
        elif "flashcard" in prompt_lower:
            if language == 'en':
                return """[
  {
    "front": "What is Demo Mode?",
    "back": "A mode that allows testing the application without OpenAI API."
  },
  {
    "front": "What is an API Key used for?",
    "back": "An authentication key required to access OpenAI services."
  },
  {
    "front": "What does StudyBuddy do?",
    "back": "An educational application that automatically generates summaries, questions, and flashcards from documents."
  },
  {
    "front": "Which file formats are supported?",
    "back": "PDF, DOCX, PPTX, and TXT formats are supported."
  },
  {
    "front": "What is a Multiple Choice Question?",
    "back": "A question type where the correct answer is selected from multiple options."
  },
  {
    "front": "How are Flashcards used?",
    "back": "Study cards with question/term on the front and answer/explanation on the back."
  },
  {
    "front": "What is a Short Answer Question?",
    "back": "Open-ended questions that students answer in their own words."
  },
  {
    "front": "What is a Fill-in-the-Blank Question?",
    "back": "A question type where the missing part of a sentence must be completed."
  },
  {
    "front": "What is a True-False Question?",
    "back": "A question that determines whether a given statement is true or false."
  },
  {
    "front": "What is GPT-3.5-turbo?",
    "back": "OpenAI's economical and fast language model."
  }
]"""
            else:  # tr
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
            if language == 'en':
                return "This is fake content prepared for demo mode. OpenAI API key is required for real AI generation."
            else:  # tr
                return "Bu demo modu için hazırlanmış sahte içeriktir. Gerçek AI üretimi için OpenAI API anahtarı gereklidir."
    
    def generate_summary(self, text: str, level: str = 'high_school', user_type: str = 'student', language: str = None) -> str:
        """
        Metinden seviyeye uygun özet üretir
        
        Args:
            text: Özetlenecek metin
            level: Kullanıcı seviyesi
            user_type: Kullanıcı tipi
            language: Dil kodu ('tr' veya 'en'), None ise self.language kullanılır
            
        Returns:
            Markdown formatında özet
        """
        # Language parametresini kullan, yoksa self.language'i kullan
        if language is None:
            language = self.language
        else:
            # Language değiştiyse prompts'u güncelle
            if language in PROMPT_TEMPLATES:
                self.prompts = PROMPT_TEMPLATES[language]
                self.language = language
        
        level_config = Config.LEVEL_SETTINGS.get(level, Config.LEVEL_SETTINGS['high_school'])
        age_desc = level_config['age_range']
        level_name = level_config['name']
        short_cfg = level_config.get('short_answer', {'max_words': 4})
        max_words = short_cfg.get('max_words', 4)
        
        # user_type_desc oluştur
        if language == 'en':
            user_type_desc = "students" if user_type == "student" else "the teacher's class"
            level_style = "simple and clear" if level in ["elementary", "middle_school"] else "academic and detailed"
        else:  # tr
            user_type_desc = "öğrenciler" if user_type == "student" else "öğretmenin sınıfı"
            level_style = "basit ve anlaşılır" if level in ["elementary", "middle_school"] else "akademik ve detaylı"
        
        # Prompt intro'yu oluştur
        prompt_intro = self.prompts['summary_intro'].format(
            level_name=level_name,
            age_range=age_desc,
            user_type_desc=user_type_desc
        )
        
        # Tam prompt'u şablondan oluştur
        prompt = self.prompts['summary_full'].format(
            intro=prompt_intro,
            level_style=level_style,
            text=text
        )

        return self._call_openai(prompt, temperature=0.5)
    
    def generate_multiple_choice(self, text: str, count: int = 5, level: str = 'high_school', user_type: str = 'student', language: str = None) -> List[Dict[str, Any]]:
        """
        Seviyeye uygun çoktan seçmeli sorular üretir
        
        Args:
            text: Soru üretilecek metin
            count: Üretilecek soru sayısı
            level: Kullanıcı seviyesi
            user_type: Kullanıcı tipi
            language: Dil kodu ('tr' veya 'en'), None ise self.language kullanılır
            
        Returns:
            Soru listesi [{"question": "...", "options": [...], "correct_answer": 0, "difficulty": "simple"}]
        """
        # Language parametresini kullan, yoksa self.language'i kullan
        if language is None:
            language = self.language
        else:
            if language in PROMPT_TEMPLATES:
                self.prompts = PROMPT_TEMPLATES[language]
                self.language = language
        
        level_config = Config.LEVEL_SETTINGS.get(level, Config.LEVEL_SETTINGS['high_school'])
        level_name = level_config['name']
        difficulty_dist = level_config['difficulty']
        
        # Zorluk dağılımını hesapla
        simple_count = int(count * difficulty_dist['simple'] / 100)
        medium_count = int(count * difficulty_dist['medium'] / 100)
        advanced_count = int(count * difficulty_dist['advanced'] / 100)
        academic_count = count - simple_count - medium_count - advanced_count
        
        # user_type_desc oluştur
        if language == 'en':
            user_type_desc = "Student" if user_type == "student" else "Teacher (preparing for class)"
        else:  # tr
            user_type_desc = "Öğrenci" if user_type == "student" else "Öğretmen (sınıf için hazırlıyor)"
        
        # Zorluk dağılımı metnini oluştur
        if language == 'en':
            difficulty_dist_text = f"- {simple_count} SIMPLE questions (basic concepts, definitions, simple relationships)\n- {medium_count} MEDIUM questions (relationships between concepts, cause-effect, comparison)\n- {advanced_count} ADVANCED questions (analysis, synthesis, deep understanding)"
            if academic_count > 0:
                difficulty_dist_text += f"\n- {academic_count} ACADEMIC questions (critical thinking, complex relationships)"
        else:  # tr
            difficulty_dist_text = f"- {simple_count} adet BASIT soru (temel kavramlar, tanımlar, basit ilişkiler)\n- {medium_count} adet ORTA soru (kavramlar arası ilişkiler, neden-sonuç, karşılaştırma)\n- {advanced_count} adet İLERİ soru (analiz, sentez, derinlemesine anlama)"
            if academic_count > 0:
                difficulty_dist_text += f"\n- {academic_count} adet AKADEMİK soru (eleştirel düşünme, karmaşık ilişkiler)"
        
        # Prompt intro'yu oluştur
        prompt_intro = self.prompts['mcq_intro'].format(
            level_name=level_name,
            count=count
        )
        
        # Tam prompt'u şablondan oluştur
        prompt = self.prompts['mcq_full'].format(
            intro=prompt_intro,
            level_name=level_name,
            user_type_desc=user_type_desc,
            difficulty_dist=difficulty_dist_text,
            text=text
        )

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
            
            # Seçenekleri randomize et (doğru cevabı farklı şıklara dağıt)
            for question in questions:
                if 'options' in question and 'correct_answer' in question:
                    options = question['options']
                    correct_index = question['correct_answer']
                    
                    # Doğru cevabı sakla
                    correct_answer = options[correct_index]
                    
                    # Seçenekleri karıştır
                    random.shuffle(options)
                    
                    # Yeni doğru cevap indeksini bul
                    new_correct_index = options.index(correct_answer)
                    question['correct_answer'] = new_correct_index
            
            return questions
        except json.JSONDecodeError as e:
            # JSON parse edilemezse, hata logla ve basit format döndür
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"JSON parse error in generate_mcq: {str(e)}")
            logger.error(f"Raw response (first 500 chars): {response[:500]}")
            
            if language == 'en':
                return [{
                    "question": "An error occurred during question generation. Please try again.",
                    "options": ["Retry", "Contact Support", "Go Back", "Try Different Text"],
                    "correct_answer": 0,
                    "difficulty": "simple",
                    "topic": "Error",
                    "explanation": "The AI response could not be parsed. This usually happens with very short or unusual texts. Please try uploading a different document or contact support if the problem persists."
                }]
            else:  # tr
                return [{
                    "question": "Soru üretimi sırasında bir hata oluştu. Lütfen tekrar deneyin.",
                    "options": ["Tekrar Dene", "Destek İle İletişime Geç", "Geri Dön", "Farklı Metin Dene"],
                    "correct_answer": 0,
                    "difficulty": "simple",
                    "topic": "Hata",
                    "explanation": "AI yanıtı işlenemedi. Bu durum genellikle çok kısa veya alışılmadık metinlerde oluşur. Lütfen farklı bir dosya yüklemeyi deneyin veya sorun devam ederse destek ekibiyle iletişime geçin."
                }]
    
    def generate_short_answer(self, text: str, count: int = 5, level: str = 'high_school', user_type: str = 'student', language: str = None) -> List[Dict[str, str]]:
        """
        Seviyeye uygun kısa cevap soruları üretir
        
        Args:
            text: Soru üretilecek metin
            count: Üretilecek soru sayısı
            level: Kullanıcı seviyesi
            user_type: Kullanıcı tipi
            language: Dil kodu ('tr' veya 'en'), None ise self.language kullanılır
            
        Returns:
            Soru listesi [{"question": "...", "answer": "...", "topic": "..."}]
        """
        # Language parametresini kullan, yoksa self.language'i kullan
        if language is None:
            language = self.language
        else:
            if language in PROMPT_TEMPLATES:
                self.prompts = PROMPT_TEMPLATES[language]
                self.language = language
        
        level_config = Config.LEVEL_SETTINGS.get(level, Config.LEVEL_SETTINGS['high_school'])
        level_name = level_config['name']
        short_cfg = level_config.get('short_answer', {'max_words': 4})
        max_words = short_cfg.get('max_words', 4)
        
        # user_type_desc oluştur
        if language == 'en':
            user_type_desc = "Student" if user_type == "student" else "Teacher (preparing for class)"
        else:  # tr
            user_type_desc = "Öğrenci" if user_type == "student" else "Öğretmen (sınıf için hazırlıyor)"
        
        # Prompt intro'yu oluştur
        prompt_intro = self.prompts['short_answer_intro'].format(
            level_name=level_name,
            count=count
        )
        
        # Tam prompt'u şablondan oluştur
        prompt = self.prompts['short_answer_full'].format(
            intro=prompt_intro,
            level_name=level_name,
            user_type_desc=user_type_desc,
            max_words=max_words,
            text=text
        )

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
            
            def clamp_words(text: str) -> str:
                words = text.strip().split()
                if not words:
                    return ""
                return " ".join(words[:max_words])
            
            for question in questions:
                question['answer'] = clamp_words(question.get('answer', ''))
                
                accepted = question.get('accepted_answers') or []
                cleaned = []
                for alt in accepted:
                    clamped = clamp_words(alt)
                    if clamped and clamped.lower() != question['answer'].lower():
                        cleaned.append(clamped)
                question['accepted_answers'] = cleaned[:2]
            
            return questions
        except json.JSONDecodeError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"JSON parse error in generate_short_answer: {str(e)}")
            logger.error(f"Raw response (first 500 chars): {response[:500]}")
            
            if language == 'en':
                return [{
                    "question": "An error occurred during question generation. Please try again.",
                    "answer": "Error",
                    "accepted_answers": [],
                    "topic": "Error"
                }]
            else:  # tr
                return [{
                    "question": "Soru üretimi sırasında bir hata oluştu. Lütfen tekrar deneyin.",
                    "answer": "Hata",
                    "accepted_answers": [],
                    "topic": "Hata"
                }]
    
    def generate_fill_blank(self, text: str, count: int = 5, level: str = 'high_school', user_type: str = 'student', language: str = None) -> List[Dict[str, Any]]:
        """
        Seviyeye uygun boş doldurma soruları üretir
        
        Args:
            text: Soru üretilecek metin
            count: Üretilecek soru sayısı
            level: Kullanıcı seviyesi
            user_type: Kullanıcı tipi
            language: Dil kodu ('tr' veya 'en'), None ise self.language kullanılır
            
        Returns:
            Soru listesi [{"question": "... ___ ...", "answer": "cevap", "options": [...], "topic": "..."}]
        """
        # Language parametresini kullan, yoksa self.language'i kullan
        if language is None:
            language = self.language
        else:
            if language in PROMPT_TEMPLATES:
                self.prompts = PROMPT_TEMPLATES[language]
                self.language = language
        
        level_config = Config.LEVEL_SETTINGS.get(level, Config.LEVEL_SETTINGS['high_school'])
        level_name = level_config['name']
        
        # user_type_desc oluştur
        if language == 'en':
            user_type_desc = "Student" if user_type == "student" else "Teacher (preparing for class)"
        else:  # tr
            user_type_desc = "Öğrenci" if user_type == "student" else "Öğretmen (sınıf için hazırlıyor)"
        
        # Prompt intro'yu oluştur
        prompt_intro = self.prompts['fill_blank_intro'].format(
            level_name=level_name,
            count=count
        )
        
        # Tam prompt'u şablondan oluştur
        prompt = self.prompts['fill_blank_full'].format(
            intro=prompt_intro,
            level_name=level_name,
            user_type_desc=user_type_desc,
            text=text
        )

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
            
            # Boş doldurma için seçenekleri randomize et
            for question in questions:
                if 'options' in question and 'answer' in question:
                    options = question['options']
                    correct_answer = question['answer']
                    
                    # Seçenekleri karıştır
                    random.shuffle(options)
                    
                    # Doğru cevabın yeni pozisyonunu güncelle
                    question['answer'] = correct_answer  # answer alanını koru
            
            return questions
        except json.JSONDecodeError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"JSON parse error in generate_fill_blank: {str(e)}")
            logger.error(f"Raw response (first 500 chars): {response[:500]}")
            
            if language == 'en':
                return [{
                    "question": "An error occurred during question generation _____. Please try again.",
                    "answer": "error",
                    "options": ["error", "retry", "support", "help"],
                    "topic": "Error"
                }]
            else:  # tr
                return [{
                    "question": "Soru üretimi sırasında bir hata _____ oluştu. Lütfen tekrar deneyin.",
                    "answer": "büyük",
                    "options": ["büyük", "küçük", "teknik", "sistem"],
                    "topic": "Hata"
                }]
    
    def generate_true_false(self, text: str, count: int = 5, level: str = 'high_school', user_type: str = 'student', language: str = None) -> List[Dict[str, Any]]:
        """
        Seviyeye uygun doğru-yanlış soruları üretir
        
        Args:
            text: Soru üretilecek metin
            count: Üretilecek soru sayısı
            level: Kullanıcı seviyesi
            user_type: Kullanıcı tipi
            language: Dil kodu ('tr' veya 'en'), None ise self.language kullanılır
            
        Returns:
            Soru listesi [{"statement": "...", "is_true": true/false, "explanation": "...", "topic": "..."}]
        """
        # Language parametresini kullan, yoksa self.language'i kullan
        if language is None:
            language = self.language
        else:
            if language in PROMPT_TEMPLATES:
                self.prompts = PROMPT_TEMPLATES[language]
                self.language = language
        
        level_config = Config.LEVEL_SETTINGS.get(level, Config.LEVEL_SETTINGS['high_school'])
        level_name = level_config['name']
        
        # user_type_desc oluştur
        if language == 'en':
            user_type_desc = "Student" if user_type == "student" else "Teacher (preparing for class)"
        else:  # tr
            user_type_desc = "Öğrenci" if user_type == "student" else "Öğretmen (sınıf için hazırlıyor)"
        
        # Prompt intro'yu oluştur
        prompt_intro = self.prompts['true_false_intro'].format(
            level_name=level_name,
            count=count
        )
        
        # Tam prompt'u şablondan oluştur
        prompt = self.prompts['true_false_full'].format(
            intro=prompt_intro,
            level_name=level_name,
            user_type_desc=user_type_desc,
            text=text
        )

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
        except json.JSONDecodeError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"JSON parse error in generate_true_false: {str(e)}")
            logger.error(f"Raw response (first 500 chars): {response[:500]}")
            
            if language == 'en':
                return [{
                    "statement": "An error occurred during question generation. Please try again or contact support.",
                    "is_true": False,
                    "explanation": "The AI response could not be parsed. This usually happens with very short or unusual texts.",
                    "topic": "Error"
                }]
            else:  # tr
                return [{
                    "statement": "Soru üretimi sırasında bir hata oluştu. Lütfen tekrar deneyin veya destek ekibiyle iletişime geçin.",
                    "is_true": False,
                    "explanation": "AI yanıtı işlenemedi. Bu durum genellikle çok kısa veya alışılmadık metinlerde oluşur.",
                    "topic": "Hata"
                }]
    
    def generate_flashcards(self, text: str, count: int = 10, level: str = 'high_school', user_type: str = 'student', language: str = None) -> List[Dict[str, str]]:
        """
        Seviyeye uygun flashcard'lar üretir
        
        Args:
            text: Flashcard üretilecek metin
            count: Üretilecek flashcard sayısı
            level: Kullanıcı seviyesi
            user_type: Kullanıcı tipi
            language: Dil kodu ('tr' veya 'en'), None ise self.language kullanılır
            
        Returns:
            Flashcard listesi [{"front": "soru", "back": "cevap", "topic": "konu"}]
        """
        # Language parametresini kullan, yoksa self.language'i kullan
        if language is None:
            language = self.language
        else:
            if language in PROMPT_TEMPLATES:
                self.prompts = PROMPT_TEMPLATES[language]
                self.language = language
        
        level_config = Config.LEVEL_SETTINGS.get(level, Config.LEVEL_SETTINGS['high_school'])
        level_name = level_config['name']
        
        # Prompt intro'yu oluştur
        prompt_intro = self.prompts['flashcard_intro'].format(
            level_name=level_name,
            count=count
        )
        
        # Tam prompt'u şablondan oluştur
        prompt = self.prompts['flashcard_full'].format(
            intro=prompt_intro,
            level_name=level_name,
            text=text
        )

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
        except json.JSONDecodeError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"JSON parse error in generate_flashcards: {str(e)}")
            logger.error(f"Raw response (first 500 chars): {response[:500]}")
            
            if language == 'en':
                return [{
                    "front": "An error occurred during flashcard generation. Please try again.",
                    "back": "The AI response could not be parsed. This usually happens with very short or unusual texts. Please try uploading a different document.",
                    "topic": "Error"
                }]
            else:  # tr
                return [{
                    "front": "Flashcard üretimi sırasında bir hata oluştu. Lütfen tekrar deneyin.",
                    "back": "AI yanıtı işlenemedi. Bu durum genellikle çok kısa veya alışılmadık metinlerde oluşur. Lütfen farklı bir dosya yüklemeyi deneyin.",
                    "topic": "Hata"
                }]
    
    def generate_all_content(self, text: str, level: str = 'high_school', user_type: str = 'student', user_plan: str = 'free', language: str = None) -> Dict[str, Any]:
        """
        Tüm içerikleri seviyeye göre tek seferde üretir
        
        Args:
            text: İçerik üretilecek metin
            level: Kullanıcı seviyesi (elementary, middle_school, high_school, university, exam_prep)
            user_type: Kullanıcı tipi (student, teacher)
            user_plan: Kullanıcı planı (free, standard, premium) - Not: Soru limitleri app.py'de uygulanır
            language: Dil kodu ('tr' veya 'en'), None ise self.language kullanılır
            
        Returns:
            Tüm içerikleri içeren dict
        """
        # Language parametresini kullan, yoksa self.language'i kullan
        if language is None:
            language = self.language
        else:
            if language in PROMPT_TEMPLATES:
                self.prompts = PROMPT_TEMPLATES[language]
                self.language = language
        
        # Seviye ayarlarini al
        level_config = Config.LEVEL_SETTINGS.get(level, Config.LEVEL_SETTINGS['high_school'])
        question_count = level_config['questions_per_type']
        flashcard_count = question_count * 2  # Flashcard sayisi daha fazla
        
        return {
            "summary": self.generate_summary(text, level, user_type, language),
            "multiple_choice": self.generate_multiple_choice(text, question_count, level, user_type, language),
            "short_answer": self.generate_short_answer(text, question_count, level, user_type, language),
            "fill_blank": self.generate_fill_blank(text, question_count, level, user_type, language),
            "true_false": self.generate_true_false(text, question_count, level, user_type, language),
            "flashcards": self.generate_flashcards(text, flashcard_count, level, user_type, language)
        }

