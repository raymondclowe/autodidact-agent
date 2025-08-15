#!/usr/bin/env python3
"""
Test for improved diagram selection - ensuring JSXGraph is prioritized over images for STEM content.

This test validates that the updated prompts guide AI models to choose interactive diagrams
over static images for mathematical concepts like trigonometry.
"""

import sys
import os
sys.path.append('.')

from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE

def test_prompt_contains_prioritization():
    """Test that the prompt contains proper prioritization guidance."""
    print("Testing prompt prioritization guidance...")
    
    # Check that interactive diagrams guidance comes before static images
    interactive_pos = TEACHING_PROMPT_TEMPLATE.find("INTERACTIVE DIAGRAMS FIRST")
    static_pos = TEACHING_PROMPT_TEMPLATE.find("STATIC IMAGES (Secondary Choice)")
    
    assert interactive_pos != -1, "Interactive diagrams guidance not found"
    assert static_pos != -1, "Static images guidance not found"
    assert interactive_pos < static_pos, "Interactive diagrams should come before static images"
    
    print("✅ Prioritization order correct")

def test_prompt_contains_decision_criteria():
    """Test that the prompt contains clear decision criteria."""
    print("Testing decision criteria...")
    
    # Check for key decision guidance
    required_phrases = [
        "PRIORITIZE interactive diagrams",
        "trigonometry",
        "triangles",
        "AVOID static images for mathematical concepts",
        "WHY CHOOSE INTERACTIVE OVER STATIC"
    ]
    
    for phrase in required_phrases:
        assert phrase.lower() in TEACHING_PROMPT_TEMPLATE.lower(), f"Missing guidance: {phrase}"
    
    print("✅ Decision criteria present")

def test_trig_example_guidance():
    """Test that trigonometry is specifically mentioned as a use case for interactive diagrams."""
    print("Testing trigonometry-specific guidance...")
    
    # Check that trigonometry is mentioned in the interactive diagrams section
    interactive_start = TEACHING_PROMPT_TEMPLATE.find("INTERACTIVE DIAGRAMS FIRST")
    static_start = TEACHING_PROMPT_TEMPLATE.find("STATIC IMAGES (Secondary Choice)")
    
    interactive_section = TEACHING_PROMPT_TEMPLATE[interactive_start:static_start]
    
    trig_keywords = ["trigonometry", "triangle", "unit circle", "sine", "cosine"]
    found_keywords = [kw for kw in trig_keywords if kw.lower() in interactive_section.lower()]
    
    assert len(found_keywords) >= 2, f"Insufficient trigonometry guidance. Found: {found_keywords}"
    
    print(f"✅ Trigonometry guidance present: {found_keywords}")

def test_warning_against_static_math():
    """Test that there's clear warning against using static images for math."""
    print("Testing warning against static images for math...")
    
    warnings = [
        "AVOID static images for mathematical concepts",
        "No generic images with mismatched labels"
    ]
    
    found_warnings = []
    for warning in warnings:
        if warning.lower() in TEACHING_PROMPT_TEMPLATE.lower():
            found_warnings.append(warning)
    
    assert len(found_warnings) >= 1, f"Missing warnings about static images for math. Found: {found_warnings}"
    
    print(f"✅ Math-specific warnings present: {found_warnings}")

def simulate_trig_scenario():
    """Simulate the scenario from the issue: user asking for triangle diagrams in trigonometry."""
    print("\nSimulating trigonometry scenario...")
    
    # This simulates what a teacher might say when asked for triangle diagrams
    scenario = """
    Student asks: "Can you show me a diagram of a triangle to help understand sine and cosine?"
    
    Expected behavior: AI should create an interactive JSXGraph triangle, not search for static images.
    """
    
    print(scenario)
    
    # Check that the prompt would guide toward JSXGraph
    interactive_section = TEACHING_PROMPT_TEMPLATE[
        TEACHING_PROMPT_TEMPLATE.find("INTERACTIVE DIAGRAMS FIRST"):
        TEACHING_PROMPT_TEMPLATE.find("STATIC IMAGES (Secondary Choice)")
    ]
    
    trig_mentioned = "trigonometry" in interactive_section.lower()
    triangle_mentioned = "triangle" in interactive_section.lower()
    
    print(f"Trigonometry mentioned in interactive section: {trig_mentioned}")
    print(f"Triangles mentioned in interactive section: {triangle_mentioned}")
    
    assert trig_mentioned and triangle_mentioned, "Trigonometry scenario not well covered"
    
    print("✅ Trigonometry scenario guidance is adequate")

def main():
    """Run all tests for the diagram selection improvement."""
    print("="*60)
    print("TESTING: Diagram Selection Improvement")
    print("Issue: AI choosing image search over JSXGraph for math concepts")
    print("="*60)
    
    try:
        test_prompt_contains_prioritization()
        test_prompt_contains_decision_criteria() 
        test_trig_example_guidance()
        test_warning_against_static_math()
        simulate_trig_scenario()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("The prompt improvements should help AI prioritize JSXGraph for STEM content")
        print("="*60)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("="*60)
        return False
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        print("="*60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)