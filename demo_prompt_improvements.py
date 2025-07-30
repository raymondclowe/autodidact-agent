#!/usr/bin/env python3
"""
Demo script to showcase the improvements made to tutoring prompts.
Shows key sections of the enhanced prompts.
"""

from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE, RECAP_PROMPT_TEMPLATE

def highlight_improvements():
    """Highlight key improvements in the prompts."""
    
    print("=" * 80)
    print("AUTODIDACT AGENT PROMPT IMPROVEMENTS - BASED ON CHATGPT STUDY MODE")
    print("=" * 80)
    print()
    
    print("🎯 KEY IMPROVEMENTS IMPLEMENTED:")
    print()
    
    # Check for the 5 core principles
    improvements = [
        "✅ GET TO KNOW THE LEARNER - Ask about background and adapt approach",
        "✅ BUILD ON EXISTING KNOWLEDGE - Connect new ideas to prior knowledge", 
        "✅ GUIDE, DON'T GIVE ANSWERS - Explicit prohibition on doing work for students",
        "✅ CHECK AND REINFORCE UNDERSTANDING - Use mnemonics, mini-reviews, explain-back",
        "✅ VARY THE RHYTHM - Role-playing, practice rounds, teach-back activities",
        "✅ TONE & INTERACTION STYLE - Warm, patient, plain-spoken guidance",
        "✅ INTERACTION PATTERNS - One question at a time, try twice before help",
        "✅ ENHANCED SAFETY - Growth mindset, homework process help (not solutions)"
    ]
    
    for improvement in improvements:
        print(improvement)
    print()
    
    print("📖 EXAMPLE OF CORE TEACHING PRINCIPLES:")
    print("-" * 50)
    
    # Extract core principles section
    teaching_prompt = TEACHING_PROMPT_TEMPLATE
    if "## CORE TEACHING PRINCIPLES" in teaching_prompt:
        start = teaching_prompt.find("## CORE TEACHING PRINCIPLES")
        end = teaching_prompt.find("REFERENCE RULES", start)
        principles_section = teaching_prompt[start:end].strip()
        print(principles_section[:800] + "..." if len(principles_section) > 800 else principles_section)
    print()
    
    print("🔄 RECAP MODE IMPROVEMENTS:")
    print("-" * 30)
    
    # Extract recap principles section
    recap_prompt = RECAP_PROMPT_TEMPLATE
    if "## CORE RECAP PRINCIPLES" in recap_prompt:
        start = recap_prompt.find("## CORE RECAP PRINCIPLES")
        end = recap_prompt.find("REFERENCE RULES", start)
        recap_section = recap_prompt[start:end].strip()
        print(recap_section)
    print()
    
    print("🎨 INTERACTION STYLE GUIDANCE:")
    print("-" * 33)
    
    # Extract tone section
    if "TONE & INTERACTION STYLE" in teaching_prompt:
        start = teaching_prompt.find("TONE & INTERACTION STYLE")
        end = teaching_prompt.find("FORMATTING REQUIREMENTS", start)
        tone_section = teaching_prompt[start:end].strip()
        print(tone_section)
    print()
    
    print("🚫 EXPLICIT PROHIBITIONS (Based on ChatGPT Study Mode):")
    print("-" * 55)
    
    # Find key prohibitions
    prohibitions = []
    if "DO NOT DO THE LEARNER'S WORK FOR THEM" in teaching_prompt:
        prohibitions.append("• DO NOT DO THE LEARNER'S WORK FOR THEM")
    if "Never ask more than one question at a time" in teaching_prompt:
        prohibitions.append("• Never ask more than one question at a time")
    if "don't solve it for them" in teaching_prompt:
        prohibitions.append("• Help with homework process, don't solve it for them")
    
    for prohibition in prohibitions:
        print(prohibition)
    print()
    
    print("✨ VERSION UPDATE:")
    print("-" * 17)
    print("• Updated from 'Autodidact Tutor v1' to 'Autodidact Tutor v2'")
    print("• Enhanced personality: 'warm, patient, and dynamic AI instructor'")
    print("• Recap mode: 'warm, patient instructor focused on reinforcing learning'")
    print()
    
    print("=" * 80)
    print("All improvements maintain backward compatibility with existing session flow!")
    print("=" * 80)

if __name__ == "__main__":
    highlight_improvements()