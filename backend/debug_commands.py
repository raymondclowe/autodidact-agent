"""
Debug commands for skipping lessons and sessions
Provides cheat commands for developers to quickly progress through lessons
"""

from typing import Dict, Any, Optional
from backend.db import complete_session, update_mastery, get_node_with_objectives

# Global debug mode state
_debug_mode_enabled = False


def is_debug_command(message: str) -> bool:
    """Check if a message is a debug command"""
    cleaned = message.strip().lower()
    return cleaned.startswith('/')


def is_debug_mode_enabled() -> bool:
    """Check if debug mode is currently enabled"""
    return _debug_mode_enabled


def set_debug_mode(enabled: bool) -> None:
    """Enable or disable debug mode"""
    global _debug_mode_enabled
    _debug_mode_enabled = enabled


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
        # This is a HARDCODED score for debug purposes - different from normal scoring
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
        
        debug_info = {
            'scoring_method': 'HARDCODED_DEBUG',
            'debug_score': debug_score,
            'normal_scoring_method': 'AI_LLM_GRADING',
            'normal_scoring_description': 'In normal sessions, scores are calculated by AI (LLM) evaluating user answers to quiz questions',
            'debug_scoring_description': f'Debug mode uses a fixed high score of {int(debug_score * 100)}% to allow quick progression'
        }
        
        return {
            'success': True,
            'score': debug_score,
            'objectives_updated': len(lo_scores),
            'message': f"🔧 DEBUG: Session force-completed with {int(debug_score * 100)}% score",
            'debug_info': debug_info if _debug_mode_enabled else None
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
    global _debug_mode_enabled
    
    if not is_debug_command(message):
        return None
    
    command = message.strip().lower()
    
    if command == '/completed':
        return force_complete_session(
            session_info['id'], 
            session_info['node_id']
        )
    elif command in ['/help', '/debug']:
        debug_status = "🟢 ON" if _debug_mode_enabled else "🔴 OFF"
        return {
            'success': True,
            'message': f"""🔧 **Debug Commands Available:**

• `/completed` - Force complete the current session with high score (85%)
• `/help` or `/debug` - Show this help message
• `/debug_mode` - Toggle debug mode {debug_status}

**Debug Mode Status:** {debug_status}

These commands are intended for developers and testing purposes to quickly progress through lessons without completing the full learning process.

**Note:** Using debug commands will mark learning objectives as mastered and allow progression to subsequent topics.""",
            'is_help': True
        }
    elif command == '/debug_mode':
        _debug_mode_enabled = not _debug_mode_enabled
        status = "🟢 ENABLED" if _debug_mode_enabled else "🔴 DISABLED"
        return {
            'success': True,
            'message': f"""🔧 **Debug Mode {status}**

**What Debug Mode Shows:**
• Detailed scoring information when using `/completed`
• Explanation of scoring methods (AI vs Hardcoded)
• Additional technical details for developers

**Scoring Methods Explained:**
• **Normal Sessions**: AI (LLM) evaluates your quiz answers and calculates scores
• **Debug Sessions**: Uses hardcoded 85% score for quick progression

Debug mode is now {status.lower()}.""",
            'is_debug_mode_toggle': True
        }
    
    return {
        'success': False,
        'error': f'Unknown debug command: {command}'
    }