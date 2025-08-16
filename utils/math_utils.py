"""
Utility functions for math rendering setup and support.
"""

import streamlit as st
from components.simple_math_renderer import MATH_RENDERER_JS

def inject_math_rendering_support():
    """
    Injects MathJax and the fallback renderer into the Streamlit app.
    This centralizes the math rendering setup to avoid duplication across files.
    """
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
      }};
      document.head.appendChild(script);
    }})();
    </script>
    
    {MATH_RENDERER_JS}
    """
    
    st.components.v1.html(math_setup_html, height=50, scrolling=False)