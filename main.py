import os
import pandas as pd
from openai import OpenAI
from annotation import get_annotation
from image import get_image_discribe
from storage import save_df_to_postgres


client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not"    
)


def main(path_to_data:str):
    rows = []
    for idx, folder in enumerate(os.listdir(path_to_data)):
        with open(os.path.join(path_to_data, folder, "text.md"), "r", encoding="utf-8") as f:
            text = f.read()

        annotation = get_annotation(text, client)

        for file in os.listdir(os.path.join(path_to_data, folder)):
            try:
                get_image_discribe(os.path.join(path_to_data, ))

        rows.append({
            "id": idx,
            "text": text,
            "annotation": annotation["annotation"],
            "subject": annotation["subject"],
            "topic": annotation["topic"]
        })

    df = pd.DataFrame(rows)
    df.to_csv("temp.csv")
    save_df_to_postgres(df, "data", "postgresql://user:password@localhost:5432/database")


if __name__=="__main__":
    main("data")