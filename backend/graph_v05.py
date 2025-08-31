# backend/graph_05.py
"""LangGraph implementation of the tutoring session flow.

Flow (v2)
──────────
load_context → intro → recap_loop → teaching_loop → testing → grading → wrap

Testing, grading, and wrap are still stubbed.
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, List
from datetime import datetime
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

from backend.session_state import (
    SessionState, Objective, QuizQuestion, TestAnswer,
    get_current_objective, has_prerequisites, all_objectives_completed,
    get_objectives_for_testing, create_initial_state,
    format_learning_objectives, format_references, calculate_final_score
)

from backend.answer_normalizer import normalize_single_character_answer

from backend.session_logger import (
    log_session_start, log_session_message, log_session_event,
    log_session_end, SessionLogger
)

from backend.db import (
    get_node_with_objectives, get_project, get_db_connection,
    update_mastery, complete_session, create_session
)

from utils.config import load_api_key
from utils.providers import create_client, get_model_for_task, get_provider_config, get_current_provider

from backend.quiz_generators import (
    generate_final_test
)

from backend.quiz_grader import (
    grade_test
)

from backend.tutor_prompts import (
    format_teaching_prompt,
    format_recap_prompt,
    TEACHING_CONTROL_SCHEMA,
    RECAP_CONTROL_SCHEMA,
    extract_control_block,
    clean_improper_citations,
    remove_control_blocks,
)

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────

# Transition message prefix used when moving to the next objective
NEXT_OBJECTIVE_PREFIX = "Let's move to the next objective:"

# ────────────────────────────────────────────────────────────────────────────
# Utilities
# ────────────────────────────────────────────────────────────────────────────

llm = None
def get_llm():
    print("-----------get_llm-----------")
    global llm
    if llm is None:
        # Get current provider and its configuration
        provider = get_current_provider()
        
        # Get API key for the current provider
        api_key = load_api_key(provider)
        if not api_key or not api_key.strip():
            print(f"[get_llm] No API key configured for provider: {provider}")
            return None

        try:
            # Get provider configuration
            config = get_provider_config(provider)
            chat_model = get_model_for_task("chat", provider)
            
            # Create ChatOpenAI instance with provider-specific settings
            llm_kwargs = {
                "model_name": chat_model,
                "temperature": 0.7,
                "openai_api_key": api_key,
            }
            
            # Add base_url if provider requires it (e.g., OpenRouter)
            if config.get("base_url"):
                llm_kwargs["base_url"] = config["base_url"]
            
            # Add OpenRouter app attribution headers if using OpenRouter
            if provider == "openrouter":
                from utils.config import APP_NAME, APP_URL
                llm_kwargs["default_headers"] = {
                    "HTTP-Referer": APP_URL,
                    "X-Title": APP_NAME,
                }
            
            llm = ChatOpenAI(**llm_kwargs)
            
            # Test the LLM with a simple call to validate the API key
            llm.invoke([{"role": "user", "content": "test"}])
        except Exception as e:
            print(f"[get_llm] Failed to initialize LLM: {str(e)}")
            llm = None
            return None
            
    return llm

def get_prerequisite_objectives(project_id: str, node_original_id: str) -> List[Objective]:
    """Get learning objectives from all prerequisite nodes"""
    prerequisites = []
    
    try:
        with get_db_connection() as conn:
            # Find all source nodes that are prerequisites for the current node
            cursor = conn.execute("""
                SELECT DISTINCT n.id, n.label, lo.id, lo.description, lo.mastery
                FROM edge e
                JOIN node n ON n.original_id = e.source AND n.project_id = e.project_id
                JOIN learning_objective lo ON lo.node_id = n.id
                WHERE e.target = ? AND e.project_id = ?
                ORDER BY n.label, lo.idx_in_node
            """, (node_original_id, project_id))
            
            for row in cursor.fetchall():
                node_id, node_label, lo_id, lo_description, lo_mastery = row
                prerequisites.append(
                    Objective(
                        id=lo_id,
                        description=lo_description,
                        mastery=lo_mastery,
                        node_id=node_id
                    )
                )
        
        print(f"[get_prerequisite_objectives] Found {len(prerequisites)} prerequisite objectives")
        return prerequisites
        
    except Exception as e:
        print(f"[get_prerequisite_objectives] Error: {str(e)}")
        return []


def calculate_session_duration(state: SessionState) -> float:
    """Calculate session duration in minutes"""
    if not state.get('session_start') or not state.get('session_end'):
        return 0.0
    
    start = datetime.fromisoformat(state['session_start'])
    end = datetime.fromisoformat(state['session_end'])
    duration = (end - start).total_seconds() / 60.0
    return round(duration, 1)


def load_context_node(state: SessionState) -> SessionState:
    """Initialize session with all necessary data from database"""
    print("-----------load_context_node-----------")
    print(f"[load_context] Loading data for node {state['node_id']}")
    
    try:
        # 1. Load node data with objectives
        node_data = get_node_with_objectives(state['node_id'])
        print(f"[load_context] node_data: {node_data}")
        if not node_data:
            raise ValueError(f"Node {state['node_id']} not found")
        
        # 2. Parse references
        references_sections_resolved = node_data.get('references_sections_resolved', [])
        
        # 3. Categorize objectives by mastery
        all_objectives = []
        objectives_to_teach = []
        objectives_already_known = []
        
        for lo in node_data.get('learning_objectives', []):
            obj = Objective(
                id=lo['id'],
                description=lo['description'],
                mastery=lo.get('mastery', 0.0),
                node_id=state['node_id']
            )
            all_objectives.append(obj)
            
            if obj.mastery < 0.7:
                objectives_to_teach.append(obj)
            else:
                objectives_already_known.append(obj)
        
        # 4. Get prerequisite objectives
        prerequisite_objectives = get_prerequisite_objectives(
            state['project_id'],
            node_data.get('original_id', '')
        )
        
        # 5. Load project resources
        resources = []
        project = get_project(state['project_id'])
        if project:
            resources = project.get('resources', [])
        
        # 6. Load learner profile context
        learner_profile_context = ""
        try:
            from backend.learner_profile import learner_profile_manager
            learner_profile_context = learner_profile_manager.get_profile_context_for_session(
                state['project_id'], 
                node_data.get('project_topic', '')
            )
        except Exception as e:
            logger.warning(f"Could not load learner profile context: {e}")
            learner_profile_context = "LEARNER PROFILE CONTEXT: Profile information not available."
        
        # Create new state with all loaded data
        new_state = {
            **state,
            'node_original_id': node_data.get('original_id', ''),
            'node_title': node_data.get('label', 'Unknown Node'),
            'project_topic': node_data.get('project_topic', ''),
            'references_sections_resolved': references_sections_resolved,
            'all_objectives': all_objectives,
            'objectives_to_teach': objectives_to_teach,
            'objectives_already_known': objectives_already_known,
            'prerequisite_objectives': prerequisite_objectives,
            'resources': resources,
            'learner_profile_context': learner_profile_context,
            'current_phase': 'intro',
            'navigate_without_user_interaction': True
        }
        
        # 6. Initialize session log
        log_session_start(new_state)
        log_session_event(new_state, "session_initialized", {
            "node": new_state['node_title'],
            "objectives_to_teach": len(objectives_to_teach),
            "objectives_already_known": len(objectives_already_known),
            "prerequisites": len(prerequisite_objectives)
        })
        
        print(f"[load_context] Loaded {len(all_objectives)} objectives, "
              f"{len(objectives_to_teach)} to teach, "
              f"{len(prerequisite_objectives)} prerequisites")
        
        return new_state
        
    except Exception as e:
        print(f"[load_context] Error loading context: {str(e)}")
        log_session_event(state, "error", {"phase": "load_context", "error": str(e)})
        raise

# ────────────────────────────────────────────────────────────────────────────
# Intro node
# ────────────────────────────────────────────────────────────────────────────

def intro_node(state: SessionState) -> SessionState:
    """Generate lesson introduction with objectives and hand control to recap phase."""
    print("-----------intro_node-----------")
    print(f"[intro_node] start state: {state}")
    
    # Generate lesson introduction message with objectives
    objectives = state.get("objectives_to_teach", [])
    node_title = state.get("node_title", "Learning Session")
    
    if objectives:
        # Create a nicely formatted introduction with objectives
        intro_content = f"# 🎓 **Welcome to: {node_title}**\n\n"
        intro_content += "## 📚 **In this lesson, you will learn:**\n\n"
        
        for obj in objectives:
            intro_content += f"• {obj.description}\n"
        
        intro_content += "\n**Let's begin your learning journey!** 🚀\n\n"
        intro_content += "I'm here to guide you through each of these objectives step by step. Are you ready to start?"
    else:
        # Fallback for sessions without objectives
        intro_content = f"# 🎓 **Welcome to: {node_title}**\n\nLet's begin this learning session! I'm here to guide you through the material."
    
    # Don't mutate state - return new state object
    return {
        **state,
        "history": state.get("history", []) + [{"role": "assistant", "content": intro_content}],
        "current_phase": "recap",
        'navigate_without_user_interaction': True
    }

# ────────────────────────────────────────────────────────────────────────────
# Recap node
# ────────────────────────────────────────────────────────────────────────────

def recap_node(state: SessionState) -> SessionState:
    """Runs prerequisite recap loop until control flag signals completion."""
    print("-----------recap_node-----------")
    # print(f"[recap_node] start state: {state}")
    
    # Get current history without mutation
    history = state.get("history", [])
    # FIXME: I think there is an infinite loop here

    recent_los = [o.description for o in state.get("prerequisite_objectives", [])]
    recent_los = recent_los + [o.description for o in state.get("objectives_already_known", [])]

    # if recent_los is empty, then we have nothing to recap
    if not recent_los:
        print(f"[recap_node] no recent_los, will return new state")
        new_state = {
            **state, 
            "current_phase": "teaching",
            'navigate_without_user_interaction': True}
        return new_state
    
    next_obj_label = (
        state.get("objectives_to_teach", [])[0].description
        if state.get("objectives_to_teach")
        else "our next topic"
    )
    print(f"[recap_node] recent_los: {recent_los}")
    print(f"[recap_node] next_obj_label: {next_obj_label}")

    sys_prompt = format_recap_prompt(
        recent_los=recent_los,
        next_obj=next_obj_label,
        refs=state.get("references_sections_resolved", []),
        learner_profile_context=state.get("learner_profile_context", "")
    )

    messages = [{"role": "system", "content": sys_prompt}, *history]

    # this was causing infinite loops
    # # seed with user readiness if session just entered recap
    # if (not history) or (history[-1]["role"] != "user"):
    #     messages.append({"role": "user", "content": "Ready"})

    try:
        # Try to get LLM response with retry
        llm = get_llm()
        if not llm:
            raise ValueError("LLM not initialized - check API key")
            
        response = llm.invoke(messages)
        assistant_content = response.content
        
        # Clean up improper citations in the response
        cleaned_content = clean_improper_citations(assistant_content, state.get("references_sections_resolved", []))
        # Remove control blocks from user-facing content
        cleaned_content = remove_control_blocks(cleaned_content)
        assistant = {"role": "assistant", "content": cleaned_content}
        print(f"[recap_node] assistant: {assistant}")
        
        # Check control block (use original content for control extraction)
        ctrl = extract_control_block(assistant_content, RECAP_CONTROL_SCHEMA)
        next_phase = "teaching" if ctrl and ctrl.get("prereq_complete") else "recap"
        
        # Return new state with updated history and phase
        return {
            **state,
            "history": history + [assistant],
            "current_phase": next_phase,
            'navigate_without_user_interaction': True if next_phase == "teaching" else False
        }
            
    except Exception as e:
        # Log error and provide fallback response
        print(f"[recap_node] LLM error: {str(e)}")
        log_session_event(state, "llm_error", {
            "phase": "recap", 
            "error": str(e),
            "retrying": False
        })
        
        # Provide a fallback response
        fallback_message = {
            "role": "assistant", 
            "content": "I apologize, I'm having some technical difficulties. "
                      "Let's proceed to the main lesson. Type 'ready' when you'd like to continue."
        }
        
        # Check if user wants to continue despite error
        next_phase = "recap"
        if history and history[-1]["role"] == "user" and "ready" in history[-1]["content"].lower():
            next_phase = "teaching"
        
        # Return new state with fallback message
        return {
            **state,
            "history": history + [fallback_message],
            "current_phase": next_phase,
            'navigate_without_user_interaction': True if next_phase == "teaching" else False
        }

# ────────────────────────────────────────────────────────────────────────────
# Teaching node (unchanged logic, now entered after recap)
# ────────────────────────────────────────────────────────────────────────────

def teaching_node(state: SessionState) -> SessionState:
    print("-----------teaching_node-----------")    
    # Get values without mutation
    history = state.get("history", [])
    idx = state.get("objective_idx", 0)
    objectives = state.get("objectives_to_teach", [])

    # Check if all objectives completed or index is out of bounds
    if idx >= len(objectives):
        return {**state, 
                "current_phase": "testing",
                'navigate_without_user_interaction': True}

    # Ensure we have a valid objective
    if not objectives or idx < 0:
        print(f"[teaching_node] ERROR: Invalid objective index {idx} for objectives list of length {len(objectives)}")
        return {**state, 
                "current_phase": "testing",
                'navigate_without_user_interaction': True}

    current_obj = objectives[idx]
    
    # Additional safety check for current_obj
    if current_obj is None:
        print(f"[teaching_node] ERROR: current_obj is None at index {idx}")
        return {**state, 
                "current_phase": "testing",
                'navigate_without_user_interaction': True}

    sys_prompt = format_teaching_prompt(
        obj_id=current_obj.id,
        obj_label=current_obj.description,
        recent=[o.description for o in state.get("objectives_already_known", [])],
        remaining=[o.description for o in objectives[idx + 1 :]],
        refs=state.get("references_sections_resolved", []),
        learner_profile_context=state.get("learner_profile_context", "")
    )

    messages = [{"role": "system", "content": sys_prompt}, *history]

    # If we're starting a new objective and there's no user message to respond to,
    # or if the last message is from the assistant, add a ready message
    if not history or history[-1]["role"] != "user":
        # Check if this is a new objective (based on transition messages)
        is_new_objective = (
            len(history) >= 2 and 
            history[-1]["role"] == "assistant" and 
            NEXT_OBJECTIVE_PREFIX in history[-1]["content"]
        )
        if is_new_objective:
            messages.append({"role": "user", "content": "I'm ready to learn about this new topic."})
        elif not history:
            messages.append({"role": "user", "content": "I'm ready to start learning."})
        else:
            # If last message was from assistant but not a transition, add a simple ready message
            messages.append({"role": "user", "content": "Please continue."})

    try:
        # Get LLM response with error handling
        llm = get_llm()
        if not llm:
            raise ValueError("LLM not initialized - check API key")
            
        response = llm.invoke(messages)
        assistant_content = response.content
        
        # Check if response is empty or whitespace-only
        if not assistant_content or not assistant_content.strip():
            print(f"[teaching_node] WARNING: LLM returned empty content for objective {current_obj.description}")
            assistant_content = f"Let me introduce you to: {current_obj.description}. What do you think this concept might involve?"
        
        # Clean up improper citations in the response
        cleaned_content = clean_improper_citations(assistant_content, state.get("references_sections_resolved", []))
        # Remove control blocks from user-facing content
        cleaned_content = remove_control_blocks(cleaned_content)
        
        # Final check for empty cleaned content
        if not cleaned_content or not cleaned_content.strip():
            print(f"[teaching_node] WARNING: Cleaned content is empty for objective {current_obj.description}")
            cleaned_content = f"Let's explore: {current_obj.description}. What questions do you have about this topic?"
            
        assistant = {"role": "assistant", "content": cleaned_content}
        print(f"[teaching_node] assistant llm call response: {response.content}")
        print(f"[teaching_node] cleaned assistant content: {cleaned_content}")

        # Check control block (use original content for control extraction)
        ctrl = extract_control_block(assistant_content, TEACHING_CONTROL_SCHEMA)
        if ctrl and ctrl.get("objective_complete"):
            # FIXME: when an objective has been completed, we should get a summary of the messages in that and only send a summary from then onwards
            new_objective_idx = idx + 1;
            if new_objective_idx < len(objectives):
                next_obj = objectives[new_objective_idx]
                if next_obj is not None and hasattr(next_obj, 'description'):
                    assistant2 = {"role": "assistant", "content": NEXT_OBJECTIVE_PREFIX + " " + next_obj.description}
                else:
                    print(f"[teaching_node] WARNING: Next objective at index {new_objective_idx} is invalid")
                    assistant2 = {"role": "assistant", "content": "Great job! You've mastered all the objectives for this node. Let's move to the testing phase!"}
            else:
                assistant2 = {"role": "assistant", "content": "Great job! You've mastered all the objectives for this node. Let's move to the testing phase!"}
            # Advance to next objective - convert set to list for proper serialization
            completed_objs = list(state.get("completed_objectives", []))
            if current_obj.id not in completed_objs:
                completed_objs = completed_objs + [current_obj.id]
            
            return {
                **state,
                "history": history + [assistant, assistant2],
                "objective_idx": idx + 1,
                # Wait for user interaction before proceeding to next objective
# Wait for user interaction before proceeding to next objective
        'navigate_without_user_interaction': False,
                "completed_objectives": completed_objs
            }
        
        # Continue with current objective
        return {
            **state,
            "history": history + [assistant],
        }
            
    except Exception as e:
        # Log error
        print(f"[teaching_node] LLM error: {str(e)}")
        log_session_event(state, "llm_error", {
            "phase": "teaching",
            "objective": current_obj.description,
            "error": str(e)
        })
        
        # Provide fallback teaching content
        fallback_message = {
            "role": "assistant",
            "content": f"""I'm experiencing some technical issues, but let me share what I know about {current_obj.description}:

