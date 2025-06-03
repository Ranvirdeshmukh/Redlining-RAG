import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import List, Dict, Any
import os
import logging
from legal_dataset_loader import get_legal_dataset_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.embedding_model = None
        self.llm_pipeline = None
        self.chroma_client = None
        self.collection = None
        self.legal_collection = None  # New legal knowledge collection
        self.initialize_models()
        self.initialize_legal_knowledge()
    
    def initialize_models(self):
        """Initialize embedding model, LLM, and vector database"""
        try:
            logger.info("Initializing embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Initializing MISTRAL-7B model...")
            # Enable actual Mistral model
            model_name = "mistralai/Mistral-7B-Instruct-v0.1"
            
            try:
                # Try to load Mistral model
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.llm_model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    trust_remote_code=True
                )
                
                self.llm_pipeline = pipeline(
                    "text-generation",
                    model=self.llm_model,
                    tokenizer=self.tokenizer,
                    device=0 if torch.cuda.is_available() else -1,
                    max_new_tokens=256,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.95
                )
                logger.info("✅ Mistral-7B model loaded successfully!")
                
            except Exception as e:
                logger.warning(f"Could not load Mistral-7B: {str(e)}")
                logger.info("Falling back to DialoGPT-medium...")
                # Fallback model
                fallback_model = "microsoft/DialoGPT-medium"
                self.llm_pipeline = pipeline(
                    "text-generation",
                    model=fallback_model,
                    tokenizer=fallback_model,
                    device=0 if torch.cuda.is_available() else -1,
                    max_length=512,
                    do_sample=True,
                    temperature=0.7
                )
            
            logger.info("Initializing ChromaDB...")
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            
            # Contract clauses collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="contract_clauses",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Legal knowledge collection
            self.legal_collection = self.chroma_client.get_or_create_collection(
                name="legal_knowledge",
                metadata={"hnsw:space": "cosine", "description": "Legal precedents and clause analysis"}
            )
            
            logger.info("All models initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            # Fallback initialization
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.llm_pipeline = None
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(name="contract_clauses")
            self.legal_collection = self.chroma_client.get_or_create_collection(name="legal_knowledge")
    
    def initialize_legal_knowledge(self):
        """Initialize legal knowledge database"""
        try:
            # Check if legal knowledge is already populated
            existing_count = self.legal_collection.count()
            
            if existing_count > 0:
                logger.info(f"Legal knowledge collection already contains {existing_count} items")
                return
            
            logger.info("Loading legal dataset...")
            dataset_loader = get_legal_dataset_loader()
            legal_data = dataset_loader.load_and_format_legal_dataset()
            
            if legal_data:
                # Populate legal knowledge collection
                self.legal_collection.add(
                    embeddings=legal_data['embeddings'],
                    documents=legal_data['texts'],
                    metadatas=legal_data['metadatas'],
                    ids=legal_data['ids']
                )
                logger.info(f"✅ Added {len(legal_data['texts'])} legal precedents to knowledge base")
            else:
                logger.warning("Failed to load legal dataset")
                
        except Exception as e:
            logger.error(f"Error initializing legal knowledge: {str(e)}")
    
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
    
    def find_legal_precedents(self, clause_text: str, n_results: int = 3) -> List[Dict]:
        """Find similar legal precedents for a given clause"""
        try:
            query_embedding = self.embedding_model.encode([clause_text]).tolist()
            
            results = self.legal_collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            precedents = []
            for i in range(len(results["documents"][0])):
                precedents.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "id": results["ids"][0][i]
                })
            
            return precedents
            
        except Exception as e:
            logger.error(f"Error finding legal precedents: {str(e)}")
            return []
    
    def generate_risk_analysis(self, clause_text: str, context: Dict = None) -> Dict[str, Any]:
        """Generate enhanced risk analysis using legal precedents and LLM"""
        try:
            # Find similar legal precedents
            precedents = self.find_legal_precedents(clause_text, n_results=3)
            
            # Create enhanced prompt with legal context
            prompt = self._create_legal_risk_prompt(clause_text, precedents, context or {})
            
            if self.llm_pipeline:
                # Generate response using the pipeline
                response = self.llm_pipeline(
                    prompt, 
                    max_new_tokens=200, 
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.eos_token_id if hasattr(self, 'tokenizer') else None
                )
                generated_text = response[0]["generated_text"]
                
                # Parse the response
                risk_level, explanation, confidence = self._parse_enhanced_llm_response(generated_text, precedents)
                
            else:
                # Enhanced fallback analysis using precedents
                risk_level, explanation, confidence = self._precedent_based_analysis(clause_text, precedents)
            
            return {
                "risk_level": risk_level,
                "explanation": explanation,
                "confidence": confidence,
                "precedents": precedents[:2],  # Include top 2 precedents
                "clause_text": clause_text
            }
            
        except Exception as e:
            logger.error(f"Error generating risk analysis: {str(e)}")
            return self._fallback_risk_analysis(clause_text)
    
    def _create_legal_risk_prompt(self, clause_text: str, precedents: List[Dict], context: Dict) -> str:
        """Create a legal-specific prompt with precedent context"""
        precedent_context = ""
        if precedents:
            precedent_context = "\nSimilar legal precedents:\n"
            for i, precedent in enumerate(precedents[:2], 1):
                risk = precedent['metadata'].get('risk_level', 'UNKNOWN')
                domain = precedent['metadata'].get('contract_domain', 'general')
                precedent_context += f"{i}. [{risk} Risk, {domain} domain] {precedent['text'][:100]}...\n"
        
        prompt = f"""<s>[INST] You are a legal AI assistant specializing in contract risk analysis. 
        
Analyze the following contract clause for legal and financial risks:

CLAUSE TO ANALYZE:
"{clause_text}"

CONTEXT: {context.get('contract_type', 'General contract')}

{precedent_context}

Based on similar legal precedents and your expertise, classify this clause as:
- RED (High Risk): Significant legal/financial exposure, immediate attention needed
- AMBER (Medium Risk): Requires careful review and consideration
- GREEN (Low Risk): Standard terms, minimal risk

Provide:
1. Risk Level: [RED/AMBER/GREEN]
2. Explanation: Brief reasoning (max 100 words)
3. Confidence: [High/Medium/Low]

Analysis: [/INST]"""
        
        return prompt
    
    def _parse_enhanced_llm_response(self, response: str, precedents: List[Dict]) -> tuple:
        """Parse enhanced LLM response with precedent context"""
        response_lower = response.lower()
        
        # Extract risk level
        if "red" in response_lower and "risk" in response_lower:
            risk_level = "RED"
        elif "amber" in response_lower or "yellow" in response_lower:
            risk_level = "AMBER"  
        elif "green" in response_lower:
            risk_level = "GREEN"
        else:
            # Use precedent consensus as fallback
            if precedents:
                precedent_risks = [p['metadata'].get('risk_level', 'GREEN') for p in precedents]
                risk_counts = {risk: precedent_risks.count(risk) for risk in ['RED', 'AMBER', 'GREEN']}
                risk_level = max(risk_counts, key=risk_counts.get)
            else:
                risk_level = "AMBER"
        
        # Extract confidence
        confidence = 0.8  # Base confidence for LLM analysis
        if "high" in response_lower and "confidence" in response_lower:
            confidence = 0.9
        elif "low" in response_lower and "confidence" in response_lower:
            confidence = 0.6
        
        # Adjust confidence based on precedent quality
        if precedents:
            avg_similarity = sum(p.get('similarity', 0) for p in precedents) / len(precedents)
            confidence = min(0.95, confidence + (avg_similarity * 0.1))
        
        # Extract explanation
        explanation_parts = response.split("Analysis:")
        if len(explanation_parts) > 1:
            explanation = explanation_parts[-1].strip()[:200]
        else:
            explanation = f"Legal analysis indicates {risk_level} risk level based on clause content and similar precedents."
        
        return risk_level, explanation, round(confidence, 2)
    
    def _precedent_based_analysis(self, clause_text: str, precedents: List[Dict]) -> tuple:
        """Enhanced fallback analysis using legal precedents"""
        if not precedents:
            return self._fallback_risk_analysis(clause_text)
        
        # Weight precedents by similarity
        weighted_risk_score = 0
        total_weight = 0
        
        risk_scores = {"RED": 3, "AMBER": 2, "GREEN": 1}
        
        for precedent in precedents:
            similarity = precedent.get('similarity', 0)
            risk_level = precedent['metadata'].get('risk_level', 'GREEN')
            precedent_strength = precedent['metadata'].get('legal_precedent', 0.5)
            
            weight = similarity * precedent_strength
            score = risk_scores.get(risk_level, 1)
            
            weighted_risk_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_risk_score = weighted_risk_score / total_weight
            
            if avg_risk_score >= 2.5:
                final_risk = "RED"
            elif avg_risk_score >= 1.5:
                final_risk = "AMBER"
            else:
                final_risk = "GREEN"
        else:
            final_risk = "AMBER"
        
        # Calculate confidence based on precedent consensus
        precedent_risks = [p['metadata'].get('risk_level', 'GREEN') for p in precedents]
        consensus = max(set(precedent_risks), key=precedent_risks.count)
        consensus_ratio = precedent_risks.count(consensus) / len(precedent_risks)
        confidence = 0.6 + (consensus_ratio * 0.3)
        
        explanation = f"Analysis based on {len(precedents)} similar legal precedents shows {final_risk} risk. " \
                     f"Precedent consensus: {consensus_ratio:.0%} agreement on risk level."
        
        return final_risk, explanation, round(confidence, 2)
    
    def _fallback_risk_analysis(self, clause_text: str) -> Dict[str, Any]:
        """Enhanced fallback analysis when other methods fail"""
        high_risk_keywords = [
            "unlimited liability", "personal guarantee", "joint and several liability",
            "liquidated damages", "penalty clause", "forfeiture", "punitive damages",
            "indemnification", "hold harmless", "defend and indemnify",
            "non-compete", "restraint of trade", "exclusivity agreement",
            "automatic renewal", "evergreen clause", "perpetual license",
            "unilateral termination", "termination for convenience",
            "assignment of all rights", "work for hire", "moral rights waiver"
        ]
        
        medium_risk_keywords = [
            "termination", "breach", "default", "material breach",
            "force majeure", "act of god", "unforeseen circumstances", 
            "intellectual property", "proprietary information", "trade secrets",
            "confidentiality", "non-disclosure", "proprietary rights",
            "governing law", "jurisdiction", "venue", "arbitration",
            "dispute resolution", "mediation", "litigation",
            "limitation of liability", "consequential damages", "indirect damages",
            "warranty disclaimer", "as is", "merchantability"
        ]
        
        text_lower = clause_text.lower()
        
        high_risk_count = sum(1 for keyword in high_risk_keywords if keyword in text_lower)
        medium_risk_count = sum(1 for keyword in medium_risk_keywords if keyword in text_lower)
        
        if high_risk_count > 0:
            return {
                "risk_level": "RED",
                "explanation": f"Contains high-risk terms: {high_risk_count} detected. Requires careful legal review.",
                "confidence": 0.7,
                "precedents": []
            }
        elif medium_risk_count > 0:
            return {
                "risk_level": "AMBER", 
                "explanation": f"Contains medium-risk terms: {medium_risk_count} detected. Review recommended.",
                "confidence": 0.6,
                "precedents": []
            }
        else:
            return {
                "risk_level": "GREEN",
                "explanation": "No significant risk indicators detected. Standard contractual language.",
                "confidence": 0.5,
                "precedents": []
            } 