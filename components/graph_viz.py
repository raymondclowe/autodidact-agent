"""
Graph visualization component for Autodidact
Creates Graphviz diagrams for the knowledge graph
"""

import graphviz
import re
from typing import Dict, List


def calculate_color_gradient(mastery: float) -> str:
    """
    Linear interpolation from white to green based on mastery 0-1
    White: #ffffff (255, 255, 255)
    Green: #26c176 (38, 193, 118)
    """
    # Ensure mastery is in [0, 1]
    mastery = max(0.0, min(1.0, mastery))
    
    r = int(255 - (255 - 38) * mastery)
    g = int(255 - (255 - 193) * mastery)
    b = int(255 - (255 - 118) * mastery)
    
    return f'#{r:02x}{g:02x}{b:02x}'


def create_knowledge_graph(
    nodes: List[Dict], 
    edges: List[Dict], 
) -> graphviz.Digraph:
    """
    Create a Graphviz diagram for the knowledge graph
    
    Args:
        nodes: List of node dictionaries with 'id', 'label', etc.
        edges: List of edge dictionaries with 'source', 'target', etc.
    
    Returns:
        Graphviz Digraph object
    """
    # Create a new directed graph with Dagre layout
    dot = graphviz.Digraph(
        comment='Knowledge Graph',
        engine='dot'  # Use dot engine for hierarchical layout
    )
    
    # Configure graph for left-to-right layout
    dot.attr(rankdir='LR')  # Left to Right layout
    
    # Configure graph attributes for better layout
    dot.attr('graph', 
             ranksep='1.5',      # Increase separation between ranks
             nodesep='0.5',      # Node separation
             fontname='Arial',
             fontsize='16',
             bgcolor='transparent'
    )
    
    # Configure default node attributes
    dot.attr('node', 
             shape='box',
             style='rounded,filled',
             fontname='Arial',
             fontsize='14',
             margin='0.2',
             penwidth='1.5'
    )
    
    # Configure default edge attributes
    dot.attr('edge',
             fontname='Arial',
             fontsize='12',
             arrowsize='0.8'
    )
    
    # Add nodes
    for node in nodes:
        # print(f"[graph_viz.py] Node: {node}")
        original_id = node['original_id']
        label = node['label']
        mastery = node['mastery']
        fillcolor = calculate_color_gradient(mastery)
        
        # Determine font color based on mastery (for contrast)
        fontcolor = 'black' if mastery < 0.5 else 'black'
        
        # # Add study time if available
        # if 'study_time_minutes' in node:
        #     label += f"\\n({node['study_time_minutes']} min)"
        
        # Add mastery percentage
        mastery_pct = int(mastery * 100)
        if mastery_pct > 0:
            label += f"\\n{mastery_pct}% mastered"

        tooltip_val = ""
        if node.get('learning_objectives'):
            tooltip_val += f"Learning Objectives:"
            for idx, lo in enumerate(node['learning_objectives']):
                # replace all [markdown links](http://...) with empty string
                # Remove markdown links - keep the text, remove the URL
                # print(f"[graph_viz.py] Learning Objective: {lo['id']} description: {lo['description']}")
                desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', lo['description']).replace("\n", " ")
                mastery = lo['mastery']
                mastery_pct = int(mastery * 100)
                tooltip_val += f"\n{idx + 1}. {desc} ({mastery_pct}% mastered)"

        # Create node with styling
        dot.node(
            original_id,
            label,
            fillcolor=fillcolor,
            fontcolor=fontcolor,
            tooltip=tooltip_val
        )
    
    # Add edges
    for edge in edges:
        source = edge['source']
        target = edge['target']
        
        # Style based on confidence
        confidence = edge.get('confidence', 1.0)
        if confidence >= 0.8:
            style = 'solid'
            penwidth = '1.5'
        elif confidence >= 0.5:
            style = 'solid'
            penwidth = '1.0'
        else:
            style = 'dashed'
            penwidth = '1.0'
        
        # Add edge with optional label
        rationale = edge.get('rationale', '')
        if rationale and len(rationale) < 30:  # Only show short rationales
            dot.edge(source, target, 
                    label=rationale,
                    style=style,
                    penwidth=penwidth,
                    color='#666666'
            )
        else:
            dot.edge(source, target,
                    style=style,
                    penwidth=penwidth,
                    color='#666666'
            )
    
    return dot


def render_graph_to_file(
    graph: graphviz.Digraph, 
    filename: str,
    format: str = 'png'
):
    """
    Render graph to a file
    
    Args:
        graph: Graphviz Digraph object
        filename: Output filename (without extension)
        format: Output format (png, pdf, svg, etc.)
    """
    if filename and graph:
        dot.render(filename, format=format, cleanup=True)
    
    return dot


def format_report_with_footnotes(report_md: str, footnotes: Dict) -> str:
    """
    Format markdown report with clickable footnotes
    
    Args:
        report_md: Raw markdown report with [^n] citations
        footnotes: Dict mapping footnote numbers to {"title": ..., "url": ...}
    
    Returns:
        Formatted markdown with footnote section
    """
    # First, ensure footnotes keys are strings
    str_footnotes = {str(k): v for k, v in footnotes.items()}
    
    # Add footnotes section at the end if not already present
    if "## References" not in report_md and "## Footnotes" not in report_md:
        report_md += "\n\n---\n\n## References\n\n"
        
        # Sort footnotes by number
        sorted_footnotes = sorted(str_footnotes.items(), key=lambda x: int(x[0]))
        
        for num, ref in sorted_footnotes:
            title = ref.get('title', 'Untitled')
            url = ref.get('url', '#')
            
            # Format as markdown footnote
            if url and url != '#':
                report_md += f"[^{num}]: [{title}]({url})\n\n"
            else:
                report_md += f"[^{num}]: {title}\n\n"
    
    return report_md 