import cv2
import base64
import io
from PIL import Image
from openai import OpenAI
import os
from cache import persistent_cache

from config import VIDEO_MODEL

@persistent_cache("cache\\video", ignore=["client"])
def get_video_annotation(video_path: str, client:OpenAI, max_frames: int = 10, fps: int = 1) -> str:
    """
    Описывает видео: извлекает кадры и отправляет в локальную LLM через LM Studio.
    """
    print("generating video annotation...")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Файл {video_path} не найден")
    
    # Извлечение кадров
    cap = cv2.VideoCapture(video_path)
    
    # Сохраняем FPS и длительность ДО закрытия cap
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if video_fps <= 0:
        duration = "неизвестно"
    else:
        duration = f"{total_frames / video_fps:.1f} сек"
    
    frames = []
    frame_count = 0
    step = max(1, total_frames // (max_frames * fps)) if total_frames > 0 else 1
    
    while cap.isOpened() and len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % step == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            buffer = io.BytesIO()
            pil_img.save(buffer, format="JPEG", quality=85)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            frames.append(f"data:image/jpeg;base64,{img_base64}")
        frame_count += 1
    
    cap.release()  # Теперь безопасно
    
    # Промпт с исправленной длительностью
    prompt = (
        "Проанализируй эти кадры из видео. "
        f"Видео длится примерно {duration}. "
        "Опиши ключевые сцены, действия, объекты и общее содержание. "
        "Будь краток, но информативен."
    )
    
    # Запрос к LLM
    response = client.chat.completions.create(
        model=VIDEO_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    *[{"type": "image_url", "image_url": {"url": frame}} for frame in frames]
                ]
            }
        ],
        max_tokens=500,
        temperature=0.3
    )
    
    print("total tokens", response.usage.total_tokens)
    return response.choices[0].message.content


def is_video_cv2(file_path):
    if not os.path.exists(file_path):
        return False
    
    # Быстрая проверка размера (изображения обычно <10MB)
    if os.path.getsize(file_path) < 1024 * 50:  # <50KB
        return False
    
    cap = cv2.VideoCapture(file_path)
    
    # Проверяем базовое открытие
    if not cap.isOpened():
        cap.release()
        return False
    
    # Ключевые проверки видео-метаданных
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if fps > 0 else 0
    
    cap.release()
    
    # Видео должно иметь >1 кадр И FPS >0 И длительность >1 сек
    return frame_count > 1 and fps > 0 and duration > 1.0