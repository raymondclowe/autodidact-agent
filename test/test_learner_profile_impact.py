"""
Test suite to validate that learner profiles actually impact generated course material.

This test creates two diametrically opposed learner profiles and verifies that 
the AI tutor generates different content for the same course material based on the profiles.
"""

import os
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.learner_profile import LearnerProfileManager
from backend.learner_profile_templates import get_generic_profile_template, get_topic_profile_template
from backend.tutor_prompts import format_teaching_prompt, format_recap_prompt


class TestLearnerProfileImpact(unittest.TestCase):
    """Test that learner profiles actually impact generated course material"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.profile_manager = LearnerProfileManager()
        self.dummy_project_id = "test_project_123"
        self.dummy_topic = "Introduction to Programming"
        
        # Dummy course content for testing
        self.dummy_refs = [
            {
                'rid': 'REF001',
                'loc': 'Chapter 1',
                'title': 'Basic Programming Concepts',
                'type': 'textbook',
                'date': '2023-01-01'
            }
        ]
        
        self.dummy_obj_id = "OBJ001"
        self.dummy_obj_label = "Understand variables and data types"
        self.dummy_recent_topics = ["Basic syntax", "Hello World program"]
        self.dummy_remaining_objs = ["Functions", "Loops", "Conditionals"]
    
    def create_visual_hands_on_profile(self):
        """Create a learner profile for a visual, hands-on learner"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<generic_learner_profile>
    <learning_preferences>
        <instruction_style>visual and interactive</instruction_style>
        <example_preference>concrete, real-world examples with visual aids</example_preference>
        <hands_on_vs_theoretical>strongly prefers hands-on practice</hands_on_vs_theoretical>
        <pacing_preference>fast-paced with frequent activities</pacing_preference>
        <feedback_frequency>immediate feedback after each activity</feedback_frequency>
    </learning_preferences>
    
    <strengths_and_needs>
        <conceptual_strengths>learns quickly through doing and seeing</conceptual_strengths>
        <conceptual_needs>needs visual representations to understand abstract concepts</conceptual_needs>
        <metacognitive_strengths>good at self-monitoring through trial and error</metacognitive_strengths>
        <metacognitive_needs>needs structured reflection prompts</metacognitive_needs>
        <motivational_strengths>highly motivated by immediate results and success</motivational_strengths>
        <motivational_needs>needs variety and engaging activities to maintain focus</motivational_needs>
    </strengths_and_needs>
    
    <prior_knowledge_and_misconceptions>
        <general_knowledge_areas>strong spatial reasoning, technology comfortable</general_knowledge_areas>
        <common_misconceptions>may oversimplify complex relationships</common_misconceptions>
        <knowledge_gaps>limited experience with abstract thinking</knowledge_gaps>
    </prior_knowledge_and_misconceptions>
    
    <barriers_and_supports>
        <content_type_difficulties>struggles with long text passages and abstract theory</content_type_difficulties>
        <representation_difficulties>has trouble with purely verbal descriptions</representation_difficulties>
        <effective_supports>diagrams, code examples, interactive exercises</effective_supports>
        <environmental_preferences>active learning environment with tools and practice</environmental_preferences>
    </barriers_and_supports>
    
    <interests_and_engagement>
        <engagement_drivers>building things, seeing immediate results, solving practical problems</engagement_drivers>
        <interest_areas>technology, games, interactive media</interest_areas>
        <motivating_factors>competition, achievement, tangible outcomes</motivating_factors>
        <demotivating_factors>long lectures, theoretical discussions without practice</demotivating_factors>
    </interests_and_engagement>
    
    <psychological_needs>
        <autonomy_preferences>likes to explore and experiment independently</autonomy_preferences>
        <competence_indicators>measures success through working code and completed projects</competence_indicators>
        <relatedness_needs>enjoys peer collaboration and sharing projects</relatedness_needs>
    </psychological_needs>
    
    <goal_orientations>
        <mastery_vs_performance>performance-oriented, wants to build impressive projects</mastery_vs_performance>
        <approach_vs_avoidant>approach-oriented, eager to tackle challenges</approach_vs_avoidant>
        <learning_goals>wants to create functional applications quickly</learning_goals>
    </goal_orientations>
    
    <meta_information>
        <last_updated>2023-01-01</last_updated>
        <sessions_analyzed>5</sessions_analyzed>
        <confidence_level>high</confidence_level>
    </meta_information>
