"""
Answer normalization utilities for handling single character answers in multiple choice questions.
"""

import re
from typing import Optional, List, Tuple


def detect_multiple_choice_pattern(question: str) -> Optional[str]:
    """
    Detect if a question contains multiple choice options.
    
    Returns:
        'numbered' if question has numbered options (1., 2., 3., etc.)
        'lettered' if question has lettered options (A., B., C., etc. or A), B), C), etc.)
        None if no multiple choice pattern is detected
    """
    # Check for numbered patterns: "1. ", "2. ", etc.
    numbered_pattern = r'\b\d+\.\s+\w'
    if re.search(numbered_pattern, question):
        return 'numbered'
    
    # Check for lettered patterns: "A. ", "B. ", "A) ", "B) ", etc.
    lettered_pattern = r'\b[A-Za-z][\.\)]\s+\w'
    if re.search(lettered_pattern, question):
        return 'lettered'
    
    return None


def extract_multiple_choice_options(question: str) -> List[Tuple[str, str]]:
    """
    Extract multiple choice options from a question.
    
    Returns:
        List of tuples (choice_key, choice_text) where:
        - choice_key is the number/letter (e.g., "1", "A")
        - choice_text is the full option text
    """
    options = []
    
    # Try numbered pattern first
    # Handle both newline-separated and inline options
    numbered_matches = re.finditer(r'(\d+)\.\s+(.+?)(?=\s+\d+\.|$)', question, re.MULTILINE)
    for match in numbered_matches:
        choice_key = match.group(1)
        choice_text = match.group(2).strip()
        options.append((choice_key, choice_text))
    
    if options:
        return options
    
    # Try lettered pattern
    # Handle both newline-separated and inline options
    lettered_matches = re.finditer(r'([A-Za-z])[\.\)]\s+(.+?)(?=\s+[A-Za-z][\.\)]|$)', question, re.MULTILINE)
    for match in lettered_matches:
        choice_key = match.group(1).upper()  # Normalize to uppercase
        choice_text = match.group(2).strip()
        options.append((choice_key, choice_text))
    
    return options


def normalize_single_character_answer(user_answer: str, question: str) -> str:
    """
    Normalize a single character answer to the full option text if it matches a multiple choice option.
    
    Args:
        user_answer: The user's input (may be single character like "1" or "b")
        question: The original question text
        
    Returns:
        The normalized answer (either the full option text or the original user_answer if no match)
    """
    # Clean up the user answer
    user_answer = user_answer.strip()
    
    # Only process single character answers
    if len(user_answer) != 1:
        return user_answer
    
    # Extract multiple choice options
    options = extract_multiple_choice_options(question)
    if not options:
        return user_answer
    
    # Try to match the user's answer to an option
    for choice_key, choice_text in options:
        # Check for exact match (case insensitive for letters)
        if user_answer.lower() == choice_key.lower():
            return choice_text
    
    # If no match found, return original answer
    return user_answer