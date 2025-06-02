import PyPDF2
import io
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str) -> List[Dict]:
        """Split text into semantic chunks with metadata"""
        cleaned_text = self.clean_text(text)
        chunks = self.text_splitter.split_text(cleaned_text)
        
        chunk_data = []
        for i, chunk in enumerate(chunks):
            # Identify potential clauses (sentences with legal keywords)
            is_clause = self._is_potential_clause(chunk)
            
            chunk_data.append({
                "chunk_id": i,
                "text": chunk,
                "is_clause": is_clause,
                "word_count": len(chunk.split()),
                "char_count": len(chunk)
            })
        
        return chunk_data
    
    def _is_potential_clause(self, text: str) -> bool:
        """Identify if text chunk is likely a contract clause"""
        legal_keywords = [
            "shall", "agree", "covenant", "warrant", "represent", "obligation",
            "liability", "indemnify", "terminate", "breach", "default", "penalty",
            "damages", "force majeure", "confidential", "proprietary", "intellectual property",
            "governing law", "jurisdiction", "arbitration", "dispute", "remedy"
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in legal_keywords if keyword in text_lower)
        
        # Consider it a clause if it has legal keywords and reasonable length
        return keyword_count >= 1 and len(text.split()) >= 10
    
    def process_document(self, pdf_content: bytes, filename: str) -> Dict:
        """Main processing pipeline"""
        try:
            # Extract text
            raw_text = self.extract_text_from_pdf(pdf_content)
            
            # Chunk text
            chunks = self.chunk_text(raw_text)
            
            # Filter clauses
            clauses = [chunk for chunk in chunks if chunk["is_clause"]]
            
            return {
                "filename": filename,
                "raw_text": raw_text,
                "total_chunks": len(chunks),
                "total_clauses": len(clauses),
                "chunks": chunks,
                "clauses": clauses,
                "word_count": len(raw_text.split()),
                "char_count": len(raw_text)
            }
        
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}") 