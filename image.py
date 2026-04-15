from openai import OpenAI
from PIL import Image
import base64
import requests

def image_to_base64(image_path):
    """Конвертирует изображение в base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_annotation(path_to_img:str, client:OpenAI):
    # Конвертируем изображение в base64
    base64_image = image_to_base64(path_to_img)

    # Запрос к модели с анализом изображения
    response = client.chat.completions.create(
        model="local-model",  # Имя загруженной модели в LM Studio (например, llava, bakllava)
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Опиши, что изображено на этой картинке. Кто там, что делают, какое окружение?"
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

    print(response.choices[0].message.content)