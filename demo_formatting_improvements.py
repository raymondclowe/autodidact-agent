#!/usr/bin/env python3
"""
Demo script showing the formatting improvements in tutor prompts.

This demonstrates how the AI is now instructed to format multiple choice questions
and other content for better readability.
"""

from backend.tutor_prompts import format_teaching_prompt, format_recap_prompt

def demo_formatting_improvements():
    """Show how the updated prompts encourage better formatting."""
    print("=== FORMATTING IMPROVEMENTS DEMO ===\n")
    
    # Sample data for demonstration
    obj_id = "concept_1"
    obj_label = "Understanding Machine Learning Basics"
    recent = ["data preprocessing", "statistical foundations"]
    remaining = ["neural networks", "deep learning"]
    refs = [
        {
            "rid": "ml_intro", 
            "title": "Introduction to Machine Learning", 
            "section": "Chapter 1", 
            "type": "book", 
            "date": "2023-01-01"
        }
    ]
    
    print("1. TEACHING PROMPT WITH FORMATTING GUIDELINES:")
    print("=" * 50)
    formatted_prompt = format_teaching_prompt(obj_id, obj_label, recent, remaining, refs)
    
    # Extract and show the formatting requirements section
    lines = formatted_prompt.split('\n')
    formatting_section = False
    for line in lines:
        if "FORMATTING REQUIREMENTS" in line:
            formatting_section = True
        if formatting_section:
            print(line)
            if line.strip() == "BEGIN TUTORING":
                break
    
    print("\n2. KEY IMPROVEMENTS:")
    print("=" * 50)
    print("✅ AI is now explicitly instructed to use markdown formatting")
    print("✅ Specific guidelines for multiple choice questions:")
    print("   - Put questions on separate lines")
    print("   - Use **A)**, **B)**, **C)** format")
    print("   - Add proper spacing between elements")
    print("✅ Increased word limit from 150 to 180 words for better formatting")
    print("✅ Instructions for bullet points, numbered lists, and emphasis")
    
    print("\n3. EXPECTED IMPROVEMENTS IN LESSONS:")
    print("=" * 50)
    print("BEFORE (cramped formatting):")
    print("What is supervised learning? A) Learning with labeled data B) Learning without data C) Learning with unlabeled data")
    
    print("\nAFTER (improved formatting):")
    print("What is supervised learning?")
    print("")
    print("**A)** Learning with labeled data")
    print("**B)** Learning without data") 
    print("**C)** Learning with unlabeled data")
    
    print("\n4. RECAP PROMPT ALSO IMPROVED:")
    print("=" * 50)
    recent_los = ["basic ML concepts", "data preprocessing"]
    next_obj = "neural network fundamentals"
    
    recap_prompt = format_recap_prompt(recent_los, next_obj, refs)
    
    # Show that recap prompt also has formatting requirements
    if "FORMATTING REQUIREMENTS" in recap_prompt:
        print("✅ Recap prompts also include formatting guidelines")
        print("✅ Emphasis on numbered lists and clear spacing")
        print("✅ Increased word limit for better presentation")
    
    print("\n=== DEMO COMPLETE ===")
    print("The AI tutor will now generate better-formatted lessons!")

if __name__ == "__main__":
    demo_formatting_improvements()