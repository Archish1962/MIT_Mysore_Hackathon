# engine/rule_engine.py
import time
from typing import Dict, Any
from .pattern_matchers import ISTVONPatternMatcher
from .context_analyzers import ContextAnalyzer
from .llm_mapper import LLMISTVONMapper
from .completion_rules import ISTVONCompletionEngine
from .istvon_schema import ISTVONSchema

class ISTVONRuleEngine:
    """Main rule engine for ISTVON mapping"""
    
    def __init__(self, use_llm: bool = True):
        self.pattern_matchers = ISTVONPatternMatcher()
        self.context_analyzer = ContextAnalyzer()
        self.completion_engine = ISTVONCompletionEngine()
        self.schema_validator = ISTVONSchema()
        
        # Initialize LLM mapper only if needed and API key is available
        self.use_llm = use_llm
        self.llm_mapper = LLMISTVONMapper() if use_llm else None
    
    def map_to_istvon(self, natural_prompt: str) -> Dict[str, Any]:
        """Map natural language prompt to ISTVON JSON"""
        start_time = time.time()
        
        try:
            # Step 1: Basic pattern matching
            preliminary_map = self.pattern_matchers.extract_istvon_elements(natural_prompt)
            
            # Step 2: Context analysis
            context_analysis = self.context_analyzer.analyze_prompt_context(natural_prompt)
            
            # Step 3: LLM-enhanced mapping for complex cases (if enabled)
            if self.use_llm and self.llm_mapper and self._needs_llm_assistance(preliminary_map, context_analysis):
                enhanced_map = self.llm_mapper.enhance_mapping(
                    natural_prompt, preliminary_map, context_analysis
                )
                final_map = enhanced_map
            else:
                final_map = preliminary_map
            
            # Step 4: Rule-based completion
            completed_map = self.completion_engine.apply_completion_rules(final_map, context_analysis)
            
            # Step 5: Schema validation
            validated_map = self.schema_validator.validate_istvon(completed_map)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "istvon_json": validated_map,
                "processing_time_ms": processing_time,
                "domain": context_analysis.get("domain", "general"),
                "used_llm": self.use_llm and self._needs_llm_assistance(preliminary_map, context_analysis)
            }
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "error": str(e),
                "processing_time_ms": processing_time,
                "istvon_json": {}
            }
    
    def _needs_llm_assistance(self, preliminary_map: Dict, context_analysis: Dict) -> bool:
        """Determine if LLM assistance is needed"""
        # Check if instructions are too vague
        instructions = preliminary_map.get("I", [])
        if not instructions or len(instructions) == 0:
            return True
        
        # Check if context suggests complexity
        complexity = context_analysis.get("complexity", "medium")
        specificity = context_analysis.get("specificity", "medium")
        
        if complexity == "complex" or specificity == "low":
            return True
        
        # Check if critical elements are missing
        if not preliminary_map.get("O") or not preliminary_map.get("V"):
            return True
        
        return False