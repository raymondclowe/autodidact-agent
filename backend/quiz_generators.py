"""
Quiz generation functionality for Autodidact v0.4
Handles generation of prerequisite quizzes, micro-quizzes, and final tests
"""

from typing import List, Dict, Optional
import json
from openai import OpenAI

from backend.session_state import Objective, QuizQuestion
from utils.config import load_api_key

# backend/quiz_generators.py
from typing import List
from langchain_openai import ChatOpenAI
from utils.config import load_api_key
from backend.session_state import Objective

_Q_PROMPT = """
You are an assessment author.

Write {n} stand-alone quiz questions that test the learner’s knowledge
of the following learning objectives:

{obj_list}

Rules
-----
1. Vary the type:
   • multiple-choice (label options a, b, c … on new lines)
   • short-answer  → append "(answer in short)" at the end
   • paraphrase    → ask for a paraphrase
2. One question can reference one or more objectives, but cover *all*
   objectives at least once in total.
3. Do **not** show the answers.
4. Output format:
   1. <question one>
   2. <question two>
   ...
"""

def generate_final_test(
    llm: ChatOpenAI,
    objectives: List[Objective],
    max_questions: int = 6,
) -> List[str]:
    """
    Ask the LLM for up to `max_questions` quiz questions and
    return them as a list of plain strings.
    """
    obj_list = "\n".join(f"- {o.description}" for o in objectives)
    prompt = _Q_PROMPT.format(n=max_questions, obj_list=obj_list)

    llm_response = llm(prompt).content.strip()

    # Split on leading numbers "1. "  "2. " …
    questions: List[str] = []
    for line in llm_response.splitlines():
        if line.lstrip().startswith(tuple(str(i) + "." for i in range(1, max_questions + 2))):
            # remove the numeric prefix
            q = line.split(".", 1)[1].strip()
            if q:
                questions.append(q)

    # Fallback: if parsing failed, keep entire response as one question
    if not questions:
        questions = [llm_response]

    # Trim to max_questions
    return questions[:max_questions]



# def generate_prerequisite_quiz(
#     prerequisites: List[Objective],
#     current_objectives: List[Objective],
#     max_questions: int = 4
# ) -> List[QuizQuestion]:
#     """
#     Generate up to 4 quiz questions covering critical prerequisites
#     """
#     if not prerequisites:
#         return []
    
#     client = OpenAI(api_key=load_api_key())
    
#     # Format prerequisites for the prompt
#     prereq_text = "\n".join([
#         f"- {obj.description} (current mastery: {obj.mastery:.0%})"
#         for obj in prerequisites
#     ])
    
#     # Format current objectives to understand what's essential
#     current_text = "\n".join([
#         f"- {obj.description}"
#         for obj in current_objectives
#     ])
    
#     prompt = f"""You are creating a prerequisite knowledge check.

# Prerequisites the student should know:
# {prereq_text}

# What they're about to learn:
# {current_text}

# Generate {max_questions} questions that verify the most essential prerequisite knowledge needed for the upcoming objectives.
# Focus on prerequisites with lower mastery scores.
# Prefer MCQ format when possible, use short answer only when MCQ doesn't make sense.

# Return ONLY valid JSON in this format:
# {{
#   "questions": [
#     {{
#       "q": "Question text",
#       "type": "mcq",  // MUST be exactly one of: mcq, short, free, paraphrase
#       "choices": ["A", "B", "C", "D"],
#       "answer": "B",
#       "objective_ids": ["prereq_obj_id"]
#     }}
#   ]
# }}

# Important: The "type" field must be EXACTLY one of these values: mcq, short, free, paraphrase
# """
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a quiz generator. Return only valid JSON."},
#                 {"role": "user", "content": prompt}
#             ],
#             response_format={"type": "json_object"},
#             temperature=0.7
#         )
        
#         data = json.loads(response.choices[0].message.content)
        
#         # Convert to QuizQuestion objects
#         questions = []
#         for q_data in data.get("questions", [])[:max_questions]:
#             # Map question to actual prerequisite objectives
#             objective_ids = []
#             for obj in prerequisites:
#                 # Simple matching - could be improved with better NLP
#                 if any(word.lower() in q_data["q"].lower() 
#                       for word in obj.description.split()[:3]):
#                     objective_ids.append(obj.id)
            
#             # If no match found, use first prerequisite
#             if not objective_ids and prerequisites:
#                 objective_ids = [prerequisites[0].id]
            
#             question = QuizQuestion(
#                 q=q_data["q"],
#                 type=q_data.get("type", "mcq"),
#                 choices=q_data.get("choices"),
#                 answer=q_data["answer"],
#                 objective_ids=objective_ids
#             )
#             questions.append(question)
        
#         return questions
        
#     except Exception as e:
#         print(f"[generate_prerequisite_quiz] Error: {str(e)}")
#         # Return a simple fallback question
#         if prerequisites:
#             return [QuizQuestion(
#                 q=f"Can you explain what you know about: {prerequisites[0].description}?",
#                 type="short",
#                 answer="Student should demonstrate understanding",
#                 objective_ids=[prerequisites[0].id]
#             )]
#         return []


# def generate_micro_quiz(
#     objective: Objective,
#     previous_responses: Optional[List[Dict]] = None
# ) -> QuizQuestion:
#     """
#     Generate a single formative quiz question for an objective
#     """
#     client = OpenAI(api_key=load_api_key())
    
