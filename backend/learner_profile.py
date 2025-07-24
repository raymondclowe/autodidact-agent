"""
Learner Profile Management Module
Handles persistent learner profiles for personalized learning experience
"""

import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from contextlib import contextmanager

from backend.learner_profile_templates import (
    get_generic_profile_template, 
    get_topic_profile_template
)
from backend.db import get_db_connection
from utils.providers import create_client, get_model_for_task

logger = logging.getLogger(__name__)

class LearnerProfileManager:
    """Manages learner profiles including creation, updates, and retrieval"""
    
    def get_generic_profile(self) -> str:
        """Get the current generic learner profile XML"""
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT profile_xml FROM generic_learner_profile 
                ORDER BY updated_at DESC LIMIT 1
            """)
            row = cursor.fetchone()
            
            if row:
                return row[0]
            else:
                # Return blank template for first time
                return get_generic_profile_template()
    
    def get_topic_profile(self, project_id: str, topic: str) -> str:
        """Get the topic-specific learner profile XML for a project"""
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT profile_xml FROM topic_learner_profile 
                WHERE project_id = ? 
                ORDER BY updated_at DESC LIMIT 1
            """, (project_id,))
            row = cursor.fetchone()
            
            if row:
                return row[0]
            else:
                # Return blank template for first time
                return get_topic_profile_template(topic, project_id)
    
    def save_generic_profile(self, profile_xml: str):
        """Save updated generic learner profile"""
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO generic_learner_profile (profile_xml, updated_at)
                VALUES (?, CURRENT_TIMESTAMP)
            """, (profile_xml,))
            conn.commit()
            logger.info("Generic learner profile updated")
    
    def save_topic_profile(self, project_id: str, topic: str, profile_xml: str):
        """Save updated topic-specific learner profile"""
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO topic_learner_profile (project_id, topic, profile_xml, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (project_id, topic, profile_xml))
            conn.commit()
            logger.info(f"Topic learner profile updated for project {project_id}")
    
    def update_profiles_from_session(self, session_id: str):
        """
        Update both generic and topic profiles based on session transcript.
        This is called at the end of a learning session.
        """
        from backend.db import get_session_info, get_transcript_for_session, get_project
        
        try:
            # Get session information
            session_info = get_session_info(session_id)
            if not session_info:
                logger.error(f"Session {session_id} not found")
                return
            
            # Get project information
            project = get_project(session_info['project_id'])
            if not project:
                logger.error(f"Project {session_info['project_id']} not found")
                return
            
            # Get session transcript
            transcript = get_transcript_for_session(session_id)
            if not transcript:
                logger.warning(f"No transcript found for session {session_id}")
                return
            
            # Format transcript for AI analysis
            transcript_text = self._format_transcript_for_analysis(transcript)
            
            # Update generic profile
            self._update_generic_profile_with_ai(transcript_text)
            
            # Update topic-specific profile
            self._update_topic_profile_with_ai(
                session_info['project_id'], 
                project['topic'], 
                transcript_text
            )
            
            logger.info(f"Profiles updated for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error updating profiles for session {session_id}: {e}")
    
    def _format_transcript_for_analysis(self, transcript: List[Dict]) -> str:
        """Format transcript entries into readable text for AI analysis"""
        formatted_lines = []
        for entry in transcript:
            role = entry['role'].upper()
            content = entry['content'].strip()
            formatted_lines.append(f"{role}: {content}")
        
        return "\n".join(formatted_lines)
    
    def _update_generic_profile_with_ai(self, transcript_text: str):
        """Use AI to update the generic learner profile based on session transcript"""
        try:
            current_profile = self.get_generic_profile()
            
            prompt = f"""Here is the existing generic learner profile:

{current_profile}

Here is the lesson transcript from a recent learning session:

{transcript_text}

Please analyze this lesson transcript and determine if the generic learner profile needs updating. Look for evidence of:
- Learning preferences (instruction style, example preferences, hands-on vs theoretical, pacing, feedback)
- Strengths and needs (conceptual, metacognitive, motivational)
- Prior knowledge and misconceptions
- Barriers and supports (content difficulties, representation issues, effective supports)
- Interests and engagement drivers
- Psychological needs (autonomy, competence, relatedness)
- Goal orientations (mastery vs performance oriented)

