import json
from openai import OpenAI
from pydantic import BaseModel
from  cache import persistent_cache

from config import TEXT_MODEL


@persistent_cache("cache\\annotation", ignore=["client"])
def get_annotation(text:str, client:OpenAI):
    print("generating annotation...")
    messages = [
        {"role": "user", "content": f"сформируй аналитическую запись на русском, содержащую предмет (дисциплину), тему, краткую аннотацию и уровень сложности для этой статьи:\n\n{text}"}
    ]

    schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "предмет (дисциплина)",
                        "enum": ["Машинное обучение", "Математика", "Русский язык", "Системное администрирование", "Философия", "Разработка"]
                    },
                    "topic": {
                        "type": "string",
                        "description": "тема статьи"
                    },
                    "annotation": {
                        "description": "краткая аннотация",
                        "type": "string",
                        #"maxLength": 200
                    },
                    "difficulty_level": {
                        "description": "уровень сложности учебного материала",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 10
                    }
                },
                "required": ["subject", "topic", "annotation", "difficulty_level"]
            }
        }
    }

    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=messages,
        response_format=schema,
        temperature=0.1
    )

    result = json.loads(response.choices[0].message.content)
    print(result)
    print("total tokens", response.usage.total_tokens)
    return result