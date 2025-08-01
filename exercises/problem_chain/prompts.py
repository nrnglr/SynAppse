# Geliştirilmiş Problem Chain Gemini Promptları

# İlk problem üretme prompt'ları - ÇOK BOYUTLU ÇÖZÜM ODaklı
PROBLEM_CHAIN_START_PROMPTS = {
    'easy': """
Sen bir yaratıcı problem tasarımcısısın. KOLAY seviyede çok boyutlu bir problem oluştur.

PROBLEM TASARIM İLKELERİ:
✓ Problem birden fazla farklı açıdan çözülebilmeli (teknolojik, sosyal, yaratıcı, pratik)
✓ İnsanlar farklı yaklaşımlar deneyebilmeli
✓ Günlük yaşamda karşılaşılabilir ama sıradışı bir durum
✓ "Bu nasıl çözülür?" sorusu birden fazla cevap üretmeli

ÖRNEK ÇOKLU ÇÖZÜM PROBLEMLERİ:
- "Mahalledeki 50 kedi aynı anda hamile kaldı ve 2 ay sonra 300+ yavru kedi sokaklarda olacak."
- "Apartmanın bodrum katında birikmiş yağmur suyu 3 aydır çekilmiyor ve sivrisinek üreme alanı oldu."

ZORUNLU ÇIKTI FORMATI:
1. Problemi açık şekilde belirt (1-2 cümle)
2. "Bu durumu nasıl çözersin?" veya benzer teşvik edici soru ile bitir

ZORUNLU KURALLAR:
- Problem + çözüm sorusu formatında yaz
- Açıklama yapma, çözüm önerme
- Maksimum 3 cümle (2 problem + 1 soru)
- Türkçe
- En az 4-5 farklı çözüm yaklaşımı mümkün olmalı

Şimdi bu kurallara uyarak problem + soru formatında yaz:
""",

    'medium': """
Sen bir yaratıcı problem tasarımcısısın. ORTA seviyede çok boyutlu bir problem oluştur.

PROBLEM TASARIM İLKELERİ:
✓ Biraz tuhaf ama mantıklı bir durum
✓ Problem çözmek için yaratıcı düşünce gerekli
✓ Birden fazla paydaş/grup etkilenmeli
✓ Farklı disiplinlerden çözüm yaklaşımları denenebilmeli
✓ Çözüm başka problemlere yol açabilir (bu iyi!)

ÖRNEK ÇOKLU ÇÖZÜM PROBLEMLERİ:
- "Şehrin ortasındaki otopark günde 3 saat kendiliğinden 30 cm yükseliyor sonra geri iniyor, arabalar mahsur kalıyor."
- "Okuldaki tüm öğrenciler aynı rüyayı görmeye başladı ve derslerde sürekli rüyalarını tartışıyor."

ZORUNLU ÇIKTI FORMATI:
1. Problemi açık şekilde belirt (1-2 cümle)
2. "Bu problemi nasıl çözersin?" veya benzer teşvik edici soru ile bitir

ZORUNLU KURALLAR:
- Problem + çözüm sorusu formatında yaz
- Açıklama yapma, çözüm önerme
- Maksimum 3 cümle (2 problem + 1 soru)
- Türkçe
- En az 5-6 farklı yaklaşımla çözülebilir olmalı
- Biraz absürd ama mantık çerçevesinde

Şimdi bu kurallara uyarak problem + soru formatında yaz:
""",

    'hard': """
Sen bir yaratıcı problem tasarımcısısın. ZOR seviyede çok katmanlı bir problem oluştur.

PROBLEM TASARIM İLKELERİ:
✓ Karmaşık, çok boyutlu durum
✓ Birden fazla grup/sistem etkilenmeli
✓ Çözüm için disiplinler arası işbirliği gerekli
✓ Her çözüm yaklaşımının kendine özgü yan etkileri olmalı
✓ Yaratıcı ve sistematik düşünce gerektirmeli

ÖRNEK ÇOKLU ÇÖZÜM PROBLEMLERİ:
- "Şehirdeki 15-25 yaş arası herkes sadece 3 saatlik dilimlerle hatırlayabiliyor, 3 saatten eski hiçbir şeyi anımsamıyor."
- "Şehrin elektriği sadece insanlar dans ederken çalışıyor, durduklarında kesiliyor ve sürekli dans etmek zorundalar."

ZORUNLU ÇIKTI FORMATI:
1. Problemi açık şekilde belirt (2-3 cümle)
2. "Bu karmaşık durumu nasıl çözersin?" veya benzer teşvik edici soru ile bitir

ZORUNLU KURALLAR:
- Problem + çözüm sorusu formatında yaz
- Açıklama yapma, çözüm önerme
- Maksimum 4 cümle (3 problem + 1 soru)
- Türkçe
- En az 7-8 farklı çözüm disiplini gerektirebilir
- Karmaşık ama çözülebilir

Şimdi bu kurallara uyarak problem + soru formatında yaz:
"""
}

