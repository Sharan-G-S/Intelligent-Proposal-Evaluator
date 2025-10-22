#!/usr/bin/env python3

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, 'app')

# Import and run the FastAPI app
from main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting AI R&D Proposal Evaluator Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)