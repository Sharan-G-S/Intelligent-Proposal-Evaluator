# src/models/novelty_analyzer.py

import chromadb
import os
import json
from sentence_transformers import SentenceTransformer

# --- Database Setup ---
DB_PATH = "vector_db"
client = chromadb.PersistentClient(path=DB_PATH)

# --- AI Model Setup ---
# We will use a powerful and efficient model from Hugging Face.
# The first time this script runs, it will download the model (might take a minute).
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Get or create the collection.
collection = client.get_or_create_collection(name="proposals")


def embed_knowledge_base():
    """
    Loads the knowledge base, creates embeddings for each project's text,
    and stores them in the ChromaDB collection.
    """
    print("--- Starting Knowledge Base Embedding Process ---")
    
    # Check if the collection is already populated to avoid re-embedding.
    if collection.count() > 0:
        print("Collection is already populated. Skipping embedding process.")
        return

    # Load our processed data
    try:
        with open('data/processed/knowledge_base.json', 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        print(f"Loaded {len(knowledge_base)} projects from knowledge_base.json")
    except FileNotFoundError:
        print("Error: knowledge_base.json not found. Please run the processing script from Phase 0.")
        return

    # Prepare data for ChromaDB
    documents_to_embed = []
    metadatas_to_store = []
    ids_to_store = []

    for project in knowledge_base:
        # The text that will be converted into a vector
        documents_to_embed.append(project['full_text'])
        
        # Additional data we want to store alongside the vector
        metadatas_to_store.append({
            "title": project['project_title'],
            "agency": project['implementing_agency'],
            "year": project['year']
        })
        
        # A unique ID for each entry
        ids_to_store.append(project['project_id'])

    print(f"Preparing to embed {len(documents_to_embed)} documents...")

    # Create embeddings for all documents at once (this is very efficient)
    embeddings = embedding_model.encode(documents_to_embed).tolist()
    print("Embeddings created successfully.")

    # Add the data to the ChromaDB collection
    collection.add(
        embeddings=embeddings,
        documents=documents_to_embed,
        metadatas=metadatas_to_store,
        ids=ids_to_store
    )
    print("Successfully added all projects to the vector database.")


# --- Main block to run the embedding process ---
if __name__ == '__main__':
    embed_knowledge_base()
    
    print("\n--- Verification ---")
    count = collection.count()
    print(f"Current number of items in collection: {count}")
    if count == 11:
        print("Verification successful: All 11 projects are in the database.")
    else:
        print("Verification failed: The number of items is not 11.")