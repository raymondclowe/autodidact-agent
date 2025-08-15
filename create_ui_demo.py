#!/usr/bin/env python3
"""
UI Display Test for Study Notes Feature
Creates visual examples of the study notes interface
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.note_generator import format_for_print, get_user_study_notes


def create_ui_demo_html():
    """Create a demo HTML showing the UI elements"""
    
    # Sample note content
    sample_content = {
        'lesson_title': 'Advanced Python Programming',
        'completion_date': '2025-08-15T15:30:00',
        'final_score': 0.91,
        'duration_minutes': 35,
        'objectives': [
            {'id': 'obj1', 'description': 'Implement object-oriented design patterns', 'mastery': 0.95, 'mastered': True},
            {'id': 'obj2', 'description': 'Use advanced Python features effectively', 'mastery': 0.88, 'mastered': True},
            {'id': 'obj3', 'description': 'Debug complex Python applications', 'mastery': 0.90, 'mastered': True}
        ],
        'key_concepts': [
            {'title': 'Design Patterns', 'explanation': 'Singleton, Factory, and Observer patterns provide reusable solutions to common programming problems.'},
            {'title': 'Decorators and Context Managers', 'explanation': 'Advanced Python features that enable clean, reusable code with separation of concerns.'},
            {'title': 'Debugging Strategies', 'explanation': 'Systematic approaches to identify and resolve complex issues in Python applications.'}
        ],
        'lesson_overview': 'In this advanced lesson, you mastered sophisticated Python programming concepts including design patterns, advanced language features, and professional debugging techniques. You demonstrated exceptional understanding by achieving high mastery scores across all objectives.',
        'insights': [
            'You showed exceptional mastery of design patterns with 95% proficiency',
            'Your understanding of advanced Python features demonstrates professional-level competency',
            'The debugging strategies you learned will be invaluable for complex projects'
        ],
        'review_questions': [
            'What are the key benefits of using the Singleton design pattern?',
            'How do decorators enhance code modularity and reusability?',
            'What systematic approach would you use to debug a complex Python application?',
            'How do context managers help with resource management?',
            'What are the trade-offs between different design patterns?'
        ],
        'performance': {
            'score': 0.91,
            'mastery_level': 'Exceptional',
            'objectives_completed': 3,
            'total_objectives': 3
        }
    }
    
    # Generate formatted HTML
    formatted_notes = format_for_print(sample_content)
    
    # Create complete HTML document with enhanced styling
    complete_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Study Notes Demo - Autodidact</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            color: #000;
            background: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        
        .demo-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .demo-header {{
            background: linear-gradient(135deg, #3498db, #2c3e50);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .demo-header h1 {{
            margin: 0;
            font-size: 28pt;
        }}
        
        .demo-header p {{
            margin: 10px 0 0 0;
            font-size: 14pt;
            opacity: 0.9;
        }}
        
        .demo-content {{
            display: flex;
            min-height: 600px;
        }}
        
        .demo-sidebar {{
            width: 300px;
            background: #f8f9fa;
            border-right: 1px solid #ddd;
            padding: 20px;
        }}
        
        .demo-main {{
            flex: 1;
            padding: 20px;
            background: white;
        }}
        
        .feature-box {{
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        
        .feature-box h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 14pt;
        }}
        
        .feature-box p {{
            margin: 0;
            font-size: 12pt;
        }}
        
        .sample-notes {{
            border: 2px solid #3498db;
            border-radius: 8px;
            padding: 0;
            background: white;
            margin-top: 20px;
        }}
        
        .notes-preview {{
            max-height: 500px;
            overflow-y: auto;
            padding: 20px;
        }}
        
        .button-demo {{
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            font-size: 14pt;
            cursor: pointer;
            margin: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .button-demo:hover {{
            background: #2980b9;
        }}
        
        .button-secondary {{
            background: #95a5a6;
        }}
        
        .button-secondary:hover {{
            background: #7f8c8d;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 24pt;
            font-weight: bold;
            color: #3498db;
            margin: 0;
        }}
        
        .stat-label {{
            font-size: 12pt;
            color: #666;
            margin: 5px 0 0 0;
        }}
        
        .printable-notes {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            color: #000;
            background: #fff;
            padding: 20px;
            border-radius: 5px;
        }}
        
        .notes-header {{
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
        }}
        
        .lesson-title {{
            font-size: 20pt;
            font-weight: bold;
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        
        .lesson-name {{
            font-size: 18pt;
            font-weight: bold;
            margin: 0 0 10px 0;
            color: #34495e;
        }}
        
        .completion-info {{
            font-size: 11pt;
            color: #666;
            margin: 5px 0;
        }}
        
        .section-divider {{
            font-family: monospace;
            text-align: center;
            margin: 15px 0;
            color: #333;
            font-size: 9pt;
        }}
        
        .lesson-overview, .objectives-section, .key-concepts, 
        .insights-section, .review-questions, .performance-section {{
            margin: 15px 0;
        }}
        
        .lesson-overview h3, .objectives-section h3, .key-concepts h3,
        .insights-section h3, .review-questions h3, .performance-section h3 {{
            font-size: 14pt;
            font-weight: bold;
            margin: 0 0 10px 0;
            color: #2c3e50;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        
        .objectives-list, .insights-list, .questions-list, .performance-list {{
            margin: 8px 0;
            padding-left: 20px;
        }}
        
        .objectives-list li, .insights-list li, .performance-list li {{
            margin: 6px 0;
            font-size: 11pt;
        }}
        
        .questions-list li {{
            margin: 8px 0;
            font-size: 11pt;
            line-height: 1.3;
        }}
        
        .concept-item {{
            margin: 10px 0;
            padding: 8px;
            border-left: 3px solid #3498db;
            background-color: #f8f9fa;
        }}
        
        .concept-item h4 {{
            font-size: 12pt;
            margin: 0 0 5px 0;
            color: #2c3e50;
        }}
        
        .concept-item p {{
            font-size: 10pt;
            margin: 0;
            line-height: 1.3;
        }}
        
        .notes-footer {{
            text-align: center;
            margin-top: 20px;
            padding-top: 10px;
            border-top: 1px solid #bdc3c7;
            font-size: 9pt;
            color: #666;
        }}
        
        @media print {{
            body {{ background: white; }}
            .demo-header, .demo-sidebar, .button-demo, .stats-grid {{ display: none; }}
            .demo-container {{ box-shadow: none; border-radius: 0; }}
            .demo-main {{ padding: 0; }}
            @page {{ margin: 1.5in 1in 1in 1.5in; size: letter; }}
        }}
    </style>
</head>
<body>
    <div class="demo-container">
        <div class="demo-header">
            <h1>📚 Autodidact Study Notes</h1>
            <p>Printable Lesson Notes Feature Demonstration</p>
        </div>
        
        <div class="demo-content">
            <div class="demo-sidebar">
                <h2 style="margin-top: 0; color: #2c3e50;">🎯 Key Features</h2>
                
                <div class="feature-box">
                    <h3>🖨️ Print Optimized</h3>
                    <p>Professional formatting with ring-binding margins for physical study materials.</p>
                </div>
                
                <div class="feature-box">
                    <h3>🤖 AI-Powered</h3>
                    <p>Automatically extracts key concepts and generates personalized summaries.</p>
                </div>
                
                <div class="feature-box">
                    <h3>📚 Collection System</h3>
                    <p>Accumulate notes across lessons to build a complete study guide.</p>
                </div>
                
                <div class="feature-box">
                    <h3>📄 Multiple Formats</h3>
                    <p>View online, print to paper, or save as PDF for offline access.</p>
                </div>
                
                <h3 style="margin-top: 30px; color: #2c3e50;">🔧 Actions</h3>
                <button class="button-demo">📝 Generate Notes</button>
                <button class="button-demo">🖨️ Print Notes</button>
                <button class="button-demo button-secondary">📄 Download PDF</button>
                <button class="button-demo button-secondary">📚 View Collection</button>
                
                <div style="margin-top: 20px; font-size: 10pt; color: #666;">
                    <p><strong>💡 Tip:</strong> Use Ctrl+P to test print functionality with this demo page!</p>
                </div>
            </div>
            
            <div class="demo-main">
                <h2 style="margin-top: 0; color: #2c3e50;">📖 Sample Study Notes</h2>
                <p>Below is an example of automatically generated study notes from a completed lesson:</p>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <p class="stat-number">91%</p>
                        <p class="stat-label">Final Score</p>
                    </div>
                    <div class="stat-card">
                        <p class="stat-number">3/3</p>
                        <p class="stat-label">Objectives Mastered</p>
                    </div>
                    <div class="stat-card">
                        <p class="stat-number">35</p>
                        <p class="stat-label">Minutes Invested</p>
                    </div>
                    <div class="stat-card">
                        <p class="stat-number">5</p>
                        <p class="stat-label">Review Questions</p>
                    </div>
                </div>
                
                <div class="sample-notes">
                    <div class="notes-preview">
                        {formatted_notes}
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e8f4f8; border-radius: 5px;">
                    <p style="margin: 0; font-size: 12pt;"><strong>🖨️ Print Instructions:</strong> This demo page is print-ready! Use <strong>Ctrl+P</strong> (or <strong>Cmd+P</strong> on Mac) to test the print functionality. The layout will automatically optimize for printing with proper margins for ring binding.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Save the demo HTML
    demo_file = Path("study_notes_ui_demo.html")
    with open(demo_file, "w", encoding="utf-8") as f:
        f.write(complete_html)
    
    print(f"✅ UI Demo created: {demo_file.absolute()}")
    return demo_file


def main():
    """Create UI demonstration"""
    print("🎨 Creating Study Notes UI Demonstration")
    print("=" * 50)
    
    demo_file = create_ui_demo_html()
    
    print(f"\n📋 **Demo Features Included:**")
    print("   • Complete study notes layout with sample content")
    print("   • Professional formatting with ring-binding margins") 
    print("   • Feature descriptions and UI elements")
    print("   • Print optimization demonstration")
    print("   • Interactive button examples")
    print("   • Statistics display")
    
    print(f"\n🚀 **How to View:**")
    print(f"   1. Open: {demo_file.absolute()}")
    print("   2. Use any web browser to view the demo")
    print("   3. Test print functionality with Ctrl+P (or Cmd+P)")
    print("   4. Verify ring-binding margins in print preview")
    
    print(f"\n💡 **This demonstrates:**")
    print("   • How study notes appear to students")
    print("   • Print-optimized formatting")
    print("   • Professional study guide appearance")
    print("   • Integration with lesson completion workflow")


if __name__ == "__main__":
    main()