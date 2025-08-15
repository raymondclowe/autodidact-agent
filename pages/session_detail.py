# """
# Tutor Session page
# Interactive learning sessions with AI tutor
# """
from __future__ import annotations
import streamlit as st
from backend.db import (
    get_node_with_objectives,
    get_session_info
)
from backend.graph_v05 import (
  create_initial_state, 
  SessionState,
  session_graph
)
from backend.debug_commands import handle_debug_command
from components.speech_controls import show_speech_controls, create_global_speech_component, create_speech_enabled_markdown
from components.image_display import render_content_with_images
from utils.speech_utils import initialize_speech_state

from pathlib import Path
import pickle
from datetime import datetime
from typing import Any, Dict

# Sidebar is shown globally in app.py

def should_clear_session_state(current_session_id: str, current_project_id: str) -> bool:
    """Check if we need to clear session state due to session/project change"""
    if 'graph_state' not in st.session_state:
        return False
    
    # Check if we're switching to a different session or project
    existing_state = st.session_state.graph_state
    if not isinstance(existing_state, dict):
        return True
    
    return (existing_state.get('session_id') != current_session_id or 
            existing_state.get('project_id') != current_project_id)

def clear_session_specific_state():
    """Clear session-specific state variables when switching sessions"""
    session_keys = [
        'graph_state', 'history', 'turn_count', 'current_phase',
        'messages', 'selected_session_id'  # Clear any lingering session selection state
    ]
    
    for key in session_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    print("[clear_session_specific_state] Cleared session state for course switch")

# Initialize speech functionality
initialize_speech_state()
create_global_speech_component()

def display_assistant_message(content: str, context: str = ""):
    """Display assistant message with speech and image support"""
    try:
        # First check if there are image requests in the content
        from components.image_display import process_image_markup
        cleaned_content, image_requests = process_image_markup(content)
        
        if image_requests:
            # If there are images, use the full image rendering
            render_content_with_images(content, context, auto_search=True)
        else:
            # No images, use standard speech-enabled markdown
            create_speech_enabled_markdown(content, add_button=True)
            
    except Exception as e:
        logging.error(f"Error in display_assistant_message: {e}")
        # Fallback to standard display
        create_speech_enabled_markdown(content, add_button=True)

# Show speech controls in header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🎓 Learning Lesson")
with col2:
    show_speech_controls(location="header")

def run_tutor_response(session_info, node_info):
    """Run the v0.4 tutor graph to generate response - pure state transformation, no UI"""
    from backend.session_state import create_initial_state
    print(f"[run_tutor_response] session_info: {session_info}")
    tutor_graph = session_graph
    
    # Check if we need to clear session state due to session/project change
    if should_clear_session_state(session_info['id'], session_info['project_id']):
        print(f"[run_tutor_response] Clearing session state due to session/project change")
        clear_session_specific_state()
    
    # Initialize or update state
    if 'graph_state' not in st.session_state:
        # Create initial state for the graph
        state = create_initial_state(
            session_id=session_info['id'],
            project_id=session_info['project_id'],
            node_id=session_info['node_id']
        )
        st.session_state.graph_state = state
    else:
        state = st.session_state.graph_state
    
    # Sync messages from UI state to graph state
    state['history'] = st.session_state.history.copy() or []
    
    # Track message count before invocation
    prev_msg_count = len(state['history'])
    
    try:
        # Run the graph with recursion limit
        config = {"recursion_limit": 10, 
                  "configurable": {"thread_id": session_info.get("id", "default")}}
        print(f"[run_tutor_response] going to invoke graph with config: {config}")
        while True:
            state = tutor_graph.invoke(state, config)
            if state.get('navigate_without_user_interaction')==True:
                state["navigate_without_user_interaction"] = False
                continue
            else:
                break
        st.session_state.graph_state = state
        # for event in tutor_graph.stream(state, config):
        #     # Update state with latest event
        #     for node_name, node_state in event.items():
        #         state = node_state
        #         st.session_state.graph_state = state
        
        # Sync messages back from graph state to UI state
        st.session_state.history = state['history'].copy()
        st.session_state.turn_count = state.get('turn_count', 0)
        st.session_state.current_phase = state.get('current_phase', 'teaching')

        _save_state(state)
        
        # Return info about what happened
        return {
            'success': True,
            'new_message_count': len(state['history']) - prev_msg_count,
            'is_completed': state.get('current_phase') == 'completed',
            'final_score': sum(state.get('objective_scores', {}).values()) / len(state['objective_scores']) if state.get('objective_scores') else 0
        }
        
    except Exception as e:
        # Return error info without displaying UI
        print(f"error in run_tutor_response: {e}")
        error_type = 'unknown'
        if "AuthenticationError" in str(type(e)):
            error_type = 'auth'
        elif "RateLimitError" in str(type(e)):
            error_type = 'rate_limit'
        elif "GraphRecursionError" in str(type(e)):
            error_type = 'recursion'
        
        return {
            'success': False,
            'error': str(e),
            'error_type': error_type,
            'debug_info': {
                "session_id": session_info['id'],
                "current_phase": state.get('current_phase', 'unknown'),
                "message_count": len(st.session_state.history),
                "objectives_to_teach": len(state.get('objectives_to_teach', [])),
                "completed_objectives": len(state.get('completed_objectives', set()))
            }
        }


