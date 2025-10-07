# main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import os
import shutil
from datetime import datetime

# Import the main functions from our modules
from src.processing.document_parser import process_new_proposal
from src.models.novelty_analyzer import calculate_novelty # Removed embed_knowledge_base
from src.processing.financial_analyzer import analyze_budget, load_rules

# --- 1. Initialize the FastAPI App ---
app = FastAPI(
    title="AI R&D Proposal Evaluator",
    description="An AI-powered system to automate the evaluation of R&D proposals."
)

# --- 2. Load Rules at Startup ---
financial_rules = {}

@app.on_event("startup")
def load_on_startup():
    """Load only the lightweight components when the API starts."""
    print("--- Application starting up ---")
    global financial_rules
    print("Loading financial rules...")
    financial_rules = load_rules()
    print("--- Application startup complete ---")


# --- 3. Define Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI R&D Proposal Evaluator API"}

@app.post("/evaluate/proposal/")
async def evaluate_proposal(file: UploadFile = File(...)):
    # ... (This function remains the same as your previous working version) ...
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    processed_data = process_new_proposal(file_path)
    if not processed_data:
        raise HTTPException(status_code=400, detail="Could not parse the document.")

    full_text = " ".join(processed_data['content'].values())
    novelty_results = calculate_novelty(full_text)
    
    mock_budget = {
        "filename": file.filename, "total_cost": 3000000,
        "costs": { "equipment": 900000, "travel": 250000, "consumables": 1500000, "contingency": 50000 },
        "items": [ "Sensors", "Domestic Travel" ]
    }
    financial_results = analyze_budget(mock_budget, financial_rules)

    risk_results = {"risk_score": 0.65, "status": "Medium Risk (Placeholder)"}

    os.remove(file_path)

    return {
        "filename": file.filename,
        "evaluation_timestamp": datetime.now().isoformat(),
        "ingestion_summary": processed_data,
        "novelty_analysis": novelty_results,
        "financial_analysis": financial_results,
        "risk_analysis": risk_results
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)