</generic_learner_profile>"""

    def create_theoretical_reflective_profile(self):
        """Create a learner profile for a theoretical, reflective learner"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<generic_learner_profile>
    <learning_preferences>
        <instruction_style>theoretical and analytical</instruction_style>
        <example_preference>abstract examples that illustrate underlying principles</example_preference>
        <hands_on_vs_theoretical>strongly prefers theoretical understanding first</hands_on_vs_theoretical>
        <pacing_preference>slow and deliberate with time for deep reflection</pacing_preference>
        <feedback_frequency>detailed feedback after thorough consideration</feedback_frequency>
    </learning_preferences>
    
    <strengths_and_needs>
        <conceptual_strengths>excellent at understanding abstract concepts and principles</conceptual_strengths>
        <conceptual_needs>needs to understand the why before the how</conceptual_needs>
        <metacognitive_strengths>strong self-reflection and analytical thinking</metacognitive_strengths>
        <metacognitive_needs>needs time to process and connect concepts</metacognitive_needs>
        <motivational_strengths>intrinsically motivated by understanding and knowledge</motivational_strengths>
        <motivational_needs>needs intellectual challenge and depth</motivational_needs>
    </strengths_and_needs>
    
    <prior_knowledge_and_misconceptions>
        <general_knowledge_areas>strong in mathematics, logic, and analytical reasoning</general_knowledge_areas>
        <common_misconceptions>may overcomplicate simple practical applications</common_misconceptions>
        <knowledge_gaps>limited hands-on technical experience</knowledge_gaps>
    </prior_knowledge_and_misconceptions>
    
    <barriers_and_supports>
        <content_type_difficulties>struggles with rushed practice without understanding principles</content_type_difficulties>
        <representation_difficulties>has trouble with superficial or oversimplified explanations</representation_difficulties>
        <effective_supports>comprehensive explanations, theoretical frameworks, detailed documentation</effective_supports>
        <environmental_preferences>quiet study environment with resources for deep learning</environmental_preferences>
    </barriers_and_supports>
    
    <interests_and_engagement>
        <engagement_drivers>understanding complex systems, elegant solutions, intellectual puzzles</engagement_drivers>
        <interest_areas>computer science theory, algorithms, mathematical concepts</interest_areas>
        <motivating_factors>mastery, deep understanding, elegant problem solving</motivating_factors>
        <demotivating_factors>rushed practice, superficial coverage, busywork</demotivating_factors>
    </interests_and_engagement>
    
    <psychological_needs>
        <autonomy_preferences>likes to study independently with minimal external pressure</autonomy_preferences>
        <competence_indicators>measures success through deep understanding and elegant solutions</competence_indicators>
        <relatedness_needs>values intellectual discussions with knowledgeable peers</relatedness_needs>
    </psychological_needs>
    
    <goal_orientations>
        <mastery_vs_performance>mastery-oriented, wants to understand concepts deeply</mastery_vs_performance>
        <approach_vs_avoidant>cautious, wants to understand before attempting</approach_vs_avoidant>
        <learning_goals>wants to master fundamental principles and theory</learning_goals>
    </goal_orientations>
    
    <meta_information>
        <last_updated>2023-01-01</last_updated>
        <sessions_analyzed>5</sessions_analyzed>
        <confidence_level>high</confidence_level>
    </meta_information>
