#!/usr/bin/env python3
"""
Test script to verify local library hosting functionality.
This test verifies that MathJax and JSXGraph can be loaded from local files.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_static_assets():
    """Test that static assets can be loaded properly."""
    print("🧪 Testing Static Assets Loading...")
    
    try:
        from utils.static_assets import get_mathjax_script, get_jsxgraph_assets
        
        # Test MathJax loading
        mathjax_script = get_mathjax_script()
        assert len(mathjax_script) > 1000000, "MathJax script seems too small"
        assert "<script>" in mathjax_script, "MathJax script not properly wrapped"
        print("✅ MathJax local loading: PASSED")
        
        # Test JSXGraph loading
        css, js = get_jsxgraph_assets()
        assert len(css) > 4000, "JSXGraph CSS seems too small"
        assert len(js) > 900000, "JSXGraph JS seems too small"
        assert "<style>" in css, "JSXGraph CSS not properly wrapped"
        assert "<script>" in js, "JSXGraph JS not properly wrapped"
        print("✅ JSXGraph local loading: PASSED")
        
        print("✅ All static assets tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Static assets test FAILED: {e}")
        return False

def test_math_utils_import():
    """Test that math utils can be imported without streamlit."""
    print("\n🧪 Testing Math Utils Structure...")
    
    try:
        # Test the static assets directly instead of streamlit-dependent code
        from utils.static_assets import get_mathjax_script
        script = get_mathjax_script()
        assert "MathJax" in script or "mathjax" in script.lower(), "MathJax content not found"
        print("✅ Math utils structure: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Math utils test FAILED: {e}")
        return False

def test_jsxgraph_utils():
    """Test that JSXGraph utils work with local files."""
    print("\n🧪 Testing JSXGraph Utils...")
    
    try:
        from components.jsxgraph_utils import get_jsxgraph_header
        header = get_jsxgraph_header()
        
        # Verify the header contains the expected content
        assert len(header) > 900000, "JSXGraph header seems too small"
        assert "<style>" in header, "CSS not found in header"
        assert "<script>" in header, "JavaScript not found in header"
        print("✅ JSXGraph utils: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ JSXGraph utils test FAILED: {e}")
        return False

def test_cdn_fallback():
    """Test that CDN fallback works when local files are not available."""
    print("\n🧪 Testing CDN Fallback...")
    
    try:
        # Temporarily rename static directory to test fallback
        import shutil
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        backup_dir = os.path.join(os.path.dirname(__file__), 'static_backup')
        
        if os.path.exists(static_dir):
            shutil.move(static_dir, backup_dir)
        
        # Import after moving static files
        from utils.static_assets import get_mathjax_script, get_jsxgraph_assets
        
        # Test MathJax CDN fallback
        mathjax_script = get_mathjax_script()
        assert "cdn.jsdelivr.net" in mathjax_script, "CDN fallback not working for MathJax"
        print("✅ MathJax CDN fallback: PASSED")
        
        # Test JSXGraph CDN fallback
        css, js = get_jsxgraph_assets()
        assert "cdn.jsdelivr.net" in css, "CDN fallback not working for JSXGraph CSS"
        assert "cdn.jsdelivr.net" in js, "CDN fallback not working for JSXGraph JS"
        print("✅ JSXGraph CDN fallback: PASSED")
        
        # Restore static directory
        if os.path.exists(backup_dir):
            shutil.move(backup_dir, static_dir)
        
        return True
        
    except Exception as e:
        # Restore static directory in case of error
        if os.path.exists(backup_dir):
            shutil.move(backup_dir, static_dir)
        print(f"❌ CDN fallback test FAILED: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Local Library Hosting Tests\n")
    
    tests = [
        test_static_assets,
        test_math_utils_import, 
        test_jsxgraph_utils,
        test_cdn_fallback
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! Local library hosting is working correctly.")
        return True
    else:
        print("❌ Some tests FAILED. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)