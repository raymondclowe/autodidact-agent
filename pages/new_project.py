"""
Create New Project page
Handles topic input, clarification, and project creation
"""

import streamlit as st
from backend.jobs import clarify_topic, rewrite_topic, start_deep_research_job
from backend.db import create_project_with_job
from utils.config import DEEP_RESEARCH_MODEL

# Initialize view state
if 'new_project_view' not in st.session_state:
    st.session_state.new_project_view = 'input'  # 'input', 'clarification', 'confirmation'

# Page header
st.markdown("# 📚 New Learning Course")

# Back button (always visible)
# if st.button("← Back", key="back_button"):
#     # Clear all state
#     for key in ['new_project_view', 'clarification_questions', 'clarification_answers', 'init_topic', 
#                 'init_hours', 'final_topic', 'final_hours']:
#         if key in st.session_state:
#             del st.session_state[key]
#     st.switch_page("pages/home.py")

# st.markdown("---")

# Show different views based on state
if st.session_state.new_project_view == 'input':
    # Main content in centered column
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Topic input
        st.markdown("#### Topic you want to learn")
        topic = st.text_input(
            "What would you like to learn?",
            placeholder="e.g., Foundations of Statistical Learning, Bitcoin consensus mechanisms",
            help="Be as specific as you like - we'll ask clarifying questions if needed",
            key="new_topic",
            value=st.session_state.init_topic if 'init_topic' in st.session_state else ""
        )
        
        # Hours input with explanation
        st.markdown("#### Study Time Commitment")
        hours = st.number_input(
            "How many hours can you dedicate to this topic?",
            min_value=4,
            max_value=40,
            value=st.session_state.init_hours if 'init_hours' in st.session_state else 20,
            help="This helps us plan the depth and pacing of your curriculum. Each topic will be designed for ~30 minute sessions. Min is 4 because lower than that you could probably just chat with an LLM. Max is 40 because AI-syllabii would probably not cut it for very large learning projects.",
            key="new_hours"
        )
        
        # Info about what happens next
        with st.expander("ℹ️ What happens next?", expanded=False):
            st.markdown("""
            1. **Clarification Questions** - We'll ask a few questions to better understand your goals
            2. **Topic Refinement** - Your answers help us create a focused learning plan
            3. **Deep Research** - Our AI researches the topic (takes 10-30 minutes)
            4. **Personalized Curriculum** - You get a complete learning path with interactive tutoring
            """)

        with st.expander("💡 Need inspiration? Try these example topics", expanded=False):
            col1, col2 = st.columns(2)    
            with col1:
                st.markdown("""
                **Technology & Programming:**
                - Foundations of Statistical Learning
                - React Hooks and State Management  
                - Bitcoin and Ethereum Internals
                - Rust Programming Language
                - Kubernetes for DevOps
                
                **Science & Mathematics:**
                - Introduction to Neuroscience
                - Linear Algebra for ML
                - Climate Change Science
                - Molecular Biology Essentials
                """)
            
            with col2:
                st.markdown("""
                **Business & Finance:**
                - Venture Capital Fundamentals
                - Digital Marketing Strategy
                - Financial Derivatives
                - Supply Chain Management
                
                **Arts & Humanities:**
                - Modern World History 1900-1950
                - Philosophy of Mind
                - Cultural Anthropology
                - Music Theory Basics
                """)

        
        # Continue button
        if st.button("Continue →", type="primary", disabled=not topic, use_container_width=True):
            if topic:
                # Get clarification questions
                with st.spinner("Preparing clarification questions..."):
                    try:
                        questions = clarify_topic(topic, hours)
                        st.session_state.init_topic = topic
                        st.session_state.init_hours = hours
                        st.session_state.clarification_questions = questions
                        st.session_state.new_project_view = 'clarification'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        print(f"[New Project] Error getting clarification: {e}")

