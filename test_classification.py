#!/usr/bin/env python3

import sys
sys.path.append('.')

from models.document_processor import DocumentProcessor
from models.rag_engine import RAGEngine
from models.redlining_classifier import RedliningClassifier

def test_classification():
    print("🔍 Testing Contract Redlining Classification...")
    
    try:
        # Initialize components
        print("📄 Initializing components...")
        rag_engine = RAGEngine()
        classifier = RedliningClassifier(rag_engine)
        
        # Test clauses
        test_clauses = [
            "The party shall have unlimited liability and personal guarantee for all damages.",
            "Both parties agree to reasonable best efforts in performing their obligations.",
            "This agreement shall be governed by the laws of Delaware with binding arbitration."
        ]
        
        print("\n🧪 Testing individual clauses:")
        for i, clause in enumerate(test_clauses, 1):
            print(f"\n--- Test {i} ---")
            print(f"Clause: {clause}")
            
            try:
                result = classifier.classify_clause(clause)
                print(f"Risk Level: {result['risk_level']}")
                print(f"Explanation: {result['explanation']}")
                print(f"Confidence: {result['confidence']}")
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n✅ Classification test completed!")
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_classification() 