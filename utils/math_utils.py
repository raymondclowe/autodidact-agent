"""
Utility functions for math rendering setup and support.
"""

import streamlit as st
from components.simple_math_renderer import MATH_RENDERER_JS
from utils.static_assets import get_mathjax_script

def inject_math_rendering_support():
    """
    Injects MathJax and the fallback renderer into the Streamlit app.
    This centralizes the math rendering setup to avoid duplication across files.
    Uses local MathJax files when available, with CDN fallback.
    """
    # Get MathJax script (local or CDN fallback)
    mathjax_script = get_mathjax_script()
    
    math_setup_html = f"""
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
          window.mathJaxReady = true;
        }}
      }}
    }};
    </script>
    
    {mathjax_script}
    
    {MATH_RENDERER_JS}
    """
    
    st.components.v1.html(math_setup_html, height=50, scrolling=False)