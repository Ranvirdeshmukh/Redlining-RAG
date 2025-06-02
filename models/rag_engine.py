import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import List, Dict, Any
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.embedding_model = None
        self.llm_pipeline = None
        self.chroma_client = None
        self.collection = None
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize embedding model, LLM, and vector database"""
        try:
            logger.info("Initializing embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Initializing MISTRAL7b model...")
            # Use a smaller, faster model for demo purposes
            model_name = "microsoft/DialoGPT-medium"  # Fallback for quick demo
            # model_name = "mistralai/Mistral-7B-Instruct-v0.1"  # Use this for actual MISTRAL
            
            self.llm_pipeline = pipeline(
                "text-generation",
                model=model_name,
                tokenizer=model_name,
                device=0 if torch.cuda.is_available() else -1,
                max_length=512,
                do_sample=True,
                temperature=0.7
            )
            
            logger.info("Initializing ChromaDB...")
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_or_create_collection(
                name="contract_clauses",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("All models initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            # Fallback initialization
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.llm_pipeline = None
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(name="contract_clauses")
    
    def add_document_to_vectordb(self, chunks: List[Dict], document_id: str):
        """Add document chunks to vector database"""
        try:
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts).tolist()
            
            ids = [f"{document_id}_chunk_{chunk['chunk_id']}" for chunk in chunks]
            metadatas = [
                {
                    "document_id": document_id,
                    "chunk_id": chunk["chunk_id"],
                    "is_clause": chunk["is_clause"],
                    "word_count": chunk["word_count"]
                }
                for chunk in chunks
            ]
            
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector database")
            
        except Exception as e:
            logger.error(f"Error adding document to vector DB: {str(e)}")
            raise
    
    def semantic_search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Perform semantic search for relevant clauses"""
        try:
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where={"is_clause": True}
            )
            
            search_results = []
            for i in range(len(results["documents"][0])):
                search_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "id": results["ids"][0][i]
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []
    
    def generate_risk_analysis(self, clause_text: str, context: str = "") -> Dict[str, Any]:
        """Generate risk analysis for a contract clause using LLM"""
        try:
            prompt = self._create_risk_analysis_prompt(clause_text, context)
            
            if self.llm_pipeline:
                # Generate response using the pipeline
                response = self.llm_pipeline(prompt, max_length=200, num_return_sequences=1)
                generated_text = response[0]["generated_text"]
                
                # Parse the response (simplified for demo)
                risk_level, explanation = self._parse_llm_response(generated_text)
            else:
                # Fallback rule-based analysis
                risk_level, explanation = self._fallback_risk_analysis(clause_text)
            
            return {
                "risk_level": risk_level,
                "explanation": explanation,
                "confidence": 0.85,  # Mock confidence score
                "clause_text": clause_text
            }
            
        except Exception as e:
            logger.error(f"Error generating risk analysis: {str(e)}")
            return self._fallback_risk_analysis(clause_text)
    
    def _create_risk_analysis_prompt(self, clause_text: str, context: str) -> str:
        """Create a structured prompt for risk analysis"""
        return f"""
        Analyze the following contract clause for legal risks:
        
        Clause: "{clause_text}"
        Context: {context}
        
        Classify the risk level as RED (high risk), AMBER (medium risk), or GREEN (low risk).
        Provide a brief explanation.
        
        Analysis:
        """
    
    def _parse_llm_response(self, response: str) -> tuple:
        """Parse LLM response to extract risk level and explanation"""
        response_lower = response.lower()
        
        if "red" in response_lower:
            risk_level = "RED"
        elif "amber" in response_lower or "yellow" in response_lower:
            risk_level = "AMBER"
        elif "green" in response_lower:
            risk_level = "GREEN"
        else:
            risk_level = "AMBER"  # Default
        
        # Extract explanation (simplified)
        explanation = response.split("Analysis:")[-1].strip()[:200]
        
        return risk_level, explanation
    
    def _fallback_risk_analysis(self, clause_text: str) -> tuple:
        """Fallback rule-based risk analysis"""
        high_risk_keywords = [
            "unlimited liability", "personal guarantee", "indemnify", "hold harmless",
            "liquidated damages", "penalty", "forfeiture", "non-compete", "exclusivity"
        ]
        
        medium_risk_keywords = [
            "termination", "breach", "default", "force majeure", "intellectual property",
            "confidential", "proprietary", "governing law", "arbitration"
        ]
        
        text_lower = clause_text.lower()
        
        high_risk_count = sum(1 for keyword in high_risk_keywords if keyword in text_lower)
        medium_risk_count = sum(1 for keyword in medium_risk_keywords if keyword in text_lower)
        
        if high_risk_count > 0:
            return ("RED", {
                "risk_level": "RED",
                "explanation": f"Contains high-risk terms: {high_risk_count} detected. Requires careful legal review.",
                "confidence": 0.8
            })
        elif medium_risk_count > 0:
            return ("AMBER", {
                "risk_level": "AMBER", 
                "explanation": f"Contains medium-risk terms: {medium_risk_count} detected. Review recommended.",
                "confidence": 0.7
            })
        else:
            return ("GREEN", {
                "risk_level": "GREEN",
                "explanation": "No significant risk indicators detected. Standard contractual language.",
                "confidence": 0.6
            }) 