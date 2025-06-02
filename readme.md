#  Contract Redlining RAG System

An AI-powered contract analysis tool that automatically identifies and categorizes legal risks in contract documents using MISTRAL7b and RAG (Retrieval-Augmented Generation) technology.

##  Features

- **📄 PDF Document Processing** - Upload and extract text from PDF contracts
- **🤖 AI-Powered Analysis** - Uses MISTRAL7b model for intelligent clause classification
- **🔍 RAG Technology** - Semantic search with ChromaDB vector database
- **🎯 Risk Classification** - Categorizes clauses into Red (High), Amber (Medium), Green (Low) risk
- **📊 Visual Dashboard** - Interactive risk analysis dashboard
- **🖼️ Redlined Output** - Color-coded contract visualization
- **📋 Detailed Reports** - Comprehensive analysis with recommendations
- **💾 Export Functionality** - Export results in JSON format
- **🔄 Real-time Processing** - Fast document analysis and results

##  Architecture

```
Contract Redlining RAG System
├── Document Processing (PyPDF2 + LangChain)
├── Vector Storage (ChromaDB)
├── AI Engine (MISTRAL7b via Transformers)
├── Risk Classification (Rule-based + LLM)
├── Web Interface (FastAPI + HTML/CSS/JS)
└── Real-time Analysis & Visualization
```

##  Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: MISTRAL7b, Transformers, Sentence Transformers
- **Vector DB**: ChromaDB
- **Document Processing**: PyPDF2, LangChain
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Modern CSS with Font Awesome icons

##  Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd redlining-rag

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Start the FastAPI server
python main.py
```

The application will be available at: `http://localhost:8000`

### 3. Usage

1. **Upload Contract**: Drag & drop or click to upload a PDF contract
2. **Analyze Document**: Click "Analyze Document" to start AI processing  
3. **Review Results**: View color-coded clauses and risk analysis
4. **Export Results**: Download analysis in JSON format

##  Project Structure

```
redlining-rag/
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
├── models/                    # Core AI models
│   ├── __init__.py
│   ├── document_processor.py  # PDF processing & text extraction
│   ├── rag_engine.py         # MISTRAL7b & ChromaDB integration
│   └── redlining_classifier.py # Risk classification logic
├── static/                    # Frontend assets
│   ├── style.css             # Modern UI styling
│   └── script.js             # Interactive functionality
├── templates/                 # HTML templates
│   └── index.html            # Main application interface
├── uploads/                   # Uploaded files (auto-created)
├── chroma_db/                # Vector database (auto-created)
└── README.md                 # Documentation
```

##  Risk Classification System

### 🔴 RED (High Risk)
- Unlimited liability clauses
- Personal guarantees
- Penalty clauses
- Non-compete agreements
- Automatic renewal terms

### 🟡 AMBER (Medium Risk)
- Termination clauses
- IP ownership terms
- Confidentiality agreements
- Governing law provisions
- Dispute resolution terms

### 🟢 GREEN (Low Risk)
- Standard boilerplate terms
- Reasonable effort clauses
- Mutual consent provisions
- Industry standard terms
- Cooperative obligations

## Configuration

### Model Configuration
The system uses a fallback approach for model loading:
- **Primary**: MISTRAL7b (requires GPU/sufficient RAM)
- **Fallback**: Smaller models for quick demos

### Customization Options
- Modify risk keywords in `redlining_classifier.py`
- Adjust chunk sizes in `document_processor.py`
- Configure embedding models in `rag_engine.py`

##  API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/upload` | POST | Upload PDF document |
| `/analyze/{doc_id}` | POST | Analyze uploaded document |
| `/search` | GET | Semantic search clauses |
| `/classify-text` | POST | Classify single text clause |
| `/health` | GET | System health check |

##  UI Features

- **Modern Design** - Clean, professional interface
- **Responsive Layout** - Works on desktop and mobile
- **Real-time Feedback** - Progress indicators and notifications
- **Interactive Elements** - Click clauses for detailed analysis
- **Keyboard Shortcuts** - Ctrl+U (upload), Ctrl+A (analyze)
- **Drag & Drop** - Intuitive file upload experience

##  Advanced Features

### Semantic Search
```javascript
// Search for similar clauses
const results = await searchClauses("liability indemnification");
```

### Batch Processing
- Process multiple documents
- Compare risk profiles
- Generate summary reports

### Performance Monitoring
- Track processing times
- Monitor model performance
- System health checks

##  Performance Optimization

- **Lazy Loading** - Models load on demand
- **Efficient Chunking** - Optimized text processing
- **Caching** - Vector embeddings cached in ChromaDB
- **Parallel Processing** - Multiple documents simultaneously

##  Security & Privacy

- Files processed locally (no external API calls)
- Temporary file storage only
- No persistent user data storage
- Secure PDF processing

## 🐛 Troubleshooting

### Common Issues

1. **Model Loading Errors**
   ```bash
   # Check available memory
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **PDF Processing Issues**
   ```bash
   # Ensure PyPDF2 is properly installed
   pip install --upgrade PyPDF2
   ```

3. **ChromaDB Errors**
   ```bash
   # Clear vector database if corrupted
   rm -rf chroma_db/
   ```

### Performance Tips

- Use GPU-enabled system for best performance
- Ensure sufficient RAM (8GB+ recommended)
- Process smaller documents first for testing

##  Future Enhancements

- [ ] Support for DOCX files
- [ ] Multi-language contract analysis
- [ ] Advanced clause templates
- [ ] Integration with legal databases
- [ ] Collaborative review features
- [ ] Advanced export formats (PDF, Word)

##  Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request



##  Support

For issues and questions:
- Create GitHub issue
- Check troubleshooting section
- Review API documentation

##  Acknowledgments

- **MISTRAL AI** - For the powerful language model
- **ChromaDB** - For efficient vector storage
- **Hugging Face** - For model hosting and transformers
- **FastAPI** - For the excellent web framework

---


>  **Disclaimer**: This tool is for assistance only. All contract analysis should be reviewed by qualified legal professionals. 