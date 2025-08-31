# backend/session_state.py
"""
Session state definitions for Autodidact v0.4 session engine
Defines the state that flows through the LangGraph nodes
"""

from typing import TypedDict, List, Dict, Optional, Literal
from pydantic import BaseModel
from datetime import datetime


class Objective(BaseModel):
    """Represents a learning objective"""
    id: str
    description: str
    mastery: float
    node_id: Optional[str] = None  # Which node this objective belongs to
    
    def is_mastered(self) -> bool:
        """Check if objective is mastered (>= 0.7)"""
        return self.mastery >= 0.7


class QuizQuestion(BaseModel):
    """Represents a quiz question"""
    q: str  # The question text
    type: Literal["mcq", "free", "short", "paraphrase"]
    choices: Optional[List[str]] = None  # For MCQ only
    answer: str  # Correct answer or expected answer pattern
    objective_ids: List[str]  # Which objectives this question tests
    
    def format_for_display(self) -> str:
        """Format question for display to user"""
        if self.type == "mcq" and self.choices:
            choices_text = "\n".join([f"{chr(65+i)}. {choice}" for i, choice in enumerate(self.choices)])
            return f"{self.q}\n\n{choices_text}"
        return self.q


class TestAnswer(BaseModel):
    """Represents a user's answer to a test question"""
    question_id: int  # Index in the test
    question: QuizQuestion
    user_answer: str
    timestamp: str


class SessionState(TypedDict, total=False):
    """Complete state for a learning session"""
    
    # Core identifiers
    session_id: str
    project_id: str
    node_id: str
    node_original_id: str  # Original ID from deep research graph
    
    # Node content
    node_title: str
    project_topic: str
    references_sections_resolved: List[Dict[str, str]]
    resources: List[Dict]  # Project-level resources
    
    # Objectives tracking
    all_objectives: List[Objective]  # All objectives for this node
    objectives_to_teach: List[Objective]  # Filtered by mastery < 0.7
    objectives_already_known: List[Objective]  # mastery >= 0.7
    prerequisite_objectives: List[Objective]  # From prerequisite nodes
    completed_objectives: List[str]  # IDs of objectives taught this session (changed from Set to List)
    
    # Runtime / session control
    current_phase: Literal[
        "load_context",
        "intro",
        "recap",
        "teaching",
        "testing",
        "grading",
        "wrap",
        "completed",
    ]
    objective_idx: int            # index into objectives_to_teach
    exit_requested: bool          # set by UI to trigger early exit
    history: List[Dict[str, str]] # chat transcript ({role, content})
    
    # Image cache for AI context awareness
    displayed_images: List[Dict[str, str]]  # List of {url, description, context} for images shown to user
    
    # Quiz tracking
    final_test_questions: List[str]
    final_test_answers: List[str]
    test_question_idx: int
    awaiting_answer: bool
    
    # Grading
    objective_scores: Dict[str, float]  # Final scores per objective ID
    
    # Metadata
    # Optional logging & timestamps
    # ──────────────────────────────────
    turn_count: int
    session_start: str #datetime str in isoformat
    last_message_ts: Optional[str] #datetime str in isoformat
    session_end: Optional[str] #datetime str in isoformat

    # Interruption handling
    interruption_detected: Optional[bool]  # True if session was resumed after interruption
    interruption_duration_minutes: Optional[float]  # How long the interruption lasted

    navigate_without_user_interaction: Optional[bool]


# Helper functions for state management

# FIXME: not sure if this will work after we move off of graph_04
def create_initial_state(
    session_id: str,
    project_id: str, 
    node_id: str
) -> Dict:
    """Create an initial session state"""
    return {
        # Core identifiers
        "session_id": session_id,
        "project_id": project_id,
        "node_id": node_id,
        "node_original_id": "",  # Will be populated by load_context
        
        # Node content
        "node_title": "",
        "project_topic": "",
        "resources": [],
        "references_sections_resolved": [],
        
        # Objectives tracking
        "all_objectives": [],
        "objectives_to_teach": [],
        "objectives_already_known": [],
        "prerequisite_objectives": [],
        "completed_objectives": [],  # Changed from set() to []
        
        # User interaction
        "current_phase": "load_context",
        "objective_idx": 0,
        "exit_requested": False,

        "history": [],
        
        # Image cache
        "displayed_images": [],
        
        # Quiz tracking
        "final_test_questions": [],
        "final_test_answers": [],
        "test_question_idx": 0,
        "awaiting_answer": False,
        
        # Grading
        "objective_scores": {},
        

        
        # Metadata
        "turn_count": 0,
        "session_start": datetime.now().isoformat(),
        "last_message_ts": None,
        "session_end": None,
        
        # Interruption handling
        "interruption_detected": False,
        "interruption_duration_minutes": None
    }


