import json
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel
from cache import persistent_cache

from config import TEXT_MODEL


@persistent_cache("cache\\order", ignore=["client"])
def get_order(df:pd.DataFrame, client:OpenAI):
    print("generating order...")
    mess = ""
    for idx, item in df.iterrows():
        mess += f"id: {item['id']}\nsubject: {item['subject']}\nannotation: {item['annotation']}\n\n"

    messages = [
        {"role": "system", "content": "ты специалист по анализу учебных материалов. твоя задача для каждого учебного материала определить какой учебный материал необходимо прочитать перед этим (если такой есть)"},
        {"role": "user", "content": mess}
    ]

    response_schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "description": "Список предметов с их связями по смыслу.",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "id учебного материала."
                        },
                        "previous_id": {
                            "type": "integer",
                            "description": "id предыдущего учебного материала"
                        }
                    },
                    "required": ["id", "previous_id"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["items"],
        "additionalProperties": False
    }

    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "items_list_response",
                "schema": response_schema,
                "strict": True
            }
        },
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)
    print("total tokens", response.usage.total_tokens)
    return result['items']