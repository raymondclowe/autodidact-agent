"""
User Management Module
Handles simple user identification and management for multi-user support
"""

import uuid
import logging
from typing import List, Dict, Optional
from contextlib import contextmanager
from backend.db import get_db_connection

logger = logging.getLogger(__name__)

# Default user for backwards compatibility
DEFAULT_USER_ID = "default"
DEFAULT_USER_NAME = "Default User"

class UserManager:
    """Manages user accounts with simple username-based identification"""
    
    def __init__(self):
        """Initialize user manager and ensure default user exists"""
        self.ensure_default_user()
    
    def ensure_default_user(self):
        """Ensure the default user exists for backwards compatibility"""
        try:
            if not self.get_user(DEFAULT_USER_ID):
                self.create_user(DEFAULT_USER_ID, DEFAULT_USER_NAME)
                logger.info("Created default user for backwards compatibility")
        except Exception as e:
            logger.error(f"Failed to ensure default user exists: {e}")
    
    def create_user(self, user_id: str, username: str) -> bool:
        """Create a new user account"""
        if not user_id or not username:
            raise ValueError("User ID and username are required")
        
        # Clean and validate inputs
        user_id = user_id.strip().lower()
        username = username.strip()
        
        if len(user_id) < 3 or len(username) < 1:
            raise ValueError("User ID must be at least 3 characters, username at least 1 character")
        
        # Validate user ID format - must be alphanumeric with no spaces or special characters
        if ' ' in user_id or not user_id.isalnum():
            raise ValueError("User ID must be alphanumeric with no spaces or special characters")
        
        # Check if user already exists
        if self.get_user(user_id):
            raise ValueError(f"User ID '{user_id}' already exists")
        
        try:
            with get_db_connection() as conn:
                conn.execute("""
                    INSERT INTO user (id, username, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (user_id, username))
                conn.commit()
                logger.info(f"Created user: {user_id} ({username})")
                return True
        except Exception as e:
            logger.error(f"Failed to create user {user_id}: {e}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user information by ID"""
        try:
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, username, created_at 
                    FROM user 
                    WHERE id = ?
                """, (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "username": row[1],
                        "created_at": row[2]
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    def list_users(self) -> List[Dict]:
        """Get all users"""
        try:
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, username, created_at 
                    FROM user 
                    ORDER BY created_at ASC
                """)
                
                return [
                    {
                        "id": row[0],
                        "username": row[1],
                        "created_at": row[2]
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []
    
    def update_username(self, user_id: str, new_username: str) -> bool:
        """Update a user's username"""
        if not new_username or not new_username.strip():
            raise ValueError("Username cannot be empty")
        
        new_username = new_username.strip()
        
        try:
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    UPDATE user 
                    SET username = ?
                    WHERE id = ?
                """, (new_username, user_id))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"User {user_id} not found")
                
                conn.commit()
                logger.info(f"Updated username for user {user_id} to: {new_username}")
                return True
        except Exception as e:
            logger.error(f"Failed to update username for user {user_id}: {e}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user and all their data"""
        if user_id == DEFAULT_USER_ID:
            raise ValueError("Cannot delete the default user")
        
        try:
            with get_db_connection() as conn:
                conn.execute("BEGIN TRANSACTION")
                
                try:
                    # Delete user's sessions and transcripts
                    cursor = conn.execute("""
                        SELECT s.id FROM session s 
                        JOIN project p ON s.project_id = p.id 
                        WHERE p.user_id = ?
                    """, (user_id,))
                    session_ids = [row[0] for row in cursor.fetchall()]
                    
                    if session_ids:
                        placeholders = ','.join(['?' for _ in session_ids])
                        conn.execute(f"""
                            DELETE FROM transcript 
                            WHERE session_id IN ({placeholders})
                        """, session_ids)
                    
                    # Delete user's sessions
                    conn.execute("""
                        DELETE FROM session 
                        WHERE project_id IN (
                            SELECT id FROM project WHERE user_id = ?
                        )
                    """, (user_id,))
                    
                    # Delete user's learning objectives
                    conn.execute("""
                        DELETE FROM learning_objective 
                        WHERE project_id IN (
                            SELECT id FROM project WHERE user_id = ?
                        )
                    """, (user_id,))
                    
                    # Delete user's edges
                    conn.execute("""
                        DELETE FROM edge 
                        WHERE project_id IN (
                            SELECT id FROM project WHERE user_id = ?
                        )
                    """, (user_id,))
                    
                    # Delete user's nodes
                    conn.execute("""
                        DELETE FROM node 
                        WHERE project_id IN (
                            SELECT id FROM project WHERE user_id = ?
                        )
                    """, (user_id,))
                    
                    # Delete user's projects
                    conn.execute("DELETE FROM project WHERE user_id = ?", (user_id,))
                    
                    # Delete user's learner profiles
                    conn.execute("DELETE FROM generic_learner_profile WHERE user_id = ?", (user_id,))
                    conn.execute("DELETE FROM topic_learner_profile WHERE user_id = ?", (user_id,))
                    
                    # Finally delete the user
                    cursor = conn.execute("DELETE FROM user WHERE id = ?", (user_id,))
                    
                    if cursor.rowcount == 0:
                        raise ValueError(f"User {user_id} not found")
                    
                    conn.commit()
                    logger.info(f"Deleted user {user_id} and all associated data")
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise

# Global instance
user_manager = UserManager()