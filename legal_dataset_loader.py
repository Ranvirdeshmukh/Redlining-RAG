import requests
import json
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import hashlib
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import re
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDatasetLoader:
    def __init__(self, cache_dir: str = "./legal_data_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Legal risk classification mappings
        self.risk_mapping = self._initialize_risk_mapping()
        
    def _initialize_risk_mapping(self) -> Dict[str, str]:
        """Map legal clause types to risk levels"""
        return {
            # HIGH RISK (RED) - Clauses that pose significant legal/financial exposure
            "Liability cap": "RED",
            "Indemnification": "RED", 
            "Limitation of liability": "RED",
            "Liquidated damages": "RED",
            "Penalty": "RED",
            "Personal guarantee": "RED",
            "Joint liability": "RED",
            "Unlimited liability": "RED",
            "Non-compete": "RED",
            "Exclusivity": "RED",
            "Assignment": "RED",
            "Termination for convenience": "RED",
            "Automatic renewal": "RED",
            "Irrevocable": "RED",
            
            # MEDIUM RISK (AMBER) - Clauses requiring careful review
            "Termination": "AMBER",
            "Breach": "AMBER", 
            "Default": "AMBER",
            "Force majeure": "AMBER",
            "Intellectual property": "AMBER",
            "Confidentiality": "AMBER",
            "Non-disclosure": "AMBER",
            "Governing law": "AMBER",
            "Jurisdiction": "AMBER",
            "Arbitration": "AMBER",
            "Dispute resolution": "AMBER",
            "Warranty": "AMBER",
            "Representation": "AMBER",
            "Material adverse change": "AMBER",
            "Change of control": "AMBER",
            
            # LOW RISK (GREEN) - Standard contractual terms
            "Notice": "GREEN",
            "Communication": "GREEN",
            "Cooperation": "GREEN",
            "Good faith": "GREEN",
            "Reasonable efforts": "GREEN",
            "Industry standard": "GREEN",
            "Mutual agreement": "GREEN",
            "Consent": "GREEN",
            "Approval": "GREEN",
            "Standard terms": "GREEN"
        }
    
    def download_cuad_dataset(self) -> Optional[Dict]:
        """Download and cache CUAD dataset"""
        try:
            cache_file = self.cache_dir / "cuad_dataset.json"
            
            if cache_file.exists():
                logger.info("Loading CUAD dataset from cache...")
                with open(cache_file, 'r') as f:
                    return json.load(f)
            
            logger.info("Downloading CUAD dataset from HuggingFace...")
            
            # Load CUAD dataset
            dataset = load_dataset("cuad", split="train[:1000]")  # Limit for demo
            
            # Convert to our format
            processed_data = []
            for item in dataset:
                contract_text = item.get('context', '')
                title = item.get('title', 'Unknown Contract')
                
                # Extract clauses from the contract text
                clauses = self._extract_clauses_from_text(contract_text)
                
                for clause in clauses:
                    processed_item = {
                        'text': clause['text'],
                        'contract_title': title,
                        'clause_type': clause['type'],
                        'risk_level': self._classify_risk_level(clause['text'], clause['type']),
                        'contract_domain': self._infer_contract_domain(title, contract_text),
                        'source': 'CUAD',
                        'precedent_strength': self._calculate_precedent_strength(clause['text'])
                    }
                    processed_data.append(processed_item)
            
            # Cache the processed data
            with open(cache_file, 'w') as f:
                json.dump(processed_data, f, indent=2)
            
            logger.info(f"Successfully processed {len(processed_data)} legal clauses from CUAD")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error downloading CUAD dataset: {str(e)}")
            return self._load_fallback_dataset()
    
    def _extract_clauses_from_text(self, contract_text: str) -> List[Dict]:
        """Extract individual clauses from contract text"""
        # Split by common clause indicators
        clause_patterns = [
            r'\d+\.\s+',  # Numbered sections
            r'\([a-z]\)\s+',  # Lettered subsections
            r'WHEREAS\s+',  # Whereas clauses
            r'NOW THEREFORE\s+',  # Therefore clauses
            r'The parties agree that\s+',  # Agreement clauses
        ]
        
        clauses = []
        sentences = re.split(r'\.(?=\s+[A-Z])', contract_text)
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) > 50:  # Filter out short fragments
                clause_type = self._identify_clause_type(sentence)
                clauses.append({
                    'text': sentence,
                    'type': clause_type,
                    'position': i
                })
        
        return clauses
    
    def _identify_clause_type(self, text: str) -> str:
        """Identify the type of legal clause"""
        text_lower = text.lower()
        
        # Check for specific clause types
        clause_indicators = {
            'liability': ['liable', 'liability', 'damages', 'harm'],
            'termination': ['terminate', 'termination', 'end', 'cancel'],
            'indemnification': ['indemnify', 'indemnification', 'hold harmless'],
            'confidentiality': ['confidential', 'non-disclosure', 'proprietary'],
            'intellectual_property': ['intellectual property', 'patent', 'copyright', 'trademark'],
            'governing_law': ['governing law', 'jurisdiction', 'venue'],
            'force_majeure': ['force majeure', 'act of god', 'unforeseeable'],
            'warranty': ['warrant', 'warranty', 'guarantee', 'represent'],
            'assignment': ['assign', 'assignment', 'transfer'],
            'notice': ['notice', 'notify', 'notification']
        }
        
        for clause_type, keywords in clause_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                return clause_type
        
        return 'general'
    
    def _classify_risk_level(self, text: str, clause_type: str) -> str:
        """Classify risk level based on text content and clause type"""
        text_lower = text.lower()
        
        # High-risk indicators
        high_risk_patterns = [
            'unlimited', 'personal guarantee', 'joint and several', 
            'liquidated damages', 'penalty', 'forfeiture', 'punitive',
            'indemnify.*all', 'hold harmless.*all', 'irrevocable',
            'non-compete', 'restraint.*trade', 'exclusivity'
        ]
        
        # Medium-risk indicators  
        medium_risk_patterns = [
            'material breach', 'default', 'termination', 'arbitration',
            'governing law', 'intellectual property', 'confidential',
            'warranty disclaimer', 'limitation.*liability'
        ]
        
        # Check patterns
        for pattern in high_risk_patterns:
            if re.search(pattern, text_lower):
                return "RED"
        
        for pattern in medium_risk_patterns:
            if re.search(pattern, text_lower):
                return "AMBER"
        
        # Check clause type mapping
        for key, risk in self.risk_mapping.items():
            if key.lower() in clause_type.lower():
                return risk
        
        return "GREEN"  # Default to low risk
    
    def _infer_contract_domain(self, title: str, text: str) -> str:
        """Infer the contract domain/type"""
        title_lower = title.lower()
        text_lower = text.lower()
        
        domain_keywords = {
            'employment': ['employment', 'employee', 'job', 'salary', 'benefits'],
            'software': ['software', 'licensing', 'code', 'development', 'SaaS'],
            'real_estate': ['property', 'lease', 'rent', 'premises', 'landlord'],
            'merger': ['merger', 'acquisition', 'purchase', 'sale', 'transaction'],
            'service': ['service', 'consulting', 'professional', 'work'],
            'supply': ['supply', 'vendor', 'procurement', 'goods', 'materials'],
            'partnership': ['partnership', 'joint venture', 'collaboration'],
            'finance': ['loan', 'credit', 'financing', 'investment', 'securities']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in title_lower or keyword in text_lower for keyword in keywords):
                return domain
        
        return 'general'
    
    def _calculate_precedent_strength(self, text: str) -> float:
        """Calculate how strong this clause is as a legal precedent"""
        # Factors that increase precedent strength
        strength = 0.5  # Base strength
        
        # Length and complexity
        word_count = len(text.split())
        if word_count > 100:
            strength += 0.2
        elif word_count > 50:
            strength += 0.1
        
        # Legal language sophistication
        legal_terms = ['whereas', 'therefore', 'notwithstanding', 'pursuant', 'heretofore']
        legal_term_count = sum(1 for term in legal_terms if term in text.lower())
        strength += min(0.3, legal_term_count * 0.1)
        
        return min(1.0, strength)
    
    def _load_fallback_dataset(self) -> List[Dict]:
        """Load a fallback synthetic legal dataset"""
        logger.info("Loading fallback synthetic legal dataset...")
        
        fallback_clauses = [
            {
                'text': 'The Company shall indemnify and hold harmless the Client against all claims, damages, and expenses arising from any breach of this Agreement.',
                'contract_title': 'Service Agreement',
                'clause_type': 'indemnification',
                'risk_level': 'RED',
                'contract_domain': 'service',
                'source': 'Synthetic',
                'precedent_strength': 0.8
            },
            {
                'text': 'Either party may terminate this Agreement upon thirty (30) days written notice to the other party.',
                'contract_title': 'General Contract',
                'clause_type': 'termination',
                'risk_level': 'AMBER',
                'contract_domain': 'general',
                'source': 'Synthetic',
                'precedent_strength': 0.7
            },
            {
                'text': 'All notices required under this Agreement shall be given in writing and delivered by certified mail.',
                'contract_title': 'Standard Contract',
                'clause_type': 'notice',
                'risk_level': 'GREEN',
                'contract_domain': 'general',
                'source': 'Synthetic',
                'precedent_strength': 0.6
            },
            {
                'text': 'The Employee agrees not to compete with the Company for a period of two (2) years following termination of employment.',
                'contract_title': 'Employment Agreement',
                'clause_type': 'non_compete',
                'risk_level': 'RED',
                'contract_domain': 'employment',
                'source': 'Synthetic',
                'precedent_strength': 0.9
            },
            {
                'text': 'This Agreement shall be governed by the laws of the State of California, without regard to conflict of law principles.',
                'contract_title': 'Service Agreement',
                'clause_type': 'governing_law',
                'risk_level': 'AMBER',
                'contract_domain': 'service',
                'source': 'Synthetic',
                'precedent_strength': 0.7
            }
        ]
        
        return fallback_clauses
    
    def format_for_chromadb(self, legal_data: List[Dict]) -> Dict[str, List]:
        """Format legal dataset for ChromaDB ingestion"""
        try:
            texts = [item['text'] for item in legal_data]
            embeddings = self.embedding_model.encode(texts).tolist()
            
            ids = [f"legal_{hashlib.md5(item['text'].encode()).hexdigest()[:8]}" for item in legal_data]
            
            metadatas = []
            for item in legal_data:
                metadatas.append({
                    'clause_type': item['clause_type'],
                    'risk_level': item['risk_level'],
                    'legal_precedent': item['precedent_strength'],
                    'contract_domain': item['contract_domain'],
                    'source': item['source'],
                    'contract_title': item.get('contract_title', 'Unknown')
                })
            
            logger.info(f"Formatted {len(texts)} legal clauses for ChromaDB")
            
            return {
                'texts': texts,
                'embeddings': embeddings,
                'ids': ids,
                'metadatas': metadatas
            }
            
        except Exception as e:
            logger.error(f"Error formatting data for ChromaDB: {str(e)}")
            raise
    
    def load_and_format_legal_dataset(self) -> Optional[Dict[str, List]]:
        """Main method to load and format legal dataset"""
        try:
            # Download/load dataset
            legal_data = self.download_cuad_dataset()
            
            if not legal_data:
                logger.error("Failed to load legal dataset")
                return None
            
            # Format for ChromaDB
            formatted_data = self.format_for_chromadb(legal_data)
            
            logger.info("✅ Legal dataset successfully loaded and formatted")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error in load_and_format_legal_dataset: {str(e)}")
            return None

# Utility function for easy integration
def get_legal_dataset_loader() -> LegalDatasetLoader:
    """Factory function to create a legal dataset loader"""
    return LegalDatasetLoader()

if __name__ == "__main__":
    # Test the loader
    loader = LegalDatasetLoader()
    data = loader.load_and_format_legal_dataset()
    if data:
        print(f"Successfully loaded {len(data['texts'])} legal clauses")
        print(f"Sample clause: {data['texts'][0][:100]}...")
        print(f"Sample metadata: {data['metadatas'][0]}") 