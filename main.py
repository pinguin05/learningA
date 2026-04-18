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

from config import POSTGRES


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

        material_type = "text"
        media_annotaion = ""
        for file in os.listdir(os.path.join(path_to_data, folder)):
            path = os.path.join(path_to_data, folder, file)
            if is_image(path):
                material_type += " + images"
                media_annotaion += f"{file}:\n{get_image_annotation(path, client)}\n"
            if is_video_cv2(path):
                material_type += " + video"
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
            "generated": False,
            "type": material_type,
            "difficulty_level": annotation["difficulty_level"]
        })
    
    df = pd.DataFrame(rows)
    
    gen_df = generate_if_need(df)
    df = pd.concat([df, gen_df])

    orders = pd.DataFrame(get_order(df, client))
    df = df.join(orders.set_index('id'), on='id')

    df.to_csv("temp.csv")
    save_df_to_postgres(df, "data", POSTGRES)

    df['text_len'] = df['text'].str.len()
    df["level_from_midle"] = df["text_len"] - df["text_len"].mean()
    save_df_to_postgres(df, "stats_data", POSTGRES)


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
                    "generated": True,
                    "type": "text",
                    "difficulty_level": annotation["difficulty_level"]
                })
                start_id += 1
    return pd.DataFrame(rows)


if __name__=="__main__":
    main("data")