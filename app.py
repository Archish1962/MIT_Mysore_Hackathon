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
            
            if not broker_result["success"]:
                # Content was blocked by broker
                processing_time = int((time.time() - start_time) * 1000)
                self.db_manager.log_transformation(
                    prompt, {}, False, 
                    "blocked", processing_time
                )
                return {
                    "success": False,
                    "error": broker_result.get("reason", "Content blocked for safety reasons"),
                    "processing_time": processing_time,
                    "blocked": True,
                    "recommendations": broker_result.get("analysis", {}).get("recommendations", [])
                }
            
            # Step 2: Analyze context
            context = self.context_analyzer.analyze_prompt_context(prompt)
            
            # Step 2: Create preliminary mapping
            preliminary_map = self._create_preliminary_mapping(prompt, context)
            
            # Step 3: Enhance with LLM (if available)
            enhanced_map = self.llm_mapper.enhance_mapping(prompt, preliminary_map, context)
            
            # Step 4: Apply completion rules
            final_map = self.completion_engine.apply_completion_rules(enhanced_map, context)
            
            # Step 5: Validate against schema
            validated_map = self.schema.validate_istvon(final_map)
            
            # Step 6: Log the transformation
            processing_time = int((time.time() - start_time) * 1000)
            self.db_manager.log_transformation(
                prompt, validated_map, True, 
                context.get('domain', 'auto'), processing_time
            )
            
            return {
                "success": True,
                "istvon": validated_map,
                "context": context,
                "processing_time": processing_time
            }
            
        except Exception as e:
            # Log failed transformation
            processing_time = int((time.time() - start_time) * 1000)
            self.db_manager.log_transformation(
                prompt, {}, False, 
                "error", processing_time
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
                    st.success("✅ Prompt processed successfully!")
                    
                    # Display results in tabs
                    tab1, tab2, tab3 = st.tabs(["🎯 ISTVON JSON", "📊 Context Analysis", "⏱️ Processing Info"])
                    
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
                
                else:
                    if result.get("blocked", False):
                        st.error("🛡️ **Content Blocked for Safety**")
                        st.error(f"❌ {result['error']}")
                        
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
    
    # Footer
    st.markdown("---")
    st.markdown("**ISTVON Framework**: Instructions, Sources, Tools, Variables, Outcome, Notifications")

if __name__ == "__main__":
    main()