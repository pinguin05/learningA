import json
from openai import OpenAI
from pydantic import BaseModel
from  cache import persistent_cache


#@persistent_cache("cache\\annotation", ignore=["client"])
def get_annotation(text:str, client:OpenAI):
    messages = [
        {"role": "user", "content": f"сформируй аналитическую запись на русском, содержащую предмет (дисциплину), тему, краткую аннотацию для этой статьи:\n\n{text}"}
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
                        "maxLength": 150
                    }
                },
                "required": ["subject", "topic", "annotation"]
            }
        }
    }

    response = client.chat.completions.create(
        model="qwen/qwen3-vl-4b",
        messages=messages,
        response_format=schema,
        temperature=0.1
    )

    result = json.loads(response.choices[0].message.content)
    print("llm response: ", result)
    return result