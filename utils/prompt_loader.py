"""
Prompt loader utility for handling Unicode-safe prompt templates
Loads prompts from external text files to avoid Unicode issues in Python source
"""

import os
from typing import Any, Dict, List
from pathlib import Path

# Get the prompts directory path
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt_template(filename: str) -> str:
    """
    Load a prompt template from a text file with proper Unicode handling
    
    Args:
        filename: Name of the prompt file (e.g., 'teaching_prompt.txt')
        
    Returns:
        The prompt template as a string
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
        UnicodeError: If there are encoding issues
    """
    prompt_path = PROMPTS_DIR / filename
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    try:
        # Read with explicit UTF-8 encoding to handle Unicode characters
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content.strip()
        
    except UnicodeDecodeError as e:
        raise UnicodeError(f"Failed to decode prompt file {filename}: {e}")

def get_teaching_prompt_template() -> str:
    """Load the teaching prompt template"""
    return load_prompt_template("teaching_prompt.txt")

def get_recap_prompt_template() -> str:
    """Load the recap prompt template"""
    return load_prompt_template("recap_prompt.txt")

def get_available_prompts() -> List[str]:
    """Get list of available prompt files"""
    if not PROMPTS_DIR.exists():
        return []
    
    return [f.name for f in PROMPTS_DIR.glob("*.txt")]

def build_ref_list(refs: List[Dict[str, Any]]) -> str:
    """Return bullet list string for the REFERENCE section of prompts."""
    return "\n".join(
        f"• [{r['rid']}] {r.get('loc') or r.get('section')} - *{r['title']}* "
        f"({r['type']}, {r['date'][:4]})" for r in refs
    )

def get_images_context_for_prompt() -> str:
    """
    Get context about images currently visible to the user for AI prompts
    This function gets the context from the session state if available
    """
    try:
        import streamlit as st
        if hasattr(st, 'session_state') and 'graph_state' in st.session_state:
            displayed_images = st.session_state.graph_state.get('displayed_images', [])
            
            if not displayed_images:
                return ""
            
            context_parts = []
            for i, img in enumerate(displayed_images[-3:], 1):  # Last 3 images only
                desc = img.get('description', 'Educational image')
                context = img.get('context', '')
                context_parts.append(f"{i}. {desc}" + (f" ({context})" if context else ""))
            
            return f"\n\nIMAGES CURRENTLY VISIBLE TO STUDENT:\n" + "\n".join(context_parts)
        
    except Exception:
        # If streamlit not available or other issues, return empty context
        pass
    
    return ""

def format_teaching_prompt(
    obj_id: str,
    obj_label: str,
    recent: List[str],
    remaining: List[str],
    refs: List[Dict[str, Any]],
    learner_profile_context: str = "",
) -> str:
    """Fill the TEACHING prompt with runtime values."""
    template = get_teaching_prompt_template()
    
    # Get images context
    images_context = get_images_context_for_prompt()
    
    return template.format(
        OBJ_ID=obj_id,
        OBJ_LABEL=obj_label,
        RECENT_TOPICS="; ".join(recent),
        REMAINING_OBJS="; ".join(remaining),
        REF_LIST_BULLETS=build_ref_list(refs),
        LEARNER_PROFILE_CONTEXT=learner_profile_context,
        VISIBLE_IMAGES_CONTEXT=images_context,
    )

def format_recap_prompt(
    recent_los: List[str],
    next_obj: str,
    refs: List[Dict[str, Any]],
    learner_profile_context: str = "",
) -> str:
    """Fill the RECAP prompt with runtime values."""
    template = get_recap_prompt_template()
    
    return template.format(
        RECENT_LOS="; ".join(recent_los),
        NEXT_OBJ=next_obj,
        REF_LIST_BULLETS=build_ref_list(refs),
        LEARNER_PROFILE_CONTEXT=learner_profile_context,
    )
