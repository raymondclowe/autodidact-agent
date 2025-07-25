"""
Learner Profile Templates
Contains XML templates for generic and topic-specific learner profiles
"""

# Generic learner profile template with all the required aspects
GENERIC_LEARNER_PROFILE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<generic_learner_profile>
    <learning_preferences>
        <instruction_style>to be determined</instruction_style>
        <example_preference>to be determined</example_preference>
        <hands_on_vs_theoretical>to be determined</hands_on_vs_theoretical>
        <pacing_preference>to be determined</pacing_preference>
        <feedback_frequency>to be determined</feedback_frequency>
    </learning_preferences>
    
    <strengths_and_needs>
        <conceptual_strengths>to be determined</conceptual_strengths>
        <conceptual_needs>to be determined</conceptual_needs>
        <metacognitive_strengths>to be determined</metacognitive_strengths>
        <metacognitive_needs>to be determined</metacognitive_needs>
        <motivational_strengths>to be determined</motivational_strengths>
        <motivational_needs>to be determined</motivational_needs>
    </strengths_and_needs>
    
    <prior_knowledge_and_misconceptions>
        <general_knowledge_areas>to be determined</general_knowledge_areas>
        <common_misconceptions>to be determined</common_misconceptions>
        <knowledge_gaps>to be determined</knowledge_gaps>
    </prior_knowledge_and_misconceptions>
    
    <barriers_and_supports>
        <content_type_difficulties>to be determined</content_type_difficulties>
        <representation_difficulties>to be determined</representation_difficulties>
        <effective_supports>to be determined</effective_supports>
        <environmental_preferences>to be determined</environmental_preferences>
    </barriers_and_supports>
    
    <interests_and_engagement>
        <engagement_drivers>to be determined</engagement_drivers>
        <interest_areas>to be determined</interest_areas>
        <motivating_factors>to be determined</motivating_factors>
        <demotivating_factors>to be determined</demotivating_factors>
    </interests_and_engagement>
    
    <psychological_needs>
        <autonomy_preferences>to be determined</autonomy_preferences>
        <competence_indicators>to be determined</competence_indicators>
        <relatedness_needs>to be determined</relatedness_needs>
    </psychological_needs>
    
    <goal_orientations>
        <mastery_vs_performance>to be determined</mastery_vs_performance>
        <approach_vs_avoidant>to be determined</approach_vs_avoidant>
        <learning_goals>to be determined</learning_goals>
    </goal_orientations>
    
    <meta_information>
        <last_updated>n/a</last_updated>
        <sessions_analyzed>0</sessions_analyzed>
        <confidence_level>low</confidence_level>
    </meta_information>
</generic_learner_profile>"""

# Topic-specific learner profile template
TOPIC_SPECIFIC_LEARNER_PROFILE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<topic_specific_learner_profile topic="{topic}">
    <topic_understanding>
        <current_knowledge_level>to be determined</current_knowledge_level>
        <specific_concepts_mastered>to be determined</specific_concepts_mastered>
        <specific_concepts_struggling>to be determined</specific_concepts_struggling>
        <prerequisite_gaps>to be determined</prerequisite_gaps>
    </topic_understanding>
    
    <topic_specific_preferences>
        <preferred_learning_approaches>to be determined</preferred_learning_approaches>
        <effective_examples>to be determined</effective_examples>
        <preferred_representations>to be determined</preferred_representations>
        <successful_practice_methods>to be determined</successful_practice_methods>
    </topic_specific_preferences>
    
    <topic_misconceptions>
        <identified_misconceptions>to be determined</identified_misconceptions>
        <recurring_errors>to be determined</recurring_errors>
        <conceptual_confusion_areas>to be determined</conceptual_confusion_areas>
    </topic_misconceptions>
    
    <topic_engagement>
        <interest_level>to be determined</interest_level>
        <motivating_aspects>to be determined</motivating_aspects>
        <challenging_aspects>to be determined</challenging_aspects>
        <real_world_connections>to be determined</real_world_connections>
    </topic_engagement>
    
    <learning_progression>
        <mastered_learning_objectives>to be determined</mastered_learning_objectives>
        <current_focus_areas>to be determined</current_focus_areas>
        <next_recommended_steps>to be determined</next_recommended_steps>
        <pace_observations>to be determined</pace_observations>
    </learning_progression>
    
    <meta_information>
        <last_updated>n/a</last_updated>
        <sessions_analyzed>0</sessions_analyzed>
        <confidence_level>low</confidence_level>
        <project_id>{project_id}</project_id>
    </meta_information>
</topic_specific_learner_profile>"""

def get_generic_profile_template():
    """Return the generic learner profile template"""
    return GENERIC_LEARNER_PROFILE_TEMPLATE

def get_topic_profile_template(topic: str, project_id: str):
    """Return the topic-specific learner profile template with topic and project_id filled in"""
    return TOPIC_SPECIFIC_LEARNER_PROFILE_TEMPLATE.format(
        topic=topic,
        project_id=project_id
    )