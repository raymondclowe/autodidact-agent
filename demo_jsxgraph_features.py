#!/usr/bin/env python3
"""
Demo script to showcase JSXGraph integration features for issue #82
"""

import streamlit as st
from components.jsxgraph_utils import (
    get_available_templates, 
    create_template_diagram,
    get_jsxgraph_header,
    create_jsxgraph_container,
    create_function_plot
)
from components.speech_controls import create_speech_enabled_markdown
from utils.providers import get_model_capability_warning, get_model_for_task

def main():
    st.set_page_config(
        page_title="JSXGraph Demo - Autodidact",
        page_icon="📐",
        layout="wide"
    )
    
    st.title("📐 JSXGraph Integration Demo")
    st.markdown("*Demonstrating interactive diagrams for STEM education*")
    
    # Show model capability warning
    st.markdown("## 🔧 Model Configuration Status")
    try:
        current_model = get_model_for_task('chat')
        st.info(f"**Current model**: {current_model}")
        
        warning = get_model_capability_warning(current_model)
        if warning:
            st.warning(warning)
        else:
            st.success("✅ Current model supports high-quality diagram generation!")
    except Exception as e:
        st.error(f"Could not check model: {e}")
    
    # Demo 1: Available Templates
    st.markdown("## 📚 Available Templates")
    templates = get_available_templates()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Template Library:**")
        for name, desc in templates.items():
            st.markdown(f"- **{name}**: {desc}")
    
    with col2:
        selected_template = st.selectbox(
            "Select a template to preview:",
            options=list(templates.keys()),
            format_func=lambda x: f"{x} - {templates[x]}"
        )
    
    # Demo 2: Template Preview
    if selected_template:
        st.markdown(f"### 🎯 Preview: {selected_template}")
        try:
            diagram_html = create_template_diagram(selected_template, f"demo_{selected_template}")
            st.components.v1.html(diagram_html, height=400, scrolling=True)
        except Exception as e:
            st.error(f"Error creating diagram: {e}")
    
    # Demo 3: JSXGraph Tag Processing
    st.markdown("## 📝 JSXGraph Tag Processing Demo")
    st.markdown("This shows how JSXGraph tags work in lesson content:")
    
    sample_lesson_text = """
    Welcome to our geometry lesson! Let's explore the **Pythagorean theorem**.

    The Pythagorean theorem states that in a right triangle, the square of the hypotenuse 
    (the side opposite the right angle) is equal to the sum of the squares of the other two sides.

    <jsxgraph>pythagorean_theorem:lesson_demo</jsxgraph>

    As you can see in the interactive diagram above, we have:
    - Side **a** (vertical)
    - Side **b** (horizontal) 
    - Side **c** (hypotenuse)

    The relationship is: \\[a^2 + b^2 = c^2\\]

    Now let's look at the unit circle:

    <jsxgraph>unit_circle:circle_demo</jsxgraph>

    The unit circle has radius 1 and is centered at the origin (0,0).
    """
    
    st.markdown("**Raw lesson content with JSXGraph tags:**")
    with st.expander("View raw text", expanded=False):
        st.code(sample_lesson_text, language="markdown")
    
    st.markdown("**Rendered lesson content:**")
    create_speech_enabled_markdown(sample_lesson_text, add_button=True)
    
    # Demo 4: Manual Diagram Creation
    st.markdown("## 🎨 Custom Diagram Creation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Function Plotter:**")
        func_expr = st.text_input("Function expression (JavaScript)", value="x*x", help="Examples: x*x, Math.sin(x), Math.cos(x)")
        x_min = st.number_input("X min", value=-5.0)
        x_max = st.number_input("X max", value=5.0)
        
        if st.button("Generate Function Plot"):
            try:
                plot_html = create_function_plot("custom_plot", func_expr, x_min, x_max)
                st.components.v1.html(plot_html, height=400, scrolling=True)
            except Exception as e:
                st.error(f"Error creating plot: {e}")
    
    with col2:
        st.markdown("**Benefits of JSXGraph Integration:**")
        st.markdown("""
        - ✅ **Interactive**: Students can manipulate diagrams
        - ✅ **Educational**: Perfect for STEM subjects
        - ✅ **No Dependencies**: Uses CDN, no local files
        - ✅ **Mobile Friendly**: Works on all devices
        - ✅ **Fast**: Lightweight and responsive
        - ✅ **Accessible**: Works with screen readers
        """)
    
    # Demo 5: Integration Status
    st.markdown("## ✅ Integration Status")
    
    status_items = [
        ("Model Updates", "✅ Updated to GPT-5 and Claude Opus 4.1", True),
        ("Model Warnings", "✅ Added capability warnings for lower models", True),
        ("JSXGraph Library", "✅ CDN integration with latest version", True),
        ("Template System", "✅ 4 predefined templates for common diagrams", True),
        ("Tag Processing", "✅ Automatic parsing of <jsxgraph> tags", True),
        ("Lesson Integration", "✅ Works with existing speech and markdown system", True),
        ("Error Handling", "✅ Graceful degradation for diagram errors", True)
    ]
    
    cols = st.columns(2)
    for i, (item, description, status) in enumerate(status_items):
        with cols[i % 2]:
            if status:
                st.success(f"**{item}**: {description}")
            else:
                st.error(f"**{item}**: {description}")
    
    st.markdown("---")
    st.markdown("**🎉 JSXGraph integration is ready for use in lessons!**")

if __name__ == "__main__":
    main()