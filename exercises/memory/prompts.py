"""
Memory Exercise AI Prompts
3 Main AI interactions for memory and synthesis exercise
"""

def get_topic_generation_prompt(difficulty):
    """
    API Call 1: Generate 3 topic options based on difficulty
    """
    
    difficulty_levels = {
        'easy': 'ortaokul-lise seviyesinde, basit ve anlaşılır',
        'medium': 'üniversite seviyesinde, orta karmaşıklıkta',
        'hard': 'lisansüstü seviyesinde, zorlayıcı ve derinlemesine'
    }
    
    level_desc = difficulty_levels.get(difficulty, 'orta seviyede')
    
    return f"""Sen bir eğitim uzmanısın. {level_desc} ve ilgi çekici bir konu seçeceksin.

GÖREV: 3 farklı öğretici kategori seç ve kullanıcıya sun.

KURALLAR:
- Her kategori ilgi çekici ve öğretici olmalı
- Konfor alanından çıkarıcı ama erişilebilir
- Kategoriler birbirinden farklı alanlardan olmalı
- Her biri 100-150 kelimelik metin yazılabilir nitelikte
- ÖNEMLİ: Kategori isimleri MAKSIMUM 3-4 kelime olmalı (ekranda güzel görünmesi için)
- Kategori isimlerinde kalınlaştırma veya özel karakter kullanma

FORMAT:
🎯 BUGÜNKÜ KONULAR:

Hangi alanda öğrenmek istiyorsunuz?
[ A ] [Kategori1]    [ B ] [Kategori2]    [ C ] [Kategori3]

ÖRNEKLER (KISA İSİMLER):
- Beyin Psikolojisi, Kuantum Fiziği, Mars Keşfi
- Osmanlı Tarihi, Yapay Zeka, Rönesans Sanatı  
- Modern Felsefe, Deniz Ekosistemleri, Kalp Sistemi

UYARI: Kategori isimleri çok uzun olmasın! 3-4 kelimeyi geçmesin.

Sadece yukarıdaki formatı kullan, başka açıklama ekleme."""

def get_text_generation_prompt(difficulty, selected_topic):
    """
    API Call 2: Generate educational text based on selected topic
    """
    
    difficulty_specs = {
        'easy': {
            'level': 'ortaokul-lise seviyesi',
            'vocabulary': 'günlük hayatta kullanılan kelimeler',
            'complexity': 'basit cümleler ve net açıklamalar'
        },
        'medium': {
            'level': 'üniversite seviyesi', 
            'vocabulary': 'akademik terimler ama açıklamalı',
            'complexity': 'orta karmaşıklıkta cümleler ve kavramlar'
        },
        'hard': {
            'level': 'lisansüstü seviyesi',
            'vocabulary': 'teknik terimler ve uzmanlık kelimeler', 
            'complexity': 'karmaşık kavramlar ve derin analiz'
        }
    }
    
    specs = difficulty_specs.get(difficulty, difficulty_specs['medium'])
    
    return f"""Sen bir uzman eğitmensin. {selected_topic} konusunda {specs['level']} bir metin yazacaksın.

GÖREV: Hafıza ve öğrenme egzersizi için öğretici metin üret.

METİN KRİTERLERİ:
- Kelime sayısı: 100-150 kelime arası (kesinlikle aşma)
- Seviye: {specs['level']}
- Dil: {specs['vocabulary']}
- Karmaşıklık: {specs['complexity']}
- İçerik: Bilgi verici, öğretici, ilgi çekici, çok komplike olmasın.
- FORMAT: Önemli kelimeleri **kalın** yazı ile vurgulayabilirsin

ANAHTAR KELIME REQUİREMENTLERİ:
- 3-5 tane önemli anahtar kavram içermeli
- Bu kavramlar hafızada kalabilir nitelikte olmalı
- Konuyla doğrudan ilişkili terimler

İÇERİK YAPISI:
1. Ana kavramı tanımla
2. Somut örnek ver
3. Günlük hayatla bağlantı kur
4. Önemli detay ekle

ÖRNEK FORMAT:
📖Konu: [KONU ADI]

"[Ana kavram tanımı]. [Somut örnek veya olay]. [Bilimsel/uzman açıklama]. [Günlük hayat uygulaması]. [Ek önemli bilgi]."

İPUCU: Önemli kelimeleri **kelime** şeklinde kalın yapabilirsin. Emojisiz ve anlaşılır metin yaz."""

def get_evaluation_prompt(original_text, text_keywords, user_recall, user_keywords, user_question, question_type):
    """
    API Call 3: Evaluate user performance and provide detailed feedback
    Updated for Q&A system (no synthesis scoring)
    """
    
    return f"""Sen bir hafıza ve öğrenme uzmanısın. Kullanıcının performansını değerlendireceksin.

ORİJİNAL METİN:
"{original_text}"

METNİN ANAHTAR KELİMELERİ:
{text_keywords}

KULLANICI CEVAPLARI:
---
Geri Çağırma: "{user_recall}"
Anahtar Kelimeler: {user_keywords}  
Sorduğu Soru: "{user_question}"
---

GÖREV: Aşağıdaki 3 kriterde 1-10 arası puan ver ve detaylı analiz yap.

DEĞERLENDIRME KRİTERLERİ:

1. GERI ÇAĞIRMA DOĞRULUĞU (1-10):
- Ana fikri ne kadar doğru yakaladı?
- Önemli detayları hatırladı mı?
- Kavramsal anlayış seviyesi nasıl?

2. ANAHTAR KELIME İSABETİ (1-10):  
- Kritik kavramları bulabildi mi?
- Kelime seçimi ne kadar isabetli?
- Benzer anlamlı alternatifler kabul et

3. GENEL ÖĞRENME SKORU (1-10):
- Metni ne kadar iyi özümsedi?
- Sorusu metnin derinliğini yansıtıyor mu?
- Genel başarı seviyesi

NOT: 'overall' skoru, 'recall' ve 'keywords' skorlarının ortalaması olarak otomatik hesaplanır.

ÇIKTI FORMATI:
```json
{{
    "scores": {{
        "recall": [1-10 arası sayı],
        "keywords": [1-10 arası sayı]
    }},
    "feedback": "[Kullanıcıya özel, motive edici, yapıcı geri bildirim. 2-3 cümle]",
    "alternative_keywords": ["önerilen_kelime1", "önerilen_kelime2", "önerilen_kelime3"],
    "detailed_analysis": {{
        "recall_analysis": "[Geri çağırma detaylı değerlendirme]",
        "keyword_analysis": "[Anahtar kelime detaylı değerlendirme]",
        "question_analysis": "[Sorunun kalitesi hakkında değerlendirme]"
    }}
}}
```

Sadece JSON formatında cevap ver, başka metin ekleme."""

def get_hint_prompt(original_text, user_input):
    """
    Optional: Generate hints during exercise if user struggles
    """
    
    return f"""Sen bir yardımcı eğitmensin. Kullanıcı hatırlamakta zorlanıyor.

ORİJİNAL METİN:
"{original_text}"

KULLANICI GİRİŞİ:
"{user_input}"

GÖREV: Hatırlamaya yardımcı ipucu ver.

İPUCU KRİTERLERİ:
- Doğrudan cevabı verme
- Hatırlamayı tetikleyici sorular sor
- Ana kavramları ima et
- Kısa ve özlü ol (1-2 cümle)

ÖRNEK FORMAT:
💡 İPUCU: "[Yönlendirici soru] [Küçük hatırlatma]"

Sadece ipucu formatında cevap ver."""