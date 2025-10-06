# src/models/novelty_analyzer.py

import chromadb
import os

# --- Database Setup ---
# Define the path where the database will be stored
DB_PATH = "vector_db"

# Create a persistent client. This will save the database to the specified path.
# If the directory doesn't exist, it will be created.
client = chromadb.PersistentClient(path=DB_PATH)

# Get or create a collection named "proposals".
# A collection is like a table in a traditional database.
collection = client.get_or_create_collection(name="proposals")


# --- Main block for testing the setup ---
if __name__ == '__main__':
    print("--- Running Novelty Analyzer Setup ---")
    
    # The setup happens when the script is imported, so we just need to confirm.
    print(f"ChromaDB client initialized. Using database at: {os.path.abspath(DB_PATH)}")
    print(f"Collection '{collection.name}' is ready.")
    
    # We can check the number of items in the collection (it should be 0 for now).
    count = collection.count()
    print(f"Current number of items in collection: {count}")
    
    if count == 0:
        print("Database is empty, which is expected for the first run.")