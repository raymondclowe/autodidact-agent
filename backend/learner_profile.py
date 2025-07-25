"""
Learner Profile Management Module
Handles persistent learner profiles for personalized learning experience
"""

import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
import logging
import re
from datetime import datetime
from contextlib import contextmanager

from backend.learner_profile_templates import (
    get_generic_profile_template, 
    get_topic_profile_template
)
from backend.db import get_db_connection
from utils.providers import create_client, get_model_for_task

logger = logging.getLogger(__name__)

# Constants
NO_CHANGE_RESPONSE = "NO CHANGE NEEDED"
MAX_TRANSCRIPT_LENGTH = 10000
DEFAULT_AI_TEMPERATURE = 0.1
PROFILE_CACHE_TTL_SECONDS = 300  # 5 minutes

# XML validation constants
GENERIC_PROFILE_ROOT = "generic_learner_profile"
TOPIC_PROFILE_ROOT = "topic_specific_learner_profile"

GENERIC_REQUIRED_SECTIONS = ["learning_preferences", "strengths_and_needs", "meta_information"]
TOPIC_REQUIRED_SECTIONS = ["topic_understanding", "topic_specific_preferences", "meta_information"]

class LearnerProfileManager:
    """Manages learner profiles including creation, updates, and retrieval"""
    
    def __init__(self):
        """Initialize the learner profile manager"""
        self._profile_cache = {}  # Simple cache for profiles during session
        self._last_cache_clear = datetime.now()
    
    def _clear_expired_cache(self):
        """Clear cache if it's expired"""
        if (datetime.now() - self._last_cache_clear).seconds > PROFILE_CACHE_TTL_SECONDS:
            self._profile_cache.clear()
            self._last_cache_clear = datetime.now()
    
    def get_generic_profile(self) -> str:
        """Get the current generic learner profile XML"""
        self._clear_expired_cache()
        
        cache_key = "generic_profile"
        if cache_key in self._profile_cache:
            return self._profile_cache[cache_key]
        
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT profile_xml FROM generic_learner_profile 
                ORDER BY updated_at DESC LIMIT 1
            """)
            row = cursor.fetchone()
            
            if row:
                profile = row[0]
                self._profile_cache[cache_key] = profile
                return profile
            else:
                # Return blank template for first time
                template = get_generic_profile_template()
                self._profile_cache[cache_key] = template
                return template
    
    def get_topic_profile(self, project_id: str, topic: str) -> str:
        """Get the topic-specific learner profile XML for a project"""
        self._clear_expired_cache()
        
        cache_key = f"topic_profile_{project_id}"
        if cache_key in self._profile_cache:
            return self._profile_cache[cache_key]
        
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT profile_xml FROM topic_learner_profile 
                WHERE project_id = ? 
                ORDER BY updated_at DESC LIMIT 1
            """, (project_id,))
            row = cursor.fetchone()
            
            if row:
                profile = row[0]
                self._profile_cache[cache_key] = profile
                return profile
            else:
                # Return blank template for first time
                template = get_topic_profile_template(topic, project_id)
                self._profile_cache[cache_key] = template
                return template
    
    def save_generic_profile(self, profile_xml: str):
        """Save updated generic learner profile"""
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO generic_learner_profile (profile_xml, updated_at)
                VALUES (?, CURRENT_TIMESTAMP)
            """, (profile_xml,))
            conn.commit()
            logger.info("Generic learner profile updated")
        
        # Clear cache to force reload
        self._profile_cache.pop("generic_profile", None)
    
    def save_topic_profile(self, project_id: str, topic: str, profile_xml: str):
        """Save updated topic-specific learner profile"""
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO topic_learner_profile (project_id, topic, profile_xml, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (project_id, topic, profile_xml))
            conn.commit()
            logger.info(f"Topic learner profile updated for project {project_id}")
        
        # Clear cache to force reload
        cache_key = f"topic_profile_{project_id}"
        self._profile_cache.pop(cache_key, None)
    
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
                # Try to get basic session info from session table directly
                with get_db_connection() as conn:
                    cursor = conn.execute("""
                        SELECT s.project_id, p.topic 
                        FROM session s 
                        JOIN project p ON s.project_id = p.id 
                        WHERE s.id = ?
                    """, (session_id,))
                    row = cursor.fetchone()
                    if row:
                        session_info = {
                            'project_id': row[0],
                            'project_topic': row[1]
                        }
                    else:
                        logger.error(f"Session {session_id} not found")
                        return
            
            # Get project information if not already available
            if 'project_topic' not in session_info:
                project = get_project(session_info['project_id'])
                if not project:
                    logger.error(f"Project {session_info['project_id']} not found")
                    return
                session_info['project_topic'] = project['topic']
            
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
                session_info['project_topic'], 
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
            
            # Sanitize transcript text to prevent potential injection issues
            sanitized_transcript = self._sanitize_text_for_ai(transcript_text)
            
            prompt = self._build_generic_profile_update_prompt(current_profile, sanitized_transcript)

            client = create_client()
            model = get_model_for_task("chat")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_AI_TEMPERATURE  # Low temperature for consistent analysis
            )
            
            result = response.choices[0].message.content.strip()
            
            if result != NO_CHANGE_RESPONSE:
                # Validate it's proper XML before saving
                if self._validate_and_save_profile(result, "generic"):
                    logger.info("Generic profile updated by AI")
                else:
                    logger.error("Failed to save generic profile due to validation errors")
            else:
                logger.info("AI determined no changes needed for generic profile")
                
        except Exception as e:
            logger.error(f"Error updating generic profile with AI: {e}")
    
    def _update_topic_profile_with_ai(self, project_id: str, topic: str, transcript_text: str):
        """Use AI to update the topic-specific learner profile based on session transcript"""
        try:
            current_profile = self.get_topic_profile(project_id, topic)
            
            # Sanitize transcript text to prevent potential injection issues
            sanitized_transcript = self._sanitize_text_for_ai(transcript_text)
            
            prompt = self._build_topic_profile_update_prompt(current_profile, topic, sanitized_transcript)

            client = create_client()
            model = get_model_for_task("chat")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_AI_TEMPERATURE  # Low temperature for consistent analysis
            )
            
            result = response.choices[0].message.content.strip()
            
            if result != NO_CHANGE_RESPONSE:
                # Validate it's proper XML before saving
                if self._validate_and_save_profile(result, "topic", project_id, topic):
                    logger.info(f"Topic profile updated by AI for project {project_id}")
                else:
                    logger.error(f"Failed to save topic profile for project {project_id} due to validation errors")
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
    
    def _sanitize_text_for_ai(self, text: str) -> str:
        """Sanitize text before sending to AI to prevent potential injection issues"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters and limit length
        sanitized = text.strip()
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        # Limit length to prevent extremely long prompts
        max_length = MAX_TRANSCRIPT_LENGTH  # Reasonable limit for session transcripts
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "\n[...transcript truncated...]"
            logger.warning(f"Transcript truncated to {max_length} characters for AI processing")
        
        return sanitized
    
    def _build_generic_profile_update_prompt(self, current_profile: str, transcript_text: str) -> str:
        """Build the prompt for generic profile updates"""
        return f"""Here is the existing generic learner profile:

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

If you determine that the profile is accurate and no updates are needed, respond with exactly: "{NO_CHANGE_RESPONSE}"

If updates are needed, provide the complete updated XML profile with specific observations from the transcript. Replace "to be determined" fields only when you have evidence from the transcript. Update the meta_information section with current timestamp and increment sessions_analyzed.

Is the profile accurate? Does it need updating? Have we learned something new about how this student best learns in general?"""
    
    def _build_topic_profile_update_prompt(self, current_profile: str, topic: str, transcript_text: str) -> str:
        """Build the prompt for topic-specific profile updates"""
        return f"""Here is the existing topic-specific learner profile for "{topic}":

{current_profile}

Here is the lesson transcript from a recent learning session on this topic:

{transcript_text}

Please analyze this lesson transcript and determine if the topic-specific learner profile needs updating. Look for evidence of:
- Topic understanding (knowledge level, concepts mastered/struggling, prerequisite gaps)
- Topic-specific learning preferences (approaches, examples, representations, practice methods)
- Topic misconceptions (identified misconceptions, recurring errors, confusion areas)
- Topic engagement (interest level, motivating/challenging aspects, real-world connections)
- Learning progression (mastered objectives, current focus, next steps, pace observations)

If you determine that the profile is accurate and no updates are needed, respond with exactly: "{NO_CHANGE_RESPONSE}"

If updates are needed, provide the complete updated XML profile with specific observations from the transcript. Replace "to be determined" fields only when you have evidence from the transcript. Update the meta_information section with current timestamp and increment sessions_analyzed.

Is the profile accurate? Does it need updating? Have we learned something new about how this student best learns this specific topic?"""
    
    def _validate_and_save_profile(self, profile_xml: str, profile_type: str, project_id: Optional[str] = None, topic: Optional[str] = None) -> bool:
        """Validate XML and save profile. Returns True if successful, False otherwise."""
        try:
            # Parse XML to validate structure
            root = ET.fromstring(profile_xml)
            
            # Basic validation of expected structure
            if profile_type == "generic":
                expected_root = GENERIC_PROFILE_ROOT
                required_sections = GENERIC_REQUIRED_SECTIONS
            elif profile_type == "topic":
                expected_root = TOPIC_PROFILE_ROOT
                required_sections = TOPIC_REQUIRED_SECTIONS
            else:
                logger.error(f"Unknown profile type: {profile_type}")
                return False
            
            if root.tag != expected_root:
                logger.error(f"Invalid XML root tag for {profile_type} profile: expected {expected_root}, got {root.tag}")
                return False
            
            # Check for required sections
            for section in required_sections:
                if root.find(section) is None:
                    logger.error(f"Missing required section '{section}' in {profile_type} profile")
                    return False
            
            # Save the profile
            if profile_type == "generic":
                self.save_generic_profile(profile_xml)
            elif profile_type == "topic":
                if not project_id or not topic:
                    logger.error("project_id and topic are required for topic profile")
                    return False
                self.save_topic_profile(project_id, topic, profile_xml)
            
            return True
            
        except ET.ParseError as e:
            logger.error(f"Invalid XML in {profile_type} profile: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating and saving {profile_type} profile: {e}")
            return False


# Global instance
learner_profile_manager = LearnerProfileManager()