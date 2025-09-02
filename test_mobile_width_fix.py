#!/usr/bin/env python3
"""
Test for mobile width issue in JSXGraph containers.
Tests that JSXGraph containers are responsive on mobile devices.
"""

def test_mobile_responsive_container():
    """Test that JSXGraph containers are responsive for mobile"""
    print("Testing JSXGraph mobile responsiveness...")
    
    from components.jsxgraph_utils import create_jsxgraph_container
    
    # Test default container creation
    container_html = create_jsxgraph_container("mobile_test", width=400, height=300)
    print(f"Container HTML: {container_html}")
    
    # Check that the fix is implemented - should now be responsive
    assert 'width: 100%' in container_html, "Expected responsive width: 100%"
    assert 'max-width: 400px' in container_html, "Expected max-width constraint"
    assert 'height: 300px' in container_html, "Expected fixed height (height doesn't cause mobile issues)"
    
    print("✅ Container now uses responsive width with max-width constraint")
    
    return True

def test_create_html_demo():
    """Create an HTML demo to visually test mobile responsiveness"""
    print("\nCreating HTML demo for mobile testing...")
    
    from components.jsxgraph_utils import (
        create_jsxgraph_container, 
        create_basic_coordinate_system,
        get_jsxgraph_header
    )
    
    # Create a demo with fixed implementation
    container = create_jsxgraph_container("demo_graph", 400, 300)
    coordinate_system = create_basic_coordinate_system("demo_graph")
    header = get_jsxgraph_header()
    
    demo_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JSXGraph Mobile Width Fix Demo</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 0;
        }}
        .mobile-test {{
            max-width: 375px; /* iPhone width */
            margin: 20px auto;
            border: 2px solid #00aa00;
            padding: 10px;
            background: #f0f9f0;
        }}
        .desktop-test {{
            max-width: 1200px;
            margin: 20px auto;
            border: 2px solid #0000aa;
            padding: 10px;
            background: #f0f0f9;
        }}
        h3 {{
            margin-top: 0;
        }}
        .fixed-width-demo {{
            width: 400px;
            height: 300px;
            margin: 10px auto;
            border: 2px solid #ff0000;
            background: #fff0f0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #cc0000;
        }}
    </style>
</head>
<body>
    <h1>JSXGraph Mobile Width Fix Demo ✅</h1>
    
    <div class="mobile-test">
        <h3>Mobile Viewport (375px wide) - FIXED</h3>
        <p>✅ The JSXGraph below now fits without horizontal scrolling!</p>
        {container}
        {coordinate_system}
        
        <h4>Compare to old fixed width:</h4>
        <div class="fixed-width-demo">400px Fixed Width<br/>(Would overflow on mobile)</div>
    </div>
    
    <div class="desktop-test">
        <h3>Desktop Viewport</h3>
        <p>✅ The JSXGraph still works normally on desktop (max-width: 400px).</p>
        {create_jsxgraph_container("demo_graph2", 400, 300)}
        {create_basic_coordinate_system("demo_graph2")}
    </div>
    
    {header}
    
    <script>
        // Log viewport and container widths for debugging
        console.log('Viewport width:', window.innerWidth);
        const container1 = document.getElementById('demo_graph');
        const container2 = document.getElementById('demo_graph2');
        console.log('Container 1 actual width:', container1.offsetWidth);
        console.log('Container 1 computed width:', getComputedStyle(container1).width);
        console.log('Container 2 actual width:', container2.offsetWidth);
        console.log('Container 2 computed width:', getComputedStyle(container2).width);
    </script>
</body>
</html>
"""
    
    # Save demo file
    with open('/tmp/mobile_width_fixed_demo.html', 'w') as f:
        f.write(demo_html)
    
    print("✅ Fixed demo HTML created at /tmp/mobile_width_fixed_demo.html")
    print("  Open this file in a browser and resize to mobile width to verify the fix")
    
    return True

def main():
    """Run mobile width tests"""
    print("🧪 Testing JSXGraph Mobile Width Issue")
    print("=" * 50)
    
    tests = [
        test_mobile_responsive_container,
        test_create_html_demo,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ Tests completed - issue reproduction successful")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)