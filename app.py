# app.py - Full ISTVON Prompt Enhancement Engine
import streamlit as st
import sys
import os
import time
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from config import Config
from database import DatabaseManager
from engine.istvon_schema import ISTVONSchema
from engine.context_analyzers import ContextAnalyzer
from engine.completion_rules import ISTVONCompletionEngine
from engine.llm_mapper import LLMISTVONMapper
from engine.broker import ISTVONBroker, BrokerDecision
from utils.helpers import HelperFunctions, ExamplePrompts

class ISTVONEngine:
    """Main ISTVON processing engine"""
    
    def __init__(self):
        self.schema = ISTVONSchema()
        self.context_analyzer = ContextAnalyzer()
        self.completion_engine = ISTVONCompletionEngine()
        self.llm_mapper = LLMISTVONMapper()
        self.broker = ISTVONBroker()
        self.db_manager = DatabaseManager()
    
    def process_prompt(self, prompt: str) -> dict:
        """Process a natural language prompt into ISTVON JSON"""
        start_time = time.time()
        
        try:
            # Step 1: Safety check with broker
            broker_result = self.broker.process_with_broker(prompt)
            
            # Extract broker decision details
            verdict = broker_result.get("verdict", "UNKNOWN")
            reason = broker_result.get("reason", "No reason provided")
            
            if not broker_result["success"]:
                # Content was blocked by broker
                processing_time = int((time.time() - start_time) * 1000)
                # Note: Rule engine decision is already logged to JSON file by broker
                return {
                    "success": False,
                    "error": reason,
                    "processing_time": processing_time,
                    "blocked": True,
                    "verdict": verdict,
                    "reason": reason,
                    "recommendations": broker_result.get("analysis", {}).get("recommendations", [])
                }
            
            # Step 2: LLM Validation - Check if prompt is sanitizable
            validation_result = self.llm_mapper.validate_sanitizability(prompt)
            
            if not validation_result.get("sanitizable", True):
                # Prompt cannot be sanitized, block it
                processing_time = int((time.time() - start_time) * 1000)
                block_reason = f"Blocked due to: {validation_result.get('reason', 'Cannot be sanitized')}"
                
                # Log the block decision to JSON file
                from utils.json_logger import RuleEngineLogger
                json_logger = RuleEngineLogger()
                json_logger.log_decision(prompt, "BLOCK", block_reason)
                
                return {
                    "success": False,
                    "error": block_reason,
                    "processing_time": processing_time,
                    "blocked": True,
                    "verdict": "BLOCK",
                    "reason": block_reason,
                    "llm_validated": True
                }
            
            # Step 3: Analyze context
            context = self.context_analyzer.analyze_prompt_context(prompt)
            
            # Step 4: Create preliminary mapping
            preliminary_map = self._create_preliminary_mapping(prompt, context)
            
            # Step 5: Enhance with LLM (if available)
            enhanced_map = self.llm_mapper.enhance_mapping(prompt, preliminary_map, context)
            
            # Step 6: Apply completion rules
            final_map = self.completion_engine.apply_completion_rules(enhanced_map, context)
            
            # Step 7: Validate against schema
            validated_map = self.schema.validate_istvon(final_map)
            
            # Step 8: Log the transformation with broker details
            processing_time = int((time.time() - start_time) * 1000)
            sanitized_prompt = broker_result.get("sanitized_prompt")
            self.db_manager.log_transformation(
                prompt, validated_map, True, 
                context.get('domain', 'auto'), processing_time, 
                verdict, reason, sanitized_prompt
            )
            
            return {
                "success": True,
                "istvon": validated_map,
                "context": context,
                "processing_time": processing_time,
                "verdict": verdict,
                "reason": reason,
                "sanitized_prompt": sanitized_prompt
            }
            
        except Exception as e:
            # Log failed transformation
            processing_time = int((time.time() - start_time) * 1000)
            self.db_manager.log_transformation(
                prompt, {}, False, 
                "error", processing_time, "ERROR", str(e)
            )
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time
            }
    
    def _create_preliminary_mapping(self, prompt: str, context: dict) -> dict:
        """Create a preliminary ISTVON mapping based on rules"""
        mapping = {
            "I": [f"Execute the requested task: {prompt[:100]}..."],
            "O": {
                "format": "Text response",
                "delivery": "Inline display",
                "success_criteria": ["Meets user requirements", "High quality output"]
            }
        }
        
        # Add domain-specific elements
        domain = context.get('domain', 'general')
        if domain != 'general':
            domain_config = Config.get_domain_config(domain)
            if domain_config.get('default_tools'):
                mapping["T"] = domain_config['default_tools']
            if domain_config.get('default_variables'):
                mapping["V"] = domain_config['default_variables']
        
        return mapping
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini API"""
        try:
            import google.generativeai as genai
            from config import Config
            
            # Configure Gemini
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel(Config.DEFAULT_MODEL)
            
            # Generate response
            response = model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            else:
                return "No response generated"
                
        except Exception as e:
            return f"Error generating response: {str(e)}"

def setup_environment():
    """Setup environment with error handling"""
    try:
        # Test imports
        from database import DatabaseManager
        from config import Config
        from engine.istvon_schema import ISTVONSchema
        from engine.context_analyzers import ContextAnalyzer
        from engine.completion_rules import ISTVONCompletionEngine
        from engine.llm_mapper import LLMISTVONMapper
        return True
    except ImportError as e:
        st.error(f"Import error: {e}")
        return False

def main():
    """Main application function"""
    
    # Set page config - MUST be first Streamlit command
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout=Config.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.title("🚀 ISTVON Prompt Enhancement Engine")
    st.markdown("Transform natural language prompts into structured ISTVON JSON")
    
    # Check if environment is setup correctly
    with st.spinner("Checking environment..."):
        if not setup_environment():
            st.error("❌ Environment setup failed. Please check the error above.")
            return
    
    st.success("✅ Environment loaded successfully!")
    
    # Initialize the engine
    engine = ISTVONEngine()
    
    # Sidebar with examples and analytics
    with st.sidebar:
        st.header("📚 Example Prompts")
        
        example_type = st.selectbox(
            "Choose an example:",
            ["Select...", "business_email", "technical_doc", "blog_post", "research_summary"]
        )
        
        if example_type != "Select...":
            example_prompt = ExamplePrompts.get_example(example_type)
            st.text_area("Example:", value=example_prompt, height=100, disabled=True)
        
        st.header("📊 Analytics")
        try:
            analytics = engine.db_manager.get_analytics()
            st.metric("Total Transformations", analytics.get('total_transformations', 0))
            st.metric("Success Rate", f"{analytics.get('success_rate', 0):.1f}%")
            st.metric("Avg Prompt Length", f"{analytics.get('avg_prompt_length', 0):.0f} chars")
        except:
            st.info("No analytics data yet")
        
        st.header("🔧 Recent Sanitized Prompts")
        try:
            sanitized_prompts = engine.db_manager.get_sanitized_prompts(5)
            if sanitized_prompts:
                for i, prompt_data in enumerate(sanitized_prompts, 1):
                    with st.expander(f"Prompt {i} - {prompt_data['verdict']}"):
                        st.write("**Original:**", prompt_data['original_prompt'][:100] + "...")
                        st.write("**Sanitized:**", prompt_data['sanitized_prompt'][:100] + "...")
                        st.write("**Time:**", prompt_data['timestamp'])
            else:
                st.info("No sanitized prompts yet")
        except:
            st.info("No sanitized prompts data yet")
    
    # Main input area
    st.subheader("📝 Enter Your Prompt")
    
    # Text area for prompt input
    prompt = st.text_area(
        "Natural language prompt:",
        placeholder="e.g., 'Write a professional email about product launch'",
        height=100,
        max_chars=Config.MAX_PROMPT_LENGTH
    )
    
    # Character count
    if prompt:
        st.caption(f"Characters: {len(prompt)}/{Config.MAX_PROMPT_LENGTH}")
    
    # Process button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        process_btn = st.button("🔄 Enhance with ISTVON", type="primary")
    
    with col2:
        clear_btn = st.button("🗑️ Clear")
    
    if clear_btn:
        st.rerun()
    
    # Process the prompt
    if process_btn:
        if prompt:
            with st.spinner("Processing your prompt..."):
                result = engine.process_prompt(prompt)
                
                if result["success"]:
                    # Store result in session state to avoid re-processing
                    st.session_state['istvon_result'] = result
                    st.session_state['original_prompt'] = prompt
                    st.success("✅ Prompt processed successfully!")
                    
                    # Display verdict and reason
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Verdict:** {result.get('verdict', 'N/A')}")
                    with col2:
                        st.info(f"**Reason:** {result.get('reason', 'N/A')}")
                    
                    # Just show success message - detailed results will be shown in session state section below
                
                else:
                    if result.get("blocked", False):
                        st.error("🛡️ **Content Blocked for Safety**")
                        st.error(f"❌ {result['error']}")
                        
                        # Show verdict and reason
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**Verdict:** {result.get('verdict', 'N/A')}")
                        with col2:
                            st.info(f"**Reason:** {result.get('reason', 'N/A')}")
                        
                        # Show safety recommendations
                        if result.get("recommendations"):
                            st.warning("💡 **Safety Recommendations:**")
                            for rec in result["recommendations"]:
                                st.write(f"• {rec}")
                        
                        st.info("🔄 **Please rephrase your prompt with appropriate language**")
                    else:
                        st.error(f"❌ Processing failed: {result['error']}")
        else:
            st.warning("Please enter a prompt first.")
    
    # Display ISTVON result from session state (if exists)
    if 'istvon_result' in st.session_state:
        result = st.session_state['istvon_result']
        
        st.markdown("---")
        st.success("✅ ISTVON Framework Generated Successfully!")
        
        # Display verdict and reason
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Verdict:** {result.get('verdict', 'N/A')}")
        with col2:
            st.info(f"**Reason:** {result.get('reason', 'N/A')}")
        
        # Display results in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 ISTVON JSON", "📊 Context Analysis", "🔧 Generate Response", "⏱️ Processing Info"])
        
        with tab1:
            st.subheader("Generated ISTVON JSON")
            st.json(result["istvon"])
            
            # Download button
            json_str = json.dumps(result["istvon"], indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"istvon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with tab2:
            st.subheader("Context Analysis")
            context = result["context"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Domain", context.get('domain', 'general'))
            with col2:
                st.metric("Complexity", context.get('complexity', 'medium'))
            with col3:
                st.metric("Specificity", context.get('specificity', 'medium'))
            
            if context.get('domain_specific_rules'):
                st.subheader("Domain Rules Applied")
                st.json(context['domain_specific_rules'])
        
        with tab3:
            st.subheader("🚀 Generate Response")
            
            # Get instructions from ISTVON "I" section
            istvon_instructions = result["istvon"].get("I", [])
            
            if istvon_instructions:
                st.write("**Select a prompt from ISTVON Instructions:**")
                
                # Create dropdown with ISTVON instructions
                selected_instruction = st.selectbox(
                    "Choose an instruction prompt:",
                    istvon_instructions,
                    key="instruction_selector"
                )
                
                # Generate response button
                col1, col2 = st.columns([1, 3])
                with col1:
                    generate_response_btn = st.button("🚀 Generate Response", type="primary", key="generate_response_from_istvon")
                
                # Generate response if button clicked
                if generate_response_btn and selected_instruction:
                    with st.spinner("Generating response..."):
                        response = engine.generate_response(selected_instruction)
                        
                        # Log the response generation
                        engine.db_manager.log_transformation(
                            selected_instruction, result["istvon"], True,
                            result["context"].get('domain', 'auto'), 0,
                            result.get('verdict', 'ALLOW'), result.get('reason', 'ISTVON instruction'),
                            selected_instruction, response
                        )
                        
                        st.success("✅ Response generated successfully!")
                        st.text_area("Generated Response:", value=response, height=200, key="response_output")
            else:
                st.warning("No instructions found in ISTVON framework.")
        
        with tab4:
            st.subheader("Processing Information")
            st.metric("Processing Time", f"{result['processing_time']} ms")
            st.metric("API Status", "✅ Configured" if Config.is_api_configured() else "⚠️ Using fallback")
            
            # Show recent transformations
            st.subheader("Recent Transformations")
            try:
                recent = engine.db_manager.get_recent_transformations(3)
                for item in recent:
                    status_icon = "✅" if item['success'] else "❌"
                    st.text(f"{status_icon} {item['prompt']} ({item['timestamp']})")
            except:
                st.info("No recent transformations")
    
    # Footer
    st.markdown("---")
    st.markdown("**ISTVON Framework**: Instructions, Sources, Tools, Variables, Outcome, Notifications")

if __name__ == "__main__":
    main()