This is an important concept in our learning journey. While I can't provide the full interactive lesson right now, 
I encourage you to:
1. Review any available resources
2. Think about how this relates to what we've learned
3. Let me know if you'd like to skip to the next topic

Type 'continue' to move to the next objective, or ask me any questions you have.""".strip()
        }
        
        # Check for manual progression
        should_advance = (history and 
                         history[-1]["role"] == "user" and 
                         "continue" in history[-1]["content"].lower())
        
        if should_advance:
            return {
                **state,
                "history": history + [fallback_message],
                "objective_idx": idx + 1
            }
        
        # Stay on current objective
        return {
            **state,
            "history": history + [fallback_message]
        }

def testing_node(state: SessionState) -> SessionState:
    """
    Simplified testing loop that:
      • generates the final test on first entry
      • alternates between asking questions and receiving answers
      • advances to grading when all questions are answered
    """
    print("-----------testing_node-----------")
    
    # Get values without mutation
    history = state.get("history", [])
    questions = state.get("final_test_questions", [])
    answers = state.get("final_test_answers", [])

    # Initialize the test once if not already done
    if not questions:
        try:
            llm = get_llm()
            if not llm:
                raise ValueError("LLM not initialized - check API key")
                
            objectives = get_objectives_for_testing(state)
            new_questions = generate_final_test(llm, objectives, max_questions=6)
            
            # Return state with initialized test
            return {
                **state,
                "final_test_questions": new_questions,
                "final_test_answers": [],
                'navigate_without_user_interaction': True
            }
            
        except Exception as e:
            # Log error
            print(f"[testing_node] Error generating test: {str(e)}")
            log_session_event(state, "test_generation_error", {"error": str(e)})
            
            # Provide simple fallback questions
            fallback_questions = [
                "Can you explain the main concept we covered today in your own words?",
                "What was the most important thing you learned in this session?",
                "How would you apply what you learned to a real-world scenario?"
            ]
            
            # Return state with fallback questions
            return {
                **state,
                "final_test_questions": fallback_questions,
                "final_test_answers": []
            }

    # Process any new user answer
    if history and history[-1]["role"] == "user" and len(answers) < len(questions):
        # User just provided an answer
        raw_answer = history[-1]["content"]
        current_question = questions[len(answers)]
        
        # Normalize single character answers for multiple choice questions
        normalized_answer = normalize_single_character_answer(raw_answer, current_question)
        
        new_answers = answers + [normalized_answer]
        return {**state, "final_test_answers": new_answers}

    # Ask next question or advance to grading
    if len(answers) < len(questions):
        # Still have questions to ask
        question_idx = len(answers)
        new_message = {
            "role": "assistant", 
            "content": f"**Question {question_idx + 1}/{len(questions)}:**\n\n{questions[question_idx]}"
        }
        
        return {
            **state,
            "history": history + [new_message]
        }
    else:
        # All questions answered - advance to grading
        return {**state, 
                "current_phase": "grading",
                'navigate_without_user_interaction': True}


def grading_node(state: SessionState) -> SessionState:
    """
    Run LLM grading over final_test_questions / answers,
    append feedback, then advance to wrap phase.
    """
    qs = state.get("final_test_questions", [])
    ans = state.get("final_test_answers", [])
    history = state.get("history", [])


    try:
        llm = get_llm()
        if not llm:
            raise ValueError("LLM not initialized - check API key")
            
        per_q, overall = grade_test(llm, qs, ans)
        
        # Build feedback bubble
        lines = [f"Q{i+1}: {round(s*100)}%" for i, s in enumerate(per_q)]
        summary = (
            "### Test Results\n"
            + "\n".join(lines)
            + f"\n\n**Overall score:** {round(overall*100)}%"
        )
        
        # Return new state with scores and feedback
        return {
            **state,
            "objective_scores": {"session": overall},
            "history": history + [{"role": "assistant", "content": summary}],
            "current_phase": "wrap",
            "session_end": datetime.now().isoformat(),
            'navigate_without_user_interaction': True
        }
        
    except Exception as e:
        # Log error
        print(f"[grading_node] Error grading test: {str(e)}")
        log_session_event(state, "grading_error", {"error": str(e)})
        
        # Provide fallback grading (assume passing grade to allow progression)
        fallback_summary = (
            "### Test Results\n"
            "I encountered an issue while grading your responses, but based on your participation "
            "throughout the session, I'm giving you credit for your effort.\n\n"
            "**Estimated score:** 75%"
        )
        
        # Return new state with fallback scores
        return {
            **state,
            "objective_scores": {"session": 0.75},
            "history": history + [{"role": "assistant", "content": fallback_summary}],
            "current_phase": "wrap",
            "session_end": datetime.now().isoformat(),
            'navigate_without_user_interaction': True
        }


def wrap_node(state: SessionState) -> SessionState:
    """
    Wrap up the session:
    1. Update mastery scores in the database
    2. Complete the session record
    3. Log session completion
    4. Provide a summary message
    """
    print("-----------wrap_node-----------")
    
    # Get values without mutation
    history = state.get("history", [])
    objectives_taught = state.get("objectives_to_teach", [])
    objective_scores = state.get("objective_scores", {})
    overall_score = objective_scores.get("session", 0.0)

    try:
        # Update mastery for each objective based on test performance
        if objectives_taught and overall_score > 0:
            # Prepare learning objective scores for the update_mastery function
            lo_scores = {}
            for obj in objectives_taught:
                # Calculate new mastery based on score (max 1.0)
                new_mastery = min(1.0, obj.mastery + (overall_score * 0.3))
                lo_scores[obj.id] = new_mastery
                
            # Update mastery for the node using the correct function signature
            if lo_scores:
                node_id = state.get("node_id")
                update_mastery(node_id, lo_scores)
                
        # Complete the session in database
        session_duration = calculate_session_duration(state)
        complete_session(
            session_id=state.get("session_id"),
            final_score=overall_score
        )
        
        # Create wrap-up message
        wrap_message = f"""
