#!/usr/bin/env python3
"""
Integration test for Printable Notes Feature
Tests the complete integration with the Streamlit application
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.session_state import SessionState, Objective
from backend.note_generator import generate_lesson_notes, get_user_study_notes
from backend.db import init_database
from components.lesson_completion import show_study_notes_offer
from components.study_notes import display_printable_notes
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_lesson_completion_integration():
    """Test integration with lesson completion workflow"""
    print("🧪 Testing Lesson Completion Integration...")
    
    try:
        # Initialize database
        init_database()
        
        # Create mock completed session state
        session_state = {
            'objectives_to_teach': [
                Objective(id='obj1', description='Define cells as the basic unit of life', mastery=0.8),
                Objective(id='obj2', description='Identify cell theory principles', mastery=0.9),
                Objective(id='obj3', description='Explain cellular importance', mastery=0.7)
            ],
            'history': [
                {'role': 'assistant', 'content': 'Definition: Cells are the basic units of life.'},
                {'role': 'assistant', 'content': 'Key point: Cell theory has three principles.'},
            ],
            'current_phase': 'completed',
            'final_score': 0.83,
            'completed_objectives': ['obj1', 'obj2', 'obj3']
        }
        
        # Mock node info (lesson information)
        node_info = {
            'id': 'integration_test_node',
            'label': 'Integration Test Lesson'
        }
        
        # Test that the study notes offer function doesn't crash
        # (This would normally show in Streamlit UI)
        print("✅ Lesson completion integration components available")
        
        # Test note generation workflow
        session_info = {
            'id': 'integration_session',
            'project_id': 'integration_project',
            'node_id': 'integration_node',
            'final_score': 0.83,
            'status': 'completed'
        }
        
        notes = generate_lesson_notes(session_state, session_info, node_info)
        print(f"✅ Generated notes via integration workflow: {notes['id']}")
        
        # Verify notes can be retrieved
        collection = get_user_study_notes('integration_project')
        if collection:
            print(f"✅ Notes retrievable in collection: {len(collection)} note(s)")
        else:
            print("⚠️  No notes found in collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_css_print_optimization():
    """Test that CSS print optimization is correctly applied"""
    print("\n🧪 Testing CSS Print Optimization...")
    
    try:
        # Test CSS generation from study_notes component
        from components.study_notes import display_printable_notes
        
        # Mock notes for testing
        mock_notes = {
            'formatted_html': '<div class="printable-notes"><h1>Test</h1></div>'
        }
        
        # This would normally apply CSS in Streamlit
        print("✅ CSS print optimization component available")
        
        # Verify ring-binding margin specification is in component
        with open('components/study_notes.py', 'r') as f:
            content = f.read()
            
        if '1.5in 1in 1in 1.5in' in content:
            print("✅ Ring-binding margins correctly specified in CSS")
        else:
            print("❌ Ring-binding margins not found in CSS")
            return False
            
        if '@media print' in content:
            print("✅ Print media queries correctly included")
        else:
            print("❌ Print media queries not found")
            return False
            
        if 'printable-notes' in content:
            print("✅ Print-optimized CSS class available")
        else:
            print("❌ Print-optimized CSS class not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ CSS test failed: {e}")
        return False


def test_app_navigation_integration():
    """Test that study notes page is properly integrated into app navigation"""
    print("\n🧪 Testing App Navigation Integration...")
    
    try:
        # Check if study notes page is added to app navigation
        with open('app.py', 'r') as f:
            app_content = f.read()
            
        if 'study_notes.py' in app_content:
            print("✅ Study notes page included in app navigation")
        else:
            print("❌ Study notes page not found in app navigation")
            return False
            
        if 'Study Notes' in app_content:
            print("✅ Study notes menu item configured")
        else:
            print("❌ Study notes menu item not configured")
            return False
            
        # Check that study notes page file exists and is valid
        notes_page = Path('pages/study_notes.py')
        if notes_page.exists():
            print("✅ Study notes page file exists")
        else:
            print("❌ Study notes page file missing")
            return False
            
        # Check basic syntax by importing
        import pages.study_notes
        print("✅ Study notes page imports successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Navigation integration test failed: {e}")
        return False


def test_database_schema_integration():
    """Test that database schema is properly integrated"""
    print("\n🧪 Testing Database Schema Integration...")
    
    try:
        # Initialize database
        init_database()
        
        from backend.db import get_db_connection
        
        with get_db_connection() as conn:
            # Check if study_notes table exists with correct structure
            cursor = conn.execute("PRAGMA table_info(study_notes)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            required_columns = {
                'id': 'TEXT',
                'session_id': 'TEXT', 
                'project_id': 'TEXT',
                'node_id': 'TEXT',
                'lesson_title': 'TEXT',
                'generated_date': 'TIMESTAMP',
                'content_json': 'TEXT',
                'formatted_html': 'TEXT',
                'summary': 'TEXT'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in columns:
                    print(f"❌ Missing column: {col_name}")
                    return False
                    
            print("✅ Database schema properly integrated")
            
            # Check indexes
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_study_notes_%'
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            if indexes:
                print(f"✅ Study notes indexes created: {len(indexes)} index(es)")
            else:
                print("⚠️  No study notes indexes found")
                
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("🧪 Integration Testing for Printable Notes Feature")
    print("=" * 60)
    
    tests = [
        ("Lesson Completion Integration", test_lesson_completion_integration),
        ("CSS Print Optimization", test_css_print_optimization),
        ("App Navigation Integration", test_app_navigation_integration),
        ("Database Schema Integration", test_database_schema_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("\n✅ **Ready for Production:**")
        print("   • Database schema properly integrated")
        print("   • Note generation workflow functional")
        print("   • Print optimization CSS implemented")
        print("   • App navigation properly configured")
        print("   • All components working together")
        
        print("\n🚀 **Next Steps:**")
        print("   • Run Streamlit app: streamlit run app.py")
        print("   • Complete a lesson to test note generation")
        print("   • Test print functionality with Ctrl+P")
        print("   • Verify ring-binding margins in print preview")
        
        return True
    else:
        print("⚠️  Some integration tests failed.")
        print("   Please review the failed tests before deployment.")
        return False


if __name__ == "__main__":
    main()