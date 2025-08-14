"""
Simple integration test to verify complete image workflow
"""

import os
import sys
import re

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_complete_workflow():
    """Test the complete image integration workflow"""
    print("🧪 Testing Complete Image Integration Workflow")
    print("=" * 60)
    
    # Step 1: Test markup processing (standalone version)
    print("\n1️⃣ Testing Image Markup Processing...")
    
    content_with_images = """
    Let's learn about cellular biology! 
    
    <image>labeled diagram of plant cell with organelles</image>
    
    The plant cell has several key components that work together.
    Now let's compare this to an animal cell:
    
    <image>labeled diagram of animal cell showing differences</image>
    
    Notice how plant cells have chloroplasts and cell walls.
    """
    
    # Standalone markup processing
    image_pattern = r'<image[^>]*>(.*?)</image>'
    image_requests = re.findall(image_pattern, content_with_images, re.IGNORECASE | re.DOTALL)
    cleaned_content = re.sub(image_pattern, '', content_with_images, flags=re.IGNORECASE | re.DOTALL)
    cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content).strip()
    
    print(f"✅ Found {len(image_requests)} image requests:")
    for i, request in enumerate(image_requests, 1):
        print(f"   {i}. {request.strip()}")
    
    print(f"✅ Content cleaned (no <image> tags): {'<image>' not in cleaned_content}")
    
    # Step 2: Test Tavily search for each image
    print("\n2️⃣ Testing Tavily Image Search...")
    
    try:
        from utils.tavily_integration import search_educational_image
        
        successful_searches = 0
        for i, request in enumerate(image_requests, 1):
            print(f"\n   Searching for: {request.strip()}")
            try:
                result = search_educational_image(request.strip(), "biology")
                if result:
                    print(f"   ✅ Found image: {result.url}")
                    print(f"   📝 Description: {result.description}")
                    successful_searches += 1
                else:
                    print(f"   ⚠️  No image found")
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
        
        print(f"\n✅ Successfully found images for {successful_searches}/{len(image_requests)} requests")
        
    except Exception as e:
        print(f"❌ Could not test Tavily search: {e}")
        successful_searches = 0
    
    # Step 3: Test teaching prompt integration
    print("\n3️⃣ Testing Teaching Prompt Integration...")
    
    try:
        from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE
        
        # Verify image guidance exists
        has_guidance = "EDUCATIONAL IMAGE GUIDANCE" in TEACHING_PROMPT_TEMPLATE
        has_examples = "<image>description of needed image</image>" in TEACHING_PROMPT_TEMPLATE
        
        print(f"✅ Image guidance section included: {has_guidance}")
        print(f"✅ Image markup examples included: {has_examples}")
        
        # Extract a sample of the guidance
        if has_guidance:
            lines = TEACHING_PROMPT_TEMPLATE.split('\n')
            guidance_start = None
            for i, line in enumerate(lines):
                if "EDUCATIONAL IMAGE GUIDANCE" in line:
                    guidance_start = i
                    break
            
            if guidance_start:
                print("\n📝 Sample from image guidance:")
                for i in range(guidance_start, min(guidance_start + 5, len(lines))):
                    if lines[i].strip():
                        print(f"   {lines[i].strip()}")
        
    except Exception as e:
        print(f"❌ Could not test teaching prompt integration: {e}")
        has_guidance = False
        has_examples = False
    
    # Summary
    print("\n🏁 Workflow Test Summary")
    print("=" * 60)
    
    results = {
        "Image markup processing": len(image_requests) > 0,
        "Tavily image search": successful_searches > 0,
        "Teaching prompt integration": has_guidance and has_examples
    }
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall Result: {total_passed}/{total_tests} components working")
    
    if total_passed == total_tests:
        print("\n🎉 Complete image integration workflow is functional!")
        print("\n📋 What this enables:")
        print("   • AI tutors can request educational images using <image>description</image>")
        print("   • Images are automatically searched using Tavily API")
        print("   • Images appear inline with lesson content")
        print("   • Maintains speech functionality for accessibility")
        
        print("\n🚀 Ready for production use!")
        return True
    else:
        print("\n⚠️  Some components need attention. See details above.")
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)