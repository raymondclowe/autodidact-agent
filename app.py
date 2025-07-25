"""
Autodidact - AI-Powered Learning Assistant
Main entry point with Streamlit navigation
"""

import sys
import argparse
import os
import streamlit as st
from components.sidebar import show_sidebar
from components.api_key_overlay import check_and_show_api_overlay
from utils.config import load_api_key, get_current_provider, configure_debug_logging

# Parse command-line arguments before Streamlit initialization
def parse_debug_args():
    """Parse command-line arguments, specifically looking for --debug flag"""
    debug_mode = False
    
    # Check for --debug in command line args without modifying sys.argv
    # Handle both direct python execution and streamlit run patterns
    if '--debug' in sys.argv:
        debug_mode = True
        # Create a copy of sys.argv without --debug for Streamlit
        filtered_argv = [arg for arg in sys.argv if arg != '--debug']
        sys.argv[:] = filtered_argv  # Update sys.argv in place
    
    # Also check for AUTODIDACT_DEBUG environment variable
    if os.getenv("AUTODIDACT_DEBUG", "").lower() in ["true", "1", "yes"]:
        debug_mode = True
    
    return debug_mode

# Initialize debug mode early (only if we're the main module)
DEBUG_MODE = False
if __name__ == "__main__" or "streamlit" in sys.modules:
    DEBUG_MODE = parse_debug_args()
    if DEBUG_MODE:
        configure_debug_logging()

# Page configuration
st.set_page_config(
    page_title="Autodidact - AI Learning Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
from backend.db import init_database
init_database()

# Initialize session state
if "api_key" not in st.session_state:
    current_provider = get_current_provider()
    st.session_state.api_key = load_api_key(current_provider)

# Store debug mode in session state
st.session_state.debug_mode = DEBUG_MODE

# Define pages
home = st.Page("pages/home.py", title="Home", url_path="", default=True)
new_project = st.Page("pages/new_project.py", title="New Project", url_path="new")
project = st.Page("pages/project_detail.py", title="Project", url_path="project")
session = st.Page("pages/session_detail.py", title="Session", url_path="session") 
settings = st.Page("pages/settings.py", title="Settings", url_path="settings")

# Create navigation with all pages
# We'll hide Project and Session from the sidebar using CSS
pg = st.navigation([home, new_project, project, session, settings])

# Always hide Project and Session page from sidebar
# Add debug mode styling if debug is enabled
debug_css = ""
if DEBUG_MODE:
    debug_css = """
/* Debug mode indicator */
.debug-banner {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #ff4b4b;
    color: white;
    text-align: center;
    padding: 5px;
    font-weight: bold;
    z-index: 9999;
    font-size: 12px;
}
/* Adjust main content to account for debug banner */
.main .block-container {
    padding-top: 40px !important;
}
"""

st.markdown(f"""
<style>
/* Hide header and auto generated nav from sidebar (this does mean you cannot close the sidebar) */
[data-testid="stSidebarHeader"] {{
    display: none !important;
}}
[data-testid="stSidebarNav"] {{
    display: none !important;
}}
{debug_css}
</style>
""", unsafe_allow_html=True)

# Show debug banner if debug mode is enabled
if DEBUG_MODE:
    st.markdown("""
    <div class="debug-banner">
        🐛 DEBUG MODE ACTIVE - Enhanced logging enabled
    </div>
    """, unsafe_allow_html=True)

# Show sidebar on all pages
show_sidebar()

# Check API key for protected pages
current_path = st.query_params.get("page", "")
if current_path not in ["", "home", "settings"] and not st.session_state.api_key:
    if not check_and_show_api_overlay():
        st.stop()

# Run selected page
pg.run() 