# # Get session info from URL or session state
project_id = st.query_params.get("project_id")
session_id = st.query_params.get("session_id")

# If not in URL but we have them in session state, set them in URL
if not project_id and "selected_project_id" in st.session_state:
    project_id = st.session_state.selected_project_id
    st.query_params["project_id"] = project_id
    del st.session_state.selected_project_id

if not session_id and "selected_session_id" in st.session_state:
    session_id = st.session_state.selected_session_id
    st.query_params["session_id"] = session_id
    del st.session_state.selected_session_id

if not project_id or not session_id:
    st.error("Invalid session URL!")
    if st.button("Go to Courses"):
        st.switch_page("pages/home.py")
    st.stop()

# Get session information
session_info = get_session_info(session_id)
print(f"session_info: {session_info}")
if not session_info:
    st.error("Lesson not found!")
    if st.button("Go to Course"):
        if project_id:
            st.session_state.selected_project_id = project_id
            st.switch_page("pages/project_detail.py")
        else:
            st.switch_page("pages/home.py")
    st.stop()

# # # Initialize session state for this session
# # if "messages" not in st.session_state:
# #     st.session_state.messages = []
# # # Remove the graph_state initialization - let run_tutor_response handle it

# Get node information
node_id = session_info['node_id']
node_info = get_node_with_objectives(node_id)
if not node_info:
    st.error("Node information not found!")
    st.stop()

# # # Check if this is a completed session
is_completed = session_info["status"] == "completed"

# Header
if is_completed:
    st.info(f"📚 **Completed Lesson** - Score: {int(session_info['final_score'] * 100)}%")
# Session info display with model capability warning
session_info_col1, session_info_col2 = st.columns([2, 1])
with session_info_col1:
    st.markdown(f"## 🎓 Learning Lesson: {node_info['label']}")
    
with session_info_col2:
    # Check for model capability warnings
    from utils.providers import get_model_capability_warning, get_model_for_task
    try:
        current_model = get_model_for_task('chat')
        warning = get_model_capability_warning(current_model)
        if warning:
            st.warning(warning)
    except Exception as e:
        # Don't fail if model checking fails
        pass

@st.dialog("Lesson Info", width="large")
def session_info_dialog():
    st.info(f"**Topic:** {node_info['label']}")
    st.markdown("### 📋 Learning Objectives")
    for i, obj in enumerate(node_info['learning_objectives'], 1):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(f"{i}. {obj['description']}")
        with col2:
            from components.speech_controls import add_speaker_button_to_text
            add_speaker_button_to_text(obj['description'])
    st.markdown("### 📚 References")
    for i, ref in enumerate(node_info['references_sections_resolved'], 1):
        nat_lang_section_text = ref.get("section") or ref.get("loc") or ""
        if nat_lang_section_text:
            nat_lang_section_text = f"({nat_lang_section_text})"
        st.markdown(f"{i}. [{ref['title']}]({ref['url']}) {nat_lang_section_text}")

