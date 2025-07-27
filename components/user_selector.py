"""
User Selector Component
Provides user selection and management UI for multi-user support
"""

import streamlit as st
from typing import Optional
from backend.user_manager import user_manager, DEFAULT_USER_ID, DEFAULT_USER_NAME

def get_current_user_id() -> str:
    """Get the current user ID from session state"""
    return st.session_state.get('current_user_id', DEFAULT_USER_ID)

def set_current_user_id(user_id: str):
    """Set the current user ID in session state"""
    st.session_state.current_user_id = user_id

def show_user_selector():
    """Display user selector in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 User")
    
    # Get all users
    users = user_manager.list_users()
    
    if not users:
        # Ensure default user exists
        user_manager.ensure_default_user()
        users = user_manager.list_users()
    
    # Create user options for selectbox
    user_options = {user['id']: f"{user['username']} ({user['id']})" for user in users}
    
    # Get current user
    current_user_id = get_current_user_id()
    
    # Show user selector
    selected_user_id = st.sidebar.selectbox(
        "Select User",
        options=list(user_options.keys()),
        format_func=lambda x: user_options[x],
        index=list(user_options.keys()).index(current_user_id) if current_user_id in user_options else 0,
        key="user_selector"
    )
    
    # Update current user if changed
    if selected_user_id != current_user_id:
        set_current_user_id(selected_user_id)
        st.rerun()
    
    # Show user management buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("➕ Add User", key="add_user_btn", help="Add a new user"):
            st.session_state.show_add_user_modal = True
    
    with col2:
        if selected_user_id != DEFAULT_USER_ID:
            if st.button("🗑️ Delete", key="delete_user_btn", help="Delete current user"):
                st.session_state.show_delete_user_modal = True
    
    # Handle add user modal
    if st.session_state.get('show_add_user_modal', False):
        show_add_user_modal()
    
    # Handle delete user modal
    if st.session_state.get('show_delete_user_modal', False):
        show_delete_user_modal(selected_user_id)

def show_add_user_modal():
    """Show modal for adding a new user"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Add New User**")
        
        with st.form("add_user_form"):
            new_user_id = st.text_input(
                "User ID", 
                placeholder="e.g., john_doe",
                help="Unique identifier (3+ characters, lowercase, no spaces)"
            ).strip().lower()
            
            new_username = st.text_input(
                "Display Name", 
                placeholder="e.g., John Doe",
                help="Friendly name to display"
            ).strip()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.form_submit_button("Create"):
                    try:
                        if not new_user_id or not new_username:
                            st.error("Both User ID and Display Name are required")
                        elif len(new_user_id) < 3:
                            st.error("User ID must be at least 3 characters")
                        elif ' ' in new_user_id or not new_user_id.isalnum():
                            st.error("User ID must be alphanumeric with no spaces")
                        else:
                            user_manager.create_user(new_user_id, new_username)
                            set_current_user_id(new_user_id)
                            st.session_state.show_add_user_modal = False
                            st.success(f"Created user: {new_username}")
                            st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Failed to create user: {e}")
            
            with col3:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_add_user_modal = False
                    st.rerun()

def show_delete_user_modal(user_id: str):
    """Show modal for deleting a user"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Delete User**")
        
        user = user_manager.get_user(user_id)
        if not user:
            st.error("User not found")
            st.session_state.show_delete_user_modal = False
            return
        
        st.warning(f"""
**Are you sure you want to delete user "{user['username']}"?**

This will permanently delete:
- All projects and learning progress
- All learner profiles
- All session history

This action cannot be undone!
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Delete", key="confirm_delete", type="primary"):
                try:
                    user_manager.delete_user(user_id)
                    # Switch to default user
                    set_current_user_id(DEFAULT_USER_ID)
                    st.session_state.show_delete_user_modal = False
                    st.success(f"Deleted user: {user['username']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete user: {e}")
        
        with col3:
            if st.button("Cancel", key="cancel_delete"):
                st.session_state.show_delete_user_modal = False
                st.rerun()

def initialize_user_session():
    """Initialize user session state"""
    if 'current_user_id' not in st.session_state:
        set_current_user_id(DEFAULT_USER_ID)
    
    # Ensure the current user exists
    current_user = user_manager.get_user(get_current_user_id())
    if not current_user:
        # Fall back to default user
        set_current_user_id(DEFAULT_USER_ID)
        user_manager.ensure_default_user()

def get_current_user_display_name() -> str:
    """Get the display name of the current user"""
    user = user_manager.get_user(get_current_user_id())
    return user['username'] if user else "Unknown User"