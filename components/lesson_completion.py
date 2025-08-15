"""
Session Completion Component for Autodidact
Displays completion summary when session ends
"""

import streamlit as st
from typing import Dict, Any
from datetime import datetime
from backend.session_state import SessionState, get_session_completion_info


def display_session_completion_summary(session_state: SessionState, node_info: Dict[str, Any]) -> None:
    """
    Display session completion summary with achievements and performance
    
    Args:
        session_state: Current session state containing completion information
        node_info: Node information containing lesson title
    """
    completion_info = get_session_completion_info(session_state)
    node_title = node_info.get('label', 'Learning Session')
    
    if not completion_info["objectives"]:
        return
    
    with st.container():
        # Celebration header
        st.markdown("# 🎉 **Congratulations! You've Successfully Completed:**")
        st.markdown(f"## ✅ **{node_title}**")
        
        # Objectives completed
        st.markdown("### 📚 **You have successfully learned:**")
        for obj_description in completion_info["objectives"]:
            st.markdown(f"• ✅ {obj_description}")
        
        # Performance metrics
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            final_score = completion_info["final_score"] * 100
            st.metric(
                label="🏆 Final Score",
                value=f"{final_score:.0f}%"
            )
            
        with col2:
            completion_pct = completion_info["completion_percentage"]
            st.metric(
                label="📈 Completion Rate", 
                value=f"{completion_pct:.0f}%"
            )
            
        with col3:
            # Calculate time taken if available
            if completion_info["session_start"] and completion_info["session_end"]:
                try:
                    start_time = datetime.fromisoformat(completion_info["session_start"])
                    end_time = datetime.fromisoformat(completion_info["session_end"])
                    duration = end_time - start_time
                    minutes = int(duration.total_seconds() / 60)
                    st.metric(
                        label="⏱️ Time Taken",
                        value=f"{minutes} min"
                    )
                except:
                    st.metric(
                        label="⏱️ Time Taken", 
                        value="--"
                    )
            else:
                st.metric(
                    label="⏱️ Time Taken",
                    value="--"
                )
        
        # Mastery level based on score
        mastery_level = get_mastery_level(completion_info["final_score"])
        st.markdown(f"### 🎯 **Mastery Level:** {mastery_level}")
        
        # Next steps
        st.divider()
        st.markdown("**Ready for the next lesson!** 🚀")


def get_mastery_level(score: float) -> str:
    """
    Determine mastery level based on final score
    
    Args:
        score: Final score as decimal (0.0 to 1.0)
        
    Returns:
        str: Mastery level description
    """
    if score >= 0.9:
        return "🌟 Excellent"
    elif score >= 0.8:
        return "⭐ Advanced" 
    elif score >= 0.7:
        return "✨ Proficient"
    elif score >= 0.6:
        return "🔹 Developing"
    else:
        return "📚 Basic"


def should_show_completion_summary(session_state: SessionState) -> bool:
    """
    Determine if completion summary should be shown
    
    Args:
        session_state: Current session state
        
    Returns:
        bool: True if completion summary should be displayed
    """
    current_phase = session_state.get("current_phase", "")
    objectives = session_state.get("objectives_to_teach", [])
    completed = set(session_state.get("completed_objectives", []))
    
    # Show completion summary if session is completed and we have completed objectives
    return (current_phase == "completed" and 
            len(objectives) > 0 and 
            len(completed) > 0)