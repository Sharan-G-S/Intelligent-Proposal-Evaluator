# 🧠 AI R&D Proposal Evaluator

**Team Zenith 07**  
*Smart India Hackathon 2025 - Problem Statement #25180*

---

## 📋 Overview

An intelligent AI-powered system for evaluating Research & Development proposals using advanced machine learning, natural language processing, and financial analysis techniques. The system provides comprehensive evaluation across novelty, financial viability, and risk assessment criteria.

### 🎯 Key Features

- **Automated Proposal Analysis**: Upload research proposals in TXT, PDF, or DOCX format
- **Novelty Detection**: Identifies similar existing projects using semantic similarity analysis
- **Financial Evaluation**: Comprehensive budget analysis with compliance checking
- **Risk Assessment**: ML-based prediction of project success probability
- **Batch Processing**: Evaluate multiple proposals simultaneously
- **Interactive Dashboard**: Real-time visualization of evaluation results
- **Detailed Reporting**: Comprehensive analysis with optimization recommendations

---

## 🏗️ System Architecture

```
intelligent-proposal-evaluator/
├── app/
│   ├── main.py                 # FastAPI main application
│   └── src/
│       ├── models/             # ML models (novelty, risk analysis)
│       └── processing/         # Document parsing and analysis
├── static/
│   └── index.html             # Frontend interface
├── data/
│   ├── raw/                   # Sample proposals
│   └── processed/             # Processed knowledge base
├── trained_models/            # Pre-trained ML models
├── simple_server.py           # Lightweight demo server
├── quick_server.py            # Fast mock analysis server
├── run_server.py              # Main server launcher
└── requirements.txt           # Python dependencies
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 4GB+ RAM recommended

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd intelligent-proposal-evaluator
```

2. **Create virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

#### Option 1: Simple Demo Server (Recommended for Quick Testing)
```bash
python3 simple_server.py
```

#### Option 2: Quick Mock Server
```bash
python3 quick_server.py
```

#### Option 3: Full Server with ML Models
```bash
python3 run_server.py
```

**Access the application**: Open your browser and navigate to `http://localhost:8000`

---

## 📊 Usage Guide

### Single File Analysis

1. Click **"Choose Files"** or drag and drop a proposal document
2. Select a single `.txt`, `.pdf`, or `.docx` file
3. Wait for processing (typically 2-5 seconds)
4. View comprehensive analysis results:
   - Document Analysis
   - Novelty Assessment
   - Financial Evaluation
   - Risk Analysis
   - Overall Approval Decision

### Batch Analysis

1. Select multiple files (up to 10)
2. Click **"Analyze All Files"**
3. View batch summary with:
   - Total files processed
   - Approved/Rejected counts
   - Average scores
4. Click on individual files for detailed results

### Test Functions

- **Test with Mock Data**: Quick demo with 3 sample proposals
- **Test Detailed Analysis**: View comprehensive analysis for a single mock proposal

---

## 🔬 Evaluation Criteria

### 1. Novelty Analysis (Innovation Assessment)
- **Similarity Detection**: Compares against existing projects database
- **Threshold**: <50% similarity = NOVEL, ≥50% = SIMILAR
- **Output**: Uniqueness percentage, similar projects list

### 2. Financial Analysis (Budget Compliance)
- **Budget Breakdown**: Equipment, Personnel, Travel, Consumables, etc.
- **Compliance Rules**: Validates against predefined financial rules
- **Health Score**: 0-100 scale (≥75 = PASS)
- **Optimization Tips**: Smart recommendations for cost reduction

### 3. Risk Assessment (Success Prediction)
- **ML-Based Prediction**: Trained on historical proposal data
- **Confidence Score**: 0-100% (≥65% = PASS)
- **Risk Level**: HIGH/MEDIUM/LOW classification

### Overall Approval
- **Criteria**: All three evaluations must PASS
- **Score**: Weighted average of all components
- **Decision**: APPROVED / REJECTED with detailed reasoning

---

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern web framework for APIs
- **Python 3.12**: Core programming language
- **scikit-learn**: Machine learning models
- **SentenceTransformer**: NLP for novelty detection
- **ChromaDB**: Vector database for similarity search
- **PyMuPDF**: PDF document processing
- **python-docx**: DOCX document processing

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript (Vanilla)**: Interactive user interface
- **Font Awesome**: Icon library
- **Google Fonts**: Typography

### Data Processing
- **YAML**: Configuration management
- **JSON**: Data interchange
- **joblib**: Model serialization

---

## 📁 Project Structure Details

### Key Files

