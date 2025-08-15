"""
Lesson Progress Component for Autodidact
Displays current progress through learning objectives during session
"""

import streamlit as st
from typing import Dict, Any
from backend.session_state import SessionState, get_objectives_progress_info


def display_lesson_progress_sidebar(session_state: SessionState) -> None:
    """
    Display lesson progress in the sidebar
    
    Args:
        session_state: Current session state containing progress information
    """
    progress_info = get_objectives_progress_info(session_state)
    
    if not progress_info["items"]:
        return
    
    with st.sidebar:
        st.markdown("### 📊 Lesson Progress")
        
        # Progress bar
        progress_percentage = (progress_info["completed_count"] / progress_info["total"]) * 100
        st.progress(progress_percentage / 100, text=f"{progress_info['completed_count']}/{progress_info['total']} objectives completed")
        
        # Individual objective status
        for item in progress_info["items"]:
            if item["status"] == "completed":
                icon = "✅"
                text_style = ""
            elif item["status"] == "current":
                icon = "🔄" 
                text_style = "**"  # Bold for current
            else:
                icon = "⭕"
                text_style = ""
            
            st.markdown(f"{icon} {text_style}{item['description']}{text_style}")


def display_lesson_progress_main(session_state: SessionState) -> None:
    """
    Display lesson progress in main content area (compact version)
    
    Args:
        session_state: Current session state containing progress information
    """
    progress_info = get_objectives_progress_info(session_state)
    
    if not progress_info["items"]:
        return
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### 📊 Lesson Progress")
            
        with col2:
            # Compact progress indicator
            progress_text = f"{progress_info['completed_count']}/{progress_info['total']}"
            st.markdown(f"**{progress_text}**")
        
        # Progress bar
        progress_percentage = (progress_info["completed_count"] / progress_info["total"]) * 100
        st.progress(progress_percentage / 100)
        
        # Expandable detailed view
        with st.expander("View detailed progress"):
            for item in progress_info["items"]:
                if item["status"] == "completed":
                    st.success(f"✅ {item['description']}")
                elif item["status"] == "current":
                    st.info(f"🔄 {item['description']} (Current)")
                else:
                    st.write(f"⭕ {item['description']}")


def display_objective_completion_celebration(objective_description: str) -> None:
    """
    Display a brief celebration when an objective is completed
    
    Args:
        objective_description: Description of the completed objective
    """
    st.success(f"🎉 **Objective Completed!** \n\n✅ {objective_description}")
    

def should_show_progress_tracking(session_state: SessionState) -> bool:
    """
    Determine if progress tracking should be shown
    
    Args:
        session_state: Current session state
        
    Returns:
        bool: True if progress tracking should be displayed
    """
    objectives = session_state.get("objectives_to_teach", [])
    current_phase = session_state.get("current_phase", "")
    
    # Show progress if we have objectives and are in teaching phase
    return len(objectives) > 0 and current_phase in ["teaching", "final_test"]