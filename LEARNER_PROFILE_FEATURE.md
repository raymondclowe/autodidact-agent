# Learner Profile Feature Documentation

The learner profile feature implements persistent learner profiles to personalize the learning experience. This documentation explains how the feature works and how to use it.

## Overview

The learner profile system maintains two types of profiles:

1. **Generic Student Profile**: Captures general learning preferences and traits that apply across all subjects
2. **Project/Topic-Specific Profile**: Captures learning patterns and needs related to a particular subject or project

Both profiles are stored in XML format and are automatically updated at the end of each learning session using AI analysis of the session transcript.

## Profile Structure

### Generic Learner Profile

The generic profile includes:

- **Learning Preferences**: Instruction style, example preferences, hands-on vs theoretical approach, pacing, feedback frequency
- **Strengths and Needs**: Conceptual, metacognitive, and motivational aspects
- **Prior Knowledge and Misconceptions**: General knowledge areas, common misconceptions, knowledge gaps
- **Barriers and Supports**: Content type difficulties, representation difficulties, effective supports, environmental preferences
- **Interests and Engagement**: Engagement drivers, interest areas, motivating/demotivating factors
- **Psychological Needs**: Autonomy preferences, competence indicators, relatedness needs
- **Goal Orientations**: Mastery vs performance orientation, approach vs avoidant style, learning goals

### Topic-Specific Learner Profile

The topic-specific profile includes:

- **Topic Understanding**: Current knowledge level, concepts mastered/struggling, prerequisite gaps
- **Topic-Specific Preferences**: Preferred learning approaches, effective examples, preferred representations, successful practice methods
- **Topic Misconceptions**: Identified misconceptions, recurring errors, conceptual confusion areas
- **Topic Engagement**: Interest level, motivating/challenging aspects, real-world connections
- **Learning Progression**: Mastered objectives, current focus areas, next recommended steps, pace observations

## Database Schema

Two new tables store the profile data:

```sql
CREATE TABLE generic_learner_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_xml TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE topic_learner_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    profile_xml TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id)
);
```

## How It Works

### 1. Profile Initialization

When the system first starts, both profiles begin as templates with placeholder values:
- Most fields are set to "to be determined" 
- Some metadata fields like `sessions_analyzed` start at 0
- `confidence_level` starts as "low"

### 2. Session Integration

At the start of each learning session:
1. The system loads both the generic and topic-specific profiles
2. Key information from the profiles is extracted and formatted
3. This learner profile context is included in all tutor prompts (teaching and recap phases)
4. The AI tutor uses this information to personalize the learning experience

### 3. Profile Updates

At the end of each learning session:
1. The session transcript is formatted for analysis
2. The AI analyzes the transcript against the current generic profile
3. If improvements are identified, the generic profile is updated
4. The AI then analyzes the transcript against the topic-specific profile
5. If improvements are identified, the topic-specific profile is updated

### 4. AI Update Process

For each profile update, the AI is prompted with:
- The existing profile XML
- The complete session transcript
- Instructions to look for specific types of evidence
- A request to either return "NO CHANGE NEEDED" or a complete updated profile

The AI only updates fields when it has clear evidence from the transcript, maintaining "to be determined" for uncertain areas.

## Code Components

### Core Files

- `backend/learner_profile.py`: Main profile management logic
- `backend/learner_profile_templates.py`: XML templates for both profile types
- `backend/db.py`: Database operations (updated to include profile tables and triggers)
- `backend/tutor_prompts.py`: Updated prompts to include learner profile context
- `backend/graph_v05.py`: Updated session flow to load and apply profiles

### Key Classes and Functions

- `LearnerProfileManager`: Main class handling all profile operations
- `get_generic_profile()`: Retrieves current generic profile
- `get_topic_profile()`: Retrieves topic-specific profile for a project
- `update_profiles_from_session()`: Updates both profiles based on session transcript
- `get_profile_context_for_session()`: Formats profile info for prompt inclusion

## Usage Examples

### Getting Profile Information

```python
from backend.learner_profile import learner_profile_manager

# Get current generic profile
generic_profile = learner_profile_manager.get_generic_profile()

# Get topic-specific profile for a project
topic_profile = learner_profile_manager.get_topic_profile(project_id, "Machine Learning")

# Get formatted context for session prompts
context = learner_profile_manager.get_profile_context_for_session(project_id, "Machine Learning")
```

### Manual Profile Updates

```python
# Update profiles after a session (automatically called by complete_session)
learner_profile_manager.update_profiles_from_session(session_id)

# Save an updated profile manually
learner_profile_manager.save_generic_profile(updated_xml)
learner_profile_manager.save_topic_profile(project_id, topic, updated_xml)
```

## Integration Points

### Session Start (load_context_node)
- Profiles are loaded and formatted into context
- Context is added to session state as `learner_profile_context`

### Teaching Prompts
- All teaching and recap prompts include learner profile context
- AI tutor can personalize based on known preferences

### Session Completion (complete_session)
- Profile updates are automatically triggered
- Both profiles are analyzed and potentially updated

## Benefits

1. **Personalization**: Each session becomes more tailored to the individual learner
2. **Adaptation**: The system learns and improves its understanding over time
3. **Consistency**: Learning preferences are maintained across different topics and sessions
4. **Efficiency**: Reduces time spent on ineffective teaching approaches
5. **Engagement**: Utilizes known motivational factors and interests

## Future Enhancements

Potential improvements to consider:

1. **Profile Confidence Scoring**: More sophisticated confidence metrics based on evidence strength
2. **Profile Visualization**: UI components to display profile information to users
3. **Profile Export/Import**: Allow users to back up or transfer profiles
4. **Multi-Modal Profiles**: Extend to include multimedia learning preferences
5. **Collaborative Profiles**: Share anonymized insights across similar learners
