import pandas as pd
from sqlalchemy import create_engine
from openai import OpenAI
from gen_check import gen_if
from annotation import get_annotation
from recomendations import get_recomendation
from storage import save_df_to_postgres
from order import get_order


POSTGRES="postgresql://user:password@localhost:5432/database"
MODEL="sage-mm-qwen3-vl-4b-sft"


client = OpenAI(
    base_url="http://66.151.33.11:1234/v1",
    api_key="not"    
)


def main():
    # eng = create_engine(POSTGRES)
    # df = pd.read_sql("SELECT * FROM data", con=eng)
    df = pd.read_csv("orig.csv")
    if len(df) < 3:
        print("в загруженном датасете слишком мало данных: ", len(df))
        return
    gen_df = generate_if_need(df)
    df = pd.concat([df, gen_df])

    orders = pd.DataFrame(get_order(df, client))
    df = df.drop(["previous_id"], axis=1, errors='ignore')
    df = df.join(orders.set_index('id'), on='id')

    df.to_csv("gen.csv")
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
    main()