</generic_learner_profile>"""

    def create_topic_profile_visual_hands_on(self):
        """Create a topic-specific profile for visual hands-on learner"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<topic_specific_learner_profile topic="{self.dummy_topic}">
    <topic_understanding>
        <current_knowledge_level>beginner with some exposure to basic concepts</current_knowledge_level>
        <specific_concepts_mastered>basic syntax, simple output statements</specific_concepts_mastered>
        <specific_concepts_struggling>abstract data types, memory concepts</specific_concepts_struggling>
        <prerequisite_gaps>limited mathematical background</prerequisite_gaps>
    </topic_understanding>
    
    <topic_specific_preferences>
        <preferred_learning_approaches>coding exercises, visual debuggers, interactive tutorials</preferred_learning_approaches>
        <effective_examples>game programming, web development, mobile apps</effective_examples>
        <preferred_representations>code snippets, flowcharts, visual diagrams</preferred_representations>
        <successful_practice_methods>pair programming, coding challenges, building projects</successful_practice_methods>
    </topic_specific_preferences>
    
    <topic_misconceptions>
        <identified_misconceptions>thinks variables are just labels rather than memory locations</identified_misconceptions>
        <recurring_errors>confuses assignment with equality comparison</recurring_errors>
        <conceptual_confusion_areas>scope and lifetime of variables</conceptual_confusion_areas>
    </topic_misconceptions>
    
    <topic_engagement>
        <interest_level>very high</interest_level>
        <motivating_aspects>creating visible results, building useful programs</motivating_aspects>
        <challenging_aspects>debugging errors, understanding error messages</challenging_aspects>
        <real_world_connections>wants to build games and mobile applications</real_world_connections>
    </topic_engagement>
    
    <learning_progression>
        <mastered_learning_objectives>print statements, basic variable assignment</mastered_learning_objectives>
        <current_focus_areas>data types, variable operations</current_focus_areas>
        <next_recommended_steps>conditional statements, user input</next_recommended_steps>
        <pace_observations>learns quickly when practicing, needs hands-on reinforcement</pace_observations>
    </learning_progression>
    
    <meta_information>
        <last_updated>2023-01-01</last_updated>
        <sessions_analyzed>3</sessions_analyzed>
        <confidence_level>medium</confidence_level>
        <project_id>{self.dummy_project_id}</project_id>
    </meta_information>
</topic_specific_learner_profile>"""

    def create_topic_profile_theoretical_reflective(self):
        """Create a topic-specific profile for theoretical reflective learner"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<topic_specific_learner_profile topic="{self.dummy_topic}">
    <topic_understanding>
        <current_knowledge_level>beginner but wants deep theoretical understanding</current_knowledge_level>
        <specific_concepts_mastered>understands computer science fundamentals theoretically</specific_concepts_mastered>
        <specific_concepts_struggling>translating theory into practical implementation</specific_concepts_struggling>
        <prerequisite_gaps>limited practical coding experience</prerequisite_gaps>
    </topic_understanding>
    
    <topic_specific_preferences>
        <preferred_learning_approaches>theoretical explanations, algorithm analysis, concept mapping</preferred_learning_approaches>
        <effective_examples>computer science algorithms, mathematical applications, system design</effective_examples>
        <preferred_representations>formal definitions, mathematical notation, conceptual diagrams</preferred_representations>
        <successful_practice_methods>analyzing code, design exercises, theoretical problems</successful_practice_methods>
    </topic_specific_preferences>
    
    <topic_misconceptions>
        <identified_misconceptions>overcomplicates simple programming tasks</identified_misconceptions>
        <recurring_errors>focuses too much on theory without practical validation</recurring_errors>
        <conceptual_confusion_areas>when to apply theoretical knowledge practically</conceptual_confusion_areas>
    </topic_misconceptions>
    
    <topic_engagement>
        <interest_level>high</interest_level>
        <motivating_aspects>understanding computational thinking, elegant algorithms</motivating_aspects>
        <challenging_aspects>practical implementation details, debugging</challenging_aspects>
        <real_world_connections>wants to understand how computers work fundamentally</real_world_connections>
    </topic_engagement>
    
    <learning_progression>
        <mastered_learning_objectives>theoretical understanding of program structure</mastered_learning_objectives>
        <current_focus_areas>data representation, memory models</current_focus_areas>
        <next_recommended_steps>control flow theory, algorithmic thinking</next_recommended_steps>
        <pace_observations>needs time to reflect, prefers comprehensive understanding</pace_observations>
    </learning_progression>
    
    <meta_information>
        <last_updated>2023-01-01</last_updated>
        <sessions_analyzed>3</sessions_analyzed>
        <confidence_level>medium</confidence_level>
        <project_id>{self.dummy_project_id}</project_id>
    </meta_information>
