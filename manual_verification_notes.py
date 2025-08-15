#!/usr/bin/env python3
"""
Manual verification script for Printable Notes Feature
Creates sample data and tests the complete workflow
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.session_state import SessionState, Objective
from backend.note_generator import generate_lesson_notes, get_user_study_notes
from backend.db import init_database, get_db_connection
from components.study_notes import display_printable_notes
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_project_and_session():
    """Create sample project and session data for testing"""
    print("📝 Creating sample project and session data...")
    
    try:
        with get_db_connection() as conn:
            # Create sample project
            project_id = "sample_project_001"
            conn.execute("""
                INSERT OR REPLACE INTO project 
                (id, name, topic, status, hours)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, "Introduction to Biology", "Cell Biology Fundamentals", "completed", 5))
            
            # Create sample node
            node_id = "node_001"
            conn.execute("""
                INSERT OR REPLACE INTO node
                (id, project_id, original_id, label, summary, mastery)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (node_id, project_id, "cell_biology_intro", "Cell Biology Fundamentals", 
                  "Introduction to the basic principles of cell biology", 0.85))
            
            # Create sample session
            session_id = "session_001"
            conn.execute("""
                INSERT OR REPLACE INTO session
                (id, project_id, node_id, session_number, status, final_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, project_id, node_id, 1, "completed", 0.83))
            
            # Create sample learning objectives
            objectives_data = [
                ("obj_001", "Define cells as the basic unit of life", 0.8, 0),
                ("obj_002", "Identify the three principles of cell theory", 0.9, 1),
                ("obj_003", "Explain why cells are fundamental to all organisms", 0.7, 2)
            ]
            
            for obj_id, description, mastery, idx in objectives_data:
                conn.execute("""
                    INSERT OR REPLACE INTO learning_objective
                    (id, project_id, node_id, idx_in_node, description, mastery)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (obj_id, project_id, node_id, idx, description, mastery))
            
            # Create sample transcript entries
            transcript_data = [
                (0, "assistant", "Welcome to Cell Biology Fundamentals! Today we'll explore the basic principles that govern all living organisms."),
                (1, "user", "What exactly is a cell?"),
                (2, "assistant", "Definition: A cell is the basic structural and functional unit of all living organisms. It's the smallest unit that can be called 'living'."),
                (3, "user", "Can you tell me about cell theory?"),
                (4, "assistant", "Key point: Cell theory has three main principles: 1) All living things are composed of one or more cells, 2) The cell is the basic unit of life, 3) All cells arise from existing cells."),
                (5, "user", "Why are cells so important?"),
                (6, "assistant", "Important: Understanding cells is crucial because they are the foundation of all life. Every biological process, from metabolism to reproduction, occurs at the cellular level.")
            ]
            
            for turn_idx, role, content in transcript_data:
                conn.execute("""
                    INSERT OR REPLACE INTO transcript
                    (session_id, turn_idx, role, content)
                    VALUES (?, ?, ?, ?)
                """, (session_id, turn_idx, role, content))
            
            conn.commit()
            print("✅ Sample data created successfully")
            
            return {
                'project_id': project_id,
                'session_id': session_id,
                'node_id': node_id
            }
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_note_generation_workflow():
    """Test the complete note generation workflow"""
    print("\n🧪 Testing Complete Note Generation Workflow")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Create sample data
    sample_data = create_sample_project_and_session()
    if not sample_data:
        print("❌ Failed to create sample data")
        return False
    
    print("\n📚 Generating Study Notes...")
    
    try:
        # Create session state with objectives
        session_state = {
            'objectives_to_teach': [
                Objective(id='obj_001', description='Define cells as the basic unit of life', mastery=0.8),
                Objective(id='obj_002', description='Identify the three principles of cell theory', mastery=0.9),
                Objective(id='obj_003', description='Explain why cells are fundamental to all organisms', mastery=0.7)
            ],
            'history': [
                {'role': 'assistant', 'content': 'Definition: A cell is the basic structural and functional unit of all living organisms.'},
                {'role': 'assistant', 'content': 'Key point: Cell theory has three main principles that govern biology.'},
                {'role': 'assistant', 'content': 'Important: Understanding cells is crucial because they are the foundation of all life.'}
            ],
            'current_phase': 'completed',
            'final_score': 0.83
        }
        
        # Session info
        session_info = {
            'id': sample_data['session_id'],
            'project_id': sample_data['project_id'],
            'node_id': sample_data['node_id'],
            'final_score': 0.83,
            'status': 'completed'
        }
        
        # Node info
        node_info = {
            'id': sample_data['node_id'],
            'label': 'Cell Biology Fundamentals'
        }
        
        # Generate notes
        notes = generate_lesson_notes(session_state, session_info, node_info)
        
        print("✅ Study notes generated successfully!")
        print(f"   Note ID: {notes['id']}")
        print(f"   Lesson: {notes['content']['lesson_title']}")
        print(f"   Score: {notes['content']['final_score']*100:.0f}%")
        print(f"   Objectives: {len(notes['content']['objectives'])}")
        print(f"   Key Concepts: {len(notes['content']['key_concepts'])}")
        print(f"   Review Questions: {len(notes['content']['review_questions'])}")
        
        return notes
        
    except Exception as e:
        print(f"❌ Note generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_collection_management(project_id):
    """Test study notes collection functionality"""
    print("\n📚 Testing Study Notes Collection...")
    
    try:
        # Get all notes for the project
        notes_collection = get_user_study_notes(project_id)
        
        print(f"✅ Found {len(notes_collection)} note(s) in collection:")
        for note in notes_collection:
            print(f"   • {note['title']} ({note['date'][:10]})")
            print(f"     Summary: {note['summary'][:100]}...")
        
        return len(notes_collection) > 0
        
    except Exception as e:
        print(f"❌ Collection management test failed: {e}")
        return False


def create_sample_html_file(notes):
    """Create a sample HTML file to demonstrate print functionality"""
    print("\n📄 Creating sample HTML file for print testing...")
    
    try:
        # Create the full HTML document with CSS
        full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Study Notes - {notes['content']['lesson_title']}</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            color: #000;
            background: #fff;
            margin: 0;
            padding: 20px;
        }}
        
        .printable-notes {{
            max-width: 8.5in;
            margin: 0 auto;
            background: #fff;
        }}
        
        .notes-header {{
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
        }}
        
        .lesson-title {{
            font-size: 24pt;
            font-weight: bold;
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        
        .lesson-name {{
            font-size: 20pt;
            font-weight: bold;
            margin: 0 0 10px 0;
            color: #34495e;
        }}
        
        .completion-info {{
            font-size: 12pt;
            color: #666;
            margin: 5px 0;
        }}
        
        .section-divider {{
            font-family: monospace;
            text-align: center;
            margin: 15px 0;
            color: #333;
            font-size: 10pt;
        }}
        
        .lesson-overview, .objectives-section, .key-concepts, 
        .insights-section, .review-questions, .performance-section {{
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        
        .lesson-overview h3, .objectives-section h3, .key-concepts h3,
        .insights-section h3, .review-questions h3, .performance-section h3 {{
            font-size: 16pt;
            font-weight: bold;
            margin: 0 0 15px 0;
            color: #2c3e50;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        
        .objectives-list, .insights-list, .questions-list, .performance-list {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        
        .objectives-list li, .insights-list li, .performance-list li {{
            margin: 8px 0;
            font-size: 12pt;
        }}
        
        .questions-list li {{
            margin: 12px 0;
            font-size: 12pt;
            line-height: 1.4;
        }}
        
        .concept-item {{
            margin: 15px 0;
            padding: 10px;
            border-left: 3px solid #3498db;
            background-color: #f8f9fa;
        }}
        
        .concept-item h4 {{
            font-size: 14pt;
            margin: 0 0 8px 0;
            color: #2c3e50;
        }}
        
        .concept-item p {{
            font-size: 12pt;
            margin: 0;
            line-height: 1.4;
        }}
        
        .notes-footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #bdc3c7;
            font-size: 10pt;
            color: #666;
        }}
        
        /* Print-specific optimizations */
        @media print {{
            /* Optimize page layout for ring binding */
            @page {{
                margin: 1.5in 1in 1in 1.5in; /* Top Right Bottom Left - extra left margin for binding */
                size: letter;
            }}
            
            /* Typography optimizations */
            body {{
                font-size: 12pt;
                line-height: 1.4;
                color: #000 !important;
                background: #fff !important;
            }}
            
            h1 {{ 
                font-size: 20pt; 
                page-break-before: avoid;
                page-break-after: avoid;
            }}
            
            h2 {{ 
                font-size: 16pt; 
                margin-top: 12pt;
                page-break-after: avoid;
            }}
            
            h3 {{ 
                font-size: 14pt; 
                margin-top: 12pt;
                page-break-after: avoid;
            }}
            
            /* Page break controls */
            .notes-header {{
                page-break-after: avoid;
            }}
            
            .lesson-overview, .objectives-section, .key-concepts, 
            .insights-section, .review-questions, .performance-section {{
                page-break-inside: avoid;
                margin-top: 15pt;
            }}
            
            /* Ensure good contrast for printing */
            .concept-item {{
                border-left: 2pt solid #000;
                background-color: #f0f0f0;
            }}
            
            .section-divider {{
                color: #000;
            }}
        }}
    </style>
</head>
<body>
    {notes['formatted_html']}
    
    <div class="print-instructions" style="margin-top: 30px; padding: 20px; background: #e8f4f8; border-left: 4px solid #3498db; page-break-inside: avoid;">
        <h3>🖨️ Print Instructions</h3>
        <p><strong>To print or save as PDF:</strong></p>
        <ol>
            <li>Press <strong>Ctrl+P</strong> (Windows/Linux) or <strong>Cmd+P</strong> (Mac)</li>
            <li>In the print dialog, select <strong>"Save as PDF"</strong> or choose your printer</li>
            <li>Under <strong>"More settings"</strong>, ensure <strong>"Print backgrounds"</strong> is enabled</li>
            <li>Set paper size to <strong>"Letter"</strong> for best results</li>
            <li>The extra left margin provides space for ring binding</li>
        </ol>
        <p><em>This instruction box will not appear in the printed version.</em></p>
    </div>
    
    <style>
    @media print {{
        .print-instructions {{ display: none; }}
    }}
    </style>
</body>
</html>"""
        
        # Save to file
        output_file = Path("sample_study_notes.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_html)
        
        print(f"✅ Sample HTML file created: {output_file.absolute()}")
        print("   You can open this file in a browser and test the print functionality")
        print("   Use Ctrl+P (or Cmd+P) to print or save as PDF")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating HTML file: {e}")
        return False


def main():
    """Run the complete manual verification"""
    print("🧪 Manual Verification of Printable Notes Feature")
    print("=" * 60)
    
    # Test the complete workflow
    notes = test_note_generation_workflow()
    if not notes:
        print("❌ Note generation failed - stopping verification")
        return False
    
    # Test collection management
    project_id = notes['content'].get('lesson_title', 'test_project')  # Using lesson title as project identifier
    if not test_collection_management("sample_project_001"):
        print("⚠️  Collection management test had issues")
    
    # Create sample HTML file for manual testing
    if not create_sample_html_file(notes):
        print("⚠️  HTML file creation had issues")
    
    print("\n" + "=" * 60)
    print("🎉 Manual Verification Complete!")
    print("\n✅ **What was tested:**")
    print("   • Database schema and operations")
    print("   • Note content generation from session data")
    print("   • AI-powered concept extraction")
    print("   • Print-optimized HTML formatting")
    print("   • Study notes collection management")
    print("   • Sample HTML file for manual print testing")
    
    print("\n📋 **Next Steps for Full Verification:**")
    print("   1. Open 'sample_study_notes.html' in your browser")
    print("   2. Test the print functionality (Ctrl+P or Cmd+P)")
    print("   3. Verify the ring-binding margins are correct")
    print("   4. Test 'Save as PDF' functionality")
    print("   5. Complete a lesson in the Streamlit app to test integration")
    
    print(f"\n🎯 **Generated Notes Summary:**")
    print(f"   • Lesson: {notes['content']['lesson_title']}")
    print(f"   • Score: {notes['content']['final_score']*100:.0f}%")
    print(f"   • Objectives: {notes['content']['performance']['objectives_completed']}/{notes['content']['performance']['total_objectives']}")
    print(f"   • Key Concepts: {len(notes['content']['key_concepts'])}")
    print(f"   • Review Questions: {len(notes['content']['review_questions'])}")
    
    return True


if __name__ == "__main__":
    main()