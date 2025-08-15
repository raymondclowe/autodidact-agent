#!/usr/bin/env python3
"""
Test script to reproduce the math formula rendering issue.
"""

import streamlit as st
from components.speech_controls import create_speech_enabled_markdown

# Add MathJax support for mathematical content rendering (from app.py)
from components.simple_math_renderer import MATH_RENDERER_JS

st.components.v1.html(f"""
<script>
window.MathJax = {{
  tex: {{
    inlineMath: [['\\\\(', '\\\\)']],
    displayMath: [['\\\\[', '\\\\]']],
    processEscapes: true,
    processEnvironments: true
  }},
  options: {{
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
  }},
  startup: {{
    ready: function () {{
      MathJax.startup.defaultReady();
      console.log('MathJax is ready and initialized');
      // Make MathJax available globally for reprocessing
      window.mathJaxReady = true;
    }}
  }}
}};

// Load MathJax with fallback
(function() {{
  var script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
  script.async = true;
  script.onload = function() {{
    console.log('MathJax script loaded successfully');
  }};
  script.onerror = function() {{
    console.log('MathJax CDN failed, using fallback renderer');
    // MathJax failed to load, SimpleMathRenderer will be used as fallback
  }};
  document.head.appendChild(script);
}})();
</script>

{MATH_RENDERER_JS}
""", height=50, scrolling=False)

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