# optional local pickle store (same as earlier helper but inline)
_STORE = Path.home() / '.autodidact' / 'projects' / project_id / 'sessions'
_STORE.mkdir(parents=True, exist_ok=True)

def _load_state(session_id: str) -> SessionState | None:
    """Load session state from pickle file if it exists, with database fallback"""
    try:
        # First try to load from pickle file
        fp = _STORE / f"{session_id}.pkl"
        if fp.exists():
            return pickle.loads(fp.read_bytes())
    except Exception as e:
        print(f"Warning: Failed to load session state from file {fp}: {e}")
    
    # Fallback to database
    try:
        from backend.db import load_session_state
        db_state = load_session_state(session_id)
        if db_state:
            return db_state
    except Exception as e:
        print(f"Warning: Failed to load session state from database: {e}")
    
    return None

def _save_state(state: SessionState):
    """Save session state to both pickle file and database"""
    # Save to pickle file
    try:
        fp = _STORE / f"{state['session_id']}.pkl"
        fp.write_bytes(pickle.dumps(state))
    except Exception as e:
        print(f"Warning: Failed to save session state to file {fp}: {e}")
    
    # Save to database as backup
    try:
        from backend.db import save_session_state
        save_session_state(state['session_id'], state)
    except Exception as e:
        print(f"Warning: Failed to save session state to database: {e}")

state: SessionState | None = _load_state(session_id)
if state is None:
    state = create_initial_state(session_id, project_id, node_id)
    # Save initial state immediately
    _save_state(state)

# Check if we need to clear session state due to session/project change
if should_clear_session_state(session_id, project_id):
    print(f"[session_detail] Clearing session state due to session/project change")
    clear_session_specific_state()

# Sync loaded state with Streamlit session state
if "history" not in st.session_state:
    st.session_state.history = state.get('history', [])
if "turn_count" not in st.session_state:
    st.session_state.turn_count = state.get('turn_count', 0)
if "current_phase" not in st.session_state:
    st.session_state.current_phase = state.get('current_phase', 'load_context')
if "graph_state" not in st.session_state:
    st.session_state.graph_state = state

# Lesson control buttons
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚪 Exit Lesson", type="secondary", use_container_width=True):
            st.session_state.selected_project_id = project_id
            st.switch_page("pages/project_detail.py")

    with col2:
        if not is_completed and st.session_state.get('graph_state'):
            # Only show early end if session is active and we've started teaching
            if st.button("⏹️ End Lesson Early", type="secondary", use_container_width=True, disabled=(not st.session_state.graph_state.get('navigate_without_user_interaction'))):
                # Set the force end flag and run the graph
                st.session_state.graph_state['exit_requested'] = True
                st.session_state.history.append({
                    "role": "user",
                    "content": "I'd like to end the session early please."
                })
                # FIXME: is this the correct way to do a rerun here?
                st.rerun()

    with col3:
        # add session info button here which opens a modal with the session info
        if st.button("📚 Lesson Info", type="secondary", use_container_width=True):
            session_info_dialog()

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Import lesson components for progress tracking and completion
from components.lesson_progress import display_lesson_progress_sidebar, should_show_progress_tracking  
from components.lesson_completion import display_session_completion_summary, should_show_completion_summary

# Display progress tracking in sidebar (only during active sessions)
if not is_completed and should_show_progress_tracking(st.session_state.get('graph_state', {})):
    display_lesson_progress_sidebar(st.session_state.get('graph_state', {}))

# Display completion summary for completed sessions  
if is_completed and should_show_completion_summary(st.session_state.get('graph_state', {})):
    display_session_completion_summary(st.session_state.get('graph_state', {}), node_info)

