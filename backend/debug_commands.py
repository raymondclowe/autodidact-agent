"""
Debug commands for skipping lessons and sessions
Provides cheat commands for developers to quickly progress through lessons
"""

from typing import Dict, Any, Optional
from backend.db import complete_session, update_mastery, get_node_with_objectives


def is_debug_command(message: str) -> bool:
    """Check if a message is a debug command"""
    cleaned = message.strip().lower()
    return cleaned.startswith('/')


def force_complete_session(session_id: str, node_id: str) -> Dict[str, Any]:
    """
    Force complete the current session with high mastery scores
    
    Args:
        session_id: ID of the session to complete
        node_id: ID of the node being learned
    
    Returns:
        Dict with completion status and details
    """
    try:
        # Set a high score for debug completion (0.85 = 85%)
        debug_score = 0.85
        
        # Get node information to update learning objectives
        node_info = get_node_with_objectives(node_id)
        if not node_info:
            return {
                'success': False,
                'error': 'Node not found'
            }
        
        # Create learning objective scores - set all to high mastery
        lo_scores = {}
        for lo in node_info.get('learning_objectives', []):
            # Set high mastery (0.85) for all learning objectives
            lo_scores[lo['id']] = debug_score
        
        # Update mastery scores
        if lo_scores:
            update_mastery(node_id, lo_scores)
        
        # Complete the session
        complete_session(session_id, debug_score)
        
        return {
            'success': True,
            'score': debug_score,
            'objectives_updated': len(lo_scores),
            'message': f"🔧 DEBUG: Session force-completed with {int(debug_score * 100)}% score"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_debug_command(message: str, session_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Handle debug commands from user input
    
    Args:
        message: User's message
        session_info: Current session information
    
    Returns:
        Dict with command result or None if not a debug command
    """
    if not is_debug_command(message):
        return None
    
    command = message.strip().lower()
    
    if command == '/completed':
        return force_complete_session(
            session_info['id'], 
            session_info['node_id']
        )
    elif command in ['/help', '/debug']:
        return {
            'success': True,
            'message': """🔧 **Debug Commands Available:**

• `/completed` - Force complete the current session with high score (85%)
• `/help` or `/debug` - Show this help message

These commands are intended for developers and testing purposes to quickly progress through lessons without completing the full learning process.

**Note:** Using debug commands will mark learning objectives as mastered and allow progression to subsequent topics.""",
            'is_help': True
        }
    
    return {
        'success': False,
        'error': f'Unknown debug command: {command}'
    }