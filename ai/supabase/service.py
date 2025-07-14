import io
import uuid
from datetime import datetime
from lobsmart.settings import supabase
from PIL.Image import Image

def upload_image_to_supabase(image: Image, bucket_name: str = "exercise-images") -> str | None:
    """
    PIL.Image nesnesini byte'a çevirir ve Supabase Storage'a yükler.

    Args:
        image (Image): Yüklenecek PIL Image nesnesi.
        bucket_name (str): Yükleneceği Supabase Storage bucket'ının adı.

    Returns:
        Yüklenen resmin public URL'i veya hata durumunda None.
    """
    try:
        # Resmi byte verisine dönüştür
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Benzersiz ve tarihe dayalı bir dosya yolu oluştur
        # Örn: 2024/07/15/some-random-uuid.png
        current_date = datetime.now()
        file_path = f"{current_date.strftime('%Y/%m/%d')}/{uuid.uuid4()}.png"

        # Supabase'e yükle
        response = supabase.storage.from_(bucket_name).upload(
            path=file_path,
            file=img_byte_arr.getvalue(),
            file_options={"content-type": "image/png"}
        )
        
        # Public URL'i al
        url_response = supabase.storage.from_(bucket_name).get_public_url(file_path)

        return url_response

    except Exception as e:
        print(f"Supabase'e resim yüklenirken hata oluştu: {e}")
        return None 