If you determine that the profile is accurate and no updates are needed, respond with exactly: "NO CHANGE NEEDED"

If updates are needed, provide the complete updated XML profile with specific observations from the transcript. Replace "to be determined" fields only when you have evidence from the transcript. Update the meta_information section with current timestamp and increment sessions_analyzed.

Is the profile accurate? Does it need updating? Have we learned something new about how this student best learns in general?"""

            client = create_client()
            model = get_model_for_task("chat")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            result = response.choices[0].message.content.strip()
            
            if result != "NO CHANGE NEEDED":
                # Validate it's proper XML before saving
                try:
                    ET.fromstring(result)
                    self.save_generic_profile(result)
                    logger.info("Generic profile updated by AI")
                except ET.ParseError as e:
                    logger.error(f"AI returned invalid XML for generic profile: {e}")
            else:
                logger.info("AI determined no changes needed for generic profile")
                
        except Exception as e:
            logger.error(f"Error updating generic profile with AI: {e}")
    
    def _update_topic_profile_with_ai(self, project_id: str, topic: str, transcript_text: str):
        """Use AI to update the topic-specific learner profile based on session transcript"""
        try:
            current_profile = self.get_topic_profile(project_id, topic)
            
            prompt = f"""Here is the existing topic-specific learner profile for "{topic}":

{current_profile}

Here is the lesson transcript from a recent learning session on this topic:

{transcript_text}

Please analyze this lesson transcript and determine if the topic-specific learner profile needs updating. Look for evidence of:
- Topic understanding (knowledge level, concepts mastered/struggling, prerequisite gaps)
- Topic-specific learning preferences (approaches, examples, representations, practice methods)
- Topic misconceptions (identified misconceptions, recurring errors, confusion areas)
- Topic engagement (interest level, motivating/challenging aspects, real-world connections)
- Learning progression (mastered objectives, current focus, next steps, pace observations)

If you determine that the profile is accurate and no updates are needed, respond with exactly: "NO CHANGE NEEDED"

If updates are needed, provide the complete updated XML profile with specific observations from the transcript. Replace "to be determined" fields only when you have evidence from the transcript. Update the meta_information section with current timestamp and increment sessions_analyzed.

Is the profile accurate? Does it need updating? Have we learned something new about how this student best learns this specific topic?"""

            client = create_client()
            model = get_model_for_task("chat")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            result = response.choices[0].message.content.strip()
            
            if result != "NO CHANGE NEEDED":
                # Validate it's proper XML before saving
                try:
                    ET.fromstring(result)
                    self.save_topic_profile(project_id, topic, result)
                    logger.info(f"Topic profile updated by AI for project {project_id}")
                except ET.ParseError as e:
                    logger.error(f"AI returned invalid XML for topic profile: {e}")
            else:
                logger.info(f"AI determined no changes needed for topic profile (project {project_id})")
                
        except Exception as e:
            logger.error(f"Error updating topic profile with AI: {e}")
    
    def get_profile_context_for_session(self, project_id: str, topic: str) -> str:
        """Get formatted profile information to include in session prompts"""
        try:
            generic_profile = self.get_generic_profile()
            topic_profile = self.get_topic_profile(project_id, topic)
            
            # Extract key information from profiles for prompt context
            context = f"""LEARNER PROFILE CONTEXT:

Generic Learning Profile:
{self._extract_key_profile_info(generic_profile)}

Topic-Specific Profile for "{topic}":
{self._extract_key_profile_info(topic_profile)}

Please use this learner profile information to personalize the learning session."""
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting profile context: {e}")
            return "LEARNER PROFILE CONTEXT: Profile information not available."
    
    def _extract_key_profile_info(self, profile_xml: str) -> str:
        """Extract key non-'to be determined' information from profile XML for prompt context"""
        try:
            root = ET.fromstring(profile_xml)
            key_info = []
            
            # Walk through all elements and collect non-placeholder values
            for elem in root.iter():
                if elem.text and elem.text.strip() and elem.text.strip() != "to be determined" and elem.text.strip() != "n/a":
                    key_info.append(f"- {elem.tag}: {elem.text.strip()}")
            
            if key_info:
                return "\n".join(key_info)
            else:
                return "- No specific learner preferences identified yet"
                
        except ET.ParseError:
            return "- Profile parsing error"


# Global instance
learner_profile_manager = LearnerProfileManager()