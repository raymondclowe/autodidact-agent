"""
Session Completion Component for Autodidact
Displays completion summary when session ends
"""

import streamlit as st
from typing import Dict, Any
from datetime import datetime
import logging
from backend.session_state import SessionState, get_session_completion_info
from backend.note_generator import generate_lesson_notes
from backend.db import get_session_info


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
        
        # Study notes generation offer
        st.divider()
        show_study_notes_offer(session_state, node_info)
        
        # Next steps
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


def show_study_notes_offer(session_state: SessionState, node_info: Dict[str, Any]) -> None:
    """
    Show offer to generate study notes after lesson completion
    
    Args:
        session_state: Current session state
        node_info: Information about the completed lesson node
    """
    # Check if lesson is truly completed
    if session_state.get("current_phase") != "completed":
        return
    
    # Create a nice offer box
    with st.container():
        st.markdown("### 📚 **Create Study Notes**")
        st.markdown(f"**Great job completing {node_info.get('label', 'this lesson')}!**")
        st.markdown("Would you like to generate printable study notes for this lesson?")
        
        # Benefits explanation
        with st.expander("📖 What's included in study notes?"):
            st.markdown("""
            Your personalized study notes will include:
            - **Lesson overview** and key concepts covered
            - **Learning objectives** you mastered
            - **Key insights** from your learning journey  
            - **Review questions** to test your knowledge
            - **Performance summary** with your scores
            - **Print-optimized format** for physical study materials
            """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 **Generate Study Notes**", type="primary", key="generate_study_notes"):
                try:
                    # Get real session info from database
                    session_id = st.session_state.get('current_session_id')
                    if not session_id:
                        st.error("Could not determine current session.")
                        return
                        
                    session_info = get_session_info(session_id)
                    if not session_info:
                        st.error(f"Could not retrieve info for session {session_id}")
                        return
                    
                    with st.spinner("✨ Generating your personalized study notes..."):
                        notes = generate_lesson_notes(session_state, session_info, node_info)
                    
                    st.success("✅ **Study notes generated successfully!**")
                    st.info("📚 Your notes have been added to your study guide collection.")
                    
                    # Show a preview and option to view full notes
                    if st.button("👁️ View Generated Notes", key="view_generated_notes"):
                        st.session_state['show_generated_notes'] = notes
                        
                except Exception as e:
                    st.error(f"❌ Error generating study notes: {str(e)}")
                    logging.error(f"Study notes generation error: {e}")
        
        with col2:
            if st.button("⏰ Maybe Later", key="study_notes_later"):
                st.info("💡 You can generate study notes later from your session history.")
        
        with col3:
            if st.button("❌ No Thanks", key="study_notes_decline"):
                st.info("Okay! You can always change your mind later.")
    
    # Display generated notes if requested
    if st.session_state.get('show_generated_notes'):
        st.markdown("---")
        st.markdown("### 📖 Your Generated Study Notes")
        
        from components.study_notes import display_printable_notes
        display_printable_notes(st.session_state['show_generated_notes'])
        
        # Clear the display flag
        if st.button("✅ Done Viewing", key="done_viewing_notes"):
            del st.session_state['show_generated_notes']