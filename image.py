import os
import base64
import requests
from openai import OpenAI
from PIL import Image
from PIL import Image, UnidentifiedImageError
from cache import persistent_cache

from config import IMG_MODEL

def image_to_base64(image_path):
    """Конвертирует изображение в base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


@persistent_cache("cache\\image", ignore=["client"])
def get_image_annotation(path_to_img:str, client:OpenAI):
    print("generating image annotation...")
    # Конвертируем изображение в base64
    base64_image = image_to_base64(path_to_img)

    # Запрос к модели с анализом изображения
    response = client.chat.completions.create(
        model=IMG_MODEL,  # Имя загруженной модели в LM Studio (например, llava, bakllava)
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Максимально кратко опиши, что изображено на этой картинке"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500,
        temperature=0.7
    )

    print("total tokens", response.usage.total_tokens)
    return response.choices[0].message.content


def is_image(file_path):
    if not os.path.exists(file_path):
        return False
    try:
        with Image.open(file_path) as img:
            img.verify()  # Проверяет целостность без полной загрузки
        return True
    except (IOError, UnidentifiedImageError):
        return False