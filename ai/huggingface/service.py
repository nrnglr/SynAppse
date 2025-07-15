import os
from huggingface_hub import InferenceClient
from decouple import config

def generate_image_from_text(prompt: str, model_name: str = "black-forest-labs/FLUX.1-schnell"):
    """
    Verilen metin isteminden bir resim oluşturur.

    Args:
        prompt (str): Resim oluşturmak için kullanılacak metin.
        model_name (str): Kullanılacak Hugging Face modeli.

    Returns:
        PIL.Image.Image: Oluşturulan resim nesnesi.
    """
    try:
        hf_token = config("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN ortam değişkeni ayarlanmamış.")

        client = InferenceClient(
            provider="nebius",
            token=hf_token, # api_key parametresi yerine token kullanıldı
        )

        image = client.text_to_image(
            prompt,
            model=model_name,
        )
        return image
    except Exception as e:
        print(f"Resim oluşturulurken bir hata oluştu: {e}")
        return None 