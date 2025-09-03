# """
# LangGraph implementation for Autodidact v0.4 session engine
# Handles the complete learning session flow with 11 nodes
# """

# from typing import Dict, List, Optional, Literal
# from datetime import datetime
# import json
# from langgraph.graph import StateGraph, END
# from langgraph.graph.message import add_messages
# from openai import OpenAI

# from backend.session_state import (
#     SessionState, Objective, QuizQuestion, TestAnswer,
#     get_current_objective, has_prerequisites, all_objectives_completed,
#     get_objectives_for_testing, create_initial_state,
#     format_learning_objectives, format_references, calculate_final_score
# )
# from backend.session_logger import (
#     log_session_start, log_session_message, log_session_event,
#     log_session_end, SessionLogger
# )
# from backend.db import (
#     get_node_with_objectives, get_project, get_db_connection,
#     update_mastery, complete_session, create_session
# )
# from utils.config import load_api_key
# from backend.quiz_generators import (
#     generate_prerequisite_quiz, generate_micro_quiz, generate_final_test
# )


# # Helper functions

# def get_next_teaching_phase(current_phase: str) -> str:
#     """Get next phase in teaching sequence"""
#     transitions = {
#         "probe_ask": "probe_respond",
#         "probe_respond": "explain_present",
#         "explain_present": "explain_respond", 
#         "explain_respond": "quiz_ask",
#         "quiz_ask": "quiz_evaluate",
#         "quiz_evaluate": "probe_ask"  # Next objective
#     }
#     return transitions.get(current_phase, "probe_ask")


# def is_waiting_phase(phase: str) -> bool:
#     """Check if phase requires user input"""
#     return phase in ["probe_ask", "explain_present", "quiz_ask"]


# def transition_phase_on_user_input(state: SessionState) -> SessionState:
#     """Transition to the appropriate response phase when user provides input"""
#     phase = state.get('current_objective_phase', 'probe_ask')
    
#     # Map waiting phases to their response phases
#     transitions_on_input = {
#         "probe_ask": "probe_respond",
#         "explain_present": "explain_respond",
#         "quiz_ask": "quiz_evaluate"
#     }
    
#     # If we're in a waiting phase and have user input, transition
#     if phase in transitions_on_input and state.get('messages') and state['messages'][-1]['role'] == 'user':
#         state['current_objective_phase'] = transitions_on_input[phase]
#         print(f"[transition_phase] {phase} -> {state['current_objective_phase']}")
    
#     return state


# def parse_final_answers(questions: List[QuizQuestion], user_text: str) -> List[str]:
#     """Use LLM to intelligently parse user's test answers"""
#     client = OpenAI(api_key=load_api_key())
    
#     # Build question list for context
#     question_list = []
#     for i, q in enumerate(questions, 1):
#         question_list.append(f"Question {i}: {q.q}")
    
#     prompt = f"""Parse the user's test answers and match them to the questions.

# Questions asked:
# {chr(10).join(question_list)}

# User's response:
# {user_text}

# Extract the answer for each question. Return a JSON array with exactly {len(questions)} strings, 
# where each string is the user's answer to the corresponding question (in order).
# If an answer is missing or unclear, use an empty string.

# Example output format: ["Answer to Q1", "Answer to Q2", "Answer to Q3", ...]
# """
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a test answer parser. Extract answers accurately, preserving the user's exact wording."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.1,
#             response_format={"type": "json_object"}
#         )
        
#         import json
#         result = json.loads(response.choices[0].message.content)
        
#         # Extract array from various possible formats
#         if isinstance(result, list):
#             answers = result
#         elif isinstance(result, dict):
#             # Try common keys
#             for key in ['answers', 'parsed_answers', 'result', 'data']:
#                 if key in result and isinstance(result[key], list):
#                     answers = result[key]
#                     break
#             else:
#                 # If no array found, return empty answers
#                 print(f"[parse_final_answers] Unexpected format: {result}")
#                 answers = [""] * len(questions)
#         else:
#             answers = [""] * len(questions)
        
#         # Ensure we have exactly the right number of answers
#         if len(answers) < len(questions):
#             answers.extend([""] * (len(questions) - len(answers)))
#         elif len(answers) > len(questions):
#             answers = answers[:len(questions)]
        
#         return answers
        
#     except Exception as e:
#         print(f"[parse_final_answers] Error parsing with LLM: {e}")
#         # Fallback to simple splitting
#         parts = user_text.split('\n\n')
#         answers = []
#         for i in range(len(questions)):
#             if i < len(parts):
#                 answers.append(parts[i].strip())
#             else:
#                 answers.append("")
#         return answers


# def calculate_session_duration(state: SessionState) -> float:
#     """Calculate session duration in minutes"""
#     if not state.get('session_start') or not state.get('session_end'):
#         return 0.0
    
#     start = datetime.fromisoformat(state['session_start'])
#     end = datetime.fromisoformat(state['session_end'])
#     duration = (end - start).total_seconds() / 60.0
#     return round(duration, 1)


# def get_tutor_system_prompt(state: SessionState) -> str:
#     """Get the system prompt for the tutor with current context"""
#     objectives_text = format_learning_objectives(state['objectives_to_teach'])
#     prereq_text = format_learning_objectives(state['prerequisite_objectives']) if state['prerequisite_objectives'] else "None"
#     references_text = format_references(state.get('references_sections', []))
    
