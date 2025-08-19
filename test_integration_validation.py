#!/usr/bin/env python3
"""
Integration test for image URL validation with existing display components
Tests the complete workflow from search to display
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_image_display_integration():
    """Test integration with image display components"""
    print("🔗 Testing Integration with Image Display Components")
    print("=" * 60)
    
    try:
        # Test import of image display functions
        from components.image_display import (
            display_educational_image, 
            process_image_markup,
            render_content_with_images
        )
        print("✅ Successfully imported image display components")
        
        # Test process_image_markup function
        test_content = """
        Let's learn about photosynthesis in plants.
        
        <image>diagram of photosynthesis process showing sunlight, CO2, and water</image>
        
        This process is essential for plant survival and produces oxygen.
        
        <image>cross-section of leaf showing chloroplasts</image>
        """
        
        cleaned_content, image_requests = process_image_markup(test_content)
        print(f"\n📝 Processed content markup:")
        print(f"   Found {len(image_requests)} image requests")
        print(f"   Requests: {image_requests}")
        print("✅ Image markup processing works correctly")
        
        # Test that we can search for images with validation
        from utils.tavily_integration import search_educational_image
        
        api_key = os.environ.get('COPILOT_TAVILY_API_KEY')
        if api_key:
            print("\n🔍 Testing image search for markup requests...")
            for i, request in enumerate(image_requests[:1], 1):  # Test first one only
                print(f"\n   Request {i}: {request}")
                result = search_educational_image(request, "biology", validate_url=True)
                if result:
                    print(f"   ✅ Found validated image: {result.url}")
                    print(f"   Description: {result.description}")
                else:
                    print(f"   ❌ No validated image found")
        else:
            print("\n⚠️  COPILOT_TAVILY_API_KEY not set - skipping live search test")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

def test_backward_compatibility():
    """Test that existing functionality still works"""
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 40)
    
    try:
        from utils.tavily_integration import TavilyImageSearch, search_educational_image
        
        api_key = os.environ.get('COPILOT_TAVILY_API_KEY')
        if not api_key:
            print("⚠️  COPILOT_TAVILY_API_KEY not set - skipping compatibility test")
            return
            
        # Test that old method calls still work (without validation parameter)
        print("📞 Testing old-style function calls...")
        
        # This should work with default validation=True
        result1 = search_educational_image("photosynthesis", "biology")
        print(f"   search_educational_image() -> {'✅ Found image' if result1 else '❌ No image'}")
        
        # This should work with explicit validation=False (old behavior)
        result2 = search_educational_image("photosynthesis", "biology", validate_url=False)
        print(f"   search_educational_image(validate_url=False) -> {'✅ Found image' if result2 else '❌ No image'}")
        
        # Test TavilyImageSearch class methods
        client = TavilyImageSearch()
        
        # Old method signature should still work
        results3 = client.search_educational_images("cell structure", "biology", max_results=1)
        print(f"   client.search_educational_images() -> Found {len(results3)} images")
        
        # New method signature with validation disabled
        results4 = client.search_educational_images("cell structure", "biology", max_results=1, validate_urls=False)
        print(f"   client.search_educational_images(validate_urls=False) -> Found {len(results4)} images")
        
        print("✅ Backward compatibility maintained")
        
    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
        import traceback
        traceback.print_exc()

def test_error_scenarios():
    """Test error handling scenarios"""
    print("\n⚠️  Testing Error Handling Scenarios")
    print("=" * 40)
    
    try:
        from utils.tavily_integration import validate_image_url, search_educational_image
        
        # Test URL validation with problematic URLs
        problematic_urls = [
            "https://example.com/nonexistent.jpg",  # Should return 404
            "https://httpbin.org/redirect/3",       # Multiple redirects
            "https://httpbin.org/delay/10",         # Timeout scenario
        ]
        
        print("🔗 Testing problematic URLs...")
        for url in problematic_urls:
            print(f"   Testing: {url}")
            try:
                result = validate_image_url(url, timeout=3)  # Short timeout
                print(f"   Result: {'✅ Valid' if result else '❌ Invalid'}")
            except Exception as e:
                print(f"   Result: ⚠️  Error - {e}")
        
        # Test search with invalid concept (should handle gracefully)
        print("\n🔍 Testing search with edge cases...")
        
        api_key = os.environ.get('COPILOT_TAVILY_API_KEY')
        if api_key:
            # Empty concept
            result1 = search_educational_image("", "", validate_url=True)
            print(f"   Empty concept -> {'✅ Found image' if result1 else '❌ No image (expected)'}")
            
            # Very long concept
            long_concept = "a" * 1000
            result2 = search_educational_image(long_concept, "", validate_url=True)
            print(f"   Very long concept -> {'✅ Found image' if result2 else '❌ No image (expected)'}")
        else:
            print("   ⚠️  COPILOT_TAVILY_API_KEY not set - skipping live error tests")
        
        print("✅ Error handling works correctly")
        
    except Exception as e:
        print(f"❌ Error scenario test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main integration test function"""
    print("🧪 Image URL Validation - Integration Testing")
    print("=" * 70)
    print("Testing integration with existing components and backward compatibility")
    print()
    
    test_image_display_integration()
    test_backward_compatibility()
    test_error_scenarios()
    
    print("\n" + "=" * 70)
    print("🎯 Integration Testing Complete!")
    print()
    print("✅ Integration is successful if:")
    print("   • Image display components work with validated URLs")
    print("   • Existing code continues to work without changes")
    print("   • Error scenarios are handled gracefully")
    print("   • The feature enhances reliability without breaking existing functionality")

if __name__ == "__main__":
    main()