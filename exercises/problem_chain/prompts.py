# Geliştirilmiş Problem Chain Gemini Promptları

# İlk problem üretme prompt'ları - ÇOK BOYUTLU ÇÖZÜM ODaklı
PROBLEM_CHAIN_START_PROMPTS = {
    'easy': """
Sen bir yaratıcı problem tasarımcısısın. KOLAY seviyede eğlenceli ama gerçekçi ve mantıklı çözümler üretilebilir bir problem oluştur.

PROBLEM TASARIM İLKELERİ:
- Eğlenceli ve biraz ilginç ama gerçek hayatta olabilir
- İnsanlar mantıklı ve yaratıcı düşünce ile çözebilmeli
- Günlük hayattan sıradışı durumlar (beklenmedik ama gerçekçi)
- Çözümler mantık çerçevesinde olmalı, büyülü değil
- Problem birden fazla mantıklı açıdan çözülebilmeli
- Tamamen normal olmayan ama imkansız da olmayan durumlar

ÖRNEK PROBLEM TARZI:
"Mahalledeki tüm kediler aynı zamanda hamile oldu ve 2 ay sonra sokakta 200+ yavru kedi olacak. Belediye henüz harekete geçmedi ve komşular endişeli. Sen hayvan sever biri olarak çözüm bulmakla görevlendirildin ama bütçen çok kısıtlı."

ZORUNLU ÇIKTI FORMATI:
1. Problemi gerçekçi şekilde belirt (2-3 cümle)
2. "Bu durumu nasıl çözersin?" veya benzer soru ile bitir

ZORUNLU KURALLAR:
- Problem + çözüm sorusu formatında yaz
- Açıklama yapma, çözüm önerme
- Maksimum 3 cümle (2 problem + 1 soru)
- Türkçe
- Gerçekçi ama eğlenceli ton
- En az 3-4 farklı mantıklı çözüm yaklaşımı mümkün olmalı
- Konuşan hayvanlar, büyü gibi fantastik unsurlar kullanma

Şimdi bu kurallara uyarak gerçekçi problem + soru formatında yaz:
""",

    'medium': """
Sen bir yaratıcı problem tasarımcısısın. ORTA seviyede gerçekçi ama ilginç, mantıklı çözümler gerektiren bir problem oluştur.

PROBLEM TASARIM İLKELERİ:
- Daha karmaşık ama hâlâ gerçek hayatta olabilir
- Modern hayatın sıradışı durumları
- Mantıklı çözümler üretilebilir olmalı
- Birden fazla kişi veya grup etkilenebilir
- Teknoloji veya sosyal durumlardan kaynaklanan problemler
- Çözümler yaratıcı ama mantık çerçevesinde

ÖRNEK PROBLEM TARZI:
"Şehirdeki tüm Wi-Fi ağları aynı anda şifre değiştirdi ve yeni şifreler sadece yerel kafede yazıyor. Kafe de sadece 10 kişilik ama tüm şehir internete bağlanmaya çalışıyor. Sen de acil online toplantın var ama kafede yer yok."

ZORUNLU ÇIKTI FORMATI:
1. Problemi gerçekçi şekilde belirt (2-3 cümle)
2. "Bu problemi nasıl çözersin?" veya benzer soru ile bitir

ZORUNLU KURALLAR:
- Problem + çözüm sorusu formatında yaz
- Açıklama yapma, çözüm önerme
- Maksimum 3 cümle (2 problem + 1 soru)
- Türkçe
- Gerçekçi ama ilginç ton
- En az 4-5 farklı mantıklı yaklaşımla çözülebilir olmalı
- Fantastik unsurlar kullanma, modern yaşam odaklı

Şimdi bu kurallara uyarak gerçekçi problem + soru formatında yaz:
""",

    'hard': """
Sen bir yaratıcı problem tasarımcısısın. ZOR seviyede karmaşık ama tamamen gerçekçi, mantıklı çözümler gerektiren bir problem oluştur.

PROBLEM TASARIM İLKELERİ:
- Karmaşık, çok katmanlı ama gerçek hayatta olabilir
- Birden fazla sistem veya grup etkilenen durumlar
- Sosyal, ekonomik veya teknolojik karmaşık durumlar
- Mantıklı çözümler için disiplinler arası düşünce gerekli
- Her çözüm yaklaşımının kendine özgü sonuçları olabilir
- Tamamen gerçekçi, büyülü hiçbir unsur yok

ÖRNEK PROBLEM TARZI:
"Şehirdeki ana elektrik santrali beklenmedik bir arıza sonucu 3 gün kapalı kalacak. Jeneratörler sadece hastaneler için yeterli. 500.000 kişilik şehirde market zincirleri kapanmaya başladı ve ATM'ler çalışmıyor. Belediye başkanı olarak acil çözüm bulmalısın."

ZORUNLU ÇIKTI FORMATI:
1. Problemi gerçekçi şekilde belirt (3-4 cümle)
2. "Bu karmaşık durumu nasıl çözersin?" veya benzer soru ile bitir

ZORUNLU KURALLAR:
- Problem + çözüm sorusu formatında yaz
- Açıklama yapma, çözüm önerme
- Maksimum 4 cümle (3 problem + 1 soru)
- Türkçe
- Gerçekçi ve ciddi ton
- En az 6-7 farklı mantıklı çözüm disiplini gerektirebilir
- Tamamen gerçekçi, fantastik unsur yok

Şimdi bu kurallara uyarak gerçekçi problem + soru formatında yaz:
"""
}

