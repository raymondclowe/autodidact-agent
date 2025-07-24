#!/usr/bin/env python3
"""
Script to create a sample project for testing the debug completion fix
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import from the project
from backend.db import (
    init_database, create_project, create_node, create_learning_objective,
    create_session
)
import json

def create_sample_project():
    """Create a sample project for testing"""
    
    # Initialize database
    init_database()
    
    # Create a test project
    project_id = create_project(
        topic="Fundamental Operational Concepts",
        report_path="/tmp/sample_report.md", 
        resources={}
    )
    
    # Create sample nodes
    node1_id = create_node(
        project_id=project_id,
        original_id="arithmetic_operations",
        label="Fundamental Operational Concepts",
        summary="Learn the four basic arithmetic operations"
    )
    
    node2_id = create_node(
        project_id=project_id,
        original_id="advanced_operations",
        label="Advanced Mathematical Operations",
        summary="Learn advanced mathematical concepts"
    )
    
    # Create learning objectives for first node
    lo1_id = create_learning_objective(
        project_id=project_id,
        node_id=node1_id,
        idx_in_node=0,
        description="Define the four core arithmetic operations and their symbolic representations"
    )
    
    lo2_id = create_learning_objective(
        project_id=project_id,
        node_id=node1_id,
        idx_in_node=1,
        description="Apply basic arithmetic operations to solve problems"
    )
    
    # Create learning objective for second node
    lo3_id = create_learning_objective(
        project_id=project_id,
        node_id=node2_id,
        idx_in_node=0,
        description="Master advanced mathematical concepts"
    )
    
    # Add edge to make node2 depend on node1
    from backend.db import get_db_connection
    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO edge (source, target, project_id, confidence, rationale)
            VALUES (?, ?, ?, ?, ?)
        """, ("arithmetic_operations", "advanced_operations", project_id, 0.9, "Sequential learning"))
        
        # Update project to completed status with graph data
        graph_data = {
            "nodes": [
                {
                    "id": node1_id,
                    "original_id": "arithmetic_operations",
                    "label": "Fundamental Operational Concepts",
                    "mastery": 0.0
                },
                {
                    "id": node2_id,
                    "original_id": "advanced_operations", 
                    "label": "Advanced Mathematical Operations",
                    "mastery": 0.0
                }
            ],
            "edges": [
                {
                    "source": "arithmetic_operations",
                    "target": "advanced_operations",
                    "confidence": 0.9
                }
            ]
        }
        
        conn.execute("""
            UPDATE project 
            SET status = 'completed', 
                resources_json = ? 
            WHERE id = ?
        """, (json.dumps({"graph": graph_data}), project_id))
        conn.commit()
    
    # Create sample report file
    report_content = """# Learning Report: Fundamental Operational Concepts

## Overview
This learning journey covers the fundamental arithmetic operations that form the basis of mathematical computation.

## Learning Objectives
1. Define the four core arithmetic operations
2. Understand symbolic representations  
3. Apply operations to solve problems

## Resources
- Basic Mathematics Textbook
- Online Practice Problems
- Interactive Tutorials
"""
    
    report_path = Path("/tmp/sample_report.md")
    report_path.write_text(report_content)
    
    print(f"✅ Sample project created!")
    print(f"   Project ID: {project_id}")
    print(f"   Node 1 (First Lesson): {node1_id}")
    print(f"   Node 2 (Second Lesson): {node2_id}")
    print(f"   Access at: http://localhost:8501/project?project_id={project_id}")
    
    return project_id, node1_id, node2_id

if __name__ == "__main__":
    create_sample_project()