#     return f"""You are "Ada", a concise, no-nonsense tutor.

# CONTEXT
# • Node: {state['node_title']}
# • Objectives to teach: 
# {objectives_text}
# • Prerequisites: 
# {prereq_text}
# • Domain level: {state['domain_level']}
# • References: {references_text}

# RULES
# 1. Never add praise unless explicitly requested
# 2. Keep explanations under 200 words
# 3. Focus on one objective at a time
# 4. Use Socratic method before explaining
# 5. Reference materials with (see {{rid}}) when relevant
# 6. Be direct and efficient"""





# # Node implementations

# def load_context_node(state: SessionState) -> SessionState:
#     """Initialize session with all necessary data from database"""
#     print(f"[load_context] Loading data for node {state['node_id']}")
    
#     try:
#         # 1. Load node data with objectives
#         node_data = get_node_with_objectives(state['node_id'])
#         if not node_data:
#             raise ValueError(f"Node {state['node_id']} not found")
        
#         # Store node info
#         state['node_original_id'] = node_data.get('original_id', '')
#         state['node_title'] = node_data.get('label', 'Unknown Node')
#         # Nodes don't have summary - removed this line
#         state['project_topic'] = node_data.get('project_topic', '')
        
#         # 2. Parse references
#         state['references_sections_resolved'] = node_data.get('references_sections_resolved', [])
        
#         # 3. Categorize objectives by mastery
#         all_objectives = []
#         objectives_to_teach = []
#         objectives_already_known = []
        
#         for lo in node_data.get('learning_objectives', []):
#             obj = Objective(
#                 id=lo['id'],
#                 description=lo['description'],
#                 mastery=lo.get('mastery', 0.0),
#                 node_id=state['node_id']
#             )
#             all_objectives.append(obj)
            
#             if obj.mastery < 0.7:
#                 objectives_to_teach.append(obj)
#             else:
#                 objectives_already_known.append(obj)
        
#         state['all_objectives'] = all_objectives
#         state['objectives_to_teach'] = objectives_to_teach
#         state['objectives_already_known'] = objectives_already_known
        
#         # 4. Get prerequisite objectives
#         state['prerequisite_objectives'] = get_prerequisite_objectives(
#             state['project_id'],
#             state['node_original_id']
#         )
        
#         # 5. Load project resources
#         project = get_project(state['project_id'])
#         if project:
#             state['resources'] = project.get('resources', [])
        
#         # 6. Initialize session log
#         log_session_start(state)
#         log_session_event(state, "session_initialized", {
#             "node": state['node_title'],
#             "objectives_to_teach": len(objectives_to_teach),
#             "objectives_already_known": len(objectives_already_known),
#             "prerequisites": len(state['prerequisite_objectives'])
#         })
        
#         print(f"[load_context] Loaded {len(all_objectives)} objectives, "
#               f"{len(objectives_to_teach)} to teach, "
#               f"{len(state['prerequisite_objectives'])} prerequisites")
        
#         state['current_phase'] = 'intro'
#         print(f"[load_context] state: {state}")
#         return state
        
#     except Exception as e:
#         print(f"[load_context] Error loading context: {str(e)}")
#         log_session_event(state, "error", {"phase": "load_context", "error": str(e)})
#         raise


# def tutor_intro_node(state: SessionState) -> SessionState:
#     """Introduce node and ask about prerequisites"""
#     print(f"[tutor_intro] Introducing {state['node_title']}")
    
#     client = OpenAI(api_key=load_api_key())
    
#     # Check if we need to process user's choice
#     if state['messages'] and state['messages'][-1]['role'] == 'user':
#         user_message = state['messages'][-1]['content'].lower()
        
#         # Parse user choice
#         if any(word in user_message for word in ['quiz', 'test', 'check']):
#             state['user_chose_quiz'] = True
#             log_session_event(state, "prerequisite_choice", {"choice": "quiz"})
#         elif any(word in user_message for word in ['summary', 'recap', 'review']):
#             state['user_chose_quiz'] = False
#             log_session_event(state, "prerequisite_choice", {"choice": "summary"})
#         else:
#             # Ask again if unclear
#             clarification = "I didn't quite catch that. Would you prefer a **quiz** to test your knowledge, or a **summary** to review the prerequisites?"
#             state['messages'].append({
#                 "role": "assistant",
#                 "content": clarification
#             })
#             log_session_message(state, "assistant", clarification, {"phase": "prereq_choice"})
#             state['turn_count'] += 1
#             return state
#     else:
#         # First time - generate introduction
#         print(f"[tutor_intro] Generating introduction for {state['node_title']}")
#         print(f"prerequisites: {has_prerequisites(state)}, {len(state['prerequisite_objectives'])}: {state['prerequisite_objectives']}")

#         # TODO: If this is the first node in the project (no learning objectives completed yet),
#         # consider using state['project_topic'] to provide context about the user's starting state
        
#         # Check if there are prerequisites to handle
#         if has_prerequisites(state):
#             # Has prerequisites - ask about quiz or summary
#             intro_prompt = f"""Introduce the node "{state['node_title']}" in 2 sentences maximum.
# Then ask if they'd like a quiz or summary of prerequisites.

# Learning objectives for this node:
# {format_learning_objectives(state['objectives_to_teach'])}
# Number of prerequisites: {len(state['prerequisite_objectives'])}

