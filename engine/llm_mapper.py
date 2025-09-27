# engine/llm_mapper.py
import json
import re
from typing import Dict, Any
from config import Config

class LLMISTVONMapper:
    """Use Gemini AI to enhance ISTVON mapping with fallback"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = None
        
        # Only initialize Gemini if API key is valid
        if self.api_key and self.api_key != 'your-gemini-api-key-here':
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(Config.DEFAULT_MODEL)
            except ImportError:
                print("Warning: google-generativeai not available. Using rule-based fallback.")
            except Exception as e:
                print(f"Warning: Gemini initialization failed: {e}. Using rule-based fallback.")
    
    def enhance_mapping(self, natural_prompt: str, preliminary_map: Dict, context_analysis: Dict) -> Dict:
        """Use LLM to enhance and complete ISTVON mapping with fallback"""
        
        if not self.model:
            return preliminary_map  # Fallback if no LLM available
        
        system_prompt = self._build_enhancement_prompt(natural_prompt, preliminary_map, context_analysis)
        
        try:
            response = self.model.generate_content(system_prompt)
            enhanced_map = self._parse_llm_response(response.text)
            return self._merge_mappings(preliminary_map, enhanced_map)
        except Exception as e:
            print(f"LLM enhancement failed: {e}. Using rule-based mapping.")
            return preliminary_map  # Fallback to rule-based mapping
    
    def _build_enhancement_prompt(self, prompt: str, preliminary_map: Dict, context: Dict) -> str:
        return f"""
        You are an ISTVON framework expert. Enhance the preliminary ISTVON mapping.
        
        NATURAL PROMPT: "{prompt}"
        
        PRELIMINARY MAPPING (rule-based):
        {json.dumps(preliminary_map, indent=2)}
        
        CONTEXT ANALYSIS:
        - Domain: {context.get('domain', 'general')}
        - Complexity: {context.get('complexity', 'medium')}
        - Specificity: {context.get('specificity', 'medium')}
        
        ENHANCEMENT TASKS:
        1. Complete missing ISTVON elements intelligently based on the prompt
        2. Improve instructions to be clear and actionable
        3. Suggest appropriate tools and variables for the domain
        4. Define clear outcomes and success criteria
        5. Keep the response structured and machine-readable
        
        Return ONLY valid JSON matching this exact ISTVON schema:
        {{
            "I": ["array of instruction strings"],
            "S": {{"documents": [], "urls": [], "data_points": {{}}}},
            "T": ["array of tool strings"],
            "V": {{"tone": "", "length": "", "complexity": "", "format": ""}},
            "O": {{"format": "", "delivery": "", "success_criteria": []}},
            "N": {{"milestones": [], "completion_notice": false}}
        }}
        
        Return ONLY the JSON, no explanations or additional text.
        """
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response to extract JSON"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return {}
        except json.JSONDecodeError:
            return {}
    
    def _merge_mappings(self, rule_based: Dict, llm_enhanced: Dict) -> Dict:
        """Merge rule-based and LLM-enhanced mappings"""
        merged = rule_based.copy()
        
        for key in llm_enhanced:
            if key in merged:
                if isinstance(merged[key], list) and isinstance(llm_enhanced[key], list):
                    # Merge lists, avoiding duplicates
                    merged[key] = list(set(merged[key] + llm_enhanced[key]))
                elif isinstance(merged[key], dict) and isinstance(llm_enhanced[key], dict):
                    # Merge dictionaries
                    merged[key].update(llm_enhanced[key])
                else:
                    # Overwrite with LLM value
                    merged[key] = llm_enhanced[key]
            else:
                merged[key] = llm_enhanced[key]
        
        return merged
    
    def validate_sanitizability(self, prompt: str) -> Dict[str, Any]:
        """Use LLM to validate if a prompt can be sanitized"""
        
        if not self.model:
            return {"sanitizable": True, "reason": "LLM not available, assuming sanitizable"}  # Fallback
        
        validation_prompt = self._build_validation_prompt(prompt)
        
        try:
            response = self.model.generate_content(validation_prompt)
            return self._parse_validation_response(response.text)
        except Exception as e:
            print(f"LLM validation failed: {e}. Assuming sanitizable.")
            return {"sanitizable": True, "reason": "LLM validation failed, assuming sanitizable"}
    
    def _build_validation_prompt(self, prompt: str) -> str:
        return f"""
        You are a content safety validator. Analyze if the following prompt can be sanitized to be safe and appropriate.
        
        PROMPT: "{prompt}"
        
        TASK: Determine if this prompt can be rewritten/sanitized to be safe and appropriate for general use.
        
        CONSIDER:
        - Can harmful intent be removed while keeping the core request?
        - Can dangerous actions be replaced with safe alternatives?
        - Is the underlying request fundamentally harmful or just poorly worded?
        
        EXAMPLES:
        - "I want to blow up an apartment" → NOT SANITIZABLE (fundamentally harmful)
        - "How to hack a computer" → SANITIZABLE (can be "How to secure a computer")
        - "Write something violent" → SANITIZABLE (can be "Write something dramatic")
        
        Return ONLY a JSON response in this exact format:
        {{
            "sanitizable": true/false,
            "reason": "Brief explanation of why it can/cannot be sanitized"
        }}
        
        Return ONLY the JSON, no explanations or additional text.
        """
    
    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM validation response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                # Ensure required fields exist
                if "sanitizable" not in result:
                    result["sanitizable"] = True
                if "reason" not in result:
                    result["reason"] = "No reason provided"
                return result
            else:
                return {"sanitizable": True, "reason": "Could not parse LLM response"}
        except json.JSONDecodeError:
            return {"sanitizable": True, "reason": "Invalid JSON response from LLM"}