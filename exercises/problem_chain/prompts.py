# Problem Chain Gemini prompts

# İlk problem üretme prompt'ları
PROBLEM_CHAIN_START_PROMPTS = {
    'easy': """
Sen bir yaratıcı problem üreticisin. KOLAY seviyede bir problem oluştur.

ZORUNLU KURALLAR:
- Problem günlük yaşamda karşılaşılabilecek SOMUT bir soruna yol açmalı
- İnsanlar "Bu sorunu nasıl çözerim?" diye düşünmeli
- Çözülebilir ve mantıklı olmalı
- 1-2 cümle uzunluğunda
- Türkçe olmalı
- Sadece problemi yaz, açıklama yapma

PROBLEM YAPISI: [Tuhaf durum] + [Bu durumun yarattığı somut rahatsızlık/zorluk]

DOĞRU ÖRNEKLER:
- "Apartman asansörü bozuldu ve tamirci 2 hafta sonra geliyor. 8. katta yaşayan yaşlı komşular alışveriş yapamıyor."
- "Komşunun kedisi her gece balkonunuza gelip opera söylüyor, kimse uyuyamıyor."

YANLIŠ ÖRNEKLER (YAPMA):
- "Kediler uçmaya başladı" (Ne sorunu var ki?)
- "Zaman durdu" (Çok fantastik)

Şimdi benzer mantıkta yeni problem üret:
""",

    'medium': """
Sen bir yaratıcı problem üreticisin. ORTA seviyede bir problem oluştur.

ZORUNLU KURALLAR:
- Durum biraz absürd olabilir AMA mutlaka SOMUT bir soruna yol açmalı
- İnsanlar gerçekten rahatsız olmalı ve çözüm aramalı
- Yaratıcı düşünce gerektirmeli ama mantıklı çözümü olmalı
- 1-2 cümle uzunluğunda
- Türkçe olmalı
- Sadece problemi yaz, açıklama yapma

PROBLEM YAPISI: [Absürd ama mümkün durum] + [Bu durumun yarattığı ciddi rahatsızlık]

DOĞRU ÖRNEKLER:
- "Şehirdeki tüm köpekler sadece gece 2-5 saatleri arasında havlıyor. Her gece aynı saatte başlıyor, kimse uyuyamıyor."
- "Köpekler konuşmaya başladı ama sürekli sahiplerini eleştiriyor, insanlar evlerinde rahat edemiyor."

YANLIŞ ÖRNEKLER (YAPMA):
- "Köpekler konuşuyor" (Sorun ne?)
- "Herkes mavi rengi unuttu" (Çok absürd, somut sorun yok)

Şimdi benzer mantıkta yeni problem üret:
""",

    'hard': """
Sen bir yaratıcı problem üreticisin. ZOR seviyede bir problem oluştur.

ZORUNLU KURALLAR:
- Çok absürd ve karmaşık durum OLUR ama MUTLAKA ciddi, somut sorunlara yol açmalı
- İnsanların hayatını ciddi şekilde zorlaştırmalı
- Çözümü başka problemlere yol açabilecek kadar karmaşık olmalı
- 2-3 cümle uzunluğunda olabilir
- Türkçe olmalı
- Sadece problemi yaz, açıklama yapma

PROBLEM YAPISI: [Çok tuhaf/karmaşık durum] + [Bu durumun yarattığı çoklu ciddi sorunlar]

DOĞRU ÖRNEKLER:
- "Dünyadaki tüm saatler rastgele hızlarda işlemeye başladı. Kimse randevularına yetişemiyor, uçaklar kaçırılıyor, toplum düzeni bozuluyor."
- "Tüm insanlar günde sadece 3 saat uyuyor ama 21 saat uyanık kalmak zorunda. İş saatleri, sosyal hayat, ekonomi tamamen altüst oldu."

YANLIŞ ÖRNEKLER (YAPMA):
- "Uzaylılar geldi" (Çok fantastik)
- "Büyü var artık" (Mantıksız)

Şimdi benzer mantıkta yeni problem üret:
"""
}