#     context = ""
#     if previous_responses:
#         # Include context about what the student has already shown
#         context = "\nPrevious responses show the student understands: " + \
#                  ", ".join([r.get("concept", "") for r in previous_responses[-2:]])
    
#     prompt = f"""Generate ONE formative assessment question for this learning objective:
# "{objective.description}"
# {context}

# The question should:
# - Check understanding, not just memorization
# - Be answerable in 1-2 sentences or as MCQ
# - Focus on application or analysis when possible

# Return ONLY valid JSON:
# {{
#   "q": "Question text",
#   "type": "mcq or short",
#   "choices": ["A", "B", "C", "D"] (only if MCQ),
#   "answer": "correct answer or key points"
# }}
# """
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a quiz generator. Return only valid JSON."},
#                 {"role": "user", "content": prompt}
#             ],
#             response_format={"type": "json_object"},
#             temperature=0.8
#         )
        
#         data = json.loads(response.choices[0].message.content)
        
#         return QuizQuestion(
#             q=data["q"],
#             type=data.get("type", "short"),
#             choices=data.get("choices"),
#             answer=data["answer"],
#             objective_ids=[objective.id]
#         )
        
#     except Exception as e:
#         print(f"[generate_micro_quiz] Error: {str(e)}")
#         # Fallback question
#         return QuizQuestion(
#             q=f"How would you apply the concept: {objective.description}?",
#             type="short",
#             answer="Student should demonstrate application",
#             objective_ids=[objective.id]
#         )


# def generate_final_test(
#     objectives: List[Objective],
#     reviewed_prerequisites: Optional[List[Objective]] = None,
#     question_distribution: Dict[str, int] = None
# ) -> List[QuizQuestion]:
#     """
#     Generate final test with default 3 MCQ + 2 short + 1 paraphrase
#     Can include reviewed prerequisites in the test
#     """
#     if question_distribution is None:
#         question_distribution = {
#             "mcq": 3,
#             "short": 2,
#             "paraphrase": 1
#         }
    
#     client = OpenAI(api_key=load_api_key())
    
#     # Format objectives
#     obj_text = "\n".join([
#         f"{i+1}. {obj.description}"
#         for i, obj in enumerate(objectives)
#     ])
    
#     # Include prerequisites if reviewed
#     prereq_text = ""
#     if reviewed_prerequisites:
#         prereq_text = "\n\nAlso reviewed prerequisites:\n" + "\n".join([
#             f"- {obj.description}"
#             for obj in reviewed_prerequisites
#         ])
    
#     # Calculate total questions
#     total_questions = sum(question_distribution.values())
    
#     prompt = f"""Create a comprehensive final test for these learning objectives:
# {obj_text}{prereq_text}

# Generate exactly:
# - {question_distribution.get('mcq', 0)} multiple choice questions
# - {question_distribution.get('short', 0)} short answer questions  
# - {question_distribution.get('paraphrase', 0)} paraphrase/explanation questions

# Distribute questions to cover all objectives proportionally.
# Questions should test understanding, application, and synthesis.

# Return ONLY valid JSON:
# {{
#   "questions": [
#     {{
#       "q": "Question text",
#       "type": "mcq/short/paraphrase",
#       "choices": ["A", "B", "C", "D"] (only for MCQ),
#       "answer": "correct answer or expected key points",
#       "objective_ids": ["obj_id1", "obj_id2"] (can test multiple)
#     }}
#   ]
# }}
# """
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a comprehensive test generator. Return only valid JSON."},
#                 {"role": "user", "content": prompt}
#             ],
#             response_format={"type": "json_object"},
#             temperature=0.7
#         )
        
#         data = json.loads(response.choices[0].message.content)
        
#         # Convert to QuizQuestion objects
#         questions = []
#         all_objectives = objectives + (reviewed_prerequisites or [])
        
#         for q_data in data.get("questions", []):
#             # Map to actual objective IDs
#             objective_ids = []
            
#             # Try to match based on question content
#             for obj in all_objectives:
#                 if any(word.lower() in q_data["q"].lower() 
#                       for word in obj.description.split()[:4]):
#                     objective_ids.append(obj.id)
            
#             # If no match, distribute evenly across objectives
#             if not objective_ids and objectives:
#                 # Assign to least-tested objective
#                 obj_question_count = {obj.id: 0 for obj in objectives}
#                 for q in questions:
#                     for oid in q.objective_ids:
#                         if oid in obj_question_count:
#                             obj_question_count[oid] += 1
                
#                 least_tested = min(obj_question_count.items(), key=lambda x: x[1])[0]
#                 objective_ids = [least_tested]
            
#             question = QuizQuestion(
#                 q=q_data["q"],
#                 type=q_data["type"],
#                 choices=q_data.get("choices"),
#                 answer=q_data["answer"],
#                 objective_ids=objective_ids
#             )
#             questions.append(question)
        
#         return questions[:total_questions]  # Ensure we don't exceed requested count
        
#     except Exception as e:
#         print(f"[generate_final_test] Error: {str(e)}")
#         # Generate simple fallback questions
#         questions = []
        
#         # One question per objective up to total needed
#         for i, obj in enumerate(objectives[:total_questions]):
#             q_type = "short" if i < 2 else "mcq"
#             question = QuizQuestion(
#                 q=f"Explain your understanding of: {obj.description}",
#                 type=q_type,
#                 answer="Student should demonstrate understanding",
#                 objective_ids=[obj.id]
#             )
#             questions.append(question)
        
#         return questions 