## Session Complete! 🎉

**Final Score:** {round(overall_score * 100)}%
**Duration:** {round(session_duration)} minutes
**Objectives Covered:** {len(objectives_taught)}

{"Great job! You've shown solid understanding of the material." if overall_score >= 0.7 else "Keep practicing! You're making progress."}

See you next time!
        """.strip()
        
        # Log session end
        log_session_end(state)
        log_session_event(state, "session_completed", {
            "final_score": overall_score,
            "duration_minutes": session_duration,
            "objectives_taught": len(objectives_taught)
        })
        
        # Return state with wrap-up message
        return {
            **state,
            "current_phase": "completed",
            "history": history + [{"role": "assistant", "content": wrap_message}]
        }
        
    except Exception as e:
        # If anything fails, at least try to log the error and provide feedback
        print(f"[wrap_node] Error during session wrap-up: {str(e)}")
        log_session_event(state, "wrap_error", {"error": str(e)})
        
        # Return state with simple completion message
        return {
            **state,
            "current_phase": "completed",
            "history": history + [{"role": "assistant", "content": "Session complete! Thank you for learning with me today."}]
        }

# ────────────────────────────────────────────────────────────────────────────
# Graph assembly
# ────────────────────────────────────────────────────────────────────────────

graph = StateGraph(SessionState)

def router_node(state: SessionState) -> SessionState:
    return state

graph.add_node("router", router_node)

def return_phase(state: SessionState) -> str:
    return state.get("current_phase", "load_context")

graph.add_conditional_edges(
    "router",
    return_phase,
    {
        "load_context": "load_context",
        "intro": "intro",
        "recap": "recap",
        "teaching": "teaching",
        "testing": "testing",
        "grading": "grading",
        "wrap": "wrap"
    }
)


graph.add_node("load_context", load_context_node)
graph.add_node("intro", intro_node)
graph.add_node("recap", recap_node)
graph.add_node("teaching", teaching_node)
graph.add_node("testing", testing_node)
graph.add_node("grading", grading_node)
graph.add_node("wrap", wrap_node)

# Edges

graph.add_edge(START, "router")

# lol I misunderstood how langgraph works so had to do things this way
# FIXME: I think all the nodes need to point to the END

graph.add_edge("grading", "wrap")

graph.add_edge("wrap", END)

# Create checkpointer for state persistence
checkpointer = MemorySaver()

# Compile with checkpointer
session_graph = graph.compile(checkpointer=checkpointer)

# ────────────────────────────────────────────────────────────────────────────
# Runner helper
# ────────────────────────────────────────────────────────────────────────────

# def run_session(initial_state: SessionState):
#     """Run the graph to completion and return final state.
    
#     Uses the session_id as thread_id for checkpointing, enabling:
#     - Session persistence across runs
#     - Ability to resume interrupted sessions
#     - State inspection for debugging
#     """
#     # Configure with thread_id for checkpointing
#     config = {"configurable": {"thread_id": initial_state.get("session_id", "default")}}
    
#     # Run the graph with checkpointing enabled
#     return session_graph.invoke(initial_state, config)


# def resume_session(session_id: str):
#     """Resume a previously checkpointed session.
    
#     Args:
#         session_id: The session ID to resume
        
#     Returns:
#         The resumed state, or None if no checkpoint exists
#     """
#     config = {"configurable": {"thread_id": session_id}}
    
#     # Resume from last checkpoint (pass None as initial state)
#     try:
#         return session_graph.invoke(None, config)
#     except Exception as e:
#         print(f"[resume_session] No checkpoint found for session {session_id}: {e}")
#         return None

# if __name__ == "__main__":
#     init_state = {
#         "session_id": "S1",
#         "node_id": "N1",
#         "project_id": "P1",
#         "history": [],
#     }
#     final = run_session(init_state)
#     for msg in final["history"]:
#         print(f"{msg['role'].upper()}: {msg['content']}")