# Sonraki problem üretme prompt'ı - GELİŞTİRİLMİŞ ÇOK BOYUTLU
PROBLEM_CHAIN_NEXT_PROMPT = """
Sen bir yaratıcı problem zinciri uzmanısın. Kullanıcının çözümünden mantıklı bir şekilde doğan YENİ çok boyutlu problem yaratacaksın.

Önceki Durum:
Problem: "{previous_problem}"
Kullanıcının Çözümü: "{user_solution}"

YARATILACAK YENİ PROBLEMİN ÖZELLİKLERİ:
✓ Önceki çözümün mantıklı bir sonucu/yan etkisi olmalı
✓ YENİ problem de birden fazla şekilde çözülebilir olmalı
✓ Sadece "olumsuz" değil, "beklenmedik" sonuç da olabilir
✓ İnsanlar yine yaratıcı düşünmek zorunda kalmalı

ÖRNEK ZINCIR MANTIK:
Problem: "50 kedi hamile, 300 yavru geliyor"
Çözüm: "Büyük kedi barınağı kuralım"
Yeni Problem: "Barınak kuruldu ama şimdi tüm şehirden sahipsiz kediler buraya geliyor, kapasite 10 kat aştı ve barınak kedi metropolü haline geldi."

ZORUNLU KURALLAR:
- SADECE YENİ PROBLEMİ YAZ, BAŞKA HİÇBİR ŞEY YAZMA
- Açıklama yapma, yorum ekleme
- 1-2 cümle maksimum
- Türkçe
- "Ancak şimdi..." / "Ama bu sefer..." ile başlayabilir
- Yeni problem de çok çözümlü olmalı

Şimdi verilen çözümden mantıklı, çok boyutlu yeni problem üret:
"""

# Final değerlendirme prompt'ı - İYİLEŞTİRİLMİŞ SKORLAMA SİSTEMİ
PROBLEM_CHAIN_EVALUATION_PROMPT = """
Sen bir yaratıcı problem çözme uzmanısın. Kullanıcının 5 turda gösterdiği performansı değerlendir.

Problem-Çözüm Zinciri:
{problem_solution_history}

DEĞERLENDİRME KRİTERLERİ (1-10 PUAN):

1. YARATICILIK (1-10): 
   - Çözümler ne kadar özgün ve beklenmedik?
   - Farklı perspektiflerden yaklaşım var mı?
   - Sıradışı bağlantılar kurulmuş mu?
   - CÖMERT PUANLA: Çaba gösterilmişse 6+, ortalama çözümler 7-8, gerçek yaratıcılık 9-10

2. PRATİKLİK (1-10):
   - Çözümler gerçek hayatta uygulanabilir mi?
   - Mantıklı ve makul yaklaşımlar mı?
   - Kaynak ve zaman açısından realistic mi?
   - CÖMERT PUANLA: Uygulanabilirse 6+, iyi planlanmışsa 7-8, mükemmel detay 9-10

PUANLAMA İLKELERİ:
✓ Metin uzunluğuna değil, fikrin kalitesine odaklan
✓ Çaba gösterilmişse minimum 6 puan ver
✓ Yaratıcılık + mantık kombinasyonu bonus puan hak eder
✓ Her türde çözüm denemesi değerlidir (teknolojik, sosyal, bireysel)

ZORUNLU ÇIKTI FORMATI (kesinlikle bu format, başka hiçbir şey yazma):
{{
    "creativity_score": 8,
    "practicality_score": 7,
    "feedback": "Harika yaratıcılık! 3. turda önerdiğin çözüm hem pratik hem özgündü. Genel olarak problemleri farklı açılardan değerlendirme becerin mükemmel gelişiyor."
}}

Şimdi bu formatta değerlendir:
"""

