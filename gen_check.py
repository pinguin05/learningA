import json
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel
from  cache import persistent_cache

from config import TEXT_MODEL


#@persistent_cache("cache\\annotation", ignore=["client"])
def gen_if(df:pd.DataFrame, client:OpenAI):
    mess = ""
    for idx, item in df.iterrows():
        mess += f"id: {item['id']}\nsubject: {item['subject']}\nannotation: {item['annotation']}\n\n"

    messages = [
        {"role": "user", "content": f"проанализируй учебные материалы и напиши список тем которые необходимо добавить, если такие есть (максимум 3).\n\n{mess}"}
    ]

    response_schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "description": "Список заголовков тем",
                "items": {"type": "string"}
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
        temperature=0.1
    )

    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    result = json.loads(response.choices[0].message.content)
    
    if len(result['items']) == 0:
        print('нет необходимости в генерации новых учебных материалов')
        return None
    
    if input(f"для {item['subject']} не хватает тем {result['items']}. Хотите сгенерировать учебные материалы на эти темы?(y/n)") != 'y':
        return None
    
    gen_materials = []
    for topic in result['items']:
        print(f"генерация учебного материала на тему: {topic}...")
        
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": f"ты агент для написания учебных материалов. Твоя задача писать учебный материал по указанной теме"},
                {"role": "user", "content": f"напиши учебный материал на тему: {topic}"}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        gen_materials.append(response.choices[0].message.content)
        print(f"затрачено токенов на генерацию: {response.usage.completion_tokens}")
    print(response.usage.total_tokens)
    return gen_materials
