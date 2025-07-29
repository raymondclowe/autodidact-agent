# Questions Per Step Feature

## Overview

The Questions Per Step feature enhances the AI tutoring system by adapting the number of questions asked in each learning step based on individual student learning styles and preferences.

## Problem Solved

Previously, the AI tutor would ask 1-3 questions per step uniformly for all students. Some students found this excessive (preferring to move quickly with fewer questions), while others wanted more thorough questioning. The AI can now detect and adapt to these different learning styles.

## How It Works

### Learning Style Detection

The system analyzes student behavior patterns to identify question preferences:

- **Minimal** (1 question per step): Student answers only 1 question fully, gives brief/shallow responses to additional questions
- **Moderate** (2-3 questions per step): Student engages comfortably with multiple questions (default)
- **Extensive** (3-4+ questions per step): Student asks follow-up questions, provides detailed responses, wants deeper exploration

### Adaptive Questioning

Based on the detected preference, the AI tutor adapts:

#### Teaching Phase
- **Minimal**: Ask only 1 focused question, move on if answered well
- **Moderate**: Ask 2-3 questions as normal (default behavior)
- **Extensive**: Ask 3-4 questions, encourage deeper exploration

#### Recap Phase
- **Minimal**: 1 focused question covering most important takeaway
- **Moderate**: 2-3 short questions or 2-question mini-quiz
- **Extensive**: 3-4 questions or longer mini-quiz for thorough understanding

## Implementation Details

### Learner Profile Fields

**Generic Profile:**
- `questions_per_step`: Overall preference across all topics (minimal/moderate/extensive)

**Topic-Specific Profile:**
- `questions_per_step_preference`: Topic-specific question preference

### AI Analysis

The profile analysis prompts now include specific guidance to detect question preferences by looking for:
- Response length and depth patterns
- Engagement with multiple questions
- Student requests for more/fewer questions
- Impatience or enthusiasm for continued questioning

### Prompt Adaptation

The tutoring prompts now include conditional logic based on the `Questions Per Step Preference` field in the learner profile context.

## Benefits

1. **Improved Engagement**: Students receive question counts that match their learning style
2. **Reduced Frustration**: Eliminates annoyance from too many or too few questions
3. **Personalized Learning**: Automatically adapts to individual preferences
4. **Maintained Effectiveness**: Learning outcomes preserved across all preference types
5. **Automatic Detection**: No manual configuration required - learns from student behavior

## Usage

The feature works automatically once implemented:

1. Students start with the default "moderate" preference
2. The AI analyzes session transcripts after each learning session
3. If patterns indicate a different preference, the profile is updated
4. Future sessions use the detected preference to adapt question count
5. The system continues to learn and refine the preference over time

## Files Modified

- `backend/learner_profile_templates.py`: Added question preference fields
- `backend/learner_profile.py`: Added detection logic and preference extraction
- `backend/tutor_prompts.py`: Updated prompts with adaptive questioning logic

## Testing

The feature includes comprehensive tests:
- `test_questions_per_step.py`: Basic functionality tests
- `test_comprehensive_questions.py`: Behavior detection tests
- `demo_questions_per_step.py`: Full demonstration and integration tests

## Future Enhancements

Potential improvements:
- Visual indicators in the UI showing current question preference
- Manual override option for students to set their preference
- Analytics dashboard showing question preference distribution
- A/B testing to optimize detection thresholds