'''Changes made to pinecone_upload.py:
FIXED BUGS:
Updated to match new Pinecone client method
1.  existing_indexes = pc.list_indexes().names() changed to
   existing_indexes = [index.name for index in pc.list_indexes()]
   
2. Added model parameter when get_embeddings is being called 
  before it was:
  embeddings = get_embeddings(texts)
  now it is:
  embeddings = get_embeddings(texts, model=model) 

3. Installed pinecone instead of pinecone-client because pinecone-client is deprecated.

IMPROVEMENTS:

1. Added SentenceTransformer embedding model
2. Model:sentence-transformers/all-MiniLM-L6-v2.
3. Fetched pinecone env,cloud and vector dimensions from config.py reducing redundancy


'''
from sentence_transformers import SentenceTransformer
import json
import time
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
import config
import numpy

# Config
DATA_FILE = "vietnam_travel_dataset.json"
BATCH_SIZE = 32

INDEX_NAME = config.PINECONE_INDEX_NAME
EMBED_VECTOR_DIM = 384  # for sentence-transformers/all-MiniLM-L6-v2


model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Pinecone client (same as before)
pc = Pinecone(api_key=config.PINECONE_API_KEY)

# Connect to Pinecone index
# existing_indexes = pc.list_indexes().names() 

# Updated to match new Pinecone client method
existing_indexes = [index.name for index in pc.list_indexes()]

if INDEX_NAME not in existing_indexes:
    print(f"Creating managed index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=config.PINECONE_VECTOR_DIM,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=config.PINECONE_CLOUD,
            region=config.PINECONE_ENV
        )
    )
else:
    print(f"Index {INDEX_NAME} already exists.")

index = pc.Index(INDEX_NAME)
print(index.describe_index_stats())

# Updated embedding function to use sentence transfromers from openai embedding
def get_embeddings(texts, model=None):
    """Generate embeddings using sentence-transformers (all-MiniLM-L6-v2)."""
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

def chunked(iterable, n):
    for i in range(0, len(iterable), n):
        yield iterable[i:i+n]

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        nodes = json.load(f)

    items = []
    for node in nodes:
        semantic_text = node.get("semantic_text") or (node.get("description") or "")[:1000]
        if not semantic_text.strip():
            continue
        meta = {
            "id": node.get("id"),
            "type": node.get("type"),
            "name": node.get("name"),
            "city": node.get("city", node.get("region", "")),
            "tags": node.get("tags", [])
        }
        items.append((node["id"], semantic_text, meta))

    print(f"Preparing to upsert {len(items)} items to Pinecone...")

    for batch in tqdm(list(chunked(items, BATCH_SIZE)), desc="Uploading batches"):
        ids = [item[0] for item in batch]
        texts = [item[1] for item in batch]
        metas = [item[2] for item in batch]

        embeddings = get_embeddings(texts, model=model)

        vectors = [
            {"id": _id, "values": emb, "metadata": meta}
            for _id, emb, meta in zip(ids, embeddings, metas)
        ]

        index.upsert(vectors)
        time.sleep(0.2)

    print("All items uploaded successfully.")
    print(index.describe_index_stats())

if __name__ == "__main__":
    main()
