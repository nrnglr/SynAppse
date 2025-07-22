from .gemini.service import GeminiService

# --- PROMPTS ---

CREATIVE_FEEDBACK_PROMPT = """
Sen bir yazarlık koçusun. Bir kullanıcıya, belirlediğin bir karakter ve 3 anahtar kelime kullanarak kısa bir hikaye yazma görevi verildi.
Şimdi kullanıcının yazdığı hikayeyi analiz et ve yapıcı geri bildirimlerde bulun.

Geri bildirim formatın şöyle olmalı:
1.  **Genel Değerlendirme:** Hikayenin genel atmosferi, tonu ve akıcılığı hakkında olumlu bir yorum yap.
2.  **Kelime Kullanımı:** Verilen 3 anahtar kelimenin hikaye içinde nasıl kullanıldığını analiz et. ("'kelime1', 'kelime2' ve 'kelime3' kelimelerini... bir şekilde kullanmışsın.")
3.  **Karakter Derinliği:** Kullanıcının, verdiğin karakteri ne kadar yansıttığını değerlendir. ("Verdiğim '[karakter]' karakterini... bir şekilde yansıtmışsın.")
4.  **Gelişim Önerisi:** Hikayeyi daha da ileri taşıyabilecek küçük ve uygulanabilir bir tavsiye ver. (Örneğin: "Bir sonraki adım olarak, karakterin iç dünyasına daha fazla odaklanabilirsin.")

Lütfen doğrudan ve cesaretlendirici bir dil kullan. Cevabın sadece bu geri bildirim metni olsun.

---
- **Verilen Karakter:** [character]
- **Verilen Anahtar Kelimeler:** [words]
- **Kullanıcının Hikayesi:**
[user_story]
---
"""

CREATIVE_FEEDBACK_PROMPT_NO_CHAR = """
Sen bir yazarlık koçusun. Bir kullanıcıya, belirlediğin 2 anahtar kelime kullanarak kısa bir hikaye yazma görevi verildi.
Şimdi kullanıcının yazdığı hikayeyi analiz et ve yapıcı geri bildirimlerde bulun.

Geri bildirim formatın şöyle olmalı:
1.  **Genel Değerlendirme:** Hikayenin genel atmosferi, tonu ve akıcılığı hakkında olumlu bir yorum yap.
2.  **Kelime Kullanımı:** Verilen 2 anahtar kelimenin hikaye içinde nasıl kullanıldığını analiz et. ("'kelime1' ve 'kelime2' kelimelerini... bir şekilde kullanmışsın.")
3.  **Gelişim Önerisi:** Hikayeyi daha da ileri taşıyabilecek küçük ve uygulanabilir bir tavsiye ver.

Lütfen doğrudan ve cesaretlendirici bir dil kullan. Cevabın sadece bu geri bildirim metni olsun.

---
- **Verilen Anahtar Kelimeler:** [words]
- **Kullanıcının Hikayesi:**
[user_story]
---
"""

MEMORY_FEEDBACK_PROMPT = """
Sen bir hafıza ve dil becerileri koçusun. Bir kullanıcıya, sırayla gösterilen kelimeleri kullanarak anlamlı bir paragraf oluşturma görevi verildi.
Lütfen kullanıcının yazdığı paragrafı analiz et ve aşağıdaki kriterlere göre geri bildirim ver:

1.  **Bağlantı Kurma Yeteneği:** Kelimeler arasında kurulan anlamsal bağlantıların ne kadar güçlü ve mantıklı olduğunu değerlendir.
2.  **Akıcılık ve Dilbilgisi:** Paragrafın genel akıcılığını ve dilbilgisi doğruluğunu yorumla.
3.  **Olumlu Pekiştirme:** Kullanıcının çabasını takdir eden kısa ve motive edici bir cümle ekle.

Lütfen doğrudan, basit ve cesaretlendirici bir dil kullan. Cevabın sadece bu geri bildirim metni olsun.

---
- **Verilen Kelimeler:** [words]
- **Kullanıcının Paragrafı:**
[user_paragraph]
---
"""

# --- Functions ---

def get_creativity_feedback(words: list, user_story: str, character: str = None) -> str:
    """
    Generates feedback for a creativity exercise story.
    The 'character' parameter is optional.
    """
    gemini_service = GeminiService()
    
    # Prompt'u karakterin varlığına göre dinamik olarak seç ve doldur
    if character:
        prompt = CREATIVE_FEEDBACK_PROMPT.replace("[character]", character).replace("[words]", ", ".join(words)).replace("[user_story]", user_story)
    else:
        prompt = CREATIVE_FEEDBACK_PROMPT_NO_CHAR.replace("[words]", ", ".join(words)).replace("[user_story]", user_story)

    feedback = gemini_service.generate_text(prompt, temperature=0.7)
    return feedback

def get_memory_feedback(words: list, user_paragraph: str) -> str:
    """
    Generates feedback for a memory exercise paragraph.
    """
    gemini_service = GeminiService()
    prompt = MEMORY_FEEDBACK_PROMPT.replace("[words]", ", ".join(words)).replace("[user_paragraph]", user_paragraph)
    feedback = gemini_service.generate_text(prompt, temperature=0.7)
    return feedback 