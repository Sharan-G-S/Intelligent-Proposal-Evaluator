#!/usr/bin/env python3

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import os
import shutil
from datetime import datetime
import random

# Create FastAPI app with minimal configuration to avoid middleware issues
app = FastAPI(
    title="AI R&D Proposal Evaluator - Quick Mode",
    description="Quick demo mode with mock analysis results",
    version="1.0.0"
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

@app.get("/api/")
def api_info():
    return {"message": "Quick Mode - AI R&D Proposal Evaluator API"}

def generate_mock_analysis(filename):
    """Generate mock analysis results for quick demo"""
    # Random but realistic scores
    novelty_score = random.randint(30, 85)
    financial_score = random.randint(70, 95)
    risk_score = random.randint(60, 90)
    
    novelty_passed = novelty_score >= 60
    financial_passed = financial_score >= 75
    risk_passed = risk_score >= 65
    
    overall_passed = novelty_passed and financial_passed and risk_passed
    overall_score = (novelty_score + financial_score + risk_score) // 3
    
    return {
        "filename": filename,
        "evaluation_timestamp": datetime.now().isoformat(),
        "content": {
            "title": f"Research Proposal from {filename}",
            "abstract": "Mock analysis - AI-based research proposal evaluation",
            "methodology": "Advanced computational analysis",
            "budget": "₹45 Lakhs allocated"
        },
        "novelty_analysis": {
            "max_similarity_percentage": 100 - novelty_score,
            "novelty_status": "NOVEL" if novelty_passed else "SIMILAR",
            "novelty_passed": novelty_passed,
            "similar_projects": [
                {"title": "Similar AI Project 1", "similarity": max(20, 100 - novelty_score - 10)},
                {"title": "Related Research 2", "similarity": max(15, 100 - novelty_score - 15)},
                {"title": "Comparable Study 3", "similarity": max(10, 100 - novelty_score - 20)}
            ]
        },
        "financial_analysis": {
            "financial_passed": financial_passed,
            "financial_health_score": financial_score,
            "rules_analysis": [
                {"rule": "Budget Limit", "status": "PASS" if financial_score > 70 else "FAIL"},
                {"rule": "Cost Distribution", "status": "PASS" if financial_score > 75 else "FAIL"},
                {"rule": "Equipment Costs", "status": "PASS" if financial_score > 80 else "FAIL"}
            ],
            "cost_breakdown": {
                "equipment": {"amount": 1800000, "percentage": "40%"},
                "personnel": {"amount": 1350000, "percentage": "30%"},
                "consumables": {"amount": 450000, "percentage": "10%"},
                "travel": {"amount": 315000, "percentage": "7%"},
                "contingency": {"amount": 225000, "percentage": "5%"},
                "overhead": {"amount": 360000, "percentage": "8%"}
            },
            "optimization_tips": [
                "Consider reducing equipment costs by 10%",
                "Optimize travel budget allocation",
                "Review contingency percentage"
            ]
        },
        "risk_analysis": {
            "risk_passed": risk_passed,
            "confidence_score": f"{risk_score}%",
            "predicted_status": "HIGH CONFIDENCE" if risk_score > 80 else "MODERATE CONFIDENCE"
        },
        "overall_approval": {
            "overall_status": "APPROVED" if overall_passed else "REJECTED",
            "approval_score": f"{overall_score}%",
            "criteria_summary": {
                "novelty": "PASS" if novelty_passed else "FAIL",
                "financial": "PASS" if financial_passed else "FAIL",
                "risk": "PASS" if risk_passed else "FAIL"
            }
        }
    }

@app.post("/evaluate/proposal/")
async def evaluate_single_proposal(file: UploadFile = File(...)):
    """Single file evaluation"""
    print(f"📄 Processing single file: {file.filename}")
    
    # Generate mock analysis instantly
    result = generate_mock_analysis(file.filename)
    print(f"✅ Generated mock analysis for: {file.filename}")
    
    return result

@app.post("/evaluate/proposals/")
async def evaluate_multiple_proposals(files: List[UploadFile] = File(...)):
    """Multiple file evaluation with instant mock results"""
    print(f"🔄 Received {len(files)} files for batch processing")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one file is required")
    
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
        
        # Generate mock analysis instantly
        analysis = generate_mock_analysis(file.filename)
        analysis["file_index"] = i
        
        # Create preview data
        file_preview = {
            "filename": file.filename,
            "file_index": i,
            "status": "completed",
            "overall_status": analysis["overall_approval"]["overall_status"],
            "approval_score": analysis["overall_approval"]["approval_score"],
            "novelty_similarity": analysis["novelty_analysis"]["max_similarity_percentage"],
            "financial_health": analysis["financial_analysis"]["financial_health_score"],
            "risk_confidence": analysis["risk_analysis"]["confidence_score"],
            "file_size": random.randint(5000, 50000),
            "sections_found": random.randint(4, 8)
        }
        
        analysis["preview"] = file_preview
        results.append(analysis)
        batch_summary["files_processed"].append(file_preview)
        
        if analysis["overall_approval"]["overall_status"] == "APPROVED":
            batch_summary["approved_count"] += 1
        else:
            batch_summary["rejected_count"] += 1
        
        print(f"✅ Generated analysis for: {file.filename} - {analysis['overall_approval']['overall_status']}")
    
    print(f"✅ Batch processing complete. {batch_summary['approved_count']} approved, {batch_summary['rejected_count']} rejected")
    
    return {
        "batch_summary": batch_summary,
        "results": results
    }

if __name__ == "__main__":
    print("🚀 Starting Quick Mode AI R&D Proposal Evaluator...")
    print("📝 Note: This is a demo mode with mock analysis results")
    print("🌐 Server will be available at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)