# Be concise and conversational."""
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[
#                     {"role": "system", "content": "You are Ada, a concise tutor. Never use praise or encouragement unless requested."},
#                     {"role": "user", "content": intro_prompt}
#                 ],
#                 temperature=0.2
#             )
            
#             message = response.choices[0].message.content
#             state['messages'].append({
#                 "role": "assistant",
#                 "content": message
#             })
#             log_session_message(state, "assistant", message, {"phase": "intro"})
#             state['turn_count'] += 1
#             # FIXME is this correct?
#             state['current_phase'] = 'prereq_choice'
#             return state
            
#         else:
#             # No prerequisites - provide a longer introduction and proceed directly
#             intro_prompt = f"""Introduce the topic "{state['node_title']}" with a 3-4 sentence overview that:
# 1. Explains what this topic covers
# 2. Why it's important or interesting
# 3. What key concepts we'll explore

# Learning objectives we'll cover:
# {format_learning_objectives(state['objectives_to_teach'])}

# End with "Let's begin." to transition to teaching.
# Be conversational but informative. No praise."""
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[
#                     {"role": "system", "content": "You are Ada, a concise tutor. Never use praise or encouragement unless requested."},
#                     {"role": "user", "content": intro_prompt}
#                 ],
#                 temperature=0.2
#             )
            
#             message = response.choices[0].message.content
#             state['messages'].append({
#                 "role": "assistant",
#                 "content": message
#             })
#             log_session_message(state, "assistant", message, {"phase": "intro"})
#             state['turn_count'] += 1
#             state['user_chose_quiz'] = None  # Skip prerequisites entirely
#             state['current_phase'] = 'teaching'
#             state['current_objective_phase'] = 'probe_ask'  # Initialize teaching phase
#             return state


# def prereq_recap_node(state: SessionState) -> SessionState:
#     """Provide summary of prerequisites"""
#     print("[prereq_recap] Summarizing prerequisites")
    
#     client = OpenAI(api_key=load_api_key())
    
#     # Format prerequisites by node
#     prereq_by_node = {}
#     for obj in state['prerequisite_objectives']:
#         if obj.node_id not in prereq_by_node:
#             prereq_by_node[obj.node_id] = []
#         prereq_by_node[obj.node_id].append(obj)
    
#     # Create structured prerequisite text
#     prereq_text = ""
#     for node_id, objectives in prereq_by_node.items():
#         prereq_text += f"\nKey concepts:\n"
#         for obj in objectives:
#             status = "(mastered)" if obj.mastery >= 0.7 else "(needs review)"
#             prereq_text += f"- {obj.description} {status}\n"
    
#     prompt = f"""Provide a concise summary of these prerequisites in ≤200 words.
# Focus on how they connect to what we're about to learn.

# Prerequisites:{prereq_text}

# What we're learning: {state['node_title']}

# Be conversational but efficient. No praise."""
    
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are Ada, a concise tutor providing prerequisite review."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.3
#     )
    
#     summary = response.choices[0].message.content
    
#     # Add transition to main content
#     summary += f"\n\nNow let's dive into {state['node_title']}."
    
#     state['messages'].append({
#         "role": "assistant",
#         "content": summary
#     })
#     log_session_message(state, "assistant", summary, {"phase": "prereq_recap"})
#     state['turn_count'] += 1
    
#     log_session_event(state, "prerequisites_reviewed", {
#         "method": "summary",
#         "prerequisite_count": len(state['prerequisite_objectives'])
#     })
    
#     state['current_phase'] = 'teaching'
#     state['current_objective_phase'] = 'probe_ask'  # Initialize teaching phase
#     return state


# def prereq_quiz_build_node(state: SessionState) -> SessionState:
#     """Generate prerequisite quiz questions"""
#     print("[prereq_quiz_build] Building prerequisite quiz")
    
#     # Generate quiz questions
#     questions = generate_prerequisite_quiz(
#         prerequisites=state['prerequisite_objectives'],
#         current_objectives=state['objectives_to_teach'],
#         max_questions=4
#     )
    
#     state['prereq_quiz_questions'] = questions
    
#     # Log the quiz generation
#     log_session_event(state, "prerequisite_quiz_generated", {
#         "question_count": len(questions),
#         "question_types": [q.type for q in questions]
#     })
    
#     # Add introduction message
#     intro = f"Let's check your understanding of the prerequisites with {len(questions)} quick questions."
#     state['messages'].append({
#         "role": "assistant", 
#         "content": intro
#     })
#     log_session_message(state, "assistant", intro, {"phase": "prereq_quiz_intro"})
#     state['turn_count'] += 1
    
#     print(f"[prereq_quiz_build] Generated {len(questions)} prerequisite questions")
    
#     state['current_phase'] = 'prereq_quiz'
#     return state


# def prereq_quiz_ask_node(state: SessionState) -> SessionState:
#     """Administer prerequisite quiz"""
#     print("[prereq_quiz_ask] Asking prerequisite questions")
    
#     client = OpenAI(api_key=load_api_key())
#     logger = SessionLogger(state['project_id'], state['session_id'])
    
#     # Determine which question we're on
#     answered_count = len(state['prereq_quiz_answers'])
#     total_questions = len(state['prereq_quiz_questions'])
    
#     # Check if we need to process an answer
#     if state['messages'] and state['messages'][-1]['role'] == 'user':
#         # Process previous answer
#         current_question = state['prereq_quiz_questions'][answered_count - 1]
#         user_answer = state['messages'][-1]['content']
        
#         # Create test answer record
#         answer_record = TestAnswer(
#             question_id=answered_count - 1,
#             question=current_question,
#             user_answer=user_answer,
#             timestamp=datetime.now().isoformat()
#         )
#         state['prereq_quiz_answers'].append(answer_record)
        
#         # Evaluate the answer
#         eval_prompt = f"""Evaluate this answer to a prerequisite question.

# Question: {current_question.q}
# Expected: {current_question.answer}
# Student answer: {user_answer}

# Provide brief feedback (1-2 sentences). If incorrect, give the key point they missed.
# No praise. Be direct and helpful."""
        
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are Ada, evaluating prerequisite knowledge."},
#                 {"role": "user", "content": eval_prompt}
#             ],
#             temperature=0.3
#         )
        
#         feedback = response.choices[0].message.content
        
#         # Log the Q&A
#         logger.log_quiz("Prerequisite Quiz", current_question, user_answer, feedback)
        
#         # Add feedback
#         state['messages'].append({
#             "role": "assistant",
#             "content": feedback
#         })
#         log_session_message(state, "assistant", feedback, {"phase": "prereq_feedback"})
#         state['turn_count'] += 1
    
#     # Check if all questions have been answered and feedback given
#     if answered_count >= total_questions:
#         # Check if we've already shown the summary
#         last_msg = state['messages'][-1] if state['messages'] else None
#         if last_msg and last_msg['role'] == 'assistant' and 'Now let\'s explore' not in last_msg['content']:
#             # We just showed feedback for the last question, now show summary
#             correct_count = sum(1 for ans in state['prereq_quiz_answers'] 
#                                if 'correct' in ans.question.answer.lower() or 
#                                ans.user_answer.lower() == ans.question.answer.lower())
            
#             summary = f"\n**Quiz Complete!**\n\nYou got {correct_count} out of {total_questions} correct. "
            
#             if correct_count == total_questions:
#                 summary += "Your prerequisite knowledge is solid."
#             elif correct_count >= total_questions * 0.7:
#                 summary += "You have a good grasp of the prerequisites."
#             else:
#                 summary += "We'll make sure to clarify these concepts as we go."
            
#             summary += f"\n\nNow let's explore {state['node_title']}."
            
#             state['messages'].append({
#                 "role": "assistant",
#                 "content": summary
#             })
#             log_session_message(state, "assistant", summary, {"phase": "prereq_quiz_complete"})
#             state['turn_count'] += 1
            
#             log_session_event(state, "prerequisite_quiz_completed", {
#                 "correct": correct_count,
#                 "total": total_questions,
#                 "score": correct_count / total_questions if total_questions > 0 else 0
#             })
        
#         # Transition to teaching
#         state['current_phase'] = 'teaching'
#         state['current_objective_phase'] = 'probe_ask'  # Initialize teaching phase
#         return state
    
#     # Ask next question
#     next_question = state['prereq_quiz_questions'][answered_count]
    
#     # Format question
#     question_text = f"**Question {answered_count + 1} of {total_questions}:**\n\n"
#     question_text += next_question.format_for_display()
    
#     state['messages'].append({
#         "role": "assistant",
#         "content": question_text
#     })
#     log_session_message(state, "assistant", question_text, {"phase": "prereq_question"})
#     state['turn_count'] += 1
    
#     return state


# def tutor_loop_node(state: SessionState) -> SessionState:
#     """Main teaching loop - teach objectives one by one using explicit state machine"""
#     # First, handle phase transitions if we just received user input
#     state = transition_phase_on_user_input(state)
    
#     current_idx = state['current_objective_index']
#     objectives = state['objectives_to_teach']
#     phase = state.get('current_objective_phase', 'probe_ask')
    
#     # Debug logging
#     print(f"[tutor_loop] Objective {current_idx + 1}/{len(objectives)}, phase={phase}")
    
#     # Check if we've completed all objectives
#     if current_idx >= len(objectives):
#         print(f"[tutor_loop] All objectives completed")
#         state['current_phase'] = 'final_test'
#         return state
    
#     current_obj = objectives[current_idx]
#     print(f"[tutor_loop] Teaching: {current_obj.description}")
    
#     client = OpenAI(api_key=load_api_key())
#     logger = SessionLogger(state['project_id'], state['session_id'])
    
#     # Handle each phase with exactly ONE action
#     if phase == 'probe_ask':
#         # Generate Socratic probe question
#         prompt = f"""We're now focusing on Objective {current_idx + 1} of {len(objectives)}:
# "{current_obj.description}"

# Start with a Socratic question to probe the student's current understanding.
# Be direct and specific. No praise."""
        
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": get_tutor_system_prompt(state)},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7
#         )
        
#         message = response.choices[0].message.content
#         state['messages'].append({"role": "assistant", "content": message})
#         log_session_message(state, "assistant", message, {"phase": "probe_ask", "objective": current_idx + 1})
#         state['turn_count'] += 1
        
#         # Stay in probe_ask phase - waiting for user response
        
#     elif phase == 'probe_respond':
#         # Process user's response to probe
#         if not state['messages'] or state['messages'][-1]['role'] != 'user':
#             # No user message to process, shouldn't happen
#             print(f"[tutor_loop] WARNING: In probe_respond but no user message")
#             state['current_objective_phase'] = 'explain_present'
#             return state
            
#         user_input = state['messages'][-1]['content']
        
#         prompt = f"""The student responded to your probe with: "{user_input}"
        
# Acknowledge their understanding level briefly, then transition to explaining the concept.
# Be concise."""
        
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": get_tutor_system_prompt(state)},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.5
#         )
        
#         message = response.choices[0].message.content
#         state['messages'].append({"role": "assistant", "content": message})
#         log_session_message(state, "assistant", message, {"phase": "probe_respond", "objective": current_idx + 1})
#         state['turn_count'] += 1
        
#         # Transition to next phase
#         state['current_objective_phase'] = 'explain_present'
        
#     elif phase == 'explain_present':
#         # Present the explanation
#         prompt = f"""Now explain the concept: "{current_obj.description}"

# Provide a clear EXPLANATION (not another question) about this concept.
# - Maximum 200 words
# - Focus on the key ideas
# - Use examples if helpful
# - Be conversational but clear
# No praise."""
        
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": get_tutor_system_prompt(state)},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.5
#         )
        
#         message = response.choices[0].message.content
#         state['messages'].append({"role": "assistant", "content": message})
#         log_session_message(state, "assistant", message, {"phase": "explain_present", "objective": current_idx + 1})
#         state['turn_count'] += 1
        
#         # Stay in explain_present phase - waiting for user response
        
#     elif phase == 'explain_respond':
#         # Handle user's response to explanation
#         if not state['messages'] or state['messages'][-1]['role'] != 'user':
#             # No user message, skip to quiz
#             print(f"[tutor_loop] No user response to explanation, moving to quiz")
#             state['current_objective_phase'] = 'quiz_ask'
#             return state
            
#         user_input = state['messages'][-1]['content']
        
#         prompt = f"""The student said: "{user_input}" after your explanation.

# Respond briefly to any questions or comments, then let them know you'll check their understanding with a quick question.
# Be concise."""
        
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": get_tutor_system_prompt(state)},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.5
#         )
        
#         message = response.choices[0].message.content
#         state['messages'].append({"role": "assistant", "content": message})
#         log_session_message(state, "assistant", message, {"phase": "explain_respond", "objective": current_idx + 1})
#         state['turn_count'] += 1
        
#         # Transition to quiz
#         state['current_objective_phase'] = 'quiz_ask'
        
#     elif phase == 'quiz_ask':
#         # Generate and ask micro-quiz
#         quiz_q = generate_micro_quiz(current_obj, state.get('micro_quiz_history', []))
        
#         # Store the quiz question
#         quiz_record = {
#             "objective_id": current_obj.id,
#             "question": quiz_q.dict(),
#             "timestamp": datetime.now().isoformat()
#         }
#         state['micro_quiz_history'].append(quiz_record)
        
#         # Format and ask the question
#         quiz_text = "\n**Quick check:**\n" + quiz_q.format_for_display()
        
#         state['messages'].append({"role": "assistant", "content": quiz_text})
#         log_session_message(state, "assistant", quiz_text, {"phase": "quiz_ask", "objective": current_idx + 1})
#         state['turn_count'] += 1
        
#         # Stay in quiz_ask phase - waiting for user response
        
#     elif phase == 'quiz_evaluate':
#         # Evaluate quiz answer
#         if not state['messages'] or state['messages'][-1]['role'] != 'user':
#             print(f"[tutor_loop] WARNING: In quiz_evaluate but no user answer")
#             # Move to next objective anyway
#             state['current_objective_index'] += 1
#             state['current_objective_phase'] = 'probe_ask'
#             return state
            
#         user_answer = state['messages'][-1]['content']
#         quiz_q = QuizQuestion(**state['micro_quiz_history'][-1]['question'])
        
#         # Log the quiz Q&A
#         logger.log_quiz("Micro-Quiz", quiz_q, user_answer)
        
#         # Evaluate the answer
#         eval_prompt = f"""Evaluate this micro-quiz answer:

# Question: {quiz_q.q}
# Expected: {quiz_q.answer}
# Student answer: {user_answer}

# Provide brief feedback (1-2 sentences).
# If correct, acknowledge and move on.
# If incorrect/incomplete, clarify the key point.
# No praise."""
        
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are Ada, evaluating student understanding."},
#                 {"role": "user", "content": eval_prompt}
#             ],
#             temperature=0.3
#         )
        
#         feedback = response.choices[0].message.content
        
#         # Mark objective as completed
#         state['completed_objectives'].add(current_obj.id)
        
#         # Add transition to next objective or completion
#         if current_idx + 1 < len(objectives):
#             feedback += f"\n\nLet's move on to the next objective."
#         else:
#             feedback += f"\n\nWe've covered all {len(objectives)} objectives for this topic."
        
#         state['messages'].append({"role": "assistant", "content": feedback})
#         log_session_message(state, "assistant", feedback, {"phase": "quiz_evaluate", "objective": current_idx + 1})
#         state['turn_count'] += 1
        
#         # Log completion
#         log_session_event(state, "objective_completed", {
#             "objective_id": current_obj.id,
#             "objective_number": current_idx + 1,
#             "description": current_obj.description
#         })
        
#         # Move to next objective
#         state['current_objective_index'] += 1
#         state['current_objective_phase'] = 'probe_ask'
        
#     else:
#         # Unknown phase - log error and try to recover
#         print(f"[tutor_loop] ERROR: Unknown phase '{phase}', resetting to probe_ask")
#         state['current_objective_phase'] = 'probe_ask'
    
#     state['current_phase'] = 'teaching'
#     return state


# def final_test_build_node(state: SessionState) -> SessionState:
#     """Build comprehensive final test"""
#     objectives_to_test = get_objectives_for_testing(state)
#     print(f"[final_test_build] Generating final test for {len(objectives_to_test)} objectives")
    
#     if not objectives_to_test:
#         print("[final_test_build] No objectives to test, skipping to wrap-up")
#         state['current_phase'] = 'wrap_up'
#         return state
    
#     # Generate final test questions
#     # Include prerequisites if they were reviewed
#     reviewed_prereqs = state['prerequisite_objectives'] if state.get('user_chose_quiz') else None
#     final_questions = generate_final_test(objectives_to_test, reviewed_prereqs)
#     state['final_test_questions'] = final_questions
    
#     # Log the test generation
#     log_session_event(state, "final_test_built", {
#         "num_questions": len(final_questions),
#         "objectives_tested": [obj.id for obj in objectives_to_test],
#         "question_types": [q.type for q in final_questions]
#     })
    
#     state['current_phase'] = 'final_test_ask'
#     return state


# def final_test_ask_node(state: SessionState) -> SessionState:
#     """Administer final test"""
#     print(f"[final_test_ask] Administering {len(state['final_test_questions'])} questions")
    
#     client = OpenAI(api_key=load_api_key())
#     logger = SessionLogger(state['project_id'], state['session_id'])
    
#     # Build the test message
#     test_intro = "Now let's assess what you've learned with a final test. Please answer each question to the best of your ability.\n\n"
    
#     questions_text = ""
#     for i, q in enumerate(state['final_test_questions'], 1):
#         questions_text += f"**Question {i}:**\n{q.format_for_display()}\n\n"
    
#     full_message = test_intro + questions_text.strip()
    
#     # Send test to user
#     state['messages'].append({"role": "assistant", "content": full_message})
#     log_session_message(state, "assistant", full_message, {"phase": "final_test"})
#     state['turn_count'] += 1
    
#     # Log test start
#     log_session_event(state, "final_test_started", {
#         "num_questions": len(state['final_test_questions'])
#     })
    
#     state['current_phase'] = 'grade_prep'
#     return state


# def grade_prep_node(state: SessionState) -> SessionState:
#     """Prepare data for grading"""
#     print("[grade_prep] Preparing grading data")
    
#     # Get the user's answer (should be the last message)
#     if not state['messages'] or state['messages'][-1]['role'] != 'user':
#         print("[grade_prep] No user answer found")
#         state['current_phase'] = 'wrap_up'
#         return state
    
#     user_answers_text = state['messages'][-1]['content']
    
#     # Use LLM to parse answers intelligently
#     parsed_answers = parse_final_answers(state['final_test_questions'], user_answers_text)
    
#     # Create TestAnswer objects
#     answers = []
#     for i, (q, user_answer) in enumerate(zip(state['final_test_questions'], parsed_answers)):
#         test_answer = TestAnswer(
#             question_id=i,
#             question=q,
#             user_answer=user_answer,
#             timestamp=datetime.now().isoformat()
#         )
#         answers.append(test_answer)
    
#     state['final_test_answers'] = answers
    
#     # Log answer collection
#     log_session_event(state, "test_answers_collected", {
#         "num_answers": len(answers)
#     })
    
#     state['current_phase'] = 'grader_call'
#     return state


# def grader_call_node(state: SessionState) -> SessionState:
#     """Call grader with expensive model and fallback"""
#     print(f"[grader_call] Grading {len(state['final_test_answers'])} responses")
    
#     client = OpenAI(api_key=load_api_key())
#     logger = SessionLogger(state['project_id'], state['session_id'])
    
#     # Grade each answer
#     objective_scores = {}
#     grading_details = []
    
#     for answer in state['final_test_answers']:
#         q = answer.question
        
#         # Build grading prompt
#         grading_prompt = f"""Grade this test answer on a scale of 0.0 to 1.0.

# Question: {q.q}
# Question Type: {q.type}
# Expected Answer: {q.answer}
# Student Answer: {answer.user_answer}

# Scoring Guidelines:
# - 1.0: Fully correct and complete
# - 0.8-0.9: Mostly correct with minor issues
# - 0.6-0.7: Partially correct
# - 0.4-0.5: Some understanding shown
# - 0.2-0.3: Minimal understanding
# - 0.0: Incorrect or no attempt

# Provide your response in this exact format:
# SCORE: [number between 0.0 and 1.0]
# REASONING: [brief explanation in 1-2 sentences]"""
        
#         # Try with expensive model first
#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4o",  # Expensive model
#                 messages=[
#                     {"role": "system", "content": "You are an expert grader. Be fair but rigorous."},
#                     {"role": "user", "content": grading_prompt}
#                 ],
#                 temperature=0.2
#             )
#             grading_text = response.choices[0].message.content
#             model_used = "gpt-4o"
#         except Exception as e:
#             print(f"[grader_call] Expensive model failed: {e}, falling back to gpt-4o-mini")
#             # Fallback to cheaper model
#             try:
#                 response = client.chat.completions.create(
#                     model="gpt-4o-mini",
#                     messages=[
#                         {"role": "system", "content": "You are an expert grader. Be fair but rigorous."},
#                         {"role": "user", "content": grading_prompt}
#                     ],
#                     temperature=0.2
#                 )
#                 grading_text = response.choices[0].message.content
#                 model_used = "gpt-4o-mini"
#             except Exception as e2:
#                 print(f"[grader_call] Fallback also failed: {e2}")
#                 grading_text = "SCORE: 0.5\nREASONING: Unable to grade automatically."
#                 model_used = "fallback"
        
#         # Parse score
#         score = 0.5  # Default
#         reasoning = "No reasoning provided"
        
#         if "SCORE:" in grading_text:
#             try:
#                 score_line = [line for line in grading_text.split('\n') if "SCORE:" in line][0]
#                 score = float(score_line.split("SCORE:")[1].strip())
#                 score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
#             except:
#                 pass
        
#         if "REASONING:" in grading_text:
#             try:
#                 reasoning_line = [line for line in grading_text.split('\n') if "REASONING:" in line][0]
#                 reasoning = reasoning_line.split("REASONING:")[1].strip()
#             except:
#                 pass
        
#         # Update scores for each objective this question tests
#         for obj_id in q.objective_ids:
#             if obj_id not in objective_scores:
#                 objective_scores[obj_id] = []
#             objective_scores[obj_id].append(score)
        
#         grading_details.append({
#             "question_id": answer.question_id,
#             "score": score,
#             "reasoning": reasoning,
#             "model_used": model_used
#         })
    
#     # Average scores per objective
#     final_objective_scores = {}
#     for obj_id, scores in objective_scores.items():
#         final_objective_scores[obj_id] = sum(scores) / len(scores)
    
#     state['objective_scores'] = final_objective_scores
    
#     # Log grading results
#     log_session_event(state, "grading_completed", {
#         "objective_scores": final_objective_scores,
#         "grading_details": grading_details,
#         "overall_score": calculate_final_score(state)
#     })
    
#     # Update mastery in database
#     update_mastery(state['node_id'], final_objective_scores)
    
#     # Add transition message before showing detailed results
#     transition_msg = "I've finished grading your test. Let me show you how you did..."
#     state['messages'].append({
#         "role": "assistant",
#         "content": transition_msg
#     })
#     log_session_message(state, "assistant", transition_msg, {"phase": "grading_complete"})
#     state['turn_count'] += 1
    
#     state['current_phase'] = 'wrap_up'
#     return state


# def tutor_wrap_up_node(state: SessionState) -> SessionState:
#     """Provide closing message with feedback"""
#     print("[tutor_wrap_up] Wrapping up session")
    
#     client = OpenAI(api_key=load_api_key())
#     logger = SessionLogger(state['project_id'], state['session_id'])
    
#     # Calculate overall performance
#     overall_score = calculate_final_score(state)
#     objectives_tested = get_objectives_for_testing(state)
    
#     # Build performance summary
#     performance_summary = f"Overall Score: {overall_score:.1%}\n\n"
    
#     if state['objective_scores']:
#         performance_summary += "Performance by Objective:\n"
#         for obj in objectives_tested:
#             if obj.id in state['objective_scores']:
#                 score = state['objective_scores'][obj.id]
#                 emoji = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
#                 performance_summary += f"{emoji} {obj.description}: {score:.1%}\n"
    
#     # Generate personalized feedback
#     feedback_prompt = f"""The student just completed a learning session on "{state['node_title']}".

# {performance_summary}

# Provide a brief wrap-up message that:
# 1. Acknowledges their effort (no excessive praise)
# 2. Highlights one strength and one area for improvement
# 3. Suggests next steps or topics to explore

# Keep it concise (≤150 words). Be encouraging but honest."""
    
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are Ada, a helpful tutor providing session feedback."},
#             {"role": "user", "content": feedback_prompt}
#         ],
#         temperature=0.7
#     )
    
#     wrap_up_message = response.choices[0].message.content
    
#     # Add performance summary to the message
#     full_message = f"## Session Complete!\n\n{performance_summary}\n{wrap_up_message}"
    
#     state['messages'].append({"role": "assistant", "content": full_message})
#     log_session_message(state, "assistant", full_message, {"phase": "wrap_up"})
#     state['turn_count'] += 1
    
#     # Mark session as completed
#     state['current_phase'] = 'completed'
#     state['session_end'] = datetime.now().isoformat()
    
#     # Complete session in database
#     complete_session(state['session_id'], overall_score)
    
#     # Log session completion
#     log_session_event(state, "session_completed", {
#         "overall_score": overall_score,
#         "duration_minutes": calculate_session_duration(state),
#         "objectives_taught": len([obj for obj in objectives_tested if obj.id in state['completed_objectives']]),
#         "objectives_mastered": len([obj_id for obj_id, score in state['objective_scores'].items() if score >= 0.7])
#     })
    
#     logger.finalize()
    
#     return state


# # Conditional edge functions

# def should_do_prerequisites(state: SessionState) -> str:
#     """Determine if we should show prereq quiz or summary"""
#     if not has_prerequisites(state):
#         # No prerequisites, skip to teaching
#         return "skip"
    
#     if state.get('user_chose_quiz') is True:
#         return "quiz"
#     elif state.get('user_chose_quiz') is False:
#         return "summary"
#     else:
#         # Still waiting for user choice
#         return "waiting"


# def should_continue_teaching(state: SessionState) -> str:
#     """Determine if teaching should continue or move to final test"""
#     # First check if user wants to end early
#     if state.get('force_end_session', False):
#         return "finish"
    
#     # Check if all objectives are completed
#     current_idx = state.get('current_objective_index', 0)
#     total_objectives = len(state.get('objectives_to_teach', []))
#     if current_idx >= total_objectives:
#         return "finish"
    
#     # Check current phase to determine if we should wait for user input
#     phase = state.get('current_objective_phase', 'probe_ask')
    
#     # Phases that wait for user input
#     if is_waiting_phase(phase):
#         # Check if we just sent a message (need to wait for user)
#         if state.get('messages') and state['messages'][-1]['role'] == 'assistant':
#             return "wait_for_input"
    
#     # Phases that should transition after user input
#     response_phases = ['probe_respond', 'explain_respond', 'quiz_evaluate']
#     if phase in response_phases:
#         # Check if we have a user message to process
#         if state.get('messages') and state['messages'][-1]['role'] == 'user':
#             # Continue to process the user input
#             return "continue"
#         else:
#             # No user input but we're in a response phase
#             # This shouldn't happen, but transition anyway
#             print(f"[should_continue_teaching] WARNING: In {phase} but no user message")
#             # Update phase to move forward
#             state['current_objective_phase'] = get_next_teaching_phase(phase)
#             return "continue"
    
#     # Default: continue processing
#     return "continue"


# # Graph creation

# def create_session_graph():
#     """Create and compile the v0.4 session graph"""
#     print("Creating v0.4 session graph...")
    
#     # Create state graph
#     workflow = StateGraph(SessionState)
    
#     # Add all nodes
#     workflow.add_node("load_context", load_context_node)
#     workflow.add_node("tutor_intro", tutor_intro_node) 
#     workflow.add_node("prereq_recap", prereq_recap_node)
#     workflow.add_node("prereq_quiz_build", prereq_quiz_build_node)
#     workflow.add_node("prereq_quiz_ask", prereq_quiz_ask_node)
#     workflow.add_node("tutor_loop", tutor_loop_node)
#     workflow.add_node("final_test_build", final_test_build_node)
#     workflow.add_node("final_test_ask", final_test_ask_node)
#     workflow.add_node("grade_prep", grade_prep_node)
#     workflow.add_node("grader_call", grader_call_node)
#     workflow.add_node("tutor_wrap_up", tutor_wrap_up_node)
    
#     # Set entry point
#     workflow.set_entry_point("load_context")
    
#     # Add fixed edges
#     workflow.add_edge("load_context", "tutor_intro")
#     workflow.add_edge("prereq_recap", "tutor_loop")
#     workflow.add_edge("prereq_quiz_build", "prereq_quiz_ask")
#     workflow.add_edge("prereq_quiz_ask", "tutor_loop")
#     workflow.add_edge("final_test_build", "final_test_ask")
#     workflow.add_edge("final_test_ask", "grade_prep")
#     workflow.add_edge("grade_prep", "grader_call")
#     workflow.add_edge("grader_call", "tutor_wrap_up")
#     workflow.add_edge("tutor_wrap_up", END)
    
#     # Add conditional edges for prerequisites
#     workflow.add_conditional_edges(
#         "tutor_intro",
#         should_do_prerequisites,
#         {
#             "quiz": "prereq_quiz_build",
#             "summary": "prereq_recap",
#             "skip": "tutor_loop",
#             "waiting": "tutor_intro"  # Loop back if still waiting
#         }
#     )
    
#     # Add conditional edge for teaching loop
#     workflow.add_conditional_edges(
#         "tutor_loop",
#         should_continue_teaching,
#         {
#             "continue": "tutor_loop",
#             "finish": "final_test_build",
#             "wait_for_input": END  # End the graph to wait for user input
#         }
#     )
    
#     # Compile the graph
#     compiled = workflow.compile()
#     print("Graph compiled successfully!")
    
#     return compiled


# # For testing
# if __name__ == "__main__":
#     from datetime import datetime
    
#     # Test graph compilation
#     graph = create_session_graph()
#     print("\nGraph nodes:", list(graph.nodes.keys()))
    
#     # Test with minimal state
#     test_state = create_initial_state(
#         session_id="test-graph-compile",
#         project_id="test-project",
#         node_id="test-node"
#     )
    
#     # Add minimal data for testing
#     test_state['node_title'] = "Test Node"
#     test_state['objectives_to_teach'] = [
#         Objective(id="test1", description="Test objective", mastery=0.3)
#     ]
    
#     print("\nTesting graph execution (first few steps)...")
#     step_count = 0
#     max_steps = 5
    
#     try:
#         for event in graph.stream(test_state):
#             step_count += 1
#             print(f"\nStep {step_count}: {list(event.keys())}")
            
#             if step_count >= max_steps:
#                 print(f"\nStopping after {max_steps} steps (graph working correctly)")
#                 break
                
#     except Exception as e:
#         print(f"\nError during graph execution: {e}")
#         import traceback
#         traceback.print_exc() 