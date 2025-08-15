"""
Study Notes Page for Autodidact
Dedicated page for viewing and managing study notes
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.study_notes import (
    display_study_guide_collection,
    display_individual_note,
    display_note_for_print
)
from backend.db import get_db_connection
import logging

logger = logging.getLogger(__name__)

def main():
    """Main function for study notes page"""
    
    st.title("📚 Study Notes")
    
    # Get available projects from session state or database
    if 'current_project_id' in st.session_state:
        project_id = st.session_state['current_project_id']
    else:
        # Try to get project from URL params or show selection
        project_id = st.query_params.get('project_id')
        if not project_id:
            show_project_selection()
            return
    
    # Handle different views based on URL parameters
    view = st.query_params.get('view', 'collection')
    note_id = st.query_params.get('note_id')
    
    if view == 'note' and note_id:
        display_single_note_view(note_id)
    elif view == 'print' and note_id:
        display_print_view(note_id)
    elif view == 'collection':
        display_collection_view(project_id)
    else:
        display_collection_view(project_id)


def show_project_selection():
    """Show project selection if no current project"""
    st.markdown("### Select a Project")
    st.info("Please select a project to view its study notes.")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT id, name, topic FROM project ORDER BY created_at DESC")
            projects = cursor.fetchall()
        
        if projects:
            for project in projects:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{project['name']}** - {project['topic']}")
                with col2:
                    if st.button("View Notes", key=f"select_{project['id']}"):
                        st.session_state['current_project_id'] = project['id']
                        st.rerun()
        else:
            st.warning("No projects found. Create a project first to generate study notes.")
            
    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")
        logger.error(f"Error in show_project_selection: {e}")


def display_collection_view(project_id: str):
    """Display the main collection view"""
    st.markdown("## 📖 Study Notes Collection")
    
    # Add navigation tabs
    tab1, tab2 = st.tabs(["📚 My Notes", "ℹ️ About"])
    
    with tab1:
        display_study_guide_collection(project_id)
    
    with tab2:
        display_about_study_notes()


def display_single_note_view(note_id: str):
    """Display a single note in detail"""
    st.markdown("## 📖 Study Note")
    
    # Add back button
    if st.button("← Back to Collection"):
        st.query_params.clear()
        st.rerun()
    
    display_individual_note(note_id)


def display_print_view(note_id: str):
    """Display note optimized for printing"""
    st.markdown("## 🖨️ Print View")
    
    # Add back button (hidden in print)
    st.markdown('<div class="print-hide">', unsafe_allow_html=True)
    if st.button("← Back to Collection"):
        st.query_params.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    display_note_for_print(note_id)


def display_about_study_notes():
    """Display information about the study notes feature"""
    st.markdown("""
    ### 🎯 About Study Notes
    
    The Study Notes feature automatically generates comprehensive, printable study materials 
    from your completed lessons. Here's how it works:
    
    #### 📝 **What's Included in Your Notes:**
    - **Lesson Overview**: Summary of what you learned
    - **Learning Objectives**: Goals you mastered during the lesson  
    - **Key Concepts**: Important ideas and definitions covered
    - **Key Insights**: Personalized takeaways from your learning
    - **Review Questions**: Questions to test your understanding
    - **Performance Summary**: Your scores and progress metrics
    
    #### 🖨️ **Printing Your Notes:**
    1. Click any **"Print"** button to open a print-optimized view
    2. Use your browser's print function (Ctrl+P or Cmd+P)
    3. Choose **"Save as PDF"** to create a digital copy
    4. Or print to paper for physical study materials
    
    #### 📚 **Building Your Study Guide:**
    - Notes are automatically saved to your collection
    - Accumulate notes from multiple lessons
    - Use **"Print All"** to create a complete study guide
    - Download as HTML files for offline access
    
    #### 💡 **Tips for Best Results:**
    - **Print Settings**: Enable "Print backgrounds" for best appearance
    - **Paper Size**: Optimized for standard letter size (8.5" x 11")
    - **Margins**: Extra left margin provided for ring binding
    - **Organization**: Notes are organized by completion date
    
    #### 🎓 **Study Strategy:**
    - Review notes immediately after completing a lesson
    - Use review questions to test retention
    - Combine notes from related lessons
    - Create a physical binder for easy reference
    
    ---
    
    **💫 Pro Tip:** The best time to generate notes is immediately after completing 
    a lesson while the material is fresh in your mind!
    """)


if __name__ == "__main__":
    main()