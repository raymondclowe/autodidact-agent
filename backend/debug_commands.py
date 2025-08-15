"""
Debug commands for skipping lessons and sessions
Provides cheat commands for developers to quickly progress through lessons
"""

import logging
from typing import Dict, Any, Optional
from backend.db import complete_session, update_mastery, update_mastery_direct, get_node_with_objectives

# Constants
DEBUG_SCORE = 0.85  # Default score for debug completions (85%)

# Global debug mode state
_debug_mode_enabled = False

# Set up logging
logger = logging.getLogger(__name__)


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
        # Set a high score for debug completion
        # This is a HARDCODED score for debug purposes - different from normal scoring
        completion_result = complete_session(session_id, DEBUG_SCORE)
        
        if completion_result['success']:
            # Update mastery for all objectives in this node (debug mode)
            node_data = get_node_with_objectives(node_id)
            if node_data and 'objectives' in node_data:
                for obj in node_data['objectives']:
                    update_mastery_direct(node_id, obj['id'], DEBUG_SCORE)
            
            logger.info(f"DEBUG: Force completed session {session_id} with score {DEBUG_SCORE}")
            
            return {
                'success': True,
                'message': f"🚀 **Session Force Completed!**\n\nScore: {int(DEBUG_SCORE * 100)}% (Debug Mode)\n\n*This was a debug completion with hardcoded high score.*",
                'is_debug_completion': True,
                'final_score': DEBUG_SCORE
            }
        else:
            return {
                'success': False,
                'error': f"Failed to complete session: {completion_result.get('error', 'Unknown error')}"
            }
    
    except Exception as e:
        logger.error(f"Error in force_complete_session: {e}")
        return {
            'success': False,
            'error': f"Error completing session: {str(e)}"
        }


def advance_to_next_objective(session_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mark the current objective as complete and advance to the next one
    This simulates the AI completing an objective naturally
    
    Args:
        session_info: Current session information
    
    Returns:
        Dict with advancement status and details
    """
    try:
        # This works by injecting a control block that the session will process
        # as if the AI naturally completed the objective
        return {
            'success': True,
            'message': "✅ **Moving to next objective...**\n\n*Marking current learning point as understood.*",
            'is_objective_advancement': True,
            'inject_control_block': True,  # Special flag for session processing
            'control_block': '{"objective_complete": true}',  # The actual control to inject
            'simulated_ai_message': "Great! I can see you understand this concept well. Let's move on to the next learning point.\n\n<control>{\"objective_complete\": true}</control>"
        }
    
    except Exception as e:
        logger.error(f"Error in advance_to_next_objective: {e}")
        return {
            'success': False,
            'error': f"Error advancing objective: {str(e)}"
        }


def handle_debug_command(message: str, session_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Handle debug commands for quick progression through lessons
    
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
    elif command in ['/next', '/got_it', '/understood']:
        return advance_to_next_objective(session_info)
    elif command in ['/help', '/debug']:
        debug_status = "🟢 ON" if _debug_mode_enabled else "🔴 OFF"
        return {
            'success': True,
            'message': f"""🔧 **Debug Commands Available:**

• `/completed` - Force complete the current session with high score ({int(DEBUG_SCORE * 100)}%)
• `/next` or `/got_it` or `/understood` - Mark current objective as complete and move to next
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
• **Debug Sessions**: Uses hardcoded {int(DEBUG_SCORE * 100)}% score for quick progression

Debug mode is now {status.lower()}.""",
            'is_debug_mode_toggle': True
        }
    
    return {
        'success': False,
        'error': f'Unknown debug command: {command}'
    }