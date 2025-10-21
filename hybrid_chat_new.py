''' Changes made in hybrid_chat_new.py:
BUGS FIXED:
1. Fixed all deprecated/v-2 incompatible Pinecone calls
2. Removed import json since it is not accessed
IMPROVEMENTS:
Since OPENAI_API_KEY is not free , chhanges from 1-3 were made.
1. Changed Embed_Model from text-embedding-3-small to all-MiniLM-L6-v2 
2. Removed openai import and added groq import because using OPENAI_API_KEY is not free.
3. Changed model from gpt-4o-mini to llama-3.3-70b-versatile
4. Improved Prompt clarity and nsurd that Neo4j queries return meaningful results.
5. Added 'CHAIN-OF-THOUGHT' style reasoning.
6. Integrated search_summary() function to summarize top nodes.
'''

from typing import List
from sentence_transformers import SentenceTransformer
from groq import Groq
from groq.types.chat.chat_completion import ChatCompletion
from typing import List
from pinecone import Pinecone, ServerlessSpec
from neo4j import GraphDatabase
import config

# -----------------------------
# Config
# -----------------------------
EMBED_MODEL = "all-MiniLM-L6-v2"
CHAT_MODEL = "llama-3.3-70b-versatile"
TOP_K = 5

INDEX_NAME = config.PINECONE_INDEX_NAME

# -----------------------------
# Initialize clients
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
client = Groq(api_key=config.GROQ_API_KEY)
pc = Pinecone(api_key=config.PINECONE_API_KEY)

# Updated to match new Pinecone client method
existing_indexes = [index.name for index in pc.list_indexes()]

# Connect to Pinecone index
if INDEX_NAME not in existing_indexes:
    print(f"Creating managed index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=config.PINECONE_VECTOR_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud=config.PINECONE_CLOUD, region=config.PINECONE_ENV)
    )

index = pc.Index(INDEX_NAME)

# Connect to Neo4j
driver = GraphDatabase.driver(
    config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
)

# -----------------------------
# Helper functions
# -----------------------------
def embed_text(text: str) -> List[float]:
    embeddings = model.encode(text, convert_to_numpy=True)
    return embeddings.tolist()

def pinecone_query(query_text: str, top_k=TOP_K):
    """Query Pinecone index using embedding."""
    vec = embed_text(query_text)
    res = index.query(
        vector=vec,
        top_k=top_k,
        include_metadata=True,
        include_values=False
    )
    return res["matches"]

def fetch_graph_context(node_ids: List[str], neighborhood_depth=1):
    """Fetch neighboring nodes from Neo4j."""
    facts = []
    with driver.session(database=config.NEO4J_DATABASE) as session:
        for nid in node_ids:
            q = (
                "MATCH (n:Entity {id:$nid})-[r]-(m:Entity) "
                "RETURN type(r) AS rel, labels(m) AS labels, m.id AS id, "
                "m.name AS name, m.type AS type, m.description AS description "
                "LIMIT 10"
            )
            recs = session.run(q, nid=nid)
            for r in recs:
                facts.append({
                    "source": nid,
                    "rel": r["rel"],
                    "target_id": r["id"],
                    "target_name": r["name"],
                    "target_desc": (r["description"] or "")[:400],
                    "labels": r["labels"]
                })
    return facts

def build_prompt(user_query, pinecone_matches, graph_facts):
    """Build a chat prompt combining vector DB matches and graph facts."""
    system = (
        "You are a knowledgeable and helpful travel assistant. "
        "Use the provided vector database results and graph-based knowledge "
        "to give accurate, well-structured, and locally relevant answers. "
        "Think step-by-step before answering (chain-of-thought reasoning). "
        "If the user query involves a multi-day plan, naturally organize information by days or steps. "
        "Structure your response clearly. Include practical tips, recommendations, or local insights when relevant. "
        "Prioritize coherence, factual correctness, and concise phrasing."
    )

    vec_context = []
    for m in pinecone_matches:
        meta = m["metadata"]
        score = m.get("score", None)
        snippet = f"- id: {m['id']}, name: {meta.get('name','')}, type: {meta.get('type','')}, score: {score}"
        if meta.get("city"):
            snippet += f", city: {meta.get('city')}"
        vec_context.append(snippet)

    graph_context = [
        f"- ({f['source']}) -[{f['rel']}]-> ({f['target_id']}) {f['target_name']}: {f['target_desc']}"
        for f in graph_facts
    ]

    prompt = [
        {"role": "system", "content": system},
        {"role": "user", "content":
         f"User query:\n{user_query}\n\n"
            "Context from vector database (most relevant snippets):\n"
            + "\n".join(vec_context[:10]) + "\n\n"
            "Related graph facts (entities and relationships):\n"
            + "\n".join(graph_context[:20]) + "\n\n"
            "Answer the user's query using the above context. Think step by step."}
    ]
    return prompt

def call_chat(prompt_messages):
    """Call Groq LLaMA chat model."""
    resp: ChatCompletion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=prompt_messages,
        max_tokens=600,
        temperature=0.2
    )
    return resp.choices[0].message.content

def search_summary(query, top_k):
    matches = pinecone_query(query, top_k=top_k)
    match_ids = [m["id"] for m in matches]
    graph_facts = fetch_graph_context(match_ids)
    return matches, graph_facts

# -----------------------------
# Interactive chat
# -----------------------------
def interactive_chat():
    print("Hello I'm Atlas your hybrid travel assistant.")
    while True:
        query = input("\nEnter your travel question or type 'exit' to quit: ").strip()
        if not query or query.lower() in ("exit","quit"):
            break       
        matches, graph_facts = search_summary(query, top_k=TOP_K)
        prompt = build_prompt(query, matches, graph_facts)
        answer = call_chat(prompt)
        print("\n=== Assistant Answer ===\n")
        print(answer)
        print("\n=== Hope that helps! Ready to explore the next idea whenever you are. ===\n")

if __name__ == "__main__":
    interactive_chat()
