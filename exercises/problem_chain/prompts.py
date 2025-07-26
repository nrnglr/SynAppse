# Problem Chain Gemini prompts

# İlk problem üretme prompt'ları
PROBLEM_CHAIN_START_PROMPTS = {
    'easy': """
Sen bir yaratıcı problem üreticisin. Kolay seviyede, günlük yaşamda karşılaşılabilecek ama biraz tuhaf bir problem üret.

Kurallar:
- Türkçe olmalı
- Günlük yaşamda olabilecek ama biraz absürd olmalı
- Çözülebilir olmalı
- 1-2 cümle uzunluğunda
- Sadece problemi yaz, başka hiçbir şey ekleme

Örnek: "Komşunun kedisi her gece sizin balkonunuza gelip opera söylüyor ve kimse uyuyamıyor."

Şimdi benzer tarzda yeni bir problem üret:
""",

    'medium': """
Sen bir yaratıcı problem üreticisin. Orta seviyede, absürd ama mantıklı çözüm gerektiren bir problem üret.

Kurallar:
- Türkçe olmalı
- Absürd ama mantıklı çözüm bulunabilir olmalı
- Yaratıcı düşünce gerektirmeli
- 1-2 cümle uzunluğunda
- Sadece problemi yaz, başka hiçbir şey ekleme

Örnek: "Şehirdeki tüm köpekler aniden konuşmaya başladı ama sadece şarkı sözleriyle iletişim kurabiliyorlar."

Şimdi benzer tarzda yeni bir problem üret:
""",

    'hard': """
Sen bir yaratıcı problem üreticisin. Zor seviyede, çok karmaşık ve çözümü yan etkiler yaratacak bir problem üret.

Kurallar:
- Türkçe olmalı
- Çok absürd ve karmaşık olmalı
- Çözümü başka problemlere yol açmalı
- Yaratıcılık sınırlarını zorlayıcı
- 2-3 cümle uzunluğunda
- Sadece problemi yaz, başka hiçbir şey ekleme

Örnek: "Dünyadaki tüm renkler kayboldu ve her şey gri tonlarında, ama insanlar hala renk görmek istiyor. Ayrıca bu durum bitkilerin fotosentez yapamamasına neden oluyor."

Şimdi benzer tarzda yeni bir problem üret:
"""
}

# Sonraki problem üretme prompt'ı
PROBLEM_CHAIN_NEXT_PROMPT = """
Sen bir yaratıcı problem zinciri oluşturucususun. Kullanıcının önerdiği çözümden kaynaklanan yeni bir problem yaratman gerekiyor.

Önceki Durum:
Problem: "{previous_problem}"
Kullanıcının Çözümü: "{user_solution}"

Görevin:
Bu çözümden doğacak yeni bir problemi düşün ve yaz. Çözümün yan etkisi veya beklenmedik sonucu olabilir.

Kurallar:
- Türkçe olmalı
- Önceki çözümle mantıklı bağlantısı olmalı
- Yeni yaratıcı çözüm gerektirmeli
- 1-3 cümle uzunluğunda
- Sadece yeni problemi yaz, başka hiçbir şey ekleme

Örnek Zincir:
Problem: "Köpekler konuşmaya başladı"
Çözüm: "Köpek çevirmenleri yetiştiririz"
Yeni Problem: "Ama şimdi köpekler sürekli insan dedikodularını yapıyor ve gizlilik kalmadı"

Şimdi verilen çözümden yeni problemi üret:
"""

# Final değerlendirme prompt'ı
PROBLEM_CHAIN_EVALUATION_PROMPT = """
Sen bir yaratıcı problem çözme uzmanısın. Kullanıcının 5 turda gösterdiği performansı değerlendir.

Problem-Çözüm Zinciri:
{problem_solution_history}

Görevin:
1. Yaratıcılık skorunu ver (1-5): Çözümlerin ne kadar yaratıcı ve özgün olduğunu değerlendir
2. Pratiklik skorunu ver (1-5): Çözümlerin ne kadar uygulanabilir olduğunu değerlendir  
3. Genel feedback yaz: Kullanıcının güçlü yönlerini ve gelişim alanlarını belirt

Çıktı formatı (kesinlikle bu format):
{{
    "creativity_score": 4,
    "practicality_score": 3,
    "feedback": "5 turda harika yaratıcılık gösterdin! Özellikle 3. turda önerdiğin çözüm çok özgündü. Pratiklik açısından biraz daha gerçekçi yaklaşımlar deneyebilirsin."
}}

Şimdi değerlendir:
"""

# Fallback problemler (Gemini başarısız olursa)
FALLBACK_PROBLEMS = {
    'easy': [
        "Elevator sürekli yanlış kata çıkıyor ve bina yöneticisi durumu çözemedi.",
        "Komşunun papağanı sabah 5'te haber spikeri taklidi yaparak herkesi uyandırıyor.",
        "Otobüs durağında her gün aynı saatte gizemli bir adam dans ediyor ve kimse nedenini bilmiyor.",
        "Ofisteki kahve makinesi sadece çay yapıyor ama kimse nasıl düzelteceğini bilmiyor.",
        "Parkta beslenmeye gelen kediler sadece lüks mamayı yiyor, normal mama kabul etmiyor."
    ],
    'medium': [
        "Şehirdeki tüm semaforer aynı anda kırmızı yanıp sönmeye başladı ve trafik durdu.",
        "İnsanlar birden sadece ters yürüyebilir hale geldi, ileri doğru yürüyemiyorlar.",
        "Telefon konuşmaları sadece şarkı söyleyerek yapılabiliyor, normal konuşma imkansız.",
        "Tüm kediler aynı anda köpek gibi havlamaya başladı ve köpekler miyavlamaya başladı.",
        "Şehirdeki tüm saatler farklı hızlarda çalışıyor, kimse doğru zamanı bilmiyor."
    ],
    'hard': [
        "Dünyada sadece Salı günü var oldu, diğer günler tamamen kayboldu ve zaman döngüsü bozuldu.",
        "İnsanlar uyurken bilinçaltlarının düşüncelerini yüksek sesle konuşur hale geldi ve mahremiyetin sonu.",
        "Yerçekimi rastgele 2 saatte bir yön değiştiriyor ve insanlar tavana, duvarlara yapışıyor.",
        "Düşünceler görünür hale geldi, herkesin kafasında düşündükleri hologram olarak beliriyor.",
        "Zaman geriye doğru akmaya başladı ama sadece Perşembe günleri, diğer günler normal."
    ]
}

# Gemini API hata mesajı için fallback
GEMINI_ERROR_FALLBACK = "Maalesef şu anda yeni problem üretilemiyor. Lütfen daha sonra tekrar deneyin."
