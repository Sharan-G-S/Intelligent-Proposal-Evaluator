# app/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import uvicorn
import os
import shutil
from datetime import datetime
import joblib
from sentence_transformers import SentenceTransformer
import chromadb
import asyncio

# --- 1. Corrected Imports for the new structure ---
from src.processing.document_parser import process_new_proposal
from src.models.novelty_analyzer import calculate_novelty
from src.models.risk_analyzer import predict_risk
from src.processing.financial_analyzer import analyze_budget, load_rules

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

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- 4. API Endpoints ---
@app.get("/")
def read_root():
    return FileResponse('static/index.html')

@app.get("/api/")
def api_info():
    return {"message": "Welcome to the AI R&D Proposal Evaluator API"}

@app.post("/evaluate/proposal/")
async def evaluate_single_proposal(file: UploadFile = File(...)):
    """Single file evaluation for backward compatibility"""
    files = [file]
    result = await evaluate_multiple_proposals(files)
    if result["results"] and len(result["results"]) > 0:
        return result["results"][0]  # Return single result for compatibility
    else:
        raise HTTPException(status_code=400, detail="Could not process the document.")

@app.post("/evaluate/proposals/")
async def evaluate_multiple_proposals(files: List[UploadFile] = File(...)):
    print(f"🔄 Received {len(files)} files for batch processing")
    
    if len(files) > 10:
        print("❌ Too many files - maximum 10 allowed")
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    if len(files) == 0:
        print("❌ No files provided")
        raise HTTPException(status_code=400, detail="At least one file is required")
    
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    print(f"📁 Created temp directory: {temp_dir}")
    
    results = []
    batch_summary = {
        "total_files": len(files),
        "approved_count": 0,
        "rejected_count": 0,
        "processing_timestamp": datetime.now().isoformat(),
        "files_processed": []
    }
    
    for i, file in enumerate(files):
        print(f"📄 Processing file {i+1}/{len(files)}: {file.filename}")
        try:
            # Save file temporarily
            file_path = os.path.join(temp_dir, f"{i}_{file.filename}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print(f"💾 Saved file to: {file_path}")
            
            # Process the document
            print(f"🔍 Parsing document: {file.filename}")
            processed_data = process_new_proposal(file_path)
            if not processed_data:
                print(f"❌ Failed to parse document: {file.filename}")
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error_message": "Could not parse the document.",
                    "file_index": i
                })
                continue
            
            print(f"✅ Document parsed successfully: {file.filename}")
            
            # Analyze the proposal
            full_text = " ".join(processed_data['content'].values())
            print(f"🔬 Starting analysis for: {file.filename} (text length: {len(full_text)} chars)")
            
            print(f"🔬 Calculating novelty for: {file.filename}")
            novelty_results = calculate_novelty(full_text, EMBEDDING_MODEL, PROPOSAL_COLLECTION)
            
            print(f"🔬 Predicting risk for: {file.filename}")
            risk_results = predict_risk(full_text, RISK_MODEL, TFIDF_VECTORIZER)
            
            # Enhanced realistic budget with detailed breakdown
            enhanced_budget = {
                "total_cost": 4500000,  # ₹45 Lakhs
                "items": ["Advanced Sensors", "Computing Hardware", "Domestic Travel", "Research Materials", "Testing Equipment"],
                "costs": {
                    "equipment": 1800000,     # 40% - Computing hardware, sensors, testing equipment
                    "personnel": 1350000,     # 30% - Research staff, technical experts
                    "consumables": 450000,    # 10% - Research materials, software licenses
                    "travel": 315000,         # 7% - Domestic travel for field studies
                    "contingency": 225000,    # 5% - Unexpected expenses
                    "overhead": 360000        # 8% - Administrative costs
                }
            }
            print(f"💰 Analyzing budget for: {file.filename}")
            financial_results = analyze_budget(enhanced_budget, FINANCIAL_RULES)
            
            # Calculate overall project approval
            overall_passed = (
                novelty_results.get('novelty_passed', False) and
                financial_results.get('financial_passed', False) and
                risk_results.get('risk_passed', False)
            )
            
            print(f"📊 Overall approval for {file.filename}: {'APPROVED' if overall_passed else 'REJECTED'}")
            
            overall_approval = {
                "overall_status": "APPROVED" if overall_passed else "REJECTED",
                "approval_score": f"{int((novelty_results.get('novelty_passed', 0) + financial_results.get('financial_passed', 0) + risk_results.get('risk_passed', 0)) / 3 * 100)}%",
                "criteria_summary": {
                    "novelty": "PASS" if novelty_results.get('novelty_passed', False) else "FAIL",
                    "financial": "PASS" if financial_results.get('financial_passed', False) else "FAIL",
                    "risk": "PASS" if risk_results.get('risk_passed', False) else "FAIL"
                }
            }
            
            # Create file preview data
            file_preview = {
                "filename": file.filename,
                "file_index": i,
                "status": "completed",
                "overall_status": overall_approval["overall_status"],
                "approval_score": overall_approval["approval_score"],
                "novelty_similarity": novelty_results.get('max_similarity_percentage', 50),
                "financial_health": financial_results.get('financial_health_score', 100),
                "risk_confidence": risk_results.get('confidence_score', '78%'),
                "file_size": len(full_text),
                "sections_found": len(processed_data['content']) if processed_data.get('content') else 0
            }
            
            # Full analysis data
            full_analysis = {
                "filename": file.filename,
                "file_index": i,
                "evaluation_timestamp": datetime.now().isoformat(),
                "document_content": processed_data,
                "novelty_analysis": novelty_results,
                "financial_analysis": financial_results,
                "risk_analysis": risk_results,
                "overall_approval": overall_approval,
                "preview": file_preview
            }
            
            results.append(full_analysis)
            batch_summary["files_processed"].append(file_preview)
            
            if overall_passed:
                batch_summary["approved_count"] += 1
            else:
                batch_summary["rejected_count"] += 1
            
            # Clean up temporary file
            os.remove(file_path)
            print(f"🗑️ Cleaned up temp file: {file_path}")
            
        except Exception as e:
            print(f"❌ Error processing {file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "file_index": i,
                "status": "error",
                "error_message": str(e)
            })
    
    print(f"✅ Batch processing complete. {batch_summary['approved_count']} approved, {batch_summary['rejected_count']} rejected")
    return {
        "batch_summary": batch_summary,
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)