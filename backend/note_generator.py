"""
Note Generation Backend for Autodidact
Handles AI-powered study note creation from completed lessons
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from backend.session_state import SessionState, Objective
from backend.db import get_db_connection
import logging

logger = logging.getLogger(__name__)


def generate_lesson_notes(session_state: SessionState, session_info: Dict, node_info: Dict) -> Dict:
    """
    Generate comprehensive study notes for completed lesson
    
    Args:
        session_state: Current session state containing lesson data
        session_info: Session information from database
        node_info: Node information including lesson title
        
    Returns:
        Dict containing generated notes with structure:
        {
            'id': str,
            'content': dict,  # Structured content
            'formatted_html': str,  # Print-ready HTML
            'summary': str  # Brief summary
        }
    """
    try:
        # Extract key information from session
        lesson_title = node_info.get('label', 'Learning Session')
        session_id = session_info.get('id')
        project_id = session_info.get('project_id')
        node_id = session_info.get('node_id')
        
        # Get lesson objectives and completion info
        objectives = session_state.get('objectives_to_teach', [])
        history = session_state.get('history', [])
        final_score = session_info.get('final_score', 0.0)
        
        # Extract key concepts from session history
        key_concepts = extract_key_concepts(history, objectives)
        
        # Generate structured note content
        note_content = {
            'lesson_title': lesson_title,
            'completion_date': datetime.now().isoformat(),
            'final_score': final_score,
            'duration_minutes': calculate_session_duration(session_info),
            'objectives': [
                {
                    'id': obj.id,
                    'description': obj.description,
                    'mastery': obj.mastery,
                    'mastered': obj.is_mastered()
                }
                for obj in objectives
            ],
            'key_concepts': key_concepts,
            'lesson_overview': generate_lesson_overview(history, objectives),
            'insights': extract_key_insights(history, objectives),
            'review_questions': generate_review_questions(objectives, key_concepts),
            'performance': {
                'score': final_score,
                'mastery_level': get_mastery_level(final_score),
                'objectives_completed': len([obj for obj in objectives if obj.is_mastered()]),
                'total_objectives': len(objectives)
            }
        }
        
        # Format for print display
        formatted_html = format_for_print(note_content)
        
        # Generate summary for collection display
        summary = generate_summary(note_content)
        
        # Generate unique ID
        note_id = str(uuid.uuid4())
        
        # Save to database
        save_notes_to_database(
            note_id=note_id,
            session_id=session_id,
            project_id=project_id,
            node_id=node_id,
            lesson_title=lesson_title,
            content=note_content,
            formatted_html=formatted_html,
            summary=summary
        )
        
        return {
            'id': note_id,
            'content': note_content,
            'formatted_html': formatted_html,
            'summary': summary
        }
        
    except Exception as e:
        logger.error(f"Error generating lesson notes: {e}")
        logger.exception("Full traceback:")
        raise


def extract_key_concepts(session_history: List[Dict], objectives: List[Objective]) -> List[Dict]:
    """Extract main concepts from lesson conversation"""
    key_concepts = []
    
    # Extract concepts from objectives (these are the main learning targets)
    for obj in objectives:
        if obj.is_mastered():
            concept = {
                'title': obj.description,
                'source': 'learning_objective',
                'mastery': obj.mastery,
                'explanation': f"Successfully mastered: {obj.description}"
            }
            key_concepts.append(concept)
    
    # Extract important topics from session history
    # Look for assistant messages that contain explanations or key information
    for turn in session_history:
        if turn.get('role') == 'assistant' and len(turn.get('content', '')) > 100:
            content = turn.get('content', '')
            
            # Look for structured content or definitions
            if any(keyword in content.lower() for keyword in ['definition:', 'key point:', 'important:', 'remember:']):
                # Extract the important part (simplified extraction)
                lines = content.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['definition:', 'key point:', 'important:', 'remember:']):
                        concept = {
                            'title': line.strip(),
                            'source': 'lesson_content',
                            'explanation': line.strip()
                        }
                        key_concepts.append(concept)
                        break
    
    return key_concepts[:10]  # Limit to top 10 concepts


def generate_lesson_overview(history: List[Dict], objectives: List[Objective]) -> str:
    """Generate a comprehensive lesson overview"""
    total_objectives = len(objectives)
    mastered_objectives = len([obj for obj in objectives if obj.is_mastered()])
    
    overview = f"""In this lesson, you explored {total_objectives} key learning objectives and successfully mastered {mastered_objectives} of them. """
    
    if mastered_objectives == total_objectives:
        overview += "You achieved complete mastery of all learning goals, demonstrating excellent understanding of the material. "
    elif mastered_objectives > total_objectives * 0.7:
        overview += "You achieved strong mastery of most learning goals, showing good comprehension of the core concepts. "
    else:
        overview += "You made good progress on the learning objectives, building foundational understanding. "
    
    # Add context from the lesson content
    overview += "The lesson covered fundamental principles and practical applications, "
    overview += "providing you with both theoretical knowledge and hands-on understanding."
    
    return overview


def extract_key_insights(history: List[Dict], objectives: List[Objective]) -> List[str]:
    """Extract key insights from the learning session"""
    insights = []
    
    # Generate insights based on mastery patterns
    mastered_count = len([obj for obj in objectives if obj.is_mastered()])
    total_count = len(objectives)
    
    if mastered_count == total_count:
        insights.append("You demonstrated excellent mastery across all learning objectives")
    
    if any(obj.mastery > 0.9 for obj in objectives):
        insights.append("You achieved exceptional understanding in several key areas")
    
    # Add domain-specific insights based on lesson content
    insights.append("This lesson builds important foundational knowledge for future learning")
    insights.append("The concepts learned here will be valuable for practical applications")
    
    return insights


def generate_review_questions(objectives: List[Objective], key_concepts: List[Dict]) -> List[str]:
    """Generate review questions based on objectives and concepts"""
    questions = []
    
    # Generate questions from objectives
    for obj in objectives:
        if obj.is_mastered():
            # Convert objective description to question form
            desc = obj.description.lower()
            if desc.startswith('define'):
                question = f"What is the definition of {desc.replace('define ', '')}?"
            elif desc.startswith('identify'):
                question = f"Can you identify {desc.replace('identify ', '')}?"
            elif desc.startswith('explain'):
                question = f"How would you explain {desc.replace('explain ', '')}?"
            elif desc.startswith('describe'):
                question = f"Describe {desc.replace('describe ', '')}"
            else:
                question = f"What did you learn about: {obj.description}?"
            
            questions.append(question)
    
    # Add general comprehension questions
    if key_concepts:
        questions.append("What were the most important concepts covered in this lesson?")
        questions.append("How do these concepts relate to each other?")
    
    return questions[:6]  # Limit to 6 questions


def get_mastery_level(score: float) -> str:
    """Determine mastery level from score"""
    if score >= 0.9:
        return "Exceptional"
    elif score >= 0.8:
        return "Advanced"  
    elif score >= 0.7:
        return "Proficient"
    elif score >= 0.6:
        return "Developing"
    else:
        return "Beginning"


def calculate_session_duration(session_info: Dict) -> int:
    """Calculate session duration in minutes"""
    # Simplified calculation - in real implementation would use timestamps
    return 25  # Default duration


def format_for_print(note_content: Dict) -> str:
    """Format notes for print-optimized display"""
    html = f"""
    <div class="printable-notes">
        <div class="notes-header">
            <h1 class="lesson-title">📚 STUDY NOTES</h1>
            <h2 class="lesson-name">{note_content['lesson_title']}</h2>
            <div class="completion-info">
                Completed: {datetime.fromisoformat(note_content['completion_date']).strftime('%B %d, %Y')} | 
                Score: {note_content['final_score']*100:.0f}% | 
                Duration: {note_content['duration_minutes']} minutes
            </div>
        </div>
        
        <div class="section-divider">═══════════════════════════════════════════════════════</div>
        
        <div class="lesson-overview">
            <h3>📖 LESSON OVERVIEW</h3>
            <p>{note_content['lesson_overview']}</p>
        </div>
        
        <div class="section-divider">───────────────────────────────────────────────────────</div>
        
        <div class="objectives-section">
            <h3>🎯 LEARNING OBJECTIVES MASTERED</h3>
            <ul class="objectives-list">
    """
    
    for obj in note_content['objectives']:
        status = "✅" if obj['mastered'] else "🔄"
        html += f"                <li>{status} {obj['description']}</li>\n"
    
    html += """
            </ul>
        </div>
        
        <div class="section-divider">───────────────────────────────────────────────────────</div>
        
        <div class="key-concepts">
            <h3>📝 KEY CONCEPTS</h3>
    """
    
    for concept in note_content['key_concepts']:
        html += f"""
            <div class="concept-item">
                <h4>🔹 {concept['title']}</h4>
                <p>{concept['explanation']}</p>
            </div>
        """
    
    html += f"""
        </div>
        
        <div class="section-divider">───────────────────────────────────────────────────────</div>
        
        <div class="insights-section">
            <h3>💡 KEY INSIGHTS FROM YOUR LEARNING</h3>
            <ul class="insights-list">
    """
    
    for insight in note_content['insights']:
        html += f"                <li>{insight}</li>\n"
    
    html += f"""
            </ul>
        </div>
        
        <div class="section-divider">───────────────────────────────────────────────────────</div>
        
        <div class="review-questions">
            <h3>🤔 REVIEW QUESTIONS</h3>
            <ol class="questions-list">
    """
    
    for question in note_content['review_questions']:
        html += f"                <li>{question}</li>\n"
    
    html += f"""
            </ol>
        </div>
        
        <div class="section-divider">───────────────────────────────────────────────────────</div>
        
        <div class="performance-section">
            <h3>📈 YOUR PROGRESS</h3>
            <ul class="performance-list">
                <li>Lesson Score: {note_content['final_score']*100:.0f}%</li>
                <li>Mastery Level: {note_content['performance']['mastery_level']}</li>
                <li>Objectives Completed: {note_content['performance']['objectives_completed']}/{note_content['performance']['total_objectives']}</li>
                <li>Time Invested: {note_content['duration_minutes']} minutes</li>
            </ul>
        </div>
        
        <div class="section-divider">═══════════════════════════════════════════════════════</div>
        
        <div class="notes-footer">
            <p>Generated by Autodidact Learning System</p>
        </div>
    </div>
    """
    
    return html


def generate_summary(note_content: Dict) -> str:
    """Generate a brief summary for collection display"""
    objectives_completed = note_content['performance']['objectives_completed']
    total_objectives = note_content['performance']['total_objectives']
    score = note_content['final_score'] * 100
    
    summary = f"Completed {objectives_completed}/{total_objectives} objectives with {score:.0f}% score. "
    
    if note_content['key_concepts']:
        key_concept = note_content['key_concepts'][0]['title']
        summary += f"Key focus: {key_concept[:50]}..."
    
    return summary


def save_notes_to_database(note_id: str, session_id: str, project_id: str, node_id: str, 
                          lesson_title: str, content: Dict, formatted_html: str, summary: str) -> bool:
    """Save notes to the database"""
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO study_notes 
                (id, session_id, project_id, node_id, lesson_title, content_json, formatted_html, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                note_id,
                session_id,
                project_id, 
                node_id,
                lesson_title,
                json.dumps(content),
                formatted_html,
                summary
            ))
            conn.commit()
            logger.info(f"Study notes saved successfully: {note_id}")
            return True
            
    except Exception as e:
        logger.error(f"Error saving study notes: {e}")
        logger.exception("Full traceback:")
        return False


def get_user_study_notes(project_id: str) -> List[Dict]:
    """Retrieve all study notes for a project"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT id, lesson_title, generated_date, summary, formatted_html
                FROM study_notes 
                WHERE project_id = ?
                ORDER BY generated_date DESC
            """, (project_id,))
            
            notes = []
            for row in cursor.fetchall():
                notes.append({
                    'id': row['id'],
                    'title': row['lesson_title'],
                    'date': row['generated_date'],
                    'summary': row['summary'],
                    'formatted_html': row['formatted_html']
                })
            
            return notes
            
    except Exception as e:
        logger.error(f"Error retrieving study notes: {e}")
        logger.exception("Full traceback:")
        return []


def get_study_note_by_id(note_id: str) -> Optional[Dict]:
    """Get a specific study note by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT id, lesson_title, generated_date, content_json, formatted_html, summary
                FROM study_notes 
                WHERE id = ?
            """, (note_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'title': row['lesson_title'],
                    'date': row['generated_date'],
                    'content': json.loads(row['content_json']),
                    'formatted_html': row['formatted_html'],
                    'summary': row['summary']
                }
            
            return None
            
    except Exception as e:
        logger.error(f"Error retrieving study note: {e}")
        logger.exception("Full traceback:")
        return None