# Geliştirilmiş Fallback problemler (Gemini başarısız olursa) - ÇOK BOYUTLU ÇÖZÜMLER
FALLBACK_PROBLEMS = {
    'easy': [
        "Mahallenizdeki 20 yaşlı aynı anda bahçıvanlık hobisi edindiği için tüm marketlerdeki tohum ve gübre tükendi, gençler evlerini süsleyemiyor. Bu durumu nasıl çözersin?",
        "Apartmanın çatısında 50 güvercin yuva kurdu ve sürekli çatırdayan sesler çıkarıyor, kimse üst katlarda rahat edemiyor. Bu problemi nasıl halledebilirsin?",
        "Okul servisindeki 15 çocuk aynı anda farklı okullara gitmeye karar verdi ama hâlâ aynı servisi kullanmak istiyor. Bu duruma nasıl bir çözüm bulursun?",
        "Kahvehanedeki 30 yaşlı amca satranç oynamayı bırakıp hep birlikte TikTok çekmeye başladı, gençler kahvehaneye giremez oldu. Bu sorunu nasıl çözersin?",
        "Apartmandaki tüm komşular aynı hafta ev boyamaya karar verdi ama sadece bir tane boyacı var şehirde. Bu problemi nasıl halledebilirsin?"
    ],
    'medium': [
        "Şehirdeki tüm köpekler sadece klasik müzik dinlerken sakin kalıyor, diğer zamanlarda sürekli stresli ve hiperaktifler. Bu tuhaf durumu nasıl çözersin?",
        "Otobüsler sadece tam 27 kişi bindiğinde hareket ediyor, az ya da çok olunca durmuyor ve ulaşım sistemi çöktü. Bu problemi nasıl halledebilirsin?",
        "İnsanlar telefonda konuşurken sadece soru sorabiliyorlar, cevap veremiyorlar ve iletişim tek yönlü hale geldi. Bu garip duruma nasıl çözüm bulursun?",
        "Şehrin ortasındaki meydan her gün 2 metre büyüyor ve artık çevredeki dükkanları kaplayacak boyuta ulaştı. Bu problemi nasıl çözersin?",
        "Trafikte sadece yeşil arabalar kırmızı ışıkta geçebiliyor, diğer renkler sürekli beklemek zorunda ve trafik felç oldu. Bu durumu nasıl düzeltebilirsin?"
    ],
    'hard': [
        "Şehirdeki 18-30 yaş arası herkesin vücut saati 26 saatlik döngüye geçti, geri kalan nüfus 24 saatte yaşıyor ve toplumsal senkronizasyon kayboldu. Bu karmaşık durumu nasıl çözersin?",
        "İnsanlar sadece grup halinde (en az 5 kişi) karar verebiliyor, bireysel karar alma yetisi kayboldu ve her küçük şey için komite kurulması gerekiyor. Bu sistematik problemi nasıl halledebilirsin?",
        "Şehrin yarısında yerçekimi %20 azaldı, yarısında normal kaldı ve iki bölge arasında geçiş yapan insanlar sürekli adaptasyon sorunu yaşıyor. Bu fiziksel durumu nasıl çözersin?",
        "Her bina sakinlerinin duygusal durumuna göre renk değiştiriyor, mahremiyyet kayboldu ve şehir sürekli değişen bir duygusal harita haline geldi. Bu karmaşık problemi nasıl halledebilirsin?",
        "Zamanın akışı her mahallede farklı hızda, merkez hızlı, kenar mahalleler yavaş işliyor ve şehir içi koordinasyon imkansız hale geldi. Bu temporal sorunu nasıl çözersin?"
    ]
}

# Gemini API hata mesajı için fallback
GEMINI_ERROR_FALLBACK = "Maalesef şu anda yeni problem üretilemiyor. Lütfen daha sonra tekrar deneyin."