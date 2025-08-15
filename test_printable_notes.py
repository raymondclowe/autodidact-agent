#!/usr/bin/env python3
"""
Test script for Printable Notes Feature
Tests the core functionality of study notes generation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.session_state import SessionState, Objective
from backend.note_generator import (
    generate_lesson_notes,
    extract_key_concepts,
    format_for_print,
    get_user_study_notes,
    save_notes_to_database
)
from backend.db import init_database
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_schema():
    """Test that database schema includes study_notes table"""
    print("🧪 Testing Database Schema...")
    
    try:
        # Initialize database to ensure tables exist
        init_database()
        print("✅ Database initialized successfully")
        
        from backend.db import get_db_connection
        with get_db_connection() as conn:
            # Check if study_notes table exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='study_notes'
            """)
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("✅ study_notes table exists")
            else:
                print("❌ study_notes table not found")
                return False
            
            # Check table schema
            cursor = conn.execute("PRAGMA table_info(study_notes)")
            columns = cursor.fetchall()
            expected_columns = {'id', 'session_id', 'project_id', 'node_id', 
                              'lesson_title', 'generated_date', 'content_json', 
                              'formatted_html', 'summary'}
            actual_columns = {col[1] for col in columns}
            
            if expected_columns.issubset(actual_columns):
                print("✅ study_notes table has correct schema")
                return True
            else:
                missing = expected_columns - actual_columns
                print(f"❌ Missing columns: {missing}")
                return False
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_note_generation():
    """Test core note generation functionality"""
    print("\n🧪 Testing Note Generation...")
    
    try:
        # Create mock session state
        session_state = {
            'objectives_to_teach': [
                Objective(id='obj1', description='Define cells as the basic unit of life', mastery=0.8),
                Objective(id='obj2', description='Identify the three principles of cell theory', mastery=0.9),
                Objective(id='obj3', description='Explain why cells are fundamental to all organisms', mastery=0.7)
            ],
            'history': [
                {'role': 'assistant', 'content': 'Definition: Cells are the basic unit of life. This is a fundamental principle.'},
                {'role': 'user', 'content': 'What are the three principles of cell theory?'},
                {'role': 'assistant', 'content': 'The three principles are: 1) All living things are made of cells, 2) Cells are the basic unit of life, 3) All cells come from existing cells.'}
            ],
            'current_phase': 'completed',
            'final_score': 0.83
        }
        
        # Mock session info
        session_info = {
            'id': 'test_session_123',
            'project_id': 'test_project_456', 
            'node_id': 'test_node_789',
            'final_score': 0.83,
            'status': 'completed'
        }
        
        # Mock node info
        node_info = {
            'id': 'test_node_789',
            'label': 'Cell Biology Fundamentals'
        }
        
        # Test note generation
        notes = generate_lesson_notes(session_state, session_info, node_info)
        
        # Verify structure
        required_keys = {'id', 'content', 'formatted_html', 'summary'}
        if not required_keys.issubset(notes.keys()):
            print(f"❌ Missing keys in notes: {required_keys - notes.keys()}")
            return False
            
        print("✅ Note generation completed successfully")
        print(f"   Generated note ID: {notes['id']}")
        print(f"   Content keys: {list(notes['content'].keys())}")
        print(f"   Summary: {notes['summary'][:100]}...")
        
        # Test HTML formatting
        html = notes['formatted_html']
        if not html or len(html) < 100:
            print("❌ HTML formatting seems incomplete")
            return False
            
        # Check for key elements in HTML
        required_elements = [
            'printable-notes',
            'STUDY NOTES',
            'Cell Biology Fundamentals',
            'LEARNING OBJECTIVES',
            'KEY CONCEPTS'
        ]
        
        for element in required_elements:
            if element not in html:
                print(f"❌ Missing HTML element: {element}")
                return False
                
        print("✅ HTML formatting contains all required elements")
        return True
        
    except Exception as e:
        print(f"❌ Note generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_key_concepts_extraction():
    """Test key concept extraction from session history"""
    print("\n🧪 Testing Key Concepts Extraction...")
    
    try:
        objectives = [
            Objective(id='obj1', description='Define cells as the basic unit of life', mastery=0.8),
            Objective(id='obj2', description='Identify cell theory principles', mastery=0.9)
        ]
        
        history = [
            {'role': 'assistant', 'content': 'Definition: Cells are the fundamental units of all living organisms.'},
            {'role': 'assistant', 'content': 'Key point: Cell theory has three main principles that govern biology.'},
            {'role': 'user', 'content': 'Can you explain more?'},
            {'role': 'assistant', 'content': 'Important: Understanding cells is crucial for all biological sciences.'}
        ]
        
        concepts = extract_key_concepts(history, objectives)
        
        if not concepts:
            print("❌ No concepts extracted")
            return False
            
        print(f"✅ Extracted {len(concepts)} key concepts:")
        for i, concept in enumerate(concepts[:3]):  # Show first 3
            print(f"   {i+1}. {concept['title']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Key concepts extraction test failed: {e}")
        return False


def test_print_formatting():
    """Test print-optimized HTML formatting"""
    print("\n🧪 Testing Print Formatting...")
    
    try:
        # Mock note content
        note_content = {
            'lesson_title': 'Test Lesson',
            'completion_date': '2025-01-08T12:00:00',
            'final_score': 0.85,
            'duration_minutes': 25,
            'objectives': [
                {'id': 'obj1', 'description': 'Test objective', 'mastery': 0.8, 'mastered': True}
            ],
            'key_concepts': [
                {'title': 'Test Concept', 'explanation': 'This is a test concept'}
            ],
            'lesson_overview': 'This is a test lesson overview.',
            'insights': ['Test insight 1', 'Test insight 2'],
            'review_questions': ['What is the test concept?'],
            'performance': {
                'score': 0.85,
                'mastery_level': 'Advanced',
                'objectives_completed': 1,
                'total_objectives': 1
            }
        }
        
        html = format_for_print(note_content)
        
        # Check for content structure (CSS is added in component, not backend)
        required_sections = [
            'STUDY NOTES',
            'LESSON OVERVIEW', 
            'LEARNING OBJECTIVES',
            'KEY CONCEPTS',
            'REVIEW QUESTIONS',
            'YOUR PROGRESS'
        ]
        
        for section in required_sections:
            if section not in html:
                print(f"❌ Missing section: {section}")
                return False
        
        # Check for printable-notes class (CSS container)
        if 'printable-notes' not in html:
            print("❌ Missing printable-notes container class")
            return False
            
        # Check for proper HTML structure (strip whitespace)
        html_stripped = html.strip()
        if not html_stripped.startswith('<div') or not html_stripped.endswith('</div>'):
            print(f"❌ Invalid HTML structure - starts with: {html_stripped[:20]}... ends with: ...{html_stripped[-20:]}")
            return False
                
        print("✅ Print formatting includes all required content sections")
        print("✅ HTML structure is valid for print optimization")
        
        # Test that CSS will be applied by component
        from components.study_notes import display_printable_notes
        # This would normally display in Streamlit, but we can test it doesn't crash
        print("✅ Print component integration available")
        
        return True
        
    except Exception as e:
        print(f"❌ Print formatting test failed: {e}")
        return False


def test_database_operations():
    """Test database storage and retrieval operations"""
    print("\n🧪 Testing Database Operations...")
    
    try:
        import uuid
        
        # Test saving notes with unique ID
        test_note_id = f"test_note_{str(uuid.uuid4())[:8]}"
        test_content = {
            'lesson_title': 'Test Lesson',
            'completion_date': '2025-01-08T12:00:00',
            'objectives': []
        }
        test_html = "<div>Test HTML content</div>"
        test_summary = "Test summary"
        
        success = save_notes_to_database(
            note_id=test_note_id,
            session_id='test_session',
            project_id='test_project_db_test',
            node_id='test_node',
            lesson_title='Test Lesson',
            content=test_content,
            formatted_html=test_html,
            summary=test_summary
        )
        
        if not success:
            print("❌ Failed to save note to database")
            return False
            
        print("✅ Note saved to database successfully")
        
        # Test retrieving notes
        notes = get_user_study_notes('test_project_db_test')
        
        if not notes:
            print("❌ Failed to retrieve notes from database")
            return False
            
        # Find our test note
        test_note = next((note for note in notes if note['id'] == test_note_id), None)
        if not test_note:
            print("❌ Test note not found in retrieved notes")
            return False
            
        print("✅ Note retrieved from database successfully")
        print(f"   Retrieved note: {test_note['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Printable Notes Feature")
    print("=" * 50)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Note Generation", test_note_generation),
        ("Key Concepts Extraction", test_key_concepts_extraction),
        ("Print Formatting", test_print_formatting),
        ("Database Operations", test_database_operations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Printable Notes feature is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    main()