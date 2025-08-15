#!/usr/bin/env python3
"""
Test script to reproduce the math formula rendering issue.
"""

import streamlit as st
from components.speech_controls import create_speech_enabled_markdown

# Add MathJax support for mathematical content rendering (from app.py)
st.markdown("""
<script>
window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
  }
};
</script>
<script async src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script async id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
""", unsafe_allow_html=True)

def test_math_rendering():
    """Test math formula rendering with MathJax."""
    
    st.title("Math Formula Rendering Test")
    
    st.subheader("1. Raw LaTeX Display Math")
    st.markdown(r"""
    Raw LaTeX formula:
    \[Total\ Magnification = Eyepiece\ Magnification \times Objective\ Magnification\]
    """)
    
    st.subheader("2. Using speech_enabled_markdown function")
    test_content = r"""
# 📐 **Microscope Magnification Formula**

Great question! The total magnification is actually quite simple:

## **The Formula:**

\[Total\ Magnification = Eyepiece\ Magnification \times Objective\ Magnification\]

## 📊 **Example:**
If your eyepiece is **10×** and you're using a **40×** objective lens:

\[Total\ Magnification = 10 \times 40 = 400×\]

This means the specimen appears 400 times larger than its actual size!

## Inline Math Test:
When \(a \ne 0\), the equation \(ax^2 + bx + c = 0\) has solutions.
"""
    
    create_speech_enabled_markdown(test_content, add_button=True)
    
    st.subheader("3. Direct Streamlit Markdown")
    st.markdown(test_content)

if __name__ == "__main__":
    test_math_rendering()