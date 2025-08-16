"""
Utility functions for loading and serving static assets locally.
This eliminates the need for CDN dependencies.
"""

import os
import base64
from typing import Optional

def get_project_root() -> str:
    """Get the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_static_file(file_path: str) -> Optional[str]:
    """
    Read a static file from the static directory.
    
    Args:
        file_path: Relative path from static/ directory (e.g., 'js/mathjax.js')
        
    Returns:
        File contents as string, or None if file not found
    """
    try:
        full_path = os.path.join(get_project_root(), 'static', file_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, OSError) as e:
        print(f"Warning: Could not read static file {file_path}: {e}")
        return None

def get_mathjax_script() -> str:
    """
    Get the MathJax script content for inline inclusion.
    
    Returns:
        JavaScript code for MathJax, either from local file or CDN fallback
    """
    # Try to load local MathJax
    local_mathjax = read_static_file('js/mathjax.js')
    
    if local_mathjax:
        return f"<script>{local_mathjax}</script>"
    else:
        # Fallback to CDN if local file not available
        print("Warning: Local MathJax not found, falling back to CDN")
        return '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>'

def get_jsxgraph_assets() -> tuple[str, str]:
    """
    Get JSXGraph CSS and JavaScript content for inline inclusion.
    
    Returns:
        Tuple of (css_content, js_content) as strings
    """
    # Try to load local JSXGraph files
    local_css = read_static_file('css/jsxgraph.css')
    local_js = read_static_file('js/jsxgraph.js')
    
    if local_css and local_js:
        css_content = f"<style>{local_css}</style>"
        js_content = f"<script>{local_js}</script>"
        return css_content, js_content
    else:
        # Fallback to CDN if local files not available
        print("Warning: Local JSXGraph files not found, falling back to CDN")
        css_content = '<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/jsxgraph/distrib/jsxgraph.css" />'
        js_content = '<script type="text/javascript" charset="UTF-8" src="https://cdn.jsdelivr.net/npm/jsxgraph/distrib/jsxgraphcore.js"></script>'
        return css_content, js_content