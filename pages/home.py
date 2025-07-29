"""
Homepage for Autodidact
Marketing and introduction page
"""

import streamlit as st
from components.speech_controls import create_global_speech_component
from utils.speech_utils import initialize_speech_state

# Sidebar is shown globally in app.py

# Initialize speech functionality
initialize_speech_state()
create_global_speech_component()

# Page header
st.markdown("""
# 🧠 Autodidact

### Transform Any Topic into a Personalized Learning Journey
""")

# Hero section
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; padding: 3rem 0;'>
        <h2>Learn Anything, Master Everything</h2>
        <p style='font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
            AI-powered personalized education that adapts to your learning style
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA button
    if st.button("🚀 Start Learning Journey", type="primary", use_container_width=True, key="hero_cta"):
        st.switch_page("pages/new_project.py")

# Features section
st.markdown("---")
st.markdown("## How Autodidact Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🔬 Deep Research
    
    Our AI conducts comprehensive research on your chosen topic, analyzing hundreds of sources to create the perfect curriculum tailored to your goals and available time.
    
    **What you get:**
    - Curated learning resources
    - Structured knowledge graph
    - Clear prerequisites mapping
    """)

with col2:
    st.markdown("""
    ### 📊 Visual Progress
    
    See your learning journey as an interactive knowledge graph. Track your progress as concepts turn from white to green, showing your mastery at a glance.
    
    **Features:**
    - Visual prerequisite tracking
    - Real-time progress updates
    - Completion milestones
    """)

with col3:
    st.markdown("""
    ### 👨‍🏫 AI Tutoring
    
    Learn through conversation with an AI tutor that understands your progress. Each 30-minute lesson adapts to your understanding level.
    
    **Experience:**
    - Personalized explanations
    - Interactive Q&A
    - Instant feedback
    """)

# Process section
st.markdown("---")
st.markdown("## Your Learning Journey")

process_col1, process_col2 = st.columns([2, 3])

with process_col1:
    st.markdown("""
    ### Simple 4-Step Process
    
    1. **Choose Your Topic**  
       Tell us what you want to learn - from quantum physics to French cooking
    
    2. **AI Research Phase**  
       Our AI analyzes the topic and creates your personalized curriculum
    
    3. **Interactive Learning**  
       Engage with AI tutors in focused 30-minute lessons
    
    4. **Track Progress**  
       Watch your knowledge graph light up as you master each concept
    """)

with process_col2:
    # Placeholder for demo image/animation
    st.info("""
    **🎯 Example Topics Our Learners Love:**
    
    • Foundations of Machine Learning  
    • Modern Web Development with React  
    • Blockchain and Cryptocurrency  
    • Neuroscience Fundamentals  
    • Digital Marketing Strategy  
    • Philosophy of Mind  
    • Quantum Computing Basics  
    • Behavioral Economics
    """)

# Benefits section
st.markdown("---")
st.markdown("## Why Choose Autodidact?")

benefit_col1, benefit_col2, benefit_col3, benefit_col4 = st.columns(4)

with benefit_col1:
    st.markdown("""
    ### 🎯 Personalized
    Every curriculum is unique, tailored to your goals and time constraints
    """)

with benefit_col2:
    st.markdown("""
    ### ⚡ Efficient
    No more wandering through random tutorials - follow the optimal path
    """)

with benefit_col3:
    st.markdown("""
    ### 🔒 Private
    Everything runs locally on your computer - your data stays yours
    """)

with benefit_col4:
    st.markdown("""
    ### 💰 Affordable
    Pay only for OpenAI API usage - typically $0.05 per lesson
    """)

# Final CTA
st.markdown("---")
final_col1, final_col2, final_col3 = st.columns([1, 2, 1])
with final_col2:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h3>Ready to Transform Your Learning?</h3>
        <p style='color: #666; margin-bottom: 1rem;'>
            Join thousands of autodidacts mastering new skills with AI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Get Started Now", type="primary", use_container_width=True, key="final_cta"):
        st.switch_page("pages/new_project.py")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.9rem; padding: 2rem 0;'>
    <p>Autodidact is open source and runs entirely on your local machine.</p>
    <p>Your learning data never leaves your computer.</p>
</div>
""", unsafe_allow_html=True) 