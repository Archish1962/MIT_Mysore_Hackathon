# test_gemini.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API connectivity and available models"""
    
    print("🔍 Testing Gemini API Configuration...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return False
    
    if api_key == 'your-gemini-api-key-here' or len(api_key) < 10:
        print("❌ Please set a valid GEMINI_API_KEY in your .env file")
        print("   Current key:", api_key[:10] + "..." if len(api_key) > 10 else api_key)
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google-generativeai: {e}")
        print("💡 Try: pip install google-generativeai")
        return False
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        print("✅ Gemini configured successfully")
        
        # List available models
        print("\n📋 Fetching available models...")
        models = genai.list_models()
        
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.split('/')[-1]
                available_models.append(model_name)
                print(f"   🔹 {model_name}")
        
        if not available_models:
            print("❌ No generateContent models available")
            return False
        
        print(f"\n✅ Found {len(available_models)} available model(s)")
        
        # Test with gemini-pro (most common)
        test_model = 'gemini-pro'
        if test_model not in available_models:
            test_model = available_models[0]  # Use first available
        
        print(f"\n🧪 Testing with model: {test_model}")
        
        model = genai.GenerativeModel(test_model)
        response = model.generate_content("Say 'TEST SUCCESSFUL' in a creative way.")
        
        if response and response.text:
            print(f"✅ API Test Successful!")
            print(f"📝 Response: {response.text}")
            return True
        else:
            print("❌ Empty response from API")
            return False
            
    except Exception as e:
        print(f"❌ API Test Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your Gemini API is working correctly.")
    else:
        print("💡 Troubleshooting tips:")
        print("1. Check your .env file has the correct API key")
        print("2. Verify internet connectivity")
        print("3. Ensure your API key has proper permissions")
        print("4. Check if the API key is expired or invalid")