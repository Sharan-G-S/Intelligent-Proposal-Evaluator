# main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import os
import shutil
from datetime import datetime

# Import the main functions from our modules
from src.processing.document_parser import process_new_proposal
from src.models.novelty_analyzer import calculate_novelty, embed_knowledge_base
# We'll add risk prediction later
from src.processing.financial_analyzer import analyze_budget, load_rules

# --- 1. Initialize the FastAPI App ---
app = FastAPI(
    title="AI R&D Proposal Evaluator",
    description="An AI-powered system to automate the evaluation of R&D proposals."
)

# --- 2. Load Models and Rules at Startup ---
financial_rules = {}

@app.on_event("startup")
def load_on_startup():
    """Load all necessary models and data when the API starts."""
    print("--- Application starting up ---")
    
    global financial_rules
    print("Loading financial rules...")
    financial_rules = load_rules()
    
    print("Ensuring knowledge base is embedded...")
    embed_knowledge_base()
    
    # We will load the risk model here in a later step
    print("--- Application startup complete ---")


# --- 3. Define a Root Endpoint ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI R&D Proposal Evaluator API"}


# --- 4. Define the Main Analysis Endpoint ---
@app.post("/evaluate/proposal/")
async def evaluate_proposal(file: UploadFile = File(...)):
    """
    Accepts a proposal file (PDF or DOCX), processes it, and returns a full evaluation.
    """
    # Create a temporary directory to save the uploaded file
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # --- Run the Full Analysis Pipeline ---
    
    # 1. Ingestion Engine (Phase 1)
    processed_data = process_new_proposal(file_path)
    if not processed_data:
        raise HTTPException(status_code=400, detail="Could not parse the document.")

    # For now, we'll use the full text for novelty and risk analysis
    full_text = " ".join(processed_data['content'].values())
    
    # 2. Novelty Engine (Phase 2)
    novelty_results = calculate_novelty(full_text)
    
    # 3. Financial Engine (Phase 3) - using a placeholder budget
    # In a real app, we would extract this from the text. For now, we use a placeholder.
    mock_budget = {
        "filename": file.filename, "total_cost": 3000000,
        "costs": { "equipment": 900000, "travel": 250000, "consumables": 1500000, "contingency": 50000 },
        "items": [ "Sensors", "Domestic Travel" ]
    }
    financial_results = analyze_budget(mock_budget, financial_rules)

    # 4. Risk Engine (Phase 4) - Placeholder for now
    risk_results = {"risk_score": 0.65, "status": "Medium Risk (Placeholder)"}

    # Clean up the temporary file
    os.remove(file_path)

    # Combine all results into a final response
    return {
        "filename": file.filename,
        "evaluation_timestamp": datetime.now().isoformat(),
        "ingestion_summary": processed_data,
        "novelty_analysis": novelty_results,
        "financial_analysis": financial_results,
        "risk_analysis": risk_results
    }


# --- 5. Main block to run the API ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)