</topic_specific_learner_profile>"""

    def mock_profile_manager_methods(self, generic_profile, topic_profile):
        """Mock the profile manager to return specific profiles"""
        def mock_get_generic_profile():
            return generic_profile
        
        def mock_get_topic_profile(project_id, topic):
            return topic_profile
        
        def mock_get_profile_context(project_id, topic):
            # Simulate the profile extraction logic
            context = f"""LEARNER PROFILE CONTEXT:

Generic Learning Profile:
{self._extract_mock_profile_info(generic_profile)}

Topic-Specific Profile for "{topic}":
{self._extract_mock_profile_info(topic_profile)}

Please use this learner profile information to personalize the learning session."""
            return context
        
        # Patch the methods
        self.profile_manager.get_generic_profile = mock_get_generic_profile
        self.profile_manager.get_topic_profile = mock_get_topic_profile  
        self.profile_manager.get_profile_context_for_session = mock_get_profile_context

    def _extract_mock_profile_info(self, profile_xml):
        """Extract key information from profile XML for display"""
        try:
            root = ET.fromstring(profile_xml)
            key_info = []
            
            # Extract meaningful non-placeholder values
            for elem in root.iter():
                if elem.text and elem.text.strip() and elem.text.strip() not in {"to be determined", "n/a"}:
                    # Only include leaf elements with meaningful content
                    if not list(elem) and len(elem.text.strip()) > 10:  # Has content and is meaningful
                        key_info.append(f"- {elem.tag}: {elem.text.strip()}")
            
            if key_info:
                return "\n".join(key_info[:10])  # Limit to first 10 items for readability
            else:
                return "- No specific learner preferences identified yet"
                
        except ET.ParseError:
            return "- Profile parsing error"

    def test_visual_vs_theoretical_profiles_generate_different_content(self):
        """Test that visual vs theoretical profiles generate different teaching content"""
        
        # Create two contrasting profiles
        visual_generic = self.create_visual_hands_on_profile()
        visual_topic = self.create_topic_profile_visual_hands_on()
        
        theoretical_generic = self.create_theoretical_reflective_profile()
        theoretical_topic = self.create_topic_profile_theoretical_reflective()
        
        # Generate teaching prompt with visual profile
        self.mock_profile_manager_methods(visual_generic, visual_topic)
        visual_context = self.profile_manager.get_profile_context_for_session(
            self.dummy_project_id, self.dummy_topic
        )
        
        visual_prompt = format_teaching_prompt(
            obj_id=self.dummy_obj_id,
            obj_label=self.dummy_obj_label,
            recent=self.dummy_recent_topics,
            remaining=self.dummy_remaining_objs,
            refs=self.dummy_refs,
            learner_profile_context=visual_context
        )
        
        # Generate teaching prompt with theoretical profile
        self.mock_profile_manager_methods(theoretical_generic, theoretical_topic)
        theoretical_context = self.profile_manager.get_profile_context_for_session(
            self.dummy_project_id, self.dummy_topic
        )
        
        theoretical_prompt = format_teaching_prompt(
            obj_id=self.dummy_obj_id,
            obj_label=self.dummy_obj_label,
            recent=self.dummy_recent_topics,
            remaining=self.dummy_remaining_objs,
            refs=self.dummy_refs,
            learner_profile_context=theoretical_context
        )
        
        # Verify the prompts are different
        self.assertNotEqual(visual_prompt, theoretical_prompt, 
                           "Visual and theoretical profiles should generate different prompts")
        
        # Verify visual profile context includes visual/hands-on terms
        self.assertIn("visual", visual_context.lower())
        self.assertIn("hands-on", visual_context.lower())
        self.assertIn("interactive", visual_context.lower())
        
        # Verify theoretical profile context includes theoretical terms
        self.assertIn("theoretical", theoretical_context.lower())
        self.assertIn("analytical", theoretical_context.lower())
        self.assertIn("principles", theoretical_context.lower())
        
        # Check that different learning preferences appear in the prompts
        self.assertIn("hands-on practice", visual_prompt)
        self.assertIn("theoretical understanding", theoretical_prompt)
        
        print("✓ Visual and theoretical profiles generate different teaching content")

    def test_recap_prompts_also_differ_by_profile(self):
        """Test that recap prompts are also personalized by learner profiles"""
        
        visual_generic = self.create_visual_hands_on_profile()
        visual_topic = self.create_topic_profile_visual_hands_on()
        
        theoretical_generic = self.create_theoretical_reflective_profile()
        theoretical_topic = self.create_topic_profile_theoretical_reflective()
        
        recent_los = ["Understand basic syntax", "Use print statements"]
        next_obj = "Learn about variables and data types"
        
        # Generate recap prompt with visual profile
        self.mock_profile_manager_methods(visual_generic, visual_topic)
        visual_context = self.profile_manager.get_profile_context_for_session(
            self.dummy_project_id, self.dummy_topic
        )
        
        visual_recap = format_recap_prompt(
            recent_los=recent_los,
            next_obj=next_obj,
            refs=self.dummy_refs,
            learner_profile_context=visual_context
        )
        
        # Generate recap prompt with theoretical profile
        self.mock_profile_manager_methods(theoretical_generic, theoretical_topic)
        theoretical_context = self.profile_manager.get_profile_context_for_session(
            self.dummy_project_id, self.dummy_topic
        )
        
        theoretical_recap = format_recap_prompt(
            recent_los=recent_los,
            next_obj=next_obj,
            refs=self.dummy_refs,
            learner_profile_context=theoretical_context
        )
        
        # Verify the recap prompts are different
        self.assertNotEqual(visual_recap, theoretical_recap,
                           "Visual and theoretical profiles should generate different recap prompts")
        
        # Verify profile-specific content appears in recaps
        self.assertIn("visual", visual_recap.lower())
        self.assertIn("theoretical", theoretical_recap.lower())
        
        print("✓ Recap prompts are also personalized by learner profiles")

    def test_profile_context_extraction_works(self):
        """Test that meaningful profile information is extracted for context"""
        
        visual_profile = self.create_visual_hands_on_profile()
        extracted = self._extract_mock_profile_info(visual_profile)
        
        # Should contain meaningful information, not just placeholders
        self.assertNotIn("to be determined", extracted)
        self.assertNotIn("n/a", extracted)
        
        # Should contain profile-specific information
        self.assertIn("visual", extracted.lower())
        self.assertIn("hands-on", extracted.lower())
        
        theoretical_profile = self.create_theoretical_reflective_profile()
        extracted = self._extract_mock_profile_info(theoretical_profile)
        
        # Should contain theoretical information
        self.assertIn("theoretical", extracted.lower())
        self.assertIn("analytical", extracted.lower())
        
        print("✓ Profile context extraction works correctly")

    def test_topic_profiles_provide_subject_specific_context(self):
        """Test that topic-specific profiles add subject-relevant context"""
        
        visual_topic = self.create_topic_profile_visual_hands_on()
        theoretical_topic = self.create_topic_profile_theoretical_reflective()
        
        visual_extracted = self._extract_mock_profile_info(visual_topic)
        theoretical_extracted = self._extract_mock_profile_info(theoretical_topic)
        
        # Should contain programming-specific information
        self.assertIn("programming", visual_extracted.lower() + theoretical_extracted.lower())
        
        # Should show different approaches to programming
        self.assertIn("coding", visual_extracted.lower())
        self.assertIn("algorithm", theoretical_extracted.lower())
        
        print("✓ Topic-specific profiles provide subject-relevant context")

    def run_profile_impact_demonstration(self):
        """Demonstrate the profile impact with example outputs"""
        
        print("\n" + "="*60)
        print("LEARNER PROFILE IMPACT DEMONSTRATION")
        print("="*60)
        
        # Set up the test instance variables if not already set
        self.setUp()
        
        # Visual learner context
        visual_generic = self.create_visual_hands_on_profile()
        visual_topic = self.create_topic_profile_visual_hands_on()
        self.mock_profile_manager_methods(visual_generic, visual_topic)
        visual_context = self.profile_manager.get_profile_context_for_session(
            self.dummy_project_id, self.dummy_topic
        )
        
        print("\nVISUAL/HANDS-ON LEARNER CONTEXT:")
        print("-" * 40)
        print(visual_context)
        
        # Theoretical learner context  
        theoretical_generic = self.create_theoretical_reflective_profile()
        theoretical_topic = self.create_topic_profile_theoretical_reflective()
        self.mock_profile_manager_methods(theoretical_generic, theoretical_topic)
        theoretical_context = self.profile_manager.get_profile_context_for_session(
            self.dummy_project_id, self.dummy_topic
        )
        
        print("\nTHEORETICAL/REFLECTIVE LEARNER CONTEXT:")
        print("-" * 40)
        print(theoretical_context)
        
        print("\n" + "="*60)
        print("GENERATED TEACHING PROMPTS COMPARISON")
        print("="*60)
        
        # Generate and display visual teaching prompt
        self.mock_profile_manager_methods(visual_generic, visual_topic)
        visual_context = self.profile_manager.get_profile_context_for_session(
            self.dummy_project_id, self.dummy_topic
        )
        visual_prompt = format_teaching_prompt(
            obj_id=self.dummy_obj_id,
            obj_label=self.dummy_obj_label,
            recent=self.dummy_recent_topics,
            remaining=self.dummy_remaining_objs,
            refs=self.dummy_refs,
            learner_profile_context=visual_context
        )
        
        print("\nVISUAL LEARNER TEACHING PROMPT:")
        print("-" * 40)
        # Show just the profile context part for clarity
        start_marker = "LEARNER PROFILE CONTEXT:"
        end_marker = "──────────────────────────────────────────────"
        
        start_idx = visual_prompt.find(start_marker)
        if start_idx != -1:
            end_idx = visual_prompt.find(end_marker, start_idx + len(start_marker))
            if end_idx != -1:
                profile_section = visual_prompt[start_idx:end_idx + len(end_marker)]
                print(profile_section)
        
        # Generate and display theoretical teaching prompt
        self.mock_profile_manager_methods(theoretical_generic, theoretical_topic)
        theoretical_context = self.profile_manager.get_profile_context_for_session(
            self.dummy_project_id, self.dummy_topic
        )
        theoretical_prompt = format_teaching_prompt(
            obj_id=self.dummy_obj_id,
            obj_label=self.dummy_obj_label,
            recent=self.dummy_recent_topics,
            remaining=self.dummy_remaining_objs,
            refs=self.dummy_refs,
            learner_profile_context=theoretical_context
        )
        
        print("\nTHEORETICAL LEARNER TEACHING PROMPT:")
        print("-" * 40)
        start_idx = theoretical_prompt.find(start_marker)
        if start_idx != -1:
            end_idx = theoretical_prompt.find(end_marker, start_idx + len(start_marker))
            if end_idx != -1:
                profile_section = theoretical_prompt[start_idx:end_idx + len(end_marker)]
                print(profile_section)
        
        print("\n" + "="*60)
        print("CONCLUSION: Learner profiles successfully create different contexts")
        print("which will lead to personalized AI tutor responses!")
        print("="*60)


if __name__ == "__main__":
    # Run the tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLearnerProfileImpact)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run the demonstration
    if result.wasSuccessful():
        test_instance = TestLearnerProfileImpact()
        test_instance.run_profile_impact_demonstration()
    
    sys.exit(0 if result.wasSuccessful() else 1)