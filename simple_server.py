#!/usr/bin/env python3

import http.server
import socketserver
import json
import cgi
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import random

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='static', **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('static/index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path == '/api/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"message": "Simple Server - AI R&D Proposal Evaluator API"}
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/evaluate/proposal/':
            self.handle_single_file()
        elif self.path == '/evaluate/proposals/':
            self.handle_multiple_files()
        else:
            self.send_error(404, "Not Found")
    
    def handle_single_file(self):
        try:
            # Parse multipart form data safely
            content_type = self.headers.get('content-type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Expected multipart/form-data")
                return
            
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "No file data received")
                return
            
            # Read and process the uploaded data
            post_data = self.rfile.read(content_length)
            
            # Extract filename from headers or use default
            boundary_match = None
            if 'boundary=' in content_type:
                boundary = content_type.split('boundary=')[1].split(';')[0].strip()
                # Simple filename extraction from multipart data
                data_str = post_data.decode('utf-8', errors='ignore')
                if 'filename=' in data_str:
                    try:
                        filename_start = data_str.find('filename="') + 10
                        filename_end = data_str.find('"', filename_start)
                        if filename_start > 9 and filename_end > filename_start:
                            filename = data_str[filename_start:filename_end]
                        else:
                            filename = f"uploaded_file_{random.randint(1000, 9999)}.txt"
                    except:
                        filename = f"uploaded_file_{random.randint(1000, 9999)}.txt"
                else:
                    filename = f"uploaded_file_{random.randint(1000, 9999)}.txt"
            else:
                filename = f"uploaded_file_{random.randint(1000, 9999)}.txt"
            
            print(f"📄 Processing file: {filename} ({len(post_data)} bytes)")
            
            # Validate file size
            if len(post_data) < 100:  # Too small to be a valid document
                self.send_error(400, "File appears to be empty or too small")
                return
            
            if len(post_data) > 10 * 1024 * 1024:  # > 10MB
                self.send_error(400, "File too large (max 10MB)")
                return
            
            # Generate comprehensive analysis
            result = self.generate_mock_analysis(filename)
            result["processing_status"] = "SUCCESS"
            result["file_size_bytes"] = len(post_data)
            result["upload_timestamp"] = datetime.now().isoformat()
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())
            
            print(f"✅ Successfully processed {filename}")
            
        except Exception as e:
            print(f"❌ Error in handle_single_file: {e}")
            
            # Send detailed error response
            error_response = {
                "error": "Analysis failed",
                "details": f"Load failed. Please check the file format and try again. Error: {str(e)}",
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
                "suggestions": [
                    "Ensure file is not corrupted",
                    "Try with a smaller file size",
                    "Check that file format is supported (TXT, PDF, DOCX)",
                    "Verify file encoding is UTF-8 for text files"
                ]
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, indent=2).encode())
    
    def handle_multiple_files(self):
        try:
            # Parse multipart form data for multiple files
            content_type = self.headers.get('content-type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Expected multipart/form-data for multiple files")
                return
            
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "No file data received")
                return
            
            post_data = self.rfile.read(content_length)
            print(f"📦 Received batch upload: {len(post_data)} bytes")
            
            # For multiple files, simulate processing 2-5 files based on data size
            estimated_files = min(max(2, len(post_data) // 50000), 10)  # Estimate based on data size
            file_count = random.randint(max(1, estimated_files-1), estimated_files+1)
            
            print(f"🔄 Processing estimated {file_count} files from upload")
            
            results = []
            
            for i in range(file_count):
                filename = f"proposal_{i+1}.txt"
                print(f"📄 Processing file {i+1}: {filename}")
                
                try:
                    analysis = self.generate_mock_analysis(filename)
                    analysis["file_index"] = i
                    analysis["processing_status"] = "SUCCESS"
                    analysis["batch_position"] = f"{i+1}/{file_count}"
                    
                    # Create preview data
                    file_preview = {
                        "filename": filename,
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
                    print(f"✅ Processed {filename}: {analysis['overall_approval']['overall_status']}")
                    
                except Exception as e:
                    print(f"❌ Error processing file {i+1}: {e}")
                    error_result = {
                        "filename": filename,
                        "file_index": i,
                        "status": "error",
                        "error_message": f"Processing failed: {str(e)}",
                        "processing_status": "FAILED"
                    }
                    results.append(error_result)
            
            # Create batch summary
            successful_results = [r for r in results if r.get("status") != "error"]
            batch_summary = {
                "total_files": file_count,
                "approved_count": sum(1 for r in successful_results if r.get("overall_approval", {}).get("overall_status") == "APPROVED"),
                "rejected_count": sum(1 for r in successful_results if r.get("overall_approval", {}).get("overall_status") == "REJECTED"),
                "error_count": len(results) - len(successful_results),
                "processing_timestamp": datetime.now().isoformat(),
                "upload_size_bytes": len(post_data),
                "files_processed": [r.get("preview", {}) for r in results if "preview" in r]
            }
            
            response = {
                "batch_summary": batch_summary,
                "results": results,
                "processing_status": "BATCH_SUCCESS"
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
            print(f"✅ Batch complete: {batch_summary['approved_count']} approved, {batch_summary['rejected_count']} rejected")
            
        except Exception as e:
            print(f"❌ Error in handle_multiple_files: {e}")
            
            # Send detailed error response
            error_response = {
                "error": "Batch analysis failed",
                "details": f"Load failed during batch processing. Please check file formats and try again. Error: {str(e)}",
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
                "suggestions": [
                    "Try with fewer files (maximum 10)",
                    "Ensure all files are valid and not corrupted",
                    "Check total upload size is under 50MB",
                    "Verify all files are supported formats"
                ]
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, indent=2).encode())
    
    def generate_mock_analysis(self, filename):
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

def main():
    PORT = 8000
    handler = CustomHTTPRequestHandler
    
    print("🚀 Starting Simple HTTP Server - AI R&D Proposal Evaluator...")
    print("📝 Note: This is a demo mode with mock analysis results")
    print(f"🌐 Server will be available at: http://localhost:{PORT}")
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"✅ Server started successfully on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")

if __name__ == "__main__":
    main()