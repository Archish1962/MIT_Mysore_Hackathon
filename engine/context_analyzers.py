# engine/context_analyzer.py
from typing import Dict, Any

class ContextAnalyzer:
    """Analyze prompt context for better ISTVON mapping"""
    
    def __init__(self):
        self.domain_keywords = {
            "technical": ["code", "programming", "software", "algorithm", "API", "technical", "develop"],
            "business": ["report", "strategy", "marketing", "sales", "business", "client", "professional"],
            "creative": ["story", "poem", "content", "creative", "narrative", "blog", "article"],
            "academic": ["research", "study", "paper", "thesis", "academic", "analysis", "summary"],
            "communication": ["email", "letter", "message", "communication", "announcement"]
        }
        
        self.complexity_indicators = {
            "simple": ["brief", "simple", "quick", "short", "basic"],
            "medium": ["detailed", "comprehensive", "analysis", "explain"],
            "complex": ["thorough", "in-depth", "research", "strategic", "comprehensive analysis"]
        }
    
    def analyze_prompt_context(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt context for better ISTVON mapping"""
        prompt_lower = prompt.lower()
        
        return {
            "domain": self._identify_domain(prompt_lower),
            "complexity": self._assess_complexity(prompt_lower),
            "specificity": self._measure_specificity(prompt_lower),
            "domain_specific_rules": self._apply_domain_rules(prompt_lower)
        }
    
    def _identify_domain(self, prompt: str) -> str:
        """Identify the primary domain of the prompt"""
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt)
            domain_scores[domain] = score
        
        best_domain = max(domain_scores, key=domain_scores.get)
        return best_domain if domain_scores[best_domain] > 0 else "general"
    
    def _assess_complexity(self, prompt: str) -> str:
        """Assess the complexity level of the prompt"""
        complexity_scores = {}
        
        for level, indicators in self.complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in prompt)
            complexity_scores[level] = score
        
        best_complexity = max(complexity_scores, key=complexity_scores.get)
        return best_complexity if complexity_scores[best_complexity] > 0 else "medium"
    
    def _measure_specificity(self, prompt: str) -> str:
        """Measure how specific/detailed the prompt is"""
        word_count = len(prompt.split())
        specific_indicators = ["specific", "detailed", "particular", "exact"]
        
        specificity_score = word_count / 10  # Normalize
        specificity_score += sum(1 for indicator in specific_indicators if indicator in prompt) * 2
        
        if specificity_score > 3:
            return "high"
        elif specificity_score > 1.5:
            return "medium"
        else:
            return "low"
    
    def _apply_domain_rules(self, prompt: str) -> Dict[str, Any]:
        """Apply domain-specific rules for ISTVON mapping"""
        domain = self._identify_domain(prompt)
        
        domain_rules = {
            "technical": {
                "default_tools": ["Code formatting", "Documentation standards", "Technical writing"],
                "default_outcome": {"format": "Technical document", "delivery": "Structured format"},
                "common_variables": {"complexity": "Technical", "format": "Markdown/Code"}
            },
            "business": {
                "default_tools": ["Business frameworks", "Professional templates", "Industry standards"],
                "default_outcome": {"format": "Business document", "delivery": "Professional format"},
                "common_variables": {"tone": "Professional", "length": "Comprehensive"}
            },
            "creative": {
                "default_tools": ["Creative writing techniques", "Style guides", "Literary devices"],
                "default_outcome": {"format": "Creative content", "delivery": "Engaging format"},
                "common_variables": {"tone": "Engaging", "format": "Narrative"}
            },
            "academic": {
                "default_tools": ["Academic standards", "Citation formats", "Research methodologies"],
                "default_outcome": {"format": "Academic paper", "delivery": "Formal structure"},
                "common_variables": {"tone": "Formal", "complexity": "Detailed"}
            },
            "communication": {
                "default_tools": ["Communication templates", "Professional etiquette", "Format guidelines"],
                "default_outcome": {"format": "Communication document", "delivery": "Direct delivery"},
                "common_variables": {"tone": "Appropriate", "length": "Concise"}
            }
        }
        
        return domain_rules.get(domain, {})