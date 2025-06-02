from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request
import uvicorn
import os
import uuid
import asyncio
from typing import Dict, Any
import logging

from models.document_processor import DocumentProcessor
from models.rag_engine import RAGEngine
from models.redlining_classifier import RedliningClassifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Contract Redlining RAG System",
    description="AI-powered contract analysis and risk assessment tool",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global variables for models (initialized on startup)
document_processor = None
rag_engine = None
redlining_classifier = None

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global document_processor, rag_engine, redlining_classifier
    
    logger.info("Initializing Contract Redlining RAG System...")
    
    try:
        # Initialize components
        document_processor = DocumentProcessor()
        logger.info("✅ Document processor initialized")
        
        rag_engine = RAGEngine()
        logger.info("✅ RAG engine initialized")
        
        redlining_classifier = RedliningClassifier(rag_engine)
        logger.info("✅ Redlining classifier initialized")
        
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        logger.info("🚀 System ready for contract analysis!")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        raise

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a contract document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Read file content
        file_content = await file.read()
        
        # Process document
        logger.info(f"Processing document: {file.filename}")
        processed_doc = document_processor.process_document(file_content, file.filename)
        
        # Add to vector database
        rag_engine.add_document_to_vectordb(processed_doc["chunks"], doc_id)
        
        # Store document metadata
        doc_metadata = {
            "doc_id": doc_id,
            "filename": file.filename,
            "total_chunks": processed_doc["total_chunks"],
            "total_clauses": processed_doc["total_clauses"],
            "word_count": processed_doc["word_count"]
        }
        
        logger.info(f"Document processed successfully: {doc_metadata}")
        
        return JSONResponse({
            "success": True,
            "message": "Document uploaded and processed successfully",
            "doc_id": doc_id,
            "metadata": doc_metadata
        })
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/analyze/{doc_id}")
async def analyze_document(doc_id: str):
    """Analyze document and generate redlined output"""
    try:
        # Get document chunks from vector database
        search_results = rag_engine.semantic_search("contract clause", n_results=100)
        
        if not search_results:
            raise HTTPException(status_code=404, detail="Document not found or no clauses detected")
        
        # Filter clauses for this document
        doc_clauses = [
            result for result in search_results 
            if result["metadata"]["document_id"] == doc_id and result["metadata"]["is_clause"]
        ]
        
        if not doc_clauses:
            raise HTTPException(status_code=404, detail="No clauses found in document")
        
        logger.info(f"Analyzing {len(doc_clauses)} clauses for document {doc_id}")
        
        # Classify all clauses
        clauses_for_classification = [{"text": clause["text"]} for clause in doc_clauses]
        analysis_result = redlining_classifier.classify_document(clauses_for_classification)
        
        # Create redlined HTML
        redlined_html = generate_redlined_html(analysis_result["classified_clauses"])
        
        # Prepare response
        response = {
            "success": True,
            "doc_id": doc_id,
            "analysis": {
                "risk_summary": analysis_result["risk_summary"],
                "risk_percentage": analysis_result["risk_percentage"],
                "overall_risk": analysis_result["overall_risk"],
                "total_clauses": analysis_result["total_clauses"],
                "recommendations": analysis_result["recommendations"]
            },
            "classified_clauses": analysis_result["classified_clauses"],
            "redlined_html": redlined_html
        }
        
        logger.info(f"Analysis completed for document {doc_id}")
        return JSONResponse(response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing document {doc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")

@app.get("/search")
async def search_clauses(query: str, limit: int = 10):
    """Search for similar clauses using semantic search"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        results = rag_engine.semantic_search(query, n_results=limit)
        
        return JSONResponse({
            "success": True,
            "query": query,
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/classify-text")
async def classify_text(request: Dict[str, Any]):
    """Classify a single text clause"""
    try:
        text = request.get("text", "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        classification = redlining_classifier.classify_clause(text)
        
        return JSONResponse({
            "success": True,
            "classification": classification
        })
        
    except Exception as e:
        logger.error(f"Error classifying text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "models_loaded": {
            "document_processor": document_processor is not None,
            "rag_engine": rag_engine is not None,
            "redlining_classifier": redlining_classifier is not None
        }
    })

def generate_redlined_html(classified_clauses):
    """Generate HTML with color-coded clauses"""
    html_parts = []
    
    html_parts.append("""
    <div class="redlined-document">
        <style>
            .risk-red { background-color: #ffebee; border-left: 4px solid #f44336; padding: 8px; margin: 4px 0; }
            .risk-amber { background-color: #fff8e1; border-left: 4px solid #ff9800; padding: 8px; margin: 4px 0; }
            .risk-green { background-color: #e8f5e8; border-left: 4px solid #4caf50; padding: 8px; margin: 4px 0; }
            .clause-text { font-family: 'Times New Roman', serif; line-height: 1.6; }
            .risk-indicator { font-weight: bold; font-size: 0.9em; margin-bottom: 4px; }
            .confidence-score { font-size: 0.8em; color: #666; }
        </style>
    """)
    
    for clause in classified_clauses:
        risk_level = clause["classification"]["risk_level"]
        confidence = clause["classification"]["confidence"]
        explanation = clause["classification"]["explanation"]
        
        css_class = f"risk-{risk_level.lower()}"
        risk_emoji = {"RED": "🔴", "AMBER": "🟡", "GREEN": "🟢"}[risk_level]
        
        html_parts.append(f"""
        <div class="{css_class}">
            <div class="risk-indicator">
                {risk_emoji} {risk_level} RISK 
                <span class="confidence-score">(Confidence: {confidence})</span>
            </div>
            <div class="clause-text">{clause['text']}</div>
            <div style="font-size: 0.85em; color: #555; margin-top: 4px; font-style: italic;">
                {explanation}
            </div>
        </div>
        """)
    
    html_parts.append("</div>")
    
    return "\n".join(html_parts)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 