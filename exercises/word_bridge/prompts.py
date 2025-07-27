# Word Bridge Gemini AI Prompts

WORD_BRIDGE_WORD_GENERATION_PROMPT = """
Sen bir kelime köprüsü egzersizi için kelime üreten bir AI asistanısın.

Zorluk Seviyesi: {difficulty}

Zorluk seviyelerine göre kelime kategorileri:
- Kolay: Somut, günlük kelimeler (ev eşyaları, hayvanlar, yiyecekler, vs.)
- Orta: Karışık kategoriler (somut + soyut kavramlar karışık)
- Zor: Soyut kavramlar, uzak çağrışımlar (duygular, felsefi kavramlar, vs.)

GÖREV: 1 hedef kelime ve 3 farklı başlangıç kelimesi seçeneği üret.

⚠️ ÖNEMLİ: Başlangıç kelimeleri ile hedef kelime arasında DİREKT/AÇIK bağlantı OLMAMALI!

Çıktı formatı (JSON):
{{
    "target_word": "kelime",
    "start_options": ["kelime1", "kelime2", "kelime3"]
}}

Şartlar:
1. Başlangıç kelimeleri birbirinden tamamen farklı kategorilerden olmalı
2. Hedef kelime ile başlangıç kelimeleri arasında AÇIK/DİREKT bağlantı olmamalı (örnek: hedef="araba" ise başlangıç="teker" OLMAMALI)
3. Çok uzak kategorilerden seç: eğer hedef hayvan ise başlangıçlar teknoloji/duygu/nesne olmalı
4. Egzersizin amacı yaratıcı düşünceyi geliştirmek, kolay bağlantıları zorlaştır
5. Türkçe kelimeler kullan
6. Uygunsuz/rahatsız edici kelimeler kullanma

ÖRNEKLER:
❌ Yanlış: hedef="köpek", başlangıç=["kedi", "kemik", "tasma"] (çok benzer/ilgili)
✅ Doğru: hedef="köpek", başlangıç=["matematik", "bulut", "aşk"] (tamamen farklı kategoriler)

❌ Yanlış: hedef="masa", başlangıç=["sandalye", "ahşap", "mobilya"] (aynı kategori)
✅ Doğru: hedef="masa", başlangıç=["rüzgar", "sevinç", "parmak"] (alakasız kategoriler)
"""

WORD_BRIDGE_SOLUTION_GENERATION_PROMPT = """
Sen bir kelime köprüsü egzersizi için örnek çözüm üreten AI asistanısın.

Başlangıç Kelimesi: {start_word}
Hedef Kelime: {target_word}
Zorluk Seviyesi: {difficulty}

GÖREV: Bu başlangıç kelimesinden hedef kelimeye ulaşan mantıklı bir kelime zinciri oluştur.

Kurallar:
1. Her ara kelime, bir önceki ve sonraki kelimeyle anlamlı bağlantı kurmalı
2. En az 3, en fazla 5 ara kelime kullan
3. Mantıklı çağrışımlar/bağlantılar kurmalı (neden-sonuç, benzerlik, kategori, kullanım, vb.)
4. Türkçe kelimeler kullan

Çıktı formatı (JSON):
{{
    "solution_path": ["başlangıç", "ara1", "ara2", "ara3", "hedef"],
    "explanations": [
        "başlangıç → ara1 bağlantısının açıklaması",
        "ara1 → ara2 bağlantısının açıklaması",
        "ara2 → ara3 bağlantısının açıklaması",
        "ara3 → hedef bağlantısının açıklaması"
    ]
}}
"""

WORD_BRIDGE_HINTS_GENERATION_PROMPT = """
Sen bir kelime köprüsü egzersizi için hint sistemi oluşturan AI asistanısın.

Örnek Çözüm Yolu: {solution_path}
Hedef Kelime: {target_word}

GÖREV: 3 seviyeli hint sistemi oluştur (En az bilgiden en çok bilgiye doğru)

Hint Seviyeleri:
1. Genel Kategori İpucu: Çok genel bir yönlendirme
2. Orta Seviye İpucu: Bir ara kelime kategorisi veya tema
3. Spesifik İpucu: Doğrudan bir ara kelimeye yakın ipucu (ama kelimeyi vermeyen)

Çıktı formatı (JSON):
{{
    "hints": [
        {{
            "level": 1,
            "text": "Genel kategori ipucu metni"
        }},
        {{
            "level": 2, 
            "text": "Orta seviye ipucu metni"
        }},
        {{
            "level": 3,
            "text": "Spesifik ipucu metni"
        }}
    ]
}}

Örnek:
Çözüm: Kalem → Yazı → Gazete → Haber → Tsunami
Hint 1: "Bu yolculukta iletişim araçları önemli rol oynuyor"
Hint 2: "Yazılı medya araçlarını düşünmelisiniz" 
Hint 3: "Felaketleri haber yapan şeyler..."
"""

WORD_BRIDGE_EVALUATION_PROMPT = """
Sen bir kelime köprüsü egzersizi değerlendiren AI asistanısın.

Kullanıcının Çözümü: {user_solution}
Örnek Çözüm: {ai_solution}
Hedef Kelime: {target_word}
Kullanılan Hint Sayısı: {hints_used}

GÖREV: Kullanıcının çözümünü analiz et ve puanla.

Değerlendirme Kriterleri (1-10 arası):
1. Mantıklılık: Her adım önceki/sonrakiyle mantıklı bağlantılı mı?
2. Yaratıcılık: Beklenmedik ama mantıklı bağlantılar var mı?
3. Verimlilik: En kısa/etkili yoldan ulaştı mı?
4. Genel Başarı: Toplam performans

Puanlama:
- Her kullanılan hint için -0.5 puan kesintisi
- Hedef kelimeye ulaşamadıysa maksimum 5 puan

Çıktı formatı (JSON):
{{
    "scores": {{
        "logic": 8,
        "creativity": 7,
        "efficiency": 6,
        "overall": 7
    }},
    "evaluation_text": "Detaylı değerlendirme metni",
    "connection_analysis": [
        "kelime1 → kelime2 bağlantısının analizi",
        "kelime2 → kelime3 bağlantısının analizi"
    ],
    "suggestions": "İyileştirme önerileri"
}}
"""

WORD_BRIDGE_ALTERNATIVES_PROMPT = """
Sen alternatif çözüm yolları üreten AI asistanısın.

Başlangıç Kelimesi: {start_word}
Hedef Kelime: {target_word}
Mevcut Çözüm: {current_solution}

GÖREV: 2-3 farklı alternatif çözüm yolu üret.

Şartlar:
1. Her alternatif farklı yaklaşım/tema kullanmalı
2. Mantıklı bağlantılar kurulmalı
3. Kısa açıklamalar ekle

Çıktı formatı (JSON):
{{
    "alternatives": [
        {{
            "path": ["başlangıç", "ara1", "ara2", "hedef"],
            "theme": "Bu çözümün ana teması",
            "description": "Kısa açıklama"
        }},
        {{
            "path": ["başlangıç", "ara1", "ara2", "ara3", "hedef"],
            "theme": "Bu çözümün ana teması", 
            "description": "Kısa açıklama"
        }}
    ]
}}
"""
