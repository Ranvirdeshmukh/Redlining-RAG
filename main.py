from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request
import uvicorn
import os
import uuid
import asyncio
from typing import Dict, Any, List
import logging
from contextlib import asynccontextmanager

from models.document_processor import DocumentProcessor
from models.rag_engine import RAGEngine
from models.redlining_classifier import RedliningClassifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for models
document_processor = None
rag_engine = None
redlining_classifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Contract Redlining RAG System",
    description="AI-powered contract analysis and risk assessment tool",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

@app.get("/legal-precedents/{clause_text}")
async def get_legal_precedents(clause_text: str, limit: int = 5):
    """Find similar legal precedents for a given clause text"""
    try:
        if not clause_text.strip():
            raise HTTPException(status_code=400, detail="Clause text cannot be empty")
        
        # Find legal precedents
        precedents = rag_engine.find_legal_precedents(clause_text, n_results=limit)
        
        if not precedents:
            return JSONResponse({
                "success": True,
                "clause_text": clause_text,
                "message": "No similar legal precedents found",
                "precedents": []
            })
        
        # Enrich precedents with risk analysis
        enriched_precedents = []
        for precedent in precedents:
            enriched_precedent = {
                "text": precedent["text"],
                "similarity": precedent["similarity"],
                "risk_level": precedent["metadata"]["risk_level"],
                "clause_type": precedent["metadata"]["clause_type"],
                "contract_domain": precedent["metadata"]["contract_domain"],
                "precedent_strength": precedent["metadata"]["legal_precedent"],
                "source": precedent["metadata"]["source"],
                "contract_title": precedent["metadata"].get("contract_title", "Unknown"),
                "risk_explanation": _get_risk_explanation(precedent["metadata"]["risk_level"])
            }
            enriched_precedents.append(enriched_precedent)
        
        # Generate summary statistics
        risk_distribution = {}
        domain_distribution = {}
        
        for precedent in enriched_precedents:
            # Risk distribution
            risk = precedent["risk_level"]
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
            
            # Domain distribution  
            domain = precedent["contract_domain"]
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        # Calculate average similarity and precedent strength
        avg_similarity = sum(p["similarity"] for p in enriched_precedents) / len(enriched_precedents)
        avg_precedent_strength = sum(p["precedent_strength"] for p in enriched_precedents) / len(enriched_precedents)
        
        return JSONResponse({
            "success": True,
            "clause_text": clause_text,
            "total_precedents": len(enriched_precedents),
            "precedents": enriched_precedents,
            "analysis": {
                "average_similarity": round(avg_similarity, 3),
                "average_precedent_strength": round(avg_precedent_strength, 3),
                "risk_distribution": risk_distribution,
                "domain_distribution": domain_distribution,
                "dominant_risk": max(risk_distribution, key=risk_distribution.get),
                "dominant_domain": max(domain_distribution, key=domain_distribution.get)
            },
            "recommendations": _generate_precedent_recommendations(enriched_precedents, clause_text)
        })
        
    except Exception as e:
        logger.error(f"Error finding legal precedents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding precedents: {str(e)}")

def _get_risk_explanation(risk_level: str) -> str:
    """Get explanation for risk level"""
    explanations = {
        "RED": "High risk - requires immediate legal attention and careful negotiation",
        "AMBER": "Medium risk - should be reviewed carefully and may need modification", 
        "GREEN": "Low risk - generally acceptable with standard terms"
    }
    return explanations.get(risk_level, "Risk level unclear")

def _generate_precedent_recommendations(precedents: List[Dict], clause_text: str) -> List[str]:
    """Generate recommendations based on precedent analysis"""
    recommendations = []
    
    if not precedents:
        return ["No precedents available for analysis"]
    
    # Risk-based recommendations
    risk_counts = {}
    for precedent in precedents:
        risk = precedent["risk_level"]
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    dominant_risk = max(risk_counts, key=risk_counts.get)
    risk_percentage = (risk_counts[dominant_risk] / len(precedents)) * 100
    
    if dominant_risk == "RED" and risk_percentage >= 60:
        recommendations.append(f"⚠️ **High Risk Alert**: {risk_percentage:.0f}% of similar clauses are high-risk")
        recommendations.append("🔍 **Immediate legal review strongly recommended**")
        recommendations.append("💼 **Consider alternative wording or additional protections**")
    elif dominant_risk == "AMBER":
        recommendations.append(f"⚡ **Moderate Risk**: {risk_percentage:.0f}% of similar clauses require careful review")
        recommendations.append("📖 **Detailed legal analysis recommended**")
    else:
        recommendations.append(f"✅ **Generally Acceptable**: {risk_percentage:.0f}% of similar clauses are low-risk")
        recommendations.append("👀 **Standard review process sufficient**")
    
    # Domain-specific recommendations
    domains = [p["contract_domain"] for p in precedents]
    dominant_domain = max(set(domains), key=domains.count) if domains else None
    
    if dominant_domain and dominant_domain != 'general':
        domain_percentage = (domains.count(dominant_domain) / len(domains)) * 100
        recommendations.append(f"📊 **Industry Context**: {domain_percentage:.0f}% from {dominant_domain} contracts")
        recommendations.append(f"🎯 **Consider {dominant_domain} industry standards and practices**")
    
    # Similarity-based recommendations
    avg_similarity = sum(p["similarity"] for p in precedents) / len(precedents)
    if avg_similarity > 0.8:
        recommendations.append(f"🎯 **Strong Matches Found**: Average similarity {avg_similarity:.1%}")
        recommendations.append("📚 **High confidence in precedent-based analysis**")
    elif avg_similarity < 0.5:
        recommendations.append(f"⚠️ **Limited Similarity**: Average similarity {avg_similarity:.1%}")
        recommendations.append("🔍 **Consider broader legal research**")
    
    # Precedent strength recommendations
    avg_strength = sum(p["precedent_strength"] for p in precedents) / len(precedents)
    if avg_strength > 0.8:
        recommendations.append("💪 **Strong Legal Precedents**: High-quality reference clauses found")
    elif avg_strength < 0.5:
        recommendations.append("⚠️ **Weak Precedents**: Consider additional legal research")
    
    return recommendations[:8]  # Limit to 8 recommendations

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