# Display chat messages from history on app rerun
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            # Use enhanced display with speech and image support
            display_assistant_message(message["content"], context=node_info.get('label', ''))
        else:
            # Regular markdown for user messages
            st.markdown(message["content"])

    # Handle initial message generation
if not is_completed and len(st.session_state.history) == 0:
    # Generate initial welcome message
    with st.chat_message("assistant"):
        with st.spinner("🤔 Preparing session..."):
            result = run_tutor_response(session_info, node_info)
            # Save state after assistant response
            if 'graph_state' in st.session_state:
                _save_state(st.session_state.graph_state)
            if result['success']:
                # Display the new message(s)
                new_messages = st.session_state.history[-result['new_message_count']:]
                print(f"new_messages: {new_messages}")
                for msg in new_messages:
                    if msg["role"] == "assistant":
                        print(f"msg to be shown: {msg['content']}")
                        display_assistant_message(msg["content"], context=node_info.get('label', ''))
            else:
                st.error(f"❌ Failed to start session: {result['error']} {result}")

# Accept user input (disabled for completed sessions)
if not is_completed:
    if prompt := st.chat_input("Your response..."):
        # Check for debug commands first
        debug_result = handle_debug_command(prompt, session_info)
        
        # Add user message to chat history (common to both paths)
        st.session_state.history.append({"role": "user", "content": prompt})
        
        # Save state after user input for normal messages
        if not debug_result and 'graph_state' in st.session_state:
            _save_state(st.session_state.graph_state)
        
        # Display user message in chat message container (common to both paths)
        with st.chat_message("user"):
            st.markdown(prompt)
        
        if debug_result:
            # Handle debug command
            if debug_result['success']:
                # Handle help vs completion commands differently
                if debug_result.get('is_help'):
                    # Add help message to chat history
                    st.session_state.history.append({
                        "role": "assistant", 
                        "content": debug_result['message']
                    })
                    
                    # Display help message
                    with st.chat_message("assistant"):
                        create_speech_enabled_markdown(debug_result['message'], add_button=True)
                elif debug_result.get('is_debug_mode_toggle'):
                    # Add debug mode toggle message to chat history
                    st.session_state.history.append({
                        "role": "assistant", 
                        "content": debug_result['message']
                    })
                    
                    # Display debug mode toggle message
                    with st.chat_message("assistant"):
                        create_speech_enabled_markdown(debug_result['message'], add_button=True)
                elif debug_result.get('is_objective_advancement'):
                    # Handle objective advancement - inject AI message with control block
                    if debug_result.get('inject_control_block'):
                        # Add the simulated AI message to history
                        simulated_message = debug_result.get('simulated_ai_message', 
                            "Great! I can see you understand this concept well. Let's move on to the next learning point.\n\n<control>{\"objective_complete\": true}</control>")
                        
                        # Add the message to history and let the normal flow process it
                        st.session_state.history.append({
                            "role": "assistant", 
                            "content": simulated_message
                        })
                        
                        # Update graph state history to match
                        if 'graph_state' in st.session_state:
                            st.session_state.graph_state['history'] = st.session_state.history.copy()
                            _save_state(st.session_state.graph_state)
                        
                        # Display the debug advancement message
                        with st.chat_message("assistant"):
                            create_speech_enabled_markdown(debug_result['message'], add_button=True)
                        
                        # Display clean version of the advancement (without control block)
                        with st.chat_message("assistant"):
                            clean_message = simulated_message.split('<control>')[0].strip()
                            create_speech_enabled_markdown(clean_message, add_button=True)
                        
                        st.rerun()  # Refresh to process the objective completion
                        
                    else:
                        # Fallback: just show the message
                        st.session_state.history.append({
                            "role": "assistant", 
                            "content": debug_result['message']
                        })
                        
                        with st.chat_message("assistant"):
                            create_speech_enabled_markdown(debug_result['message'], add_button=True)
                else:
                    # Add system message about debug completion
                    st.session_state.history.append({
                        "role": "assistant", 
                        "content": debug_result['message']
                    })
                    
                    # Display debug completion message
                    with st.chat_message("assistant"):
                        create_speech_enabled_markdown(debug_result['message'], add_button=True)
                        st.balloons()
                        st.success(f"🎉 **Debug Lesson Complete!** Score: {int(debug_result['score'] * 100)}%")
                        
                        # Show debug info if debug mode is enabled
                        if debug_result.get('debug_info'):
                            with st.expander("🔧 Debug Scoring Information", expanded=True):
                                st.json(debug_result['debug_info'])
                        
                        # Show completion buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Back to Course", type="primary", use_container_width=True, key="debug_back"):
                                st.session_state.selected_project_id = session_info['project_id']
                                st.switch_page("pages/project_detail.py")
                        with col2:
                            if st.button("📊 View Progress", type="secondary", use_container_width=True, key="debug_progress"):
                                st.session_state.selected_project_id = session_info['project_id']
                                st.switch_page("pages/project_detail.py")
                    
                    st.stop()  # Prevent further processing for completion command
            else:
                # Show error for failed debug command
                st.error(f"Debug command failed: {debug_result['error']}")
                st.stop()
        else:
            # Normal message processing
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    result = run_tutor_response(session_info, node_info)
                    # Save state after assistant response
                    if 'graph_state' in st.session_state:
                        _save_state(st.session_state.graph_state)
                    if result['success']:
                        # Display new assistant messages
                        new_messages = st.session_state.history[-result['new_message_count']:]
                        print(f"new_messages: {new_messages}")
                        for msg in new_messages:
                            if msg["role"] == "assistant":
                                print(f"msg to be shown: {msg['content']}")
                                display_assistant_message(msg["content"], context=node_info.get('label', ''))
                        print(f"result: {result}")
                        print(f"st.session_state.history: {st.session_state.history}")
                        # Check if session is completed
                        if result['is_completed']:
                            st.balloons()
                            st.success(f"🎉 **Lesson Complete!** Your score: {int(result['final_score'] * 100)}%")
                            
                            # Show debug info if debug mode is enabled
                            from backend.debug_commands import is_debug_mode_enabled
                            if is_debug_mode_enabled():
                                with st.expander("🔧 Normal Lesson Scoring Information", expanded=True):
                                    scoring_info = {
                                        'scoring_method': 'AI_LLM_GRADING',
                                        'final_score': result['final_score'],
                                        'scoring_description': 'AI (LLM) evaluated your quiz answers and calculated this score',
                                        'debug_mode_note': 'This is a NORMAL session - scores are calculated by AI, not hardcoded'
                                    }
                                    if 'debug_info' in result:
                                        scoring_info.update(result['debug_info'])
                                    st.json(scoring_info)
                            
                            # Show completion buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ Back to Course", type="primary", use_container_width=True, key="normal_back"):
                                    st.session_state.selected_project_id = session_info['project_id']
                                    st.switch_page("pages/project_detail.py")
                            with col2:
                                if st.button("📊 View Progress", type="secondary", use_container_width=True, key="normal_progress"):
                                    st.session_state.selected_project_id = session_info['project_id']
                                    st.switch_page("pages/project_detail.py")
                    else:
                        # Handle errors
                        if result['error_type'] == 'auth':
                            st.error("❌ API key authentication failed. Please check your API key in Settings.")
                            if st.button("Go to Settings"):
                                st.switch_page("pages/settings.py")
                        elif result['error_type'] == 'rate_limit':
                            st.error("⏳ Rate limit reached. Please wait a moment and try again.")
                            st.info("Consider upgrading your OpenAI plan for higher rate limits.")
                        elif result['error_type'] == 'recursion':
                            st.error("⚠️ Lesson is taking too long. The conversation might be stuck in a loop.")
                            st.info("Try refreshing the page or starting a new lesson.")
                        else:
                            st.error(f"❌ Error in tutor response: {result['error']}")
                            st.info("Try refreshing the page or starting a new session.")
                        # Show debug info in expander
                        with st.expander("🐛 Debug Information"):
                            st.json(result['debug_info'])
else:
    st.info("This session has been completed. Exit to start a new session on a different topic!")