# download_model.py
from sentence_transformers import SentenceTransformer

print("--- Starting model download ---")
print("This may take a few minutes depending on your internet speed...")

# This line will download the model and save it to a local cache
SentenceTransformer('all-MiniLM-L6-v2')

print("--- Model download complete! ---")