elif st.session_state.new_project_view == 'clarification':
    # Clarification questions view
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("### Clarification Questions")
        st.markdown(f"I'd like to understand more about **\"{st.session_state.init_topic}\"** to create the best learning plan for you. ({st.session_state.init_hours} hours)")
        st.markdown("*Please answer the questions below. Feel free to be as detailed as you'd like, or leave questions blank if they don't apply.*")
        st.markdown("---")
        
        # Show numbered questions
        for i, question in enumerate(st.session_state.clarification_questions, 1):
            st.markdown(f"**{i}.** {question}")
        
        # Single text area for all answers
        user_answers = st.text_area(
            "Your answers:",
            height=200,
            placeholder="Type your answers here. You can answer all questions together or number your responses (1., 2., etc.)",
            key="clarification_answers_input",
            value=st.session_state.clarification_answers if 'clarification_answers' in st.session_state else ""
        )
        
        # Action buttons
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("✅ Submit Answers", type="primary", use_container_width=True):
                # Process answers
                with st.spinner("Processing your answers..."):
                    try:
                        original_topic = st.session_state.init_topic
                        questions = st.session_state.clarification_questions
                        hours = st.session_state.init_hours
                        
                        # Handle empty answers
                        if not user_answers.strip():
                            rewritten_topic = original_topic
                            print("[New Project] No answers provided, using original topic")
                        else:
                            rewritten_topic = rewrite_topic(original_topic, questions, user_answers)
                            print(f"[New Project] Topic rewritten: '{rewritten_topic}'")
                        
                        # Store for confirmation view
                        st.session_state.clarification_answers = user_answers
                        st.session_state.final_topic = rewritten_topic
                        st.session_state.final_hours = hours
                        st.session_state.new_project_view = 'confirmation'
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error processing answers: {str(e)}")
                        print(f"[New Project] Error rewriting topic: {e}")
        
        with col_b:
            if st.button("⬅ Back to Topic", use_container_width=True):
                st.session_state.new_project_view = 'input'
                st.rerun()

elif st.session_state.new_project_view == 'confirmation':
    # Confirmation view
    st.markdown("### Your personalized learning course is ready!")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        final_topic = st.session_state.final_topic

        st.markdown("#### Refined topic prompt")
        possibly_changed_final_topic = st.text_area(
            "What would you like to learn?",
            help="User's topic, supplemented with clarifying QAs. Change this to change the input to our research stage",
            key="possibly_changed_final_topic",
            value=final_topic if final_topic else "",
            height=170 # 5 lines of text
        )
        
        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Study time:** {st.session_state.final_hours} hours")
        with col_b:
            st.markdown(f"**Lessons:** ~{st.session_state.final_hours * 2} lessons of 30 minutes each")
        
        st.markdown("---")
        
        st.markdown("### Ready to start?")
        st.markdown("Clicking 'Start Deep Research' will begin creating your personalized curriculum. This process takes 10-30 minutes, but you can navigate to other courses while it completes.")
        
        # Action buttons
        col_1, col_2 = st.columns(2)
        with col_1:
            if st.button("🚀 Start Deep Research", type="primary", use_container_width=True):
                try:
                    st.session_state.final_topic = possibly_changed_final_topic
                    model_to_use = DEEP_RESEARCH_MODEL
                    # Start deep research job
                    with st.spinner("Starting deep research..."):
                        job_id = start_deep_research_job(
                            st.session_state.final_topic, 
                            st.session_state.final_hours
                        )
                        print(f"[New Project] Started deep research job: {job_id}")
                    
                    # Create project with job_id
                    project_id = create_project_with_job(
                        topic=st.session_state.final_topic,
                        name=st.session_state.init_topic,  # Use initial topic as name
                        job_id=job_id,
                        model_used=model_to_use,
                        status='processing',
                        hours=st.session_state.final_hours
                    )
                    print(f"[New Project] Created project: {project_id}")
                    
                    # Clear all state
                    for key in ['new_project_view', 'init_topic', 'init_hours',
                                'clarification_questions', 'clarification_answers',
                                'final_topic', 'final_hours']:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    # Navigate to project page
                    st.session_state.selected_project_id = project_id
                    st.switch_page("pages/project_detail.py")
                    
                except Exception as e:
                    st.error(f"Failed to start research: {str(e)}")
                    print(f"[New Project] Error starting research: {e}")
        
        with col_2:
            if st.button("⬅ Revise Answers", use_container_width=True):
                st.session_state.new_project_view = 'clarification'
                st.rerun()