# Sonraki problem üretme prompt'ı -
PROBLEM_CHAIN_NEXT_PROMPT = """
Sen bir yaratıcı problem zinciri uzmanısın. Kullanıcının çözümünden mantıklı bir şekilde doğan YENİ çok boyutlu problem yaratacaksın. Bu problemler aynı bağlam içinde kalsa da önceki problemlere benzer olmayacak.

Önceki Durum:
Problem: "{previous_problem}"
Kullanıcının Çözümü: "{user_solution}"

YARATILACAK YENİ PROBLEMİN ÖZELLİKLERİ:
✓ Önceki çözümün mantıklı bir sonucu/yan etkisi olmalı fakat önceki problemle aynı veya çok benzer olmamalı
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
- Metin uzunluğuna değil, fikrin kalitesine odaklan
- Çaba gösterilmişse minimum 6 puan ver
- Yaratıcılık + mantık kombinasyonu bonus puan hak eder
- Her türde çözüm denemesi değerlidir (teknolojik, sosyal, bireysel)

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
        "Mahalledeki 30 kedi aynı anda hamile oldu ve 2 ay sonra sokakta 150+ yavru kedi olacak. Belediye henüz harekete geçmedi ve komşular endişeli. Sen hayvan sever biri olarak çözüm bulmakla görevlendirildin ama bütçen çok kısıtlı. Bu durumu nasıl çözersin?",
        "Apartmanın bodrum katında 3 aydır su birikmiş ve sivrisinek üreme alanı olmuş. Yönetim şirketi ilgilenmiyor ve tüm alt katlar etkilendi. Sen de birinci katta oturuyorsun ve durum kötüleşiyor. Bu problemi nasıl halledebilirsin?",
        "Okul kantininde yemek fiyatları %200 arttı ve öğrencilerin yarısı yemek alamıyor. Okul yönetimi 'enflasyon' diyor ama kantinci lüks araba almış. Sen öğrenci temsilcisi olarak duruma çözüm bulmalısın. Bu duruma nasıl bir çözüm bulursun?",
        "Mahallede internet sadece bir kafede var ama kafe sahibi günde sadece 3 saat açık tutuyor. Herkesin işi internetten ve uzaktan eğitim var. Sen de acil online toplantın var ama sıra çok uzun. Bu sorunu nasıl çözersin?",
        "Apartmandaki 20 komşu aynı hafta taşınmaya karar verdi ama şehirde sadece 2 nakliye firması var. Herkes aynı gün taşınmak istiyor ve fiyatlar tavan yaptı. Sen de taşınman gerekiyor ama bütçen kısıtlı. Bu problemi nasıl halledebilirsin?"
    ],
    'medium': [
        "Şehirdeki tüm ATM'ler aynı gün bozuldu ve bankalar 3 gün tatilde. İnsanlar nakit sıkıntısı çekiyor ve marketler kartla ödeme kabul etmiyor. Sen de cebinde sadece 50 lira var ve market alışverişi yapman gerekiyor. Bu tuhaf durumu nasıl çözersin?",
        "Şehirdeki tüm otobüsler grev yaptı ve özel araç sahipleri fahiş fiyat istiyorlar. Sen de arabası olmayan biri olarak 20 km uzaktaki işine gitmek zorundasın. Taksi parası da çok pahalı. Bu problemi nasıl halledebilirsin?",
        "Mahallende elektrik 1 haftadır günde sadece 4 saat veriliyor ama saatleri belli değil. Buzdolabındaki yiyecekler bozuluyor ve telefonunu da şarj edemiyorsun. İş yerinde de jeneratör yok. Bu garip duruma nasıl çözüm bulursun?",
        "Üniversitede final sınavları bu hafta ama kütüphane tadilatta ve evde çalışamıyorsun. Kafeler de çok gürültülü ve pahalı. 5 farklı dersten sınava hazırlanman gerekiyor. Bu problemi nasıl çözersin?",
        "Şehirde su kesintisi 5 gündür devam ediyor ve tankerler sadece günde 1 saat geliyor. Su kuyrukları çok uzun ve sen de günlük işlerini halletmek zorundasın. Su biriktirme de yasaklandı. Bu durumu nasıl düzeltebilirsin?"
    ],
    'hard': [
        "Şehirdeki ana elektrik santrali beklenmedik arıza sonucu 3 gün kapalı kalacak. Jeneratörler sadece hastaneler için yeterli. 500.000 kişilik şehirde marketler kapanmaya başladı ve ATM'ler çalışmıyor. Belediye başkanı olarak acil çözüm bulmalısın. Bu karmaşık durumu nasıl çözersin?",
        "Şehirdeki tüm fabrikalar aynı hafta işçi çıkarmaya başladı ve işsizlik %40'a yükseldi. Yerel ekonomi çöktü ve insanlar şehri terk etmeye başladı. Sen belediye meclis üyesi olarak ekonomiyi canlandırmak zorundasın. Bu sistematik problemi nasıl halledebilirsin?",
        "Şehrin ana yolu heyelan sonucu kapandı ve alternatif yol 3 kat daha uzun. Kamyon trafiği durdu, marketlerde mal sıkıntısı başladı ve fiyatlar yükseliyor. Sen lojistik şirketi sahibi olarak çözüm bulmalısın. Bu fiziksel durumu nasıl çözersin?",
        "Şehirdeki 3 büyük hastane aynı hafta personel sıkıntısı yaşamaya başladı ve acil servisler kapandı. En yakın hastane 100 km uzakta ve ambulanslar da yetersiz. Sen sağlık müdürü olarak acil çözüm bulmalısın. Bu karmaşık problemi nasıl halledebilirsin?",
        "Şehirdeki tüm okullarda öğretmen sıkıntısı yaşanıyor ve derslerin yarısı iptal ediliyor. Veliler endişeli ve özel dersler çok pahalı. Uzaktan eğitim de alt yapı yetersizliği yüzünden çalışmıyor. Sen eğitim müdürü olarak çözüm bulmalısın. Bu eğitim krizini nasıl çözersin?"
    ]
}

# Gemini API hata mesajı için fallback
GEMINI_ERROR_FALLBACK = "Maalesef şu anda yeni problem üretilemiyor. Lütfen daha sonra tekrar deneyin."