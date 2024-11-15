import os
import json
import urllib.request
from pymilvus import MilvusClient, model
from tqdm import tqdm
import pandas as pd

from openai import OpenAI


os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ["OPENAI_API_KEY"] = "your_api_key_here"

openai_client = OpenAI(base_url="your_api_base_here")

def process_news_file(file_path):
    df = pd.read_csv(file_path)
    text_lines = df.apply(lambda row: '###'.join(row.astype(str)), axis=1).tolist()

    def emb_text(text):
        return (
            openai_client.embeddings.create(input=text, model="text-embedding-3-small")
           .data[0]
           .embedding
        )

    test_embedding = emb_text("This is a test")
    embedding_dim = len(test_embedding)
    milvus_client = MilvusClient(uri="./milvus_demo.db")

    collection_name = "my_news_collection"


    milvus_client.create_collection(
        collection_name=collection_name,
        dimension=embedding_dim,
        metric_type="IP",
        consistency_level="Strong",
    )

    data = []

    for i, line in enumerate(tqdm(text_lines, desc="Creating embeddings")):
        try:
            line_embedding = emb_text(line)
            if len(line.split()) <= 8190:
                data.append({"id": i, "vector": line_embedding, "text": line})
            else:
                print(f"Skipping line {i} due to excessive token length.")
        except Exception as e:
            print(f"Error processing line {i}: {e}")

    milvus_client.insert(collection_name=collection_name, data=data)