# Sonraki problem üretme prompt'ı
PROBLEM_CHAIN_NEXT_PROMPT = """
Sen bir yaratıcı problem zinciri uzmanısın. Kullanıcının çözümünden doğan YENİ bir problem yaratacaksın.

Önceki Durum:
Problem: "{previous_problem}"
Kullanıcının Çözümü: "{user_solution}"

Görevin:
Bu çözümün yan etkisi, beklenmedik sonucu veya yol açtığı yeni sorunu yaz.

ZORUNLU KURALLAR:
- Önceki çözümle MANTIKLI bağlantısı olmalı
- Yeni çözüm gerektiren SOMUT bir sorun yaratmalı
- "Ama şimdi..." veya "Ancak..." diye başlayabilirsin
- 1-2 cümle uzunluğunda
- Türkçe olmalı
- Sadece yeni problemi yaz, başka hiçbir şey ekleme

MANTIK ÖRNEĞİ:
Problem: "Köpekler havlıyor, kimse uyuyamıyor"
Çözüm: "Köpeklere uyku ilacı veririz"
Yeni Problem: "Ama şimdi köpekler gündüz de uyuyor, hırsızlık olayları arttı çünkü köpekler evleri koruyamıyor"

Şimdi verilen çözümden mantıklı yeni problem üret:
"""

# Final değerlendirme prompt'ı
PROBLEM_CHAIN_EVALUATION_PROMPT = """
Sen bir yaratıcı problem çözme uzmanısın. Kullanıcının 5 turda gösterdiği performansı değerlendir.

Problem-Çözüm Zinciri:
{problem_solution_history}

DEĞERLENDİRME KRİTERLERİ:
1. YARATICILIK (1-5): Çözümler ne kadar özgün ve beklenmedik?
2. PRATİKLİK (1-5): Çözümler gerçek hayatta uygulanabilir mi?
3. TUTARLILIK: Çözümler problemi gerçekten çözüyor mu?

ZORUNLU ÇIKTI FORMATI (kesinlikle bu format, başka hiçbir şey yazma):
{{
    "creativity_score": 4,
    "practicality_score": 3,
    "feedback": "5 turda güzel yaratıcılık gösterdin! 3. turda önerdiğin çözüm çok özgündü. Pratiklik açısından biraz daha gerçekçi yaklaşımlar deneyebilirsin. Genel olarak problemlerin mantığını iyi kavradın."
}}

Şimdi bu formatta değerlendir:
"""

# Fallback problemler (Gemini başarısız olursa)
FALLBACK_PROBLEMS = {
    'easy': [
        "Apartman asansörü sürekli yanlış kata çıkıyor ve bina yöneticisi durumu çözemedi. Sakinler geç kalıyor ve yoruluyor.",
        "Komşunun papağanı her sabah 5'te haber spikeri taklidi yaparak tüm mahalleyi uyandırıyor.",
        "Otobüs durağında her gün aynı saatte gizemli bir adam dans ediyor ve insanlar durağı kullanmaya çekiniyor.",
        "Ofisteki kahve makinesi bozuldu ve sadece çay yapıyor, çalışanlar kafein eksikliğinden verimli çalışamıyor.",
        "Parkta beslenmeye gelen kediler sadece lüks mamayı yiyor, besleyen yaşlıların bütçesi tükendi."
    ],
    'medium': [
        "Şehirdeki tüm semaforer aynı anda sürekli kırmızı yanıp sönmeye başladı ve trafik tamamen durdu.",
        "İnsanlar birden sadece geriye doğru yürüyebilir hale geldi, ileri yürüyemiyorlar ve işe gidemiyorlar.",
        "Telefon konuşmaları sadece şarkı söyleyerek yapılabiliyor, acil durumlar ve iş görüşmeleri imkansız hale geldi.",
        "Tüm kediler köpek gibi havlamaya, köpekler miyavlamaya başladı ve sahipleri evcil hayvanlarını tanıyamıyor.",
        "Şehirdeki tüm saatler farklı hızlarda çalışıyor, kimse randevularına yetişemiyor ve kaos var."
    ],
    'hard': [
        "Dünyada sadece Salı günü var oldu, diğer günler kayboldu ve zaman döngüsü bozuldu. İnsanlar aynı günü tekrar yaşamaya mahkum.",
        "İnsanlar uyurken düşüncelerini yüksek sesle konuşur hale geldi. Gizlilik kalmadı, evlilikler ve arkadaşlıklar çöküyor.",
        "Yerçekimi rastgele 2 saatte bir yön değiştiriyor. İnsanlar tavana çarpıyor, yemek yiyemiyor, hayat durdu.",
        "Düşünceler görünür hale geldi, herkesin kafasında düşündükleri hologram olarak beliriyor ve toplum çöktü.",
        "Zaman geriye doğru akmaya başladı ama sadece Perşembe günleri. İnsanlar yaşlanıp gençleşiyor, akılları karışıyor."
    ]
}

# Gemini API hata mesajı için fallback
GEMINI_ERROR_FALLBACK = "Maalesef şu anda yeni problem üretilemiyor. Lütfen daha sonra tekrar deneyin."