import os
import random
import sys
import requests
import re

from django.conf import settings
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.wsgi import get_wsgi_application
from django.template import engines

# === DJANGO MINIMAL SETTINGS ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = 'very-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = ['django.contrib.sessions']
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
]
ROOT_URLCONF = '__main__'
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': False,
    'OPTIONS': {'loaders': [('django.template.loaders.locmem.Loader', {
        'synappse_index.html': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Synappse | Mantık Avcısı</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href='{{ tailwindcdn }}' rel="stylesheet">
    <style>
        .scrollbar::-webkit-scrollbar {width: 8px;}
        .scrollbar::-webkit-scrollbar-thumb {background: #d4d4d8; border-radius: 6px;}
    </style>
</head>
<body class="bg-gradient-to-br from-sky-50 to-indigo-100 min-h-screen">
    <div class="max-w-2xl mx-auto my-8 p-8 bg-white rounded-2xl shadow-xl">
        <h1 class="text-3xl font-extrabold mb-3 text-indigo-700 text-center">🧠 Synappse: Mantık Avcısı</h1>
        <div class="flex flex-col md:flex-row justify-between items-center mb-5 gap-2">
            <div class="text-lg font-semibold text-indigo-900">Zorluk:</div>
            <form method="post" class="flex gap-2" >
                {% csrf_token %}
                {% for z in difficulties %}
                <button name="difficulty" value="{{z}}" type="submit"
                  class="px-4 py-1.5 rounded-xl focus:outline-none focus:ring-2 
                  transition text-sm font-semibold
                  {% if difficulty == z %} bg-indigo-600 text-white ring-2 ring-indigo-400 {% else %} bg-indigo-100 hover:bg-indigo-200 text-indigo-700 {% endif %}">
                  {{ z|capfirst }}
                </button>
                {% endfor %}
            </form>
        </div>
        <div class="mb-4 bg-indigo-50 border-l-4 border-indigo-400 p-4 rounded-xl">
            <div class="font-bold text-indigo-700 mb-2">Egzersiz Paragrafı:</div>
            <div class="text-gray-800">{{ paragraph }}</div>
        </div>
        <div class="mb-6 text-gray-600 text-sm flex items-center gap-2">
            <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m2 4V9a4 4 0 10-8 0v7a4 4 0 108 0zm6 0v-7a4 4 0 00-8 0v7a4 4 0 008 0z" /></svg>
            <span>Görev: Paragraftaki mantık hatalarını/çelişkileri bul ve Synappse ile sohbet et! Yanıtını yaz, Synappse değerlendirsin.</span>
        </div>
        <div class="scrollbar max-h-64 overflow-y-auto mb-4">
            {% for msg in history %}
                {% if msg.role == "user" %}
                    <div class="flex justify-end mb-1">
                        <div class="bg-indigo-100 text-indigo-900 px-4 py-2 rounded-xl rounded-br-sm max-w-lg shadow">{{ msg.content }}</div>
                    </div>
                {% elif msg.role == "synappse" %}
                    <div class="flex justify-start mb-1">
                        <div class="bg-yellow-100 text-yellow-900 px-4 py-2 rounded-xl rounded-bl-sm max-w-lg shadow">{{ msg.content|safe }}</div>
                    </div>
                {% endif %}
            {% endfor %}
        </div>
        <form method="post" class="mt-4">
            {% csrf_token %}
            <textarea name="user_input" placeholder="Çelişkileri/hataları yaz veya açıklama iste!..." class="w-full rounded-lg border border-indigo-200 focus:ring-2 focus:ring-indigo-400 p-3 mb-2 text-gray-800" autocomplete="off"></textarea>
            <div class="flex flex-wrap gap-2">
                <button type="submit" name="submit" value="gonder" class="bg-indigo-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-indigo-700 transition">Gönder</button>
                <button type="submit" name="submit" value="new" class="bg-green-500 text-white px-6 py-2 rounded-lg font-bold hover:bg-green-600 transition">Başka Egzersiz</button>
            </div>
        </form>
        <div class="mt-6 text-xs text-gray-400 text-center border-t pt-4">Her egzersiz için yeni, yaratıcı bir paragraf gelir. Sohbet geçmişi ve cevaplar sadece bu oturumda saklanır.</div>
    </div>
</body>
</html>
'''
    })]},
}]
# context_processors YOK! (tamamen kaldırıldı)

if not settings.configured:
    settings.configure(**{k: v for k, v in locals().items() if k.isupper()})

# Kolay seviyeye uygun gündelik, somut ve basit konular
EASY_TOPICS = [
    "parkta yürüyüş yapmak", "evde temizlik yapmak", "telefonunu şarj etmek", "arkadaşla sinemaya gitmek",
    "spor salonunda antrenman yapmak", "kitapçıda kitap aramak", "evcil hayvanını gezdirmek", "müzik dinlemek",
    "alışveriş yaparken indirimleri takip etmek", "otobüsle seyahat etmek", "komşuya yardım etmek", "dondurma almak",
    "bilgisayarda oyun oynamak", "piknik yapmak", "yeni bir tarif denemek", "çamaşır yıkamak", "bahçede çiçek sulamak",
    "market alışverişi", "kütüphanede ders çalışmak", "bisiklet sürmek"
]

# Orta seviyeye uygun, biraz daha geniş ve mizahi/düşündürücü gündelik konular
MEDIUM_TOPICS = [
    "trafikte sıkışıp kalmak", "yeni bir dil öğrenmeye çalışmak", "evde unutulan anahtar yüzünden dışarıda kalmak",
    "bir partide yanlışlıkla yabancıyla sohbet etmek", "telefonu düşürüp ekranın kırılması", "yanlışlıkla mesajı yanlış kişiye atmak",
    "erken kalkmaya çalışmak ama alarmı kapatmak", "alışverişte yanlış ürünü almak", "yoğun iş temposunda unuttuğun önemli randevu",
    "tatilde kaybolmak", "evcil hayvanın eşyaları dağıtması", "spor yaparken sakatlanmak", "internette yanlış bilgiye inanmak",
    "yemek yaparken malzemeyi unutmaktan kaynaklı başarısızlık", "dostlarla yapılan yanlış anlaşılma", "trafik ışığında beklerken telefonu şarj etme çabası"
]

# Zor seviyeye uygun, bilimsel, felsefi, paradoks veya soyut konular
HARD_TOPICS = [
    "zaman yolculuğunun paradoksları", "sonsuzluk kavramı ve mantıksal tutarsızlıklar",
    "bilinç ve yapay zekanın farkları", "evrenin başlangıcı ve neden-sonuç ilişkisi",
    "özgür irade ve determinizm çelişkisi", "paradoksal düşünce deneyleri", "algı ve gerçeklik arasındaki farklar",
    "bir gemi tüm parçaları değiştirilirse aynı gemi midir?", "karınca ve insanın algı farkları",
    "bilgiye ulaşmanın sınırları ve çelişkiler", "varlık ve yokluk felsefesi", "sonsuz küçük ve sonsuz büyük kavramları",
    "kendini referans alan tanımların tutarsızlıkları", "paradoksal dil oyunları", "zamanın akışının doğası"
]

def get_topic(difficulty):
    if difficulty == "kolay":
        return random.choice(EASY_TOPICS)
    elif difficulty == "orta":
        return random.choice(MEDIUM_TOPICS)
    elif difficulty == "zor":
        return random.choice(HARD_TOPICS)
    else:
        return random.choice(EASY_TOPICS)

def get_prompt(difficulty):
    topic = get_topic(difficulty)

    if difficulty == "kolay":
        return (
            f"Sadece bir tane, kısa ve kolay bir paragraf yaz. "
            f"Her seferinde farklı bir gündelik yaşam konusunu seç. Bu sefer konu: {topic}. "
            "Olay akışı mantıklı olsun"
            "Saçma veya absürt örnekler verme, paragraf bir insan tarafından yazılmış gibi doğal gözükmeli"
            "Paragrafın genel anlatımı gerçek hayatta olabilecek gibi görünmeli"
            "Paragrafta en az bir tane bariz, anlaşılması kolay mantık hatası veya çelişki bulunsun. "
            "Cümleler sade ve anlaşılır olsun. Paragraf 3-4 cümle uzunluğunda olsun.\n\n"
            "Sonunda sadece o paragrafa ait mantık hatalarını madde madde, kısa ve net şekilde yaz.\n\n"
            "Yanıt formatı şu şekilde olmalı:\n"
            "Paragraf:\n"
            "[Buraya paragraf]\n\n"
            "Hatalar:\n"
            "- hata1\n\n"
            "Başka açıklama ekleme."
        )
    elif difficulty == "orta":
        return (
            f"Bir tane kısa ve özgün bir paragraf yaz. Kurallar:\n"
            f"- Paragraf gündelik hayat veya mizahi/düşündürücü bir konudan olsun. Bu sefer konu: {topic}.\n"
            "- İçinde en az iki mantık hatası veya çelişki bulunsun, ama hemen fark edilemeyebilir.\n"
            "- Paragraf 4-5 cümle uzunluğunda olsun.\n"
            "- Cümleler sade, anlamlı ve doğal bir anlatım sunsun.\n\n"
            "Paragrafın sonunda yalnızca o paragrafa ait mantık hatalarını maddeler halinde yaz.\n\n"
            "Yanıt şu formatta olmalı:\n"
            "Paragraf:\n"
            "[Buraya paragraf]\n\n"
            "Hatalar:\n"
            "- hata1\n"
            "- hata2\n\n"
            "Ekstra açıklama ekleme."
        )
    elif difficulty == "zor":
        return (
            f"Yaratıcı ve düşündürücü bir paragraf yaz. Kurallar:\n"
            f"- Bilim, paradokslar, felsefi konular gibi daha soyut ve karmaşık temalar seçebilirsin. Bu sefer konu: {topic}.\n"
            " Paragrafın anlamlı, tutarlı görünmesine dikkat et; mantık hataları dikkatli okuyunca fark edilsin.\n"
            "- İçinde üç veya daha fazla mantık hatası veya çelişki olsun.\n"
            "- Paragraf 5-6 cümle uzunluğunda olsun.\n\n"
            "Paragrafın ardından yalnızca o paragrafa ait mantık hatalarını maddeler halinde yaz.\n\n"
            "Yanıt şu formatta olmalı:\n"
            "Paragraf:\n"
            "[Buraya paragraf]\n\n"
            "Hatalar:\n"
            "- hata1\n"
            "- hata2\n"
            "- hata3\n\n"
            "Başka açıklama ekleme."
        )
    else:
        return get_prompt("kolay")

GEMINI_API_KEY = "AIzaSyAqVK8lkZzJQ5StyG8lMZK2qsfNXMMYffc"  # <-- BURAYA KENDİ KEY'İNİ YAZ
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_paragraph_and_errors(difficulty):
    prompt = get_prompt(difficulty)
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=18
        )
        text = response.json()['candidates'][0]['content']['parts'][0]['text']
        lines = text.strip().splitlines()
        paragraph = ""
        errors = []
        in_errors = False
        for line in lines:
            if line.strip().lower().startswith("hatalar:"):
                in_errors = True
                continue
            if in_errors:
                if line.strip().startswith("-"):
                    errors.append(line.strip()[1:].strip())
                elif line.strip() == "":
                    break
            elif line.strip().lower().startswith("paragraf:"):
                paragraph = line.split(":",1)[1].strip()
            elif not in_errors and paragraph == "" and line.strip() != "":
                paragraph = line.strip()
        return paragraph, errors
    except Exception as e:
        return "Egzersiz paragrafı alınamadı. Lütfen tekrar deneyiniz.", []

import re

def detect_specific_error_request(user_input):
    user_input = user_input.lower()
    match = re.search(r"(\d+)[\.\s]*açıklama", user_input)
    if match:
        return int(match.group(1))
    return None


def synappse_chatbot(user_input, paragraph, errors, explain_count=0):
    specific_error_index = detect_specific_error_request(user_input)

    if specific_error_index:
        if 1 <= specific_error_index <= len(errors):
            selected_error = errors[specific_error_index - 1]
            return (
                f"{specific_error_index}. açıklamanı sorduğun için yalnızca bu hatayı açıklıyorum:\n\n"
                f"**{specific_error_index}. Hata:** {selected_error}\n\n"
                "Bu, şu nedenle mantık hatası sayılır:\n\n"
                f"{selected_error} ifadesi paragraftaki olaylar arasında mantıklı bir neden-sonuç ilişkisi kurmamaktadır "
                "veya kendi içinde çelişkili bir iddia barındırmaktadır. Bu nedenle mantık hatası olarak kabul edilir.\n\n"
                "Dilersen diğer hataları da ayrı ayrı açıklayabilirim."
            )

    explain_triggers = ["bulamadım", "ipucu", "açıkla", "neden", "niye", "detay", "anlamadım"]
    wants_explanation = any(word in user_input.lower() for word in explain_triggers)

    if wants_explanation:
        if explain_count < 2:
            prompt = (
                "Aşağıda bir mantık paragrafı ve hatalar listelenmiştir.\n"
                "Karşındaki kişi, bu hataların neden mantık hatası olduğunu soruyor, kendisi bulamamış "
                "İpucu verici ve motive edici şekilde kısa açıklamalar yap. (harika tarzı kelimler kullanma)"
                f"Paragraf:\n{paragraph}\n\n"
                "Hatalar:\n" +
                "\n".join(f"- {err}" for err in errors) +
                "\nAçıklamalar (ipucu modunda):"
            )
        else:
            hatalar_metni = "\n".join(f"{i + 1}. {err}" for i, err in enumerate(errors))
            prompt = (
                "Aşağıda bir paragraf ve mantık hataları listelenmiştir.\n\n"
                "Kullanıcı mantık hatalarını bulamadı, bu yüzden artık açıklama bekliyor.\n"
                "Yanıtının başında kibar ve motive edici kısa bir giriş cümlesi yaz (örneğin: 'Bulamadın ama üzülme, birlikte bakalım.').\n\n"
                "Sonrasında HER HATAYI AYRI BİR PARAGRAF olarak açıkla.\n"
                "- Her hatanın başında hatanın numarasını kullanabilirsin.\n"
                "- Her açıklama kısa, net ve öğretici olsun.\n"
                "- Sohbet havasında anlatma, doğrudan açıklayıcı cümleler kur.\n"
                "- Karmaşık terim kullanma, herkesin anlayacağı açıklamalar yap.\n\n"
                f"Paragraf:\n{paragraph}\n\n"
                "Hatalar:\n" + hatalar_metni + "\n\n"
                "Şimdi yanıtını şu şekilde ver:\n"
                "- Kısa motive edici giriş cümlesi.\n"
                "- Her hatayı ayrı paragraf halinde açıkla:"
            )
    else:
        prompt = (
            "Bir arkadaşınla mantık hataları bulma oyunu oynuyorsun. Aşağıda bir paragraf ve gerçek hatalar var. "
            "Arkadaşının verdiği cevapta bu hataları yakalayıp yakalamadığını sohbet havasında, samimi ve motive edici cümlelerle değerlendir. "
            "Eğer doğruysa, tebrik et ve kısaca açıklama yap; eksikse, dostça ipucu ver. "
            "Eğer arkadaşın paragrafta hata olmadığını veya kendi görüşünün doğru olduğunu savunursa, ona empatik, saygılı ve sohbet tarzında cevap ver. "
            "Yine de metindeki mantık hatasını kibarca açıkla ve görüşüne saygı duyduğunu belirt. "
            "Lütfen teknik veya sistemsel ifadeler kullanma, doğrudan arkadaşına konuşuyormuş gibi yaz ve sadece doğal sohbet cümleleri kur.\n\n"
            f"Paragraf:\n{paragraph}\n\n"
            "Hatalar:\n" +
            "\n".join(f"- {err}" for err in errors) +
            f"\n\nArkadaşının cevabı:\n{user_input}\n"
            "Yanıtını doğal sohbet diliyle ver."
        )

    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=18
        )
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception:
        return "Synappse bağlantı hatası: Lütfen tekrar deneyin."



@csrf_exempt
def index(request):
    from django.template import loader

    if not hasattr(request, 'session'):
        return HttpResponse("Session middleware is required.", status=500)

    if 'difficulty' not in request.session:
        request.session['difficulty'] = 'kolay'
    difficulty = request.session['difficulty']
    difficulties = ["kolay", "orta", "zor"]

    # Yeni egzersiz istenmişse veya sayfa ilk defa GET ile açılmışsa
    if request.method == "GET" or (request.method == "POST" and request.POST.get("submit") == "new"):
        # Yeni paragraf ve hataları al
        paragraph, errors = get_paragraph_and_errors(difficulty)
        request.session['paragraph'] = paragraph
        request.session['errors'] = errors
        request.session['history'] = []
        request.session['explain_count'] = 0
        show_reveal = False
        request.session['show_reveal'] = False
    else:
        # Önceki verileri yükle
        paragraph = request.session.get('paragraph')
        errors = request.session.get('errors')
        history = request.session.get('history', [])
        show_reveal = request.session.get('show_reveal', False)
        explain_count = request.session.get('explain_count', 0)

        # POST işlemleri
        if request.method == "POST":
            if 'difficulty' in request.POST:
                # Zorluk seçildi, her şeyi sıfırla
                difficulty = request.POST['difficulty']
                request.session['difficulty'] = difficulty
                return redirect('/')

            submit_type = request.POST.get("submit")
            user_input = request.POST.get("user_input", "").strip()

            if submit_type == "reveal":
                show_reveal = True
                request.session['show_reveal'] = True

            elif submit_type == "gonder" and user_input:
                # Kullanıcının gönderdiği mesaja göre açıklama yap
                if any(w in user_input.lower() for w in ["açıkla", "ipucu", "anlamadım", "bulamadım", "detay", "nerede"]):
                    explain_count += 1
                    request.session['explain_count'] = explain_count
                else:
                    explain_count = 0
                    request.session['explain_count'] = 0

                # Chatbot yanıtı al
                synappse_reply = synappse_chatbot(
                    user_input,
                    paragraph,
                    errors,
                    explain_count=explain_count
                )

                if synappse_reply:
                    history.append({"role": "user", "content": user_input})
                    history.append({"role": "synappse", "content": synappse_reply})
                    request.session['history'] = history

    # Yeniden verileri oku (GET veya POST olabilir)
    paragraph = request.session.get('paragraph')
    errors = request.session.get('errors', [])
    history = request.session.get('history', [])
    show_reveal = request.session.get('show_reveal', False)
    difficulty = request.session.get('difficulty')

    template = engines['django'].get_template('synappse_index.html')
    html = template.render({
        "paragraph": paragraph,
        "errors": errors,
        "history": history,
        "show_reveal": show_reveal,
        "difficulty": difficulty,
        "tailwindcdn": "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css",
        "difficulties": difficulties
    }, request)
    return HttpResponse(html)


urlpatterns = [path('', index),]

application = get_wsgi_application()

if __name__ == '__main__':
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "__main__")
    django.setup()
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
