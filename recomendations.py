import json
from openai import OpenAI
from pydantic import BaseModel
from  cache import persistent_cache

from config import TEXT_MODEL


@persistent_cache("cache\\recomendations", ignore=["client"])
def get_recomendation(text:str, client:OpenAI, path_to_rec:str="recomendations.md"):
    print("generating recomnedations...")
    with open(path_to_rec, "r", encoding="utf-8") as f:
        recs = f.read()
    messages = [
        {"role": "system", "content": f"ты специалист по анализу учебных материалов. твоя задача анализировать учебные материалы на соответствие методическим рекомендациям:\n\n{recs}"},
        {"role": "user", "content": f"составь отчёт о соответствии методическим рекомендациям этого текста:\n\n{text}"}
    ]

    schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "struct": {
                        "type": "integer",
                        "description": "структура",
                        "maximum": 1,
                        "minimum": 0,
                        "multipleOf": 0.1
                    },
                    "validity": {
                        "type": "integer",
                        "description": "Методическая обоснованность",
                        "maximum": 1,
                        "minimum": 0,
                        "multipleOf": 0.1
                    },
                    "availability": {
                        "description": "Доступность и язык изложения",
                        "type": "integer",
                        "maximum": 1,
                        "minimum": 0,
                        "multipleOf": 0.1
                    },
                    "summary": {
                        "description": "короткий вывод о соответсвии методическим материалам",
                        "type": "string",
                        "maxLength": 250
                    }
                },
                "required": ["struct", "validity", "availability", "summary"]
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
    print("total tokens", response.usage.total_tokens)
    return result