- **`simple_server.py`**: Lightweight HTTP server with mock analysis (best for demos)
- **`quick_server.py`**: FastAPI server with instant mock results
- **`run_server.py`**: Full production server with ML models
- **`app/main.py`**: Main FastAPI application with complete processing pipeline
- **`financial_rules.yaml`**: Budget compliance rules configuration
- **`requirements.txt`**: Python package dependencies

### Models & Data

- **`trained_models/`**: Pre-trained risk assessment models
  - `risk_model.joblib`: Logistic regression classifier
  - `tfidf_vectorizer.joblib`: Text vectorizer
- **`data/raw/proposals/`**: Sample proposal documents
- **`data/processed/`**: Knowledge base for novelty detection
- **`vector_db/`**: ChromaDB vector embeddings

---

## 🎨 Features in Detail

### Real-time Processing
- Asynchronous file upload handling
- Progress indicators during analysis
- Instant feedback on errors

### Comprehensive Error Handling
- File validation (size, format, encoding)
- Graceful fallback for processing issues
- Detailed error messages with troubleshooting tips

### Responsive Design
- Mobile-friendly interface
- Grid-based layout for results
- Color-coded status indicators
- Interactive cards with hover effects

### Advanced Analytics
- Semantic similarity using sentence transformers
- Financial health scoring algorithm
- ML-based risk prediction
- Multi-criteria decision making

---

## 📝 API Documentation

### Endpoints

#### `GET /`
- **Description**: Serves the main web interface
- **Response**: HTML page

#### `GET /api/`
- **Description**: API information
- **Response**: JSON with API details

#### `POST /evaluate/proposal/`
- **Description**: Evaluate a single proposal
- **Request**: Multipart form data with `file` field
- **Response**: JSON with comprehensive analysis
- **Example**:
```bash
curl -X POST "http://localhost:8000/evaluate/proposal/" \
  -F "file=@proposal.txt"
```

#### `POST /evaluate/proposals/`
- **Description**: Batch evaluate multiple proposals
- **Request**: Multipart form data with `files` field (max 10 files)
- **Response**: JSON with batch summary and individual results
- **Example**:
```bash
curl -X POST "http://localhost:8000/evaluate/proposals/" \
  -F "files=@proposal1.txt" \
  -F "files=@proposal2.txt"
```

---

## 🔧 Configuration

### Financial Rules (`financial_rules.yaml`)
Customize budget validation rules:
- Maximum budget limits
- Cost distribution requirements
- Category-specific constraints
- Compliance thresholds

### Model Configuration
Adjust ML model parameters in `app/main.py`:
- Similarity thresholds
- Risk prediction confidence levels
- Scoring weights

---

## 🧪 Testing

### Manual Testing
1. Use provided sample proposals in `data/raw/proposals/content/`
2. Click "Test with Mock Data" button for instant demo
3. Upload your own proposal documents

### API Testing
```bash
# Test single file
curl -X POST "http://localhost:8000/evaluate/proposal/" \
  -F "file=@data/raw/proposals/content/MOC_01.txt" | jq .

# Test API health
curl http://localhost:8000/api/
```

---

## 📦 Dependencies

### Core Requirements
```
fastapi>=0.104.1
uvicorn>=0.24.0
python-multipart>=0.0.6
sentence-transformers>=2.2.2
chromadb>=0.4.18
scikit-learn>=1.3.0
PyMuPDF>=1.23.0
python-docx>=1.1.0
PyYAML>=6.0
joblib>=1.3.2
```

See `requirements.txt` for complete list.

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Load failed" error  
**Solution**: Ensure file is valid, not corrupted, and under 10MB

**Issue**: Port 8000 already in use  
**Solution**: 
```bash
lsof -ti:8000 | xargs kill -9
```

**Issue**: sklearn version warnings  
**Solution**: Upgrade scikit-learn:
```bash
pip install --upgrade scikit-learn
```

**Issue**: Import errors  
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 🚀 Deployment

### Production Deployment

1. **Set environment variables**
```bash
export PORT=8000
export HOST=0.0.0.0
```

2. **Run with gunicorn**
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

3. **Docker deployment**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "run_server.py"]
```

---

## 👥 Team Zenith 07

**Smart India Hackathon 2025**  
Problem Statement: #25180 - AI-Powered R&D Proposal Evaluation System

### Team Members
- [Add team member names]
- [Add team member names]
- [Add team member names]

### Mentors
- [Add mentor names]

---

## 📄 License

[Add your license information]

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

For issues, questions, or suggestions:
- Create an issue in the repository
- Contact Team Zenith 07

---

## 🙏 Acknowledgments

- Smart India Hackathon 2025 organizers
- All mentors and supporters
- Open-source community for excellent libraries

---

**Built with ❤️ by Team Zenith 07**

*Last Updated: October 2025*
