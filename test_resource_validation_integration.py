#!/usr/bin/env python3
"""
Integration test for resource creation validation.

This validates that the test harness correctly integrates with the existing 
components and provides actionable feedback for prompt improvement.
"""

import sys
import os
sys.path.append('.')

from test_resource_creation_harness import ResourceCreationHarness, ResourceType

def test_harness_integration():
    """Test that the harness integrates properly with existing components"""
    print("🧪 Testing Resource Creation Harness Integration")
    print("=" * 60)
    
    harness = ResourceCreationHarness()
    
    # Test that prompt template loads correctly
    assert len(harness.prompt_template) > 1000, "Prompt template should be substantial"
    print("✅ Prompt template loaded successfully")
    
    # Test that scenarios are created
    assert len(harness.test_scenarios) > 0, "Should have test scenarios"
    print(f"✅ Created {len(harness.test_scenarios)} test scenarios")
    
    # Test individual analysis functions
    latex_analysis = harness.analyze_prompt_for_resource_type(ResourceType.LATEX_MATH)
    jsxgraph_analysis = harness.analyze_prompt_for_resource_type(ResourceType.JSXGRAPH_DIAGRAM)
    image_analysis = harness.analyze_prompt_for_resource_type(ResourceType.TAVILY_IMAGE)
    
    print(f"✅ LaTeX analysis - Guidance: {latex_analysis.guidance_score:.2f}")
    print(f"✅ JSXGraph analysis - Guidance: {jsxgraph_analysis.guidance_score:.2f}")
    print(f"✅ Image analysis - Guidance: {image_analysis.guidance_score:.2f}")
    
    # Test AI decision simulation
    test_scenario = harness.test_scenarios[0]  # Use first scenario
    ai_decisions = harness.simulate_ai_decision(test_scenario)
    
    assert len(ai_decisions) == 3, "Should simulate all 3 resource types"
    print(f"✅ AI decision simulation working: {len(ai_decisions)} resource types evaluated")
    
    return True

def test_specific_scenarios():
    """Test specific scenarios that should work well"""
    print("\n🎯 Testing Specific Scenarios")
    print("=" * 60)
    
    harness = ResourceCreationHarness()
    
    # Test trigonometry scenario (should pass based on existing prompt improvements)
    trig_scenarios = [s for s in harness.test_scenarios if 'trigonometry' in s.description.lower()]
    if trig_scenarios:
        result = harness.run_scenario_test(trig_scenarios[0])
        print(f"Trigonometry test: {'✅ PASSED' if result.passed else '❌ FAILED'} (Score: {result.overall_score:.2f})")
        
        # Check that JSXGraph has high probability for trig
        jsx_prob = result.ai_decision_simulation.get(ResourceType.JSXGRAPH_DIAGRAM, 0)
        assert jsx_prob > 0.5, f"JSXGraph probability should be high for trig scenario, got {jsx_prob}"
        print("✅ JSXGraph correctly favored for trigonometry")
    
    # Test biology scenario (should favor images)
    bio_scenarios = [s for s in harness.test_scenarios if s.subject_area == 'biology']
    if bio_scenarios:
        result = harness.run_scenario_test(bio_scenarios[0])
        print(f"Biology test: {'✅ PASSED' if result.passed else '❌ FAILED'} (Score: {result.overall_score:.2f})")
        
        # Check that images have high probability for biology
        img_prob = result.ai_decision_simulation.get(ResourceType.TAVILY_IMAGE, 0)
        assert img_prob > 0.5, f"Image probability should be high for biology scenario, got {img_prob}"
        print("✅ Images correctly favored for biology")
    
    return True

def test_extensibility():
    """Test that the harness can be extended for new resource types"""
    print("\n🚀 Testing Extensibility for Future Resource Types")
    print("=" * 60)
    
    harness = ResourceCreationHarness()
    
    # Test that future resource types are handled gracefully
    youtube_analysis = harness.analyze_prompt_for_resource_type(ResourceType.YOUTUBE_VIDEO)
    animation_analysis = harness.analyze_prompt_for_resource_type(ResourceType.AI_ANIMATION)
    
    # Should return analysis with appropriate messages about not being implemented
    assert youtube_analysis.guidance_score == 0.0, "Unimplemented resource types should have zero guidance score"
    assert len(youtube_analysis.issues) > 0, "Should have issues noted for unimplemented types"
    assert "not implemented" in " ".join(youtube_analysis.issues).lower(), "Should mention not implemented"
    
    print("✅ Future resource types handled gracefully")
    print(f"✅ YouTube video analysis: {len(youtube_analysis.issues)} issues noted")
    print(f"✅ AI animation analysis: {len(animation_analysis.recommendations)} recommendations")
    
    return True

def test_output_generation():
    """Test that the harness generates useful output files"""
    print("\n📊 Testing Output Generation")
    print("=" * 60)
    
    harness = ResourceCreationHarness()
    
    # Run a couple of quick tests
    results = []
    for scenario in harness.test_scenarios[:3]:  # Just test first 3 for speed
        result = harness.run_scenario_test(scenario)
        results.append(result)
    
    harness.results = results
    
    # Test report generation
    report = harness.generate_report()
    assert len(report) > 1000, "Report should be substantial"
    assert "COMPREHENSIVE RESOURCE CREATION TEST HARNESS REPORT" in report, "Report should have proper header"
    print("✅ Report generation working")
    
    # Test JSON output
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_file = f.name
    
    try:
        harness.save_detailed_results(json_file)
        
        # Verify JSON file was created and has content
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert 'test_summary' in data, "JSON should have test summary"
        assert 'test_results' in data, "JSON should have test results"
        assert len(data['test_results']) == len(results), "JSON should have all results"
        print("✅ JSON output generation working")
        
    finally:
        # Clean up
        if os.path.exists(json_file):
            os.unlink(json_file)
    
    return True

def main():
    """Run all integration tests"""
    print("🔧 RESOURCE CREATION HARNESS INTEGRATION TESTS")
    print("=" * 80)
    
    tests = [
        ("Basic Integration", test_harness_integration),
        ("Specific Scenarios", test_specific_scenarios), 
        ("Extensibility", test_extensibility),
        ("Output Generation", test_output_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            test_func()
            print(f"✅ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
    
    print(f"\n📊 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests PASSED! The test harness is working correctly.")
        print("\n💡 The harness is ready to help fine-tune prompts for better AI resource selection.")
        print("Use test_resource_creation_harness.py to analyze and improve prompt effectiveness.")
        return True
    else:
        print("❌ Some integration tests FAILED. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)