def get_current_objective(state: SessionState) -> Optional[Objective]:
    """Get the current objective being taught"""
    if state["objective_idx"] < len(state["objectives_to_teach"]):
        return state["objectives_to_teach"][state["objective_idx"]]
    return None


def has_prerequisites(state: SessionState) -> bool:
    """Check if this node has any prerequisites"""
    return len(state["prerequisite_objectives"]) > 0


def all_objectives_completed(state: SessionState) -> bool:
    """Check if all objectives have been taught"""
    return state["objective_idx"] >= len(state["objectives_to_teach"])


def get_objectives_for_testing(state: SessionState) -> List[Objective]:
    """Get objectives that should be included in final test"""
    if state["exit_requested"]:
        # Only test objectives that were actually taught
        return [
            obj for obj in state["objectives_to_teach"]
            if obj.id in state["completed_objectives"]
        ]
    else:
        # Test all objectives that needed teaching
        return state["objectives_to_teach"]


def get_formatted_objectives_for_intro(state: SessionState) -> List[str]:
    """Get formatted objectives list for lesson introduction display"""
    objectives = state.get("objectives_to_teach", [])
    return [obj.description for obj in objectives]


def get_objectives_progress_info(state: SessionState) -> Dict:
    """Get objectives progress information for progress tracking"""
    objectives = state.get("objectives_to_teach", [])
    current_idx = state.get("objective_idx", 0)
    completed = set(state.get("completed_objectives", []))
    
    progress_items = []
    for i, obj in enumerate(objectives):
        status = "completed" if obj.id in completed else "current" if i == current_idx else "upcoming"
        progress_items.append({
            "description": obj.description,
            "status": status,
            "index": i
        })
    
    return {
        "items": progress_items,
        "total": len(objectives),
        "completed_count": len([item for item in progress_items if item["status"] == "completed"]),
        "current_index": current_idx
    }


def get_session_completion_info(state: SessionState) -> Dict:
    """Get session completion summary information"""
    objectives = state.get("objectives_to_teach", [])
    completed = set(state.get("completed_objectives", []))
    scores = state.get("objective_scores", {})
    
    completed_objectives = [obj for obj in objectives if obj.id in completed]
    total_score = sum(scores.values()) / len(scores) if scores else 0.0
    
    return {
        "objectives": [obj.description for obj in completed_objectives],
        "total_objectives": len(objectives),
        "completed_count": len(completed_objectives),
        "final_score": total_score,
        "completion_percentage": (len(completed_objectives) / len(objectives)) * 100 if objectives else 100,
        "session_start": state.get("session_start"),
        "session_end": state.get("session_end")
    }


def calculate_final_score(state: SessionState) -> float:
    """Calculate overall mastery score from objective scores"""
    if not state["objective_scores"]:
        return 0.0
    return sum(state["objective_scores"].values()) / len(state["objective_scores"])


def detect_session_interruption(state: SessionState, threshold_minutes: float = 10.0) -> tuple[bool, float]:
    """Detect if session was interrupted based on last message timestamp
    
    Args:
        state: Current session state
        threshold_minutes: Minutes of inactivity to consider an interruption
        
    Returns:
        tuple of (was_interrupted, minutes_since_last_message)
    """
    if not state.get("last_message_ts"):
        return False, 0.0
    
    try:
        last_message_time = datetime.fromisoformat(state["last_message_ts"])
        current_time = datetime.now()
        
        # Calculate time difference in minutes
        time_diff = current_time - last_message_time
        minutes_elapsed = time_diff.total_seconds() / 60.0
        
        # Consider it an interruption if more than threshold minutes have passed
        was_interrupted = minutes_elapsed >= threshold_minutes
        return was_interrupted, minutes_elapsed
    except (ValueError, TypeError):
        # Invalid timestamp format
        return False, 0.0


def format_learning_objectives(objectives: List[Objective]) -> str:
    """Format objectives for display in prompts"""
    if not objectives:
        return "No objectives"
    return "\n".join([f"- {obj.description}" for obj in objectives])


def format_references(references: List[Dict]) -> str:
    """Format references for inclusion in prompts"""
    if not references:
        return "No specific references"
    
    formatted = []
    for ref in references:
        rid = ref.get("rid", "unknown")
        loc = ref.get("loc", "")
        formatted.append(f"- {rid}: {loc}")
    
    return "\n".join(formatted) 