# engine/broker.py
from typing import Dict, Any, List, Tuple
from enum import Enum
import re
import json
from .pattern_matchers import ISTVONPatternMatcher
from .context_analyzers import ContextAnalyzer
from .llm_mapper import LLMISTVONMapper
from .completion_rules import ISTVONCompletionEngine
from .istvon_schema import ISTVONSchema

class BrokerDecision(Enum):
    """Broker decision types"""
    ALLOW = "ALLOW"           # Safe to proceed with LLM enhancement
    NEEDS_FIX = "NEEDS_FIX"   # Contains unsafe content, needs sanitization
    BLOCK = "BLOCK"          # Too dangerous, block completely

class ISTVONBroker:
    """Broker logic for enforcing safety and content filtering"""
    
    def __init__(self):
        self.pattern_matcher = ISTVONPatternMatcher()
        self.context_analyzer = ContextAnalyzer()
        self.llm_mapper = LLMISTVONMapper()
        self.completion_engine = ISTVONCompletionEngine()
        self.schema_validator = ISTVONSchema()
        
        # Unsafe content patterns
        self.unsafe_patterns = {
            "malicious": [
                r"(hack|exploit|attack|malware|virus|trojan)",
                r"(phishing|scam|fraud|steal|stealing)",
                r"(illegal|unlawful|criminal|terrorist)",
                r"(violence|harm|kill|murder|suicide)",
                r"(explosive|bomb|weapon|gun|knife|poison|blow.?up)",
                r"(self.?harm|self.?injury|cut.?myself|hurt.?myself)",
                r"(destroy|damage|break.?into|burglary|theft)"
            ],
            "inappropriate": [
                r"(explicit|pornographic|adult content)",
                r"(hate speech|discrimination|racist)",
                r"(harassment|bullying|threats)"
            ],
            "sensitive": [
                r"(personal data|private information|confidential)",
                r"(financial|banking|credit card|ssn)",
                r"(medical|health records|patient data)"
            ],
            "dangerous": [
                r"(make.?explosive|create.?bomb|build.?weapon)",
                r"(how.?to.?kill|how.?to.?harm|how.?to.?hurt)",
                r"(suicide|self.?destruct|end.?my.?life)",
                r"(attack.?people|hurt.?others|harm.?someone)",
                r"(illegal.?drug|drug.?manufacture|poison.?recipe)"
            ]
        }
        
        # COSTAR gap patterns (missing critical elements)
        self.costar_gaps = {
            "context": [r"context|background|situation"],
            "objective": [r"goal|objective|purpose|aim"],
            "success": [r"success|completion|done|finished"],
            "timeline": [r"when|time|deadline|schedule"],
            "audience": [r"for|target|audience|recipient"],
            "resources": [r"using|with|tools|resources"]
        }
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt and make broker decision"""
        
        # Step 1: Safety analysis
        safety_result = self._analyze_safety(prompt)
        
        # Step 2: COSTAR gap analysis
        costar_gaps = self._analyze_costar_gaps(prompt)
        
        # Step 3: Context analysis
        context = self.context_analyzer.analyze_prompt_context(prompt)
        
        # Step 4: Make broker decision
        decision = self._make_broker_decision(safety_result, costar_gaps, context)
        
        return {
            "decision": decision,
            "safety_analysis": safety_result,
            "costar_gaps": costar_gaps,
            "context": context,
            "recommendations": self._get_recommendations(decision, safety_result, costar_gaps)
        }
    
    def _analyze_safety(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt for unsafe content"""
        prompt_lower = prompt.lower()
        safety_issues = []
        risk_level = "low"
        
        for category, patterns in self.unsafe_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    safety_issues.append({
                        "category": category,
                        "pattern": pattern,
                        "severity": self._get_severity(category)
                    })
        
        # Determine overall risk level
        if any(issue["severity"] == "high" for issue in safety_issues):
            risk_level = "high"
        elif any(issue["severity"] == "medium" for issue in safety_issues):
            risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "issues": safety_issues,
            "is_safe": risk_level == "low"
        }
    
    def _analyze_costar_gaps(self, prompt: str) -> Dict[str, Any]:
        """Analyze for COSTAR gaps (missing critical elements)"""
        prompt_lower = prompt.lower()
        gaps = []
        
        for element, patterns in self.costar_gaps.items():
            if not any(re.search(pattern, prompt_lower) for pattern in patterns):
                gaps.append(element)
        
        return {
            "missing_elements": gaps,
            "completeness_score": (len(self.costar_gaps) - len(gaps)) / len(self.costar_gaps),
            "needs_enhancement": len(gaps) > 0
        }
    
    def _make_broker_decision(self, safety_result: Dict, costar_gaps: Dict, context: Dict) -> BrokerDecision:
        """Make broker decision based on analysis"""
        
        # Block if high risk
        if safety_result["risk_level"] == "high":
            return BrokerDecision.BLOCK
        
        # Needs fix if medium risk or significant gaps
        if (safety_result["risk_level"] == "medium" or 
            costar_gaps["completeness_score"] < 0.5):
            return BrokerDecision.NEEDS_FIX
        
        # Allow if safe and reasonably complete
        return BrokerDecision.ALLOW
    
    def _get_severity(self, category: str) -> str:
        """Get severity level for safety category"""
        severity_map = {
            "malicious": "high",
            "inappropriate": "medium", 
            "sensitive": "medium",
            "dangerous": "high"
        }
        return severity_map.get(category, "low")
    
    def _get_recommendations(self, decision: BrokerDecision, safety_result: Dict, costar_gaps: Dict) -> List[str]:
        """Get recommendations based on broker decision"""
        recommendations = []
        
        if decision == BrokerDecision.BLOCK:
            recommendations.append("❌ BLOCKED: Content contains high-risk elements")
            recommendations.append("Please revise your prompt to remove unsafe content")
        
        elif decision == BrokerDecision.NEEDS_FIX:
            if safety_result["risk_level"] != "low":
                recommendations.append("⚠️ Contains potentially unsafe content")
                recommendations.append("Consider removing or rephrasing sensitive terms")
            
            if costar_gaps["missing_elements"]:
                recommendations.append("📝 Missing critical elements:")
                for element in costar_gaps["missing_elements"]:
                    recommendations.append(f"  - {element.capitalize()}")
                recommendations.append("Consider adding more context and details")
        
        else:  # ALLOW
            recommendations.append("✅ Safe to proceed with ISTVON enhancement")
            if costar_gaps["completeness_score"] < 0.8:
                recommendations.append("💡 Consider adding more details for better results")
        
        return recommendations
    
    def process_with_broker(self, prompt: str) -> Dict[str, Any]:
        """Process prompt through broker with appropriate action"""
        
        analysis = self.analyze_prompt(prompt)
        decision = analysis["decision"]
        
        if decision == BrokerDecision.BLOCK:
            return {
                "success": False,
                "decision": "BLOCK",
                "reason": "Content blocked due to safety concerns",
                "analysis": analysis
            }
        
        elif decision == BrokerDecision.NEEDS_FIX:
            # Try to sanitize and enhance
            sanitized_prompt = self._sanitize_prompt(prompt)
            enhanced_prompt = self._enhance_prompt(sanitized_prompt, analysis)
            
            return {
                "success": True,
                "decision": "NEEDS_FIX",
                "original_prompt": prompt,
                "sanitized_prompt": sanitized_prompt,
                "enhanced_prompt": enhanced_prompt,
                "analysis": analysis
            }
        
        else:  # ALLOW
            # Proceed with normal ISTVON processing
            return {
                "success": True,
                "decision": "ALLOW",
                "prompt": prompt,
                "analysis": analysis
            }
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt by removing or replacing unsafe content"""
        sanitized = prompt
        
        # Replace unsafe terms with safer alternatives
        replacements = {
            r'\bhack\b': 'optimize',
            r'\bexploit\b': 'utilize',
            r'\battack\b': 'address',
            r'\bsteal\b': 'obtain',
            r'\bkill\b': 'stop',
            r'\bmurder\b': 'eliminate'
        }
        
        for pattern, replacement in replacements.items():
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def _enhance_prompt(self, prompt: str, analysis: Dict) -> str:
        """Enhance prompt by adding missing COSTAR elements"""
        enhanced = prompt
        gaps = analysis["costar_gaps"]["missing_elements"]
        
        enhancements = []
        
        if "context" in gaps:
            enhancements.append("Please provide context and background information.")
        
        if "objective" in gaps:
            enhancements.append("Please specify your goal or objective.")
        
        if "success" in gaps:
            enhancements.append("Please define what success looks like.")
        
        if "timeline" in gaps:
            enhancements.append("Please specify any time constraints or deadlines.")
        
        if "audience" in gaps:
            enhancements.append("Please specify your target audience.")
        
        if "resources" in gaps:
            enhancements.append("Please specify any tools or resources to use.")
        
        if enhancements:
            enhanced += "\n\nAdditional guidance: " + " ".join(enhancements)
        
        return enhanced
