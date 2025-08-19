#!/usr/bin/env python3
"""
Manual verification script for image URL validation functionality
This script demonstrates and tests the image URL validation feature
"""

import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_url_validation():
    """Test the URL validation functionality with real URLs"""
    from utils.tavily_integration import validate_image_url
    
    print("🔍 Testing URL Validation Functionality")
    print("=" * 50)
    
    # Test cases with real URLs that should work
    test_cases = [
        # Valid image URLs (we'll use placeholder URLs that should fail gracefully)
        ("https://httpbin.org/image/png", "PNG from httpbin", True),
        ("https://httpbin.org/image/jpeg", "JPEG from httpbin", True),
        
        # Invalid URLs
        ("https://httpbin.org/html", "HTML page", False),
        ("https://httpbin.org/status/404", "404 error", False),
        ("not-a-url", "Invalid URL format", False),
        ("", "Empty URL", False),
    ]
    
    for url, description, expected in test_cases:
        print(f"\n🔗 Testing: {description}")
        print(f"   URL: {url}")
        print(f"   Expected: {'✅ Valid' if expected else '❌ Invalid'}")
        
        try:
            result = validate_image_url(url, timeout=5)
            status = "✅ Valid" if result else "❌ Invalid"
            print(f"   Result: {status}")
            
            if result == expected:
                print("   ✅ Test PASSED")
            else:
                print("   ❌ Test FAILED")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")

def test_image_search_with_validation():
    """Test the image search with validation enabled"""
    print("\n\n🔍 Testing Image Search with Validation")
    print("=" * 50)
    
    try:
        from utils.tavily_integration import search_educational_image
        
        # Test if API key is available
        api_key = os.environ.get('COPILOT_TAVILY_API_KEY')
        if not api_key:
            print("⚠️  COPILOT_TAVILY_API_KEY not set - skipping live API tests")
            print("   Set the environment variable to test with real Tavily API")
            return
        
        print("🔑 API key found, testing with real Tavily API...")
        
        # Test search with validation enabled
        print("\n🔍 Searching for 'photosynthesis' with validation ENABLED...")
        result_with_validation = search_educational_image(
            "photosynthesis", 
            "biology", 
            validate_url=True
        )
        
        if result_with_validation:
            print(f"✅ Found validated image:")
            print(f"   URL: {result_with_validation.url}")
            print(f"   Description: {result_with_validation.description}")
            print(f"   Title: {result_with_validation.title}")
            print(f"   Source: {result_with_validation.source}")
        else:
            print("❌ No validated images found")
        
        # Test search with validation disabled for comparison
        print("\n🔍 Searching for 'photosynthesis' with validation DISABLED...")
        result_without_validation = search_educational_image(
            "photosynthesis", 
            "biology", 
            validate_url=False
        )
        
        if result_without_validation:
            print(f"✅ Found unvalidated image:")
            print(f"   URL: {result_without_validation.url}")
            print(f"   Description: {result_without_validation.description}")
        else:
            print("❌ No images found")
            
    except Exception as e:
        print(f"❌ Error during image search test: {e}")
        import traceback
        traceback.print_exc()

def test_integration_scenarios():
    """Test various integration scenarios"""
    print("\n\n🔍 Testing Integration Scenarios")
    print("=" * 50)
    
    try:
        from utils.tavily_integration import TavilyImageSearch
        
        api_key = os.environ.get('COPILOT_TAVILY_API_KEY')
        if not api_key:
            print("⚠️  COPILOT_TAVILY_API_KEY not set - skipping integration tests")
            return
            
        client = TavilyImageSearch()
        
        # Test 1: Search with validation, should filter out bad URLs
        print("\n📚 Test 1: Search with validation (max_results=2)")
        results = client.search_educational_images(
            "cell structure", 
            "biology",
            max_results=2,
            validate_urls=True
        )
        
        print(f"   Found {len(results)} validated images")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result.url}")
            print(f"      Desc: {result.description}")
        
        # Test 2: Search without validation for comparison
        print("\n📚 Test 2: Search without validation (max_results=2)")
        results_unvalidated = client.search_educational_images(
            "cell structure", 
            "biology",
            max_results=2,
            validate_urls=False
        )
        
        print(f"   Found {len(results_unvalidated)} unvalidated images")
        for i, result in enumerate(results_unvalidated, 1):
            print(f"   {i}. {result.url}")
            print(f"      Desc: {result.description}")
            
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("🧪 Image URL Validation - Manual Verification")
    print("=" * 60)
    print("This script tests the new image URL validation functionality")
    print("that ensures Tavily search results are actual image files.")
    print()
    
    # Run tests
    test_url_validation()
    test_image_search_with_validation()
    test_integration_scenarios()
    
    print("\n" + "=" * 60)
    print("🎯 Manual Verification Complete!")
    print()
    print("✅ The image URL validation feature is working correctly if:")
    print("   • URL validation correctly identifies valid vs invalid image URLs")
    print("   • Image search with validation returns only working image URLs")
    print("   • The retry logic finds valid images even if some URLs are bad")
    print("   • Error handling works gracefully when no valid images are found")

if __name__ == "__main__":
    main()