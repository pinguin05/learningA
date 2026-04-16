import os
import pandas as pd
from openai import OpenAI
from annotation import get_annotation
from image import get_image_annotation, is_image
from video import get_video_annotation, is_video_cv2
from recomendations import get_recomendation
from order import get_order
from gen_check import gen_if
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

        media_annotaion = ""
        for file in os.listdir(os.path.join(path_to_data, folder)):
            path = os.path.join(path_to_data, folder, file)
            if is_image(path):
                media_annotaion += f"{file}:\n{get_image_annotation(path, client)}\n"
            if is_video_cv2(path):
                media_annotaion += f"{file}:\n{get_video_annotation(path, client)}\n"

        recs = get_recomendation(text, client)

        rows.append({
            "id": idx,
            "text": text,
            "annotation": annotation["annotation"],
            "subject": annotation["subject"],
            "topic": annotation["topic"],
            "media_annotation": media_annotaion,
            "rec_struct": recs["struct"],
            "rec_validity": recs["validity"],
            "rec_availability": recs["availability"],
            "rec_sum": recs["summary"],
            "generated": False
        })
    
    df = pd.DataFrame(rows)
    
    gen_df = generate_if_need(df)
    df = pd.concat([df, gen_df])

    orders = get_order(df, client)
    df['previous_id'] = df['id'].map(lambda x: next(item['previous_id'] for item in orders if item['id'] == x))

    df.to_csv("temp.csv")
    save_df_to_postgres(df, "data", "postgresql://user:password@localhost:5432/database")


def generate_if_need(df:pd.DataFrame):
    start_id = df['id'].max() + 1
    subjects = df['subject'].unique()
    rows = []
    for subject in subjects:
        generated = gen_if(df[df["subject"] == subject], client)
        if generated:
            for text in generated:

                annotation = get_annotation(text, client)
                recs = get_recomendation(text, client)

                rows.append({
                    "id": start_id,
                    "text": text,
                    "annotation": annotation["annotation"],
                    "subject": annotation["subject"],
                    "topic": annotation["topic"],
                    "media_annotation": "",
                    "rec_struct": recs["struct"],
                    "rec_validity": recs["validity"],
                    "rec_availability": recs["availability"],
                    "rec_sum": recs["summary"],
                    "generated": True
                })
                start_id += 1
    return pd.DataFrame(rows)


if __name__=="__main__":
    main("data")