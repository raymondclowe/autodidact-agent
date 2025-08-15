"""
Lesson Introduction Component for Autodidact
Displays lesson objectives at session start to set clear expectations
"""

import streamlit as st
from typing import Dict, Any
from backend.session_state import SessionState, get_formatted_objectives_for_intro


def display_lesson_introduction(session_state: SessionState, node_info: Dict[str, Any]) -> None:
    """
    Display lesson objectives at session start
    
    Args:
        session_state: Current session state containing objectives
        node_info: Node information containing lesson title and metadata
    """
    objectives_list = get_formatted_objectives_for_intro(session_state)
    node_title = node_info.get('label', 'Learning Session')
    
    # Only display if we have objectives to show
    if not objectives_list:
        return
    
    # Create the introduction container
    with st.container():
        # Welcome header with lesson title
        st.markdown(f"# 🎓 **Welcome to: {node_title}**")
        st.markdown("## 📚 **In this lesson, you will learn:**")
        
        # List objectives with bullet points
        for obj_description in objectives_list:
            st.markdown(f"• {obj_description}")
        
        # Motivational footer
        st.markdown("**Let's begin your learning journey!** 🚀")
        
        # Add visual separator
        st.divider()


def should_show_lesson_intro(session_state: SessionState) -> bool:
    """
    Determine if lesson introduction should be shown
    
    Args:
        session_state: Current session state
        
    Returns:
        bool: True if introduction should be displayed
    """
    # Show intro only if we have objectives and no chat history yet
    objectives = session_state.get("objectives_to_teach", [])
    history = session_state.get("history", [])
    
    return len(objectives) > 0 and len(history) == 0