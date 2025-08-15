#!/usr/bin/env python3
"""
Integration test for the trigonometry scenario specifically mentioned in the issue.

This test simulates the exact scenario: user asks about trigonometry with triangles
and requests diagrams. The AI should choose JSXGraph over image search.
"""

import sys
import os
sys.path.append('.')

from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE

def test_trig_scenario_prioritization():
    """Test that trigonometry triangle scenario is well-guided toward JSXGraph."""
    print("="*60)
    print("TESTING: Trigonometry Triangle Scenario")
    print("Simulating: User asks for triangle diagrams to understand sin/cos")
    print("="*60)
    
    # Extract the sections we care about
    sections = {
        'interactive_start': TEACHING_PROMPT_TEMPLATE.find("INTERACTIVE DIAGRAMS FIRST"),
        'static_start': TEACHING_PROMPT_TEMPLATE.find("STATIC IMAGES (Secondary Choice)"),
        'safety_start': TEACHING_PROMPT_TEMPLATE.find("SAFETY & STYLE")
    }
    
    # Validate section order
    print(f"✅ Section positions: Interactive={sections['interactive_start']}, Static={sections['static_start']}")
    assert sections['interactive_start'] < sections['static_start'], "Interactive should come before static"
    
    # Extract the interactive diagrams section
    interactive_section = TEACHING_PROMPT_TEMPLATE[
        sections['interactive_start']:sections['static_start']
    ]
    
    # Check for trigonometry-specific guidance
    trig_keywords = {
        'trigonometry': 'trigonometry' in interactive_section.lower(),
        'triangle': 'triangle' in interactive_section.lower(),
        'sine': 'sine' in interactive_section.lower() or 'sin' in interactive_section.lower(),
        'cosine': 'cosine' in interactive_section.lower() or 'cos' in interactive_section.lower(),
        'unit circle': 'unit circle' in interactive_section.lower()
    }
    
    print("\n📊 Trigonometry keyword coverage in Interactive Diagrams section:")
    for keyword, found in trig_keywords.items():
        status = "✅" if found else "❌"
        print(f"  {status} '{keyword}': {found}")
    
    # Should have at least 3 of the 5 keywords
    found_count = sum(trig_keywords.values())
    assert found_count >= 3, f"Insufficient trigonometry coverage: {found_count}/5 keywords found"
    
    # Check for prioritization language
    prioritization_phrases = [
        'prioritize interactive diagrams',
        'preferred for stem',
        'mathematical concepts',
        'avoid static images for mathematical'
    ]
    
    print("\n🎯 Prioritization guidance:")
    found_prioritization = []
    for phrase in prioritization_phrases:
        if phrase.lower() in TEACHING_PROMPT_TEMPLATE.lower():
            found_prioritization.append(phrase)
            print(f"  ✅ Found: '{phrase}'")
    
    assert len(found_prioritization) >= 2, f"Insufficient prioritization guidance: {found_prioritization}"
    
    print(f"\n✅ Trigonometry scenario adequately covered!")
    print(f"   Keywords: {found_count}/5, Prioritization: {len(found_prioritization)}/4")

def test_decision_flow():
    """Test that the decision flow is clear: Interactive first, static as fallback."""
    print("\n" + "="*60)
    print("TESTING: Decision Flow Clarity")
    print("="*60)
    
    # Check the flow of information
    template = TEACHING_PROMPT_TEMPLATE.lower()
    
    # Find key decision points
    interactive_pos = template.find("interactive diagrams first")
    mathematical_pos = template.find("mathematical concepts")
    avoid_static_pos = template.find("avoid static images for mathematical")
    secondary_choice_pos = template.find("secondary choice")
    
    positions = {
        'Interactive first': interactive_pos,
        'Mathematical concepts': mathematical_pos, 
        'Avoid static for math': avoid_static_pos,
        'Static as secondary': secondary_choice_pos
    }
    
    print("Decision flow positions:")
    for name, pos in positions.items():
        status = "✅" if pos != -1 else "❌"
        print(f"  {status} {name}: position {pos}")
    
    # Verify logical flow
    assert interactive_pos != -1, "Missing 'Interactive diagrams first' guidance"
    assert mathematical_pos != -1, "Missing mathematical concepts guidance"
    assert avoid_static_pos != -1, "Missing warning about static images for math"
    assert secondary_choice_pos != -1, "Missing secondary choice guidance"
    
    # Verify order makes sense
    assert interactive_pos < secondary_choice_pos, "Interactive guidance should come before static guidance"
    
    print("✅ Decision flow is logically ordered")

def test_specific_jsxgraph_examples():
    """Test that specific JSXGraph examples relevant to trig are present."""
    print("\n" + "="*60)
    print("TESTING: JSXGraph Examples for Trigonometry")
    print("="*60)
    
    template = TEACHING_PROMPT_TEMPLATE.lower()
    
    # Look for JSXGraph-specific examples that would help with trig
    jsxgraph_examples = [
        'triangle:',  # Template triangle
        'custom:',    # Custom JSXGraph
        'create(\'point\'',  # Point creation
        'create(\'circle\'', # Circle for unit circle
        'board.create',  # General creation syntax
    ]
    
    print("JSXGraph syntax examples:")
    found_examples = []
    for example in jsxgraph_examples:
        if example in template:
            found_examples.append(example)
            print(f"  ✅ Found: '{example}'")
        else:
            print(f"  ❌ Missing: '{example}'")
    
    assert len(found_examples) >= 3, f"Insufficient JSXGraph examples: {found_examples}"
    
    print(f"✅ JSXGraph examples adequate: {len(found_examples)}/5")

def simulate_ai_decision_process():
    """Simulate how an AI would interpret the prompt for the trig scenario."""
    print("\n" + "="*60)
    print("SIMULATING: AI Decision Process")
    print("Scenario: 'Can you show me a diagram of a triangle to help understand sine and cosine?'")
    print("="*60)
    
    # This simulates an AI reading the prompt and making decisions
    decision_factors = []
    
    template = TEACHING_PROMPT_TEMPLATE.lower()
    
    # Factor 1: Does the prompt mention prioritizing interactive for STEM?
    if 'prioritize interactive diagrams' in template and 'stem' in template:
        decision_factors.append("✅ STEM priority guidance found")
    else:
        decision_factors.append("❌ Missing STEM priority guidance")
    
    # Factor 2: Is trigonometry specifically mentioned as suitable for interactive?
    if 'trigonometry' in template and 'triangle' in template:
        decision_factors.append("✅ Trigonometry explicitly mentioned for interactive")
    else:
        decision_factors.append("❌ Trigonometry not explicitly mentioned")
    
    # Factor 3: Is there warning against static images for math?
    if 'avoid static images for mathematical' in template:
        decision_factors.append("✅ Warning against static images for math")
    else:
        decision_factors.append("❌ Missing warning against static for math")
    
    # Factor 4: Are there JSXGraph examples for triangles?
    if 'triangle:' in template:
        decision_factors.append("✅ Triangle template available")
    else:
        decision_factors.append("❌ No triangle template mentioned")
    
    # Factor 5: Is the guidance clear about when to use static vs interactive?
    if 'secondary choice' in template and 'non-mathematical content' in template:
        decision_factors.append("✅ Clear guidance on when to use static images")
    else:
        decision_factors.append("❌ Unclear guidance on image usage")
    
    print("AI Decision Factors:")
    for factor in decision_factors:
        print(f"  {factor}")
    
    positive_factors = sum(1 for f in decision_factors if f.startswith("✅"))
    
    print(f"\nDecision Score: {positive_factors}/5 factors favor JSXGraph")
    
    if positive_factors >= 4:
        print("🎉 AI would likely choose JSXGraph for trigonometry triangles!")
    elif positive_factors >= 3:
        print("⚠️  AI might choose JSXGraph, but guidance could be clearer")
    else:
        print("❌ AI might still choose static images - guidance needs improvement")
    
    assert positive_factors >= 4, f"Decision guidance not strong enough: {positive_factors}/5"

def main():
    """Run the comprehensive trigonometry scenario test."""
    print("🔍 COMPREHENSIVE TRIGONOMETRY SCENARIO TEST")
    print("Testing the exact issue: AI choosing image search over JSXGraph for trig")
    
    try:
        test_trig_scenario_prioritization()
        test_decision_flow()
        test_specific_jsxgraph_examples()
        simulate_ai_decision_process()
        
        print("\n" + "="*60)
        print("🎉 ALL TRIGONOMETRY SCENARIO TESTS PASSED!")
        print("The prompt improvements should resolve the issue.")
        print("AI should now choose JSXGraph over image search for triangle/trig diagrams.")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)