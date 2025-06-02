from typing import Dict, List, Any
import logging
from .rag_engine import RAGEngine

logger = logging.getLogger(__name__)

class RedliningClassifier:
    def __init__(self, rag_engine: RAGEngine):
        self.rag_engine = rag_engine
        self.risk_criteria = self._initialize_risk_criteria()
    
    def _initialize_risk_criteria(self) -> Dict:
        """Initialize comprehensive risk assessment criteria"""
        return {
            "RED": {
                "keywords": [
                    "unlimited liability", "personal guarantee", "joint and several liability",
                    "liquidated damages", "penalty clause", "forfeiture", "punitive damages",
                    "indemnification", "hold harmless", "defend and indemnify",
                    "non-compete", "restraint of trade", "exclusivity agreement",
                    "automatic renewal", "evergreen clause", "perpetual license",
                    "unilateral termination", "termination for convenience",
                    "assignment of all rights", "work for hire", "moral rights waiver"
                ],
                "patterns": [
                    r"shall be liable for all damages",
                    r"unlimited.*liability",
                    r"personal.*guarantee",
                    r"indemnify.*against.*all.*claims"
                ],
                "threshold": 1
            },
            "AMBER": {
                "keywords": [
                    "termination", "breach", "default", "material breach",
                    "force majeure", "act of god", "unforeseen circumstances",
                    "intellectual property", "proprietary information", "trade secrets",
                    "confidentiality", "non-disclosure", "proprietary rights",
                    "governing law", "jurisdiction", "venue", "arbitration",
                    "dispute resolution", "mediation", "litigation",
                    "limitation of liability", "consequential damages", "indirect damages",
                    "warranty disclaimer", "as is", "merchantability"
                ],
                "patterns": [
                    r"governing law.*shall be",
                    r"disputes.*shall be.*resolved",
                    r"limitation.*of.*liability",
                    r"confidential.*information"
                ],
                "threshold": 1
            },
            "GREEN": {
                "keywords": [
                    "standard terms", "industry standard", "customary",
                    "reasonable", "good faith", "best efforts",
                    "mutual agreement", "consent", "approval",
                    "notification", "notice", "communication",
                    "cooperation", "assistance", "support"
                ],
                "patterns": [
                    r"reasonable.*efforts",
                    r"good.*faith",
                    r"mutual.*consent",
                    r"industry.*standard"
                ],
                "threshold": 1
            }
        }
    
    def classify_clause(self, clause_text: str, context: Dict = None) -> Dict[str, Any]:
        """Classify a single clause into risk categories"""
        try:
            # Get initial rule-based classification
            rule_based_result = self._rule_based_classification(clause_text)
            
            # Enhance with RAG analysis
            rag_result = self.rag_engine.generate_risk_analysis(clause_text, context or {})
            
            # Combine results
            final_result = self._combine_classifications(rule_based_result, rag_result)
            
            return {
                "clause_text": clause_text,
                "risk_level": final_result["risk_level"],
                "explanation": final_result["explanation"],
                "confidence": final_result["confidence"],
                "rule_based": rule_based_result,
                "rag_based": rag_result,
                "recommendations": self._generate_recommendations(final_result["risk_level"], clause_text)
            }
            
        except Exception as e:
            logger.error(f"Error classifying clause: {str(e)}")
            return self._default_classification(clause_text)
    
    def _rule_based_classification(self, clause_text: str) -> Dict[str, Any]:
        """Perform rule-based classification using keywords and patterns"""
        clause_lower = clause_text.lower()
        scores = {"RED": 0, "AMBER": 0, "GREEN": 0}
        matched_keywords = {"RED": [], "AMBER": [], "GREEN": []}
        
        # Check keywords for each risk level
        for risk_level, criteria in self.risk_criteria.items():
            for keyword in criteria["keywords"]:
                if keyword.lower() in clause_lower:
                    scores[risk_level] += 1
                    matched_keywords[risk_level].append(keyword)
        
        # Determine classification based on scores
        max_score = max(scores.values())
        if max_score == 0:
            risk_level = "GREEN"
            confidence = 0.5
        else:
            risk_level = max(scores, key=scores.get)
            confidence = min(0.9, 0.6 + (max_score * 0.1))
        
        return {
            "risk_level": risk_level,
            "confidence": confidence,
            "scores": scores,
            "matched_keywords": matched_keywords[risk_level],
            "explanation": self._generate_rule_explanation(risk_level, matched_keywords[risk_level])
        }
    
    def _combine_classifications(self, rule_based: Dict, rag_based: Dict) -> Dict[str, Any]:
        """Combine rule-based and RAG-based classifications"""
        # Weight the classifications (70% rule-based, 30% RAG for reliability)
        rule_weight = 0.7
        rag_weight = 0.3
        
        # Risk level priority: RED > AMBER > GREEN
        risk_priority = {"RED": 3, "AMBER": 2, "GREEN": 1}
        
        rule_priority = risk_priority.get(rule_based["risk_level"], 1)
        rag_priority = risk_priority.get(rag_based.get("risk_level", "GREEN"), 1)
        
        # Calculate weighted priority
        weighted_priority = (rule_priority * rule_weight) + (rag_priority * rag_weight)
        
        # Determine final risk level
        if weighted_priority >= 2.5:
            final_risk = "RED"
        elif weighted_priority >= 1.5:
            final_risk = "AMBER"
        else:
            final_risk = "GREEN"
        
        # Calculate combined confidence
        combined_confidence = (
            rule_based["confidence"] * rule_weight + 
            rag_based.get("confidence", 0.5) * rag_weight
        )
        
        # Create combined explanation
        combined_explanation = self._create_combined_explanation(rule_based, rag_based, final_risk)
        
        return {
            "risk_level": final_risk,
            "confidence": round(combined_confidence, 2),
            "explanation": combined_explanation
        }
    
    def _generate_rule_explanation(self, risk_level: str, matched_keywords: List[str]) -> str:
        """Generate explanation for rule-based classification"""
        if not matched_keywords:
            return "No specific risk indicators found in standard keyword analysis."
        
        keyword_text = ", ".join(matched_keywords[:3])  # Show top 3 keywords
        
        explanations = {
            "RED": f"High-risk terms detected: {keyword_text}. Requires immediate legal review and negotiation.",
            "AMBER": f"Medium-risk terms identified: {keyword_text}. Careful review and potential modification recommended.",
            "GREEN": f"Standard terms found: {keyword_text}. Generally acceptable with minimal risk."
        }
        
        return explanations.get(risk_level, "Standard contractual language.")
    
    def _create_combined_explanation(self, rule_based: Dict, rag_based: Dict, final_risk: str) -> str:
        """Create comprehensive explanation combining both analyses"""
        rule_explanation = rule_based.get("explanation", "")
        rag_explanation = rag_based.get("explanation", "")
        
        base_explanations = {
            "RED": "⚠️ HIGH RISK: This clause poses significant legal or financial risks.",
            "AMBER": "⚡ MEDIUM RISK: This clause requires careful consideration and review.", 
            "GREEN": "✅ LOW RISK: This clause appears to be standard and acceptable."
        }
        
        combined = f"{base_explanations[final_risk]} {rule_explanation}"
        
        if rag_explanation and rag_explanation != rule_explanation:
            combined += f" Additional analysis: {rag_explanation[:100]}..."
        
        return combined
    
    def _generate_recommendations(self, risk_level: str, clause_text: str) -> List[str]:
        """Generate specific recommendations based on risk level"""
        recommendations = {
            "RED": [
                "🔍 Immediate legal review required",
                "💼 Consider negotiating alternative terms",
                "⚖️ Assess potential financial exposure",
                "📋 Document all risk factors",
                "🤝 Seek mutual liability caps"
            ],
            "AMBER": [
                "📖 Review clause carefully",
                "🔄 Consider clarifying language",
                "💭 Understand implications fully",
                "⏰ Set appropriate timelines",
                "📞 Consult legal counsel if needed"
            ],
            "GREEN": [
                "✓ Standard clause - generally acceptable",
                "👀 Quick review for consistency",
                "📝 Ensure alignment with business terms",
                "🔗 Check integration with other clauses"
            ]
        }
        
        return recommendations.get(risk_level, ["Review clause as needed"])
    
    def _default_classification(self, clause_text: str) -> Dict[str, Any]:
        """Default classification when analysis fails"""
        return {
            "clause_text": clause_text,
            "risk_level": "AMBER",
            "explanation": "Unable to complete analysis. Manual review recommended.",
            "confidence": 0.3,
            "rule_based": {"risk_level": "AMBER", "confidence": 0.3},
            "rag_based": {"risk_level": "AMBER", "confidence": 0.3},
            "recommendations": ["Manual legal review required due to analysis error"]
        }
    
    def classify_document(self, clauses: List[Dict]) -> Dict[str, Any]:
        """Classify all clauses in a document"""
        try:
            classified_clauses = []
            risk_summary = {"RED": 0, "AMBER": 0, "GREEN": 0}
            
            for clause in clauses:
                classification = self.classify_clause(clause["text"])
                classified_clauses.append({
                    **clause,
                    "classification": classification
                })
                risk_summary[classification["risk_level"]] += 1
            
            # Calculate overall document risk
            total_clauses = len(classified_clauses)
            risk_percentage = {
                level: round((count / total_clauses) * 100, 1) 
                for level, count in risk_summary.items()
            }
            
            overall_risk = self._calculate_overall_risk(risk_summary)
            
            return {
                "classified_clauses": classified_clauses,
                "risk_summary": risk_summary,
                "risk_percentage": risk_percentage,
                "overall_risk": overall_risk,
                "total_clauses": total_clauses,
                "recommendations": self._generate_document_recommendations(overall_risk, risk_summary)
            }
            
        except Exception as e:
            logger.error(f"Error classifying document: {str(e)}")
            raise
    
    def _calculate_overall_risk(self, risk_summary: Dict[str, int]) -> str:
        """Calculate overall document risk level"""
        total = sum(risk_summary.values())
        if total == 0:
            return "GREEN"
        
        red_percentage = (risk_summary["RED"] / total) * 100
        amber_percentage = (risk_summary["AMBER"] / total) * 100
        
        if red_percentage > 20:
            return "RED"
        elif red_percentage > 0 or amber_percentage > 50:
            return "AMBER"
        else:
            return "GREEN"
    
    def _generate_document_recommendations(self, overall_risk: str, risk_summary: Dict[str, int]) -> List[str]:
        """Generate recommendations for the entire document"""
        recommendations = []
        
        if risk_summary["RED"] > 0:
            recommendations.append(f"🚨 {risk_summary['RED']} high-risk clauses require immediate attention")
        
        if risk_summary["AMBER"] > 0:
            recommendations.append(f"⚠️ {risk_summary['AMBER']} medium-risk clauses need review")
        
        if overall_risk == "RED":
            recommendations.extend([
                "💼 Recommend comprehensive legal review before signing",
                "🔄 Consider substantial revisions to high-risk clauses",
                "💰 Assess total financial exposure"
            ])
        elif overall_risk == "AMBER":
            recommendations.extend([
                "📖 Detailed review recommended",
                "🤝 Negotiate key terms where possible",
                "⚖️ Ensure risk mitigation measures"
            ])
        else:
            recommendations.append("✅ Document appears acceptable with standard risk levels")
        
        return recommendations 