# src/models/novelty_analyzer.py

import chromadb
import os
import json
from sentence_transformers import SentenceTransformer

# --- Database Setup ---
DB_PATH = "vector_db"
client = chromadb.PersistentClient(path=DB_PATH)

# --- AI Model Setup ---
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
collection = client.get_or_create_collection(name="proposals")


def embed_knowledge_base():
    """
    Loads the knowledge base and stores project embeddings in ChromaDB.
    """
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
    
    collection.add(
        embeddings=embeddings,
        documents=documents_to_embed,
        metadatas=metadatas_to_store,
        ids=ids_to_store
    )
    print("Successfully embedded and stored the knowledge base.")


def calculate_novelty(new_proposal_text: str, n_results: int = 3) -> dict:
    """
    Calculates the novelty of a new proposal by comparing it against the knowledge base.
    """
    print(f"\n--- Calculating Novelty for New Proposal ---")
    
    # Step 1: Create an embedding for the new text
    new_embedding = embedding_model.encode(new_proposal_text).tolist()
    
    # Step 2: Query the collection to find the 'n' most similar results
    results = collection.query(
        query_embeddings=[new_embedding],
        n_results=n_results
    )
    
    # Step 3: Extract the distances and metadata
    # ChromaDB's distance is L2 squared. Lower distance = more similar.
    distances = results['distances'][0]
    metadatas = results['metadatas'][0]
    ids = results['ids'][0]
    
    # Step 4: Calculate a novelty score. We'll define novelty as the distance
    # to the single closest match. A higher score means more novel.
    # We round it for readability.
    novelty_score = round(distances[0], 4) if distances else -1

    print(f"Novelty Score (distance to closest match): {novelty_score}")
    print("Most similar projects found:")
    for i in range(len(ids)):
        print(f"  - ID: {ids[i]}, Title: \"{metadatas[i]['title']}\", Distance: {round(distances[i], 4)}")
        
    return {
        "novelty_score": novelty_score,
        "similar_projects": [
            {"id": ids[i], "title": metadatas[i]['title'], "distance": distances[i]} for i in range(len(ids))
        ]
    }

# --- Main block to run the full process ---
if __name__ == '__main__':
    # First, ensure the knowledge base is embedded in the DB
    embed_knowledge_base()
    print(f"\nTotal items in collection: {collection.count()}")
    print("\nLow novelty score means Red flag (similar to existing projects).")
    
    # Now, test the novelty calculation with a sample text.
    # This text is intentionally similar to MOC_01 to test the search.
    sample_text = """
    This research proposes the development of an intelligent shovel bucket for use in mining.
    By using sensors, data analytics, and machine learning, we aim to improve the efficiency
    and safety of excavation. The smart bucket will monitor digging forces and wear in real-time.
    """
    
    novelty_results = calculate_novelty(sample_text)