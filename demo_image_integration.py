#!/usr/bin/env python3
"""
Demo script for testing Tavily image integration
This script tests the image search functionality without requiring Streamlit
"""

import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_image_markup_processing():
    """Test the image markup processing functionality"""
    print("\n🔍 Testing Image Markup Processing")
    print("=" * 50)
    
    # Test content with image requests
    test_content = """
    Welcome to our biology lesson on photosynthesis!
    
    <image>diagram of photosynthesis process in plants</image>
    
    Photosynthesis is the process by which plants convert sunlight into energy.
    Let's also look at the cellular structure:
    
    <image>labeled cross-section of a leaf showing chloroplasts</image>
    
    Understanding these concepts is crucial for biology.
    """
    
    # Import the processing function
    try:
        from components.image_display import process_image_markup
        cleaned_content, image_requests = process_image_markup(test_content)
        
        print(f"✅ Found {len(image_requests)} image requests:")
        for i, request in enumerate(image_requests, 1):
            print(f"   {i}. {request}")
        
        print(f"\n✅ Cleaned content length: {len(cleaned_content)} characters")
        print(f"✅ Image markup removed: {'<image>' not in cleaned_content}")
        
        return image_requests
        
    except ImportError as e:
        print(f"❌ Could not import image display component: {e}")
        return []

def test_tavily_api_connection():
    """Test connection to Tavily API"""
    print("\n🌐 Testing Tavily API Connection")
    print("=" * 50)
    
    try:
        from utils.tavily_integration import TavilyImageSearch, search_educational_image
        
        # Check if API key is available
        api_key = os.getenv('COPILOT_TAVILY_API_KEY')
        if not api_key:
            print("❌ No Tavily API key found in environment")
            return False
        
        print(f"✅ API key found: {api_key[:8]}...")
        
        # Initialize client
        client = TavilyImageSearch()
        print("✅ Tavily client initialized successfully")
        
        # Test search functionality
        print("\n🔍 Testing image search...")
        try:
            result = search_educational_image("photosynthesis diagram", "biology")
            
            if result:
                print(f"✅ Image search successful!")
                print(f"   URL: {result.url}")
                print(f"   Description: {result.description}")
                if result.source:
                    print(f"   Source: {result.source}")
                return True
            else:
                print("⚠️  No images found for test search")
                return False
                
        except Exception as e:
            print(f"❌ Image search failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import Tavily integration: {e}")
        return False
    except Exception as e:
        print(f"❌ Tavily API test failed: {e}")
        return False

def test_teaching_prompts():
    """Test that teaching prompts include image guidance"""
    print("\n📝 Testing Teaching Prompt Integration")
    print("=" * 50)
    
    try:
        from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE
        
        # Check for image guidance
        has_image_guidance = "EDUCATIONAL IMAGE GUIDANCE" in TEACHING_PROMPT_TEMPLATE
        has_image_examples = "<image>" in TEACHING_PROMPT_TEMPLATE
        
        print(f"✅ Image guidance section: {has_image_guidance}")
        print(f"✅ Image markup examples: {has_image_examples}")
        
        if has_image_guidance and has_image_examples:
            print("✅ Teaching prompts properly include image support!")
            return True
        else:
            print("❌ Teaching prompts missing image support")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import teaching prompts: {e}")
        return False

def main():
    """Main demo function"""
    print("🖼️ Autodidact Image Integration Demo")
    print("=" * 50)
    
    results = {
        'markup_processing': False,
        'tavily_connection': False,
        'teaching_prompts': False
    }
    
    # Test each component
    try:
        image_requests = test_image_markup_processing()
        results['markup_processing'] = len(image_requests) > 0
    except Exception as e:
        print(f"❌ Markup processing test failed: {e}")
    
    try:
        results['tavily_connection'] = test_tavily_api_connection()
    except Exception as e:
        print(f"❌ Tavily connection test failed: {e}")
    
    try:
        results['teaching_prompts'] = test_teaching_prompts()
    except Exception as e:
        print(f"❌ Teaching prompts test failed: {e}")
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All image integration tests passed!")
        print("\n📝 Next steps:")
        print("   1. Start the Streamlit app: streamlit run app.py")
        print("   2. Create a new course/lesson")
        print("   3. Include <image>description</image> tags in AI responses")
        print("   4. Verify images appear automatically")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)