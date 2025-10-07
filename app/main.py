# app/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import os
import shutil
from datetime import datetime
import joblib
from sentence_transformers import SentenceTransformer
import chromadb

# --- 1. Corrected Imports for the new structure ---
from app.src.processing.document_parser import process_new_proposal
from app.src.models.novelty_analyzer import calculate_novelty
from app.src.models.risk_analyzer import predict_risk
from app.src.processing.financial_analyzer import analyze_budget, load_rules

# --- 2. Load all models and data ONCE at the start ---
print("--- Server is starting: Loading all models and data... ---")

FINANCIAL_RULES = load_rules('financial_rules.yaml')
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
db_client = chromadb.PersistentClient(path="vector_db")
PROPOSAL_COLLECTION = db_client.get_or_create_collection(name="proposals")
RISK_MODEL = joblib.load("trained_models/risk_model.joblib")
TFIDF_VECTORIZER = joblib.load("trained_models/tfidf_vectorizer.joblib")

print("--- All models loaded. API is ready. ---")

# --- 3. Initialize the FastAPI App ---
app = FastAPI(title="AI R&D Proposal Evaluator")

# --- 4. API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI R&D Proposal Evaluator API"}

@app.post("/evaluate/proposal/")
async def evaluate_proposal(file: UploadFile = File(...)):
    # ... (The rest of this function is exactly the same) ...
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    processed_data = process_new_proposal(file_path)
    if not processed_data:
        raise HTTPException(status_code=400, detail="Could not parse the document.")
    full_text = " ".join(processed_data['content'].values())
    novelty_results = calculate_novelty(full_text, EMBEDDING_MODEL, PROPOSAL_COLLECTION)
    risk_results = predict_risk(full_text, RISK_MODEL, TFIDF_VECTORIZER)
    mock_budget = { "total_cost": 3000000, "items": ["Sensors", "Domestic Travel"], "costs": { "equipment": 900000, "contingency": 50000 } }
    financial_results = analyze_budget(mock_budget, FINANCIAL_RULES)
    os.remove(file_path)
    return {
        "filename": file.filename, "evaluation_timestamp": datetime.now().isoformat(),
        "novelty_analysis": novelty_results, "financial_analysis": financial_results,
        "risk_analysis": risk_results
    }