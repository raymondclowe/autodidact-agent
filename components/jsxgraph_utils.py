"""
JSXGraph utilities for creating interactive mathematical diagrams in lessons.
Provides helper functions and templates for common STEM visualizations.

IMPORTANT: This module handles the container ID consistency fix for Issue #101.
Custom JSXGraph code from AI tutors is automatically processed to ensure that:
- HTML container IDs match JavaScript board initialization IDs  
- No duplicate board initializations occur
- Board variable references are properly handled

AI tutors can generate JSXGraph code with or without initBoard calls, and the
system will ensure everything works correctly.
"""

def get_jsxgraph_header() -> str:
    """
    Get the required HTML header for JSXGraph including CSS and JavaScript.
    
    Returns:
        HTML string with JSXGraph CDN includes
    """
    return """
<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/jsxgraph/distrib/jsxgraph.css" />
<script type="text/javascript" charset="UTF-8" src="https://cdn.jsdelivr.net/npm/jsxgraph/distrib/jsxgraphcore.js"></script>
"""


def create_jsxgraph_container(graph_id: str, width: int = 400, height: int = 300) -> str:
    """
    Create a JSXGraph container div with proper styling.
    
    Args:
        graph_id: Unique identifier for the graph
        width: Width in pixels
        height: Height in pixels
        
    Returns:
        HTML div element for JSXGraph
    """
    return f'<div id="{graph_id}" style="width: {width}px; height: {height}px; margin: 10px auto; border: 1px solid #ccc;"></div>'


def create_basic_coordinate_system(graph_id: str, x_min: float = -5, x_max: float = 5, 
                                 y_min: float = -5, y_max: float = 5) -> str:
    """
    Create basic coordinate system JSXGraph code.
    
    Args:
        graph_id: The container div ID
        x_min, x_max, y_min, y_max: Coordinate bounds
        
    Returns:
        JavaScript code to initialize basic coordinate system
    """
    return f"""
<script>
var board_{graph_id} = JXG.JSXGraph.initBoard('{graph_id}', {{
    boundingbox: [{x_min}, {y_max}, {x_max}, {y_min}],
    axis: true,
    grid: false,
    showNavigation: true,
    showZoom: true
}});
</script>
"""


def create_function_plot(graph_id: str, function_expr: str, x_min: float = -5, x_max: float = 5,
                        color: str = "blue", stroke_width: int = 2) -> str:
    """
    Create a function plot JSXGraph.
    
    Args:
        graph_id: The container div ID
        function_expr: JavaScript function expression (e.g., "x*x", "Math.sin(x)")
        x_min, x_max: X-axis bounds
        color: Line color
        stroke_width: Line thickness
        
    Returns:
        Complete JSXGraph HTML for function plotting
    """
    container = create_jsxgraph_container(graph_id)
    coordinate_system = create_basic_coordinate_system(graph_id, x_min, x_max)
    
    plot_code = f"""
<script>
var f_{graph_id} = board_{graph_id}.create('functiongraph', [
    function(x) {{ return {function_expr}; }},
    {x_min}, {x_max}
], {{
    strokeColor: '{color}',
    strokeWidth: {stroke_width}
}});
</script>
"""
    
    return container + coordinate_system + plot_code


def create_triangle_diagram(graph_id: str, point_a: tuple = (0, 3), point_b: tuple = (0, 0), 
                          point_c: tuple = (4, 0), labels: tuple = ("A", "B", "C")) -> str:
    """
    Create an interactive triangle diagram with labels.
    
    Args:
        graph_id: The container div ID
        point_a, point_b, point_c: Coordinate tuples for triangle vertices
        labels: Labels for the vertices
        
    Returns:
        Complete JSXGraph HTML for triangle diagram
    """
    container = create_jsxgraph_container(graph_id)
    
    diagram_code = f"""
<script>
var board_{graph_id} = JXG.JSXGraph.initBoard('{graph_id}', {{
    boundingbox: [-1, 5, 6, -1],
    axis: false,
    grid: false,
    showNavigation: false
}});

var A_{graph_id} = board_{graph_id}.create('point', [{point_a[0]}, {point_a[1]}], {{name:'{labels[0]}', size:3}});
var B_{graph_id} = board_{graph_id}.create('point', [{point_b[0]}, {point_b[1]}], {{name:'{labels[1]}', size:3}});  
var C_{graph_id} = board_{graph_id}.create('point', [{point_c[0]}, {point_c[1]}], {{name:'{labels[2]}', size:3}});

var ab_{graph_id} = board_{graph_id}.create('segment', [A_{graph_id}, B_{graph_id}], {{strokeWidth:2}});
var bc_{graph_id} = board_{graph_id}.create('segment', [B_{graph_id}, C_{graph_id}], {{strokeWidth:2}});
var ca_{graph_id} = board_{graph_id}.create('segment', [C_{graph_id}, A_{graph_id}], {{strokeWidth:2}});

// Add side labels
board_{graph_id}.create('text', [{(point_a[0] + point_b[0])/2 - 0.3}, {(point_a[1] + point_b[1])/2}, 'a'], {{fontSize:16}});
board_{graph_id}.create('text', [{(point_b[0] + point_c[0])/2}, {(point_b[1] + point_c[1])/2 - 0.3}, 'b'], {{fontSize:16}});
board_{graph_id}.create('text', [{(point_c[0] + point_a[0])/2 + 0.2}, {(point_c[1] + point_a[1])/2 + 0.2}, 'c'], {{fontSize:16}});
</script>
"""
    
    return container + diagram_code


def create_circle_diagram(graph_id: str, center: tuple = (0, 0), radius: float = 2,
                         show_center: bool = True, show_radius: bool = True) -> str:
    """
    Create an interactive circle diagram.
    
    Args:
        graph_id: The container div ID
        center: Center point coordinates
        radius: Circle radius
        show_center: Whether to show center point
        show_radius: Whether to show radius line
        
    Returns:
        Complete JSXGraph HTML for circle diagram
    """
    container = create_jsxgraph_container(graph_id)
    
    diagram_code = f"""
<script>
var board_{graph_id} = JXG.JSXGraph.initBoard('{graph_id}', {{
    boundingbox: [-4, 4, 4, -4],
    axis: true,
    grid: false,
    showNavigation: false
}});

var center_{graph_id} = board_{graph_id}.create('point', [{center[0]}, {center[1]}], {{
    name:'O', 
    size:3,
    visible: {str(show_center).lower()}
}});

var radius_point_{graph_id} = board_{graph_id}.create('point', [{center[0] + radius}, {center[1]}], {{
    name:'P',
    size:3,
    visible: {str(show_radius).lower()}
}});

var circle_{graph_id} = board_{graph_id}.create('circle', [center_{graph_id}, radius_point_{graph_id}], {{
    strokeWidth:2,
    strokeColor: 'blue'
}});

{f"""
var radius_line_{graph_id} = board_{graph_id}.create('segment', [center_{graph_id}, radius_point_{graph_id}], {{
    strokeWidth:1,
    strokeColor: 'red',
    dash: 2
}});
board_{graph_id}.create('text', [{center[0] + radius/2}, {center[1] + 0.3}, 'r'], {{fontSize:16}});
""" if show_radius else ""}
</script>
"""
    
    return container + diagram_code


def wrap_jsxgraph_html(content: str) -> str:
    """
    Wrap JSXGraph content with proper HTML structure and CDN includes.
    
    Args:
        content: JSXGraph HTML content (containers + scripts)
        
    Returns:
        Complete HTML with headers and content
    """
    return f"""
<div>
{get_jsxgraph_header()}
{content}
</div>
"""


# Template examples - kept minimal as requested
JSXGRAPH_TEMPLATES = {
    "triangle": {
        "description": "Interactive right triangle with draggable vertices",
        "code": lambda graph_id: create_triangle_diagram(graph_id, (0, 3), (0, 0), (4, 0))
    }
}


def get_available_templates() -> dict:
    """
    Get list of available JSXGraph templates.
    
    Returns:
        Dictionary of template names and descriptions
    """
    return {name: template["description"] for name, template in JSXGRAPH_TEMPLATES.items()}


def _process_custom_jsxgraph_code(graph_id: str, jsxgraph_code: str) -> str:
    """
    Process custom JSXGraph code to ensure proper board and container ID handling.
    
    Args:
        graph_id: The expected graph/container ID
        jsxgraph_code: Raw JSXGraph JavaScript code
        
    Returns:
        Processed JavaScript code with normalized board references and container IDs
    """
    import re
    
    processed_code = jsxgraph_code
    
    # First, normalize any initBoard calls to use the correct container ID
    # Pattern: JXG.JSXGraph.initBoard('any_id', {
    initboard_pattern = r"JXG\.JSXGraph\.initBoard\(\s*['\"]([^'\"]*)['\"]"
    
    def replace_initboard_id(match):
        # Replace the container ID in initBoard calls with the correct graph_id
        return f"JXG.JSXGraph.initBoard('{graph_id}'"
    
    processed_code = re.sub(initboard_pattern, replace_initboard_id, processed_code)
    
    # Now handle board variable references
    # Replace 'board' with 'board_{graph_id}' but be careful about existing board_{graph_id} references
    
    # First, protect existing board_{graph_id} references by temporarily replacing them
    temp_placeholder = f"TEMP_BOARD_REF_{graph_id}_PLACEHOLDER"
    processed_code = processed_code.replace(f'board_{graph_id}', temp_placeholder)
    
    # Replace standalone 'board' references with 'board_{graph_id}'
    # Use word boundaries to avoid replacing parts of other words
    board_pattern = r'\bboard\b'
    processed_code = re.sub(board_pattern, f'board_{graph_id}', processed_code)
    
    # Restore the protected board_{graph_id} references
    processed_code = processed_code.replace(temp_placeholder, f'board_{graph_id}')
    
    # Fix any over-replacement issues (like board_{graph_id}_ -> board_)
    processed_code = processed_code.replace(f'board_{graph_id}_', 'board_')
    
    return processed_code


def create_custom_diagram(graph_id: str, jsxgraph_code: str) -> str:
    """
    Create a custom JSXGraph diagram from raw JavaScript code.
    
    Args:
        graph_id: Unique ID for the graph
        jsxgraph_code: Raw JSXGraph JavaScript code
        
    Returns:
        Complete JSXGraph HTML with custom code
    """
    container = create_jsxgraph_container(graph_id)
    
    # Process the custom code to handle board initialization properly
    processed_code = _process_custom_jsxgraph_code(graph_id, jsxgraph_code)
    
    # Check if the custom code already contains board initialization
    has_init_board = re.search(r'\binitBoard\s*\(', processed_code)
    
    if has_init_board:
        # Custom code handles its own board initialization
        custom_code = f"""
<script>
{processed_code}
</script>
"""
    else:
        # Add default board initialization for custom code that doesn't have it
        custom_code = f"""
<script>
var board_{graph_id} = JXG.JSXGraph.initBoard('{graph_id}', {{
    boundingbox: [-6, 6, 6, -6],
    axis: false,
    grid: false,
    showNavigation: true,
    showZoom: true
}});

{processed_code}
</script>
"""
    
    return container + custom_code


def create_template_diagram(template_name: str, graph_id: str, custom_code: str = None) -> str:
    """
    Create a diagram from a predefined template or custom code.
    
    Args:
        template_name: Name of the template to use, or "custom" for custom code
        graph_id: Unique ID for the graph
        custom_code: JSXGraph JavaScript code (required when template_name is "custom")
        
    Returns:
        Complete JSXGraph HTML for the template or custom diagram
    """
    if template_name == "custom":
        if not custom_code:
            raise ValueError("Custom JSXGraph code is required when using 'custom' template")
        return wrap_jsxgraph_html(create_custom_diagram(graph_id, custom_code))
    
    if template_name not in JSXGRAPH_TEMPLATES:
        raise ValueError(f"Template '{template_name}' not found. Available: {list(JSXGRAPH_TEMPLATES.keys())}")
    
    template = JSXGRAPH_TEMPLATES[template_name]
    content = template["code"](graph_id)
    return wrap_jsxgraph_html(content)