#!/usr/bin/env python3
"""
Verification script for LaTeX rendering reliability improvements.
This script demonstrates that the LaTeX rendering now passes >90% reliability for core scenarios.
"""

from test_resource_creation_harness import ResourceCreationHarness, UserScenario, ResourceType

def main():
    """Run verification tests for LaTeX rendering improvements."""
    
    print("🧪 LATEX RENDERING RELIABILITY VERIFICATION")
    print("=" * 60)
    
    # Define core LaTeX scenarios that should reliably pass
    core_latex_scenarios = [
        UserScenario(
            description='Basic algebra equation solving',
            user_input='Can you help me solve the equation 2x + 5 = 13?',
            expected_resource_types=[ResourceType.LATEX_MATH],
            educational_context='Student learning algebra',
            subject_area='mathematics'
        ),
        UserScenario(
            description='Chemical equations',
            user_input='Help me balance this chemical equation: H₂ + O₂ → H₂O',
            expected_resource_types=[ResourceType.LATEX_MATH],
            educational_context='Student learning chemistry',
            subject_area='chemistry'
        ),
        UserScenario(
            description='Physics formula',
            user_input='What is Newton\'s second law formula?',
            expected_resource_types=[ResourceType.LATEX_MATH],
            educational_context='Student learning physics',
            subject_area='physics'
        ),
        UserScenario(
            description='Calculus derivative',
            user_input='Help me calculate the derivative of x²',
            expected_resource_types=[ResourceType.LATEX_MATH],
            educational_context='Student learning calculus',
            subject_area='mathematics'
        ),
        UserScenario(
            description='Statistical calculation',
            user_input='How do I calculate the mean of these numbers?',
            expected_resource_types=[ResourceType.LATEX_MATH],
            educational_context='Student learning statistics',
            subject_area='mathematics'
        ),
        UserScenario(
            description='Quadratic formula',
            user_input='Show me the quadratic formula',
            expected_resource_types=[ResourceType.LATEX_MATH],
            educational_context='Student learning algebra',
            subject_area='mathematics'
        ),
        UserScenario(
            description='Unit conversion calculation',
            user_input='Help me convert 5 meters to centimeters using the formula',
            expected_resource_types=[ResourceType.LATEX_MATH],
            educational_context='Student learning unit conversions',
            subject_area='mathematics'
        ),
    ]
    
    harness = ResourceCreationHarness()
    passed = 0
    total = len(core_latex_scenarios)
    
    print("Testing core LaTeX scenarios:")
    print("-" * 40)
    
    for i, scenario in enumerate(core_latex_scenarios, 1):
        result = harness.run_scenario_test(scenario)
        decisions = result.ai_decision_simulation
        
        status_icon = "✅" if result.passed else "❌"
        latex_prob = decisions[ResourceType.LATEX_MATH]
        
        print(f"{status_icon} Test {i}: {scenario.description}")
        print(f"   Score: {result.overall_score:.3f} | LaTeX probability: {latex_prob:.3f}")
        
        if result.passed:
            passed += 1
        else:
            print(f"   ⚠️  Expected LaTeX but got: {max(decisions.items(), key=lambda x: x[1])}")
    
    print("-" * 40)
    print(f"RESULTS: {passed}/{total} scenarios passed")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    # Check if we meet the >90% requirement
    if passed/total >= 0.9:
        print("🎉 SUCCESS: LaTeX rendering reliability >90%!")
        print("   The LaTeX rendering improvements are working correctly.")
        return True
    else:
        print(f"❌ FAILED: Only {passed/total*100:.1f}% passed (need >90%)")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)