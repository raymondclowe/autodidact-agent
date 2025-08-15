"""
Study Notes Display Component for Autodidact
Handles display of generated study notes with print optimization
"""

import streamlit as st
from typing import Dict, Any, Optional
from backend.note_generator import get_study_note_by_id, get_user_study_notes
import logging

logger = logging.getLogger(__name__)


def display_printable_notes(notes: Dict[str, Any]) -> None:
    """
    Display notes in print-ready format with optimized styling
    
    Args:
        notes: Dictionary containing note content and formatted HTML
    """
    # Add print-optimized CSS with ring-binding margins
    st.markdown("""
    <style>
    .printable-notes {
        font-family: 'Times New Roman', serif;
        line-height: 1.6;
        color: #000;
        background: #fff;
        padding: 0;
        margin: 0;
    }
    
    .notes-header {
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 2px solid #333;
        padding-bottom: 15px;
    }
    
    .lesson-title {
        font-size: 24pt;
        font-weight: bold;
        margin: 0 0 10px 0;
        color: #2c3e50;
    }
    
    .lesson-name {
        font-size: 20pt;
        font-weight: bold;
        margin: 0 0 10px 0;
        color: #34495e;
    }
    
    .completion-info {
        font-size: 12pt;
        color: #666;
        margin: 5px 0;
    }
    
    .section-divider {
        font-family: monospace;
        text-align: center;
        margin: 15px 0;
        color: #333;
        font-size: 10pt;
    }
    
    .lesson-overview, .objectives-section, .key-concepts, 
    .insights-section, .review-questions, .performance-section {
        margin: 20px 0;
        page-break-inside: avoid;
    }
    
    .lesson-overview h3, .objectives-section h3, .key-concepts h3,
    .insights-section h3, .review-questions h3, .performance-section h3 {
        font-size: 16pt;
        font-weight: bold;
        margin: 0 0 15px 0;
        color: #2c3e50;
        border-bottom: 1px solid #bdc3c7;
        padding-bottom: 5px;
    }
    
    .objectives-list, .insights-list, .questions-list, .performance-list {
        margin: 10px 0;
        padding-left: 20px;
    }
    
    .objectives-list li, .insights-list li, .performance-list li {
        margin: 8px 0;
        font-size: 12pt;
    }
    
    .questions-list li {
        margin: 12px 0;
        font-size: 12pt;
        line-height: 1.4;
    }
    
    .concept-item {
        margin: 15px 0;
        padding: 10px;
        border-left: 3px solid #3498db;
        background-color: #f8f9fa;
    }
    
    .concept-item h4 {
        font-size: 14pt;
        margin: 0 0 8px 0;
        color: #2c3e50;
    }
    
    .concept-item p {
        font-size: 12pt;
        margin: 0;
        line-height: 1.4;
    }
    
    .notes-footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #bdc3c7;
        font-size: 10pt;
        color: #666;
    }
    
    /* Print-specific optimizations */
    @media print {
        /* Hide Streamlit UI elements */
        .stApp > header, .stApp > footer, .stSidebar, 
        .print-hide, .stButton, .stSelectbox, .stColumns {
            display: none !important;
        }
        
        /* Optimize page layout for ring binding */
        @page {
            margin: 1.5in 1in 1in 1.5in; /* Top Right Bottom Left - extra left margin for binding */
            size: letter;
        }
        
        /* Typography optimizations */
        body, .printable-notes {
            font-size: 12pt;
            line-height: 1.4;
            color: #000 !important;
            background: #fff !important;
        }
        
        h1 { 
            font-size: 20pt; 
            page-break-before: avoid;
            page-break-after: avoid;
        }
        
        h2 { 
            font-size: 16pt; 
            margin-top: 12pt;
            page-break-after: avoid;
        }
        
        h3 { 
            font-size: 14pt; 
            margin-top: 12pt;
            page-break-after: avoid;
        }
        
        /* Page break controls */
        .page-break { 
            page-break-before: always; 
        }
        
        .notes-header {
            page-break-after: avoid;
        }
        
        .lesson-overview, .objectives-section, .key-concepts, 
        .insights-section, .review-questions, .performance-section {
            page-break-inside: avoid;
            margin-top: 15pt;
        }
        
        /* Ensure good contrast for printing */
        .concept-item {
            border-left: 2pt solid #000;
            background-color: #f0f0f0;
        }
        
        .section-divider {
            color: #000;
        }
    }
    
    /* Screen display optimizations */
    @media screen {
        .printable-notes {
            max-width: 8.5in;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 5px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display the formatted notes
    st.markdown(notes['formatted_html'], unsafe_allow_html=True)


def show_note_generation_offer(session_state: Dict, session_info: Dict, node_info: Dict) -> Optional[Dict]:
    """
    Display note generation offer at lesson completion
    
    Args:
        session_state: Current session state
        session_info: Session information
        node_info: Node information
        
    Returns:
        Generated notes if user accepts, None otherwise
    """
    # Check if we should show the offer (lesson must be completed)
    if not session_info.get('final_score') or session_info.get('status') != 'completed':
        return None
    
    # Create a modal-like container for the offer
    with st.container():
        st.markdown("---")
        st.markdown("### 📚 **Create Study Notes**")
        st.markdown(f"**Congratulations on completing {node_info.get('label', 'this lesson')}!**")
        st.markdown("Would you like to generate printable study notes for this lesson? These notes will be added to your study guide collection.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 **Generate Notes**", type="primary", key="generate_notes"):
                try:
                    from backend.note_generator import generate_lesson_notes
                    with st.spinner("Generating your study notes..."):
                        notes = generate_lesson_notes(session_state, session_info, node_info)
                    st.success("✅ Study notes generated successfully!")
                    return notes
                except Exception as e:
                    st.error(f"❌ Error generating notes: {str(e)}")
                    logger.error(f"Error in note generation: {e}")
                    return None
        
        with col2:
            if st.button("⏰ Maybe Later", key="maybe_later"):
                st.info("You can generate notes later from your session history.")
                return None
        
        with col3:
            if st.button("❌ No Thanks", key="no_thanks"):
                st.info("Okay, no study notes will be generated.")
                return None
    
    return None


def display_study_guide_collection(project_id: str) -> None:
    """
    Display all collected study notes for a project
    
    Args:
        project_id: Project ID to show notes for
    """
    st.markdown("# 📚 Your Study Guide Collection")
    
    try:
        notes_collection = get_user_study_notes(project_id)
        
        if not notes_collection:
            st.info("📝 No study notes generated yet. Complete some lessons to start building your collection!")
            return
        
        st.markdown(f"**{len(notes_collection)} study note(s) in your collection**")
        
        # Display each note in an expandable section
        for note in notes_collection:
            with st.expander(f"📖 {note['title']} - {note['date'][:10]}", expanded=False):
                st.markdown(f"**Generated:** {note['date']}")
                st.markdown(f"**Summary:** {note['summary']}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📝 View Full Notes", key=f"view_{note['id']}"):
                        st.session_state[f"show_note_{note['id']}"] = True
                
                with col2:
                    if st.button("🖨️ Print", key=f"print_{note['id']}"):
                        st.session_state[f"print_note_{note['id']}"] = True
                
                with col3:
                    if st.button("📄 Download HTML", key=f"download_{note['id']}"):
                        # Provide download button for the HTML content
                        st.download_button(
                            label="📄 Download",
                            data=note['formatted_html'],
                            file_name=f"study_notes_{note['title'].replace(' ', '_')}.html",
                            mime="text/html",
                            key=f"dl_{note['id']}"
                        )
        
        # Bulk actions
        st.divider()
        st.markdown("### 🔧 Bulk Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 **Print All Notes**", help="Open all notes in a print-friendly format"):
                st.session_state["print_all_notes"] = True
                
        with col2:
            if st.button("📄 **Download All as HTML**", help="Download all notes as a single HTML file"):
                combined_html = generate_combined_html(notes_collection)
                st.download_button(
                    label="📄 Download Complete Study Guide",
                    data=combined_html,
                    file_name=f"complete_study_guide_{project_id}.html",
                    mime="text/html"
                )
        
        # Handle note display requests
        for note in notes_collection:
            if st.session_state.get(f"show_note_{note['id']}", False):
                display_individual_note(note['id'])
                st.session_state[f"show_note_{note['id']}"] = False
            
            if st.session_state.get(f"print_note_{note['id']}", False):
                display_note_for_print(note['id'])
                st.session_state[f"print_note_{note['id']}"] = False
        
        # Handle print all request
        if st.session_state.get("print_all_notes", False):
            display_all_notes_for_print(notes_collection)
            st.session_state["print_all_notes"] = False
            
    except Exception as e:
        st.error(f"❌ Error loading study notes: {str(e)}")
        logger.error(f"Error in display_study_guide_collection: {e}")


def display_individual_note(note_id: str) -> None:
    """Display a single note in full format"""
    try:
        note = get_study_note_by_id(note_id)
        if note:
            st.markdown("---")
            st.markdown(f"## 📖 {note['title']}")
            display_printable_notes(note)
            
            # Add print button
            col1, col2 = st.columns(2)
            with col1:
                st.button("🖨️ Print This Note", 
                         help="Use your browser's print function (Ctrl+P) to print or save as PDF",
                         key=f"print_individual_{note_id}")
            with col2:
                st.download_button(
                    label="📄 Download HTML",
                    data=note['formatted_html'],
                    file_name=f"study_note_{note['title'].replace(' ', '_')}.html",
                    mime="text/html",
                    key=f"download_individual_{note_id}"
                )
        else:
            st.error("Note not found")
    except Exception as e:
        st.error(f"Error displaying note: {str(e)}")
        logger.error(f"Error in display_individual_note: {e}")


def display_note_for_print(note_id: str) -> None:
    """Display a note optimized for printing"""
    try:
        note = get_study_note_by_id(note_id)
        if note:
            st.markdown("---")
            st.markdown("### 🖨️ Print View")
            st.markdown("**Use your browser's print function (Ctrl+P or Cmd+P) to print or save as PDF**")
            
            # Hide this message in print view
            st.markdown('<div class="print-hide">', unsafe_allow_html=True)
            st.info("💡 **Tip:** In your browser's print dialog, select 'More settings' and ensure 'Print backgrounds' is enabled for best results.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            display_printable_notes(note)
        else:
            st.error("Note not found")
    except Exception as e:
        st.error(f"Error displaying note for print: {str(e)}")
        logger.error(f"Error in display_note_for_print: {e}")


def display_all_notes_for_print(notes_collection: list) -> None:
    """Display all notes in a print-optimized format"""
    st.markdown("---")
    st.markdown("### 🖨️ Print All Notes")
    st.markdown("**Use your browser's print function (Ctrl+P or Cmd+P) to print or save as PDF**")
    
    # Hide this message in print view
    st.markdown('<div class="print-hide">', unsafe_allow_html=True)
    st.info("💡 **Tip:** This will print all your study notes as one document. Perfect for creating a complete study guide!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    for i, note_summary in enumerate(notes_collection):
        try:
            note = get_study_note_by_id(note_summary['id'])
            if note:
                # Add page break before each note (except the first)
                if i > 0:
                    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
                
                display_printable_notes(note)
        except Exception as e:
            logger.error(f"Error displaying note {note_summary['id']}: {e}")
            continue


def generate_combined_html(notes_collection: list) -> str:
    """Generate a combined HTML file with all notes"""
    try:
        html_parts = ["""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Complete Study Guide</title>
            <meta charset="utf-8">
            <style>
                body { font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0; padding: 20px; }
                .page-break { page-break-before: always; }
                @media print {
                    @page { margin: 1.5in 1in 1in 1.5in; size: letter; }
                }
            </style>
        </head>
        <body>
        <h1>📚 Complete Study Guide</h1>
        <p>Generated by Autodidact Learning System</p>
        <hr>
        """]
        
        for i, note_summary in enumerate(notes_collection):
            note = get_study_note_by_id(note_summary['id'])
            if note:
                if i > 0:
                    html_parts.append('<div class="page-break"></div>')
                html_parts.append(note['formatted_html'])
        
        html_parts.append("</body></html>")
        return "\n".join(html_parts)
    except Exception as e:
        logger.error(f"Error generating combined HTML: {e}")
        return "<html><body><h1>Error generating study guide</h1></body></html>"