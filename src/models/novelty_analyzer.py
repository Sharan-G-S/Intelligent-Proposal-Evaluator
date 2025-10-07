# src/models/novelty_analyzer.py

import chromadb
import os
import json
from sentence_transformers import SentenceTransformer

# --- Load the model ONCE when the file is imported ---
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Database Setup ---
DB_PATH = "vector_db"
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="proposals")


def embed_knowledge_base():
    # ... (This function remains the same, but no longer loads the model) ...
    if collection.count() > 0:
        print("Knowledge base is already embedded.")
        return
    try:
        with open('data/processed/knowledge_base.json', 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
    except FileNotFoundError:
        print("Error: knowledge_base.json not found.")
        return
    documents_to_embed = [project['full_text'] for project in knowledge_base]
    metadatas_to_store = [{"title": p['project_title']} for p in knowledge_base]
    ids_to_store = [project['project_id'] for project in knowledge_base]
    embeddings = embedding_model.encode(documents_to_embed).tolist()
    collection.add(embeddings=embeddings, documents=documents_to_embed, metadatas=metadatas_to_store, ids=ids_to_store)
    print("Successfully embedded and stored the knowledge base.")


def calculate_novelty(new_proposal_text: str, n_results: int = 3) -> dict:
    # ... (This function remains the same) ...
    new_embedding = embedding_model.encode(new_proposal_text).tolist()
    results = collection.query(query_embeddings=[new_embedding], n_results=n_results)
    distances = results['distances'][0]
    metadatas = results['metadatas'][0]
    ids = results['ids'][0]
    novelty_score = round(distances[0], 4) if distances else -1
    return {
        "novelty_score": novelty_score,
        "similar_projects": [{"id": ids[i], "title": metadatas[i]['title'], "distance": distances[i]} for i in range(len(ids))]
    }