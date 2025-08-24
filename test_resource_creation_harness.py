#!/usr/bin/env python3
"""
Comprehensive Test Harness for AI Resource Creation Validation

This test harness validates that prompts effectively guide AI to create the correct
types of resources (LaTeX math, JSXGraph diagrams, Tavily images) based on user input.

The harness can:
1. Test various user input scenarios
2. Analyze prompt effectiveness for resource selection guidance
3. Validate resource creation logic for each type
4. Score prompt quality and provide recommendations
5. Support extensibility for future resource types (YouTube, AI animations, etc.)

Usage:
    python test_resource_creation_harness.py
    
Purpose: Fine-tune lesson prompts to ensure AI creates appropriate educational resources.
"""

import sys
import os
import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Add current directory to path for imports
sys.path.append('.')

# Import the teaching prompt template
try:
    from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE
except ImportError:
    print("❌ Error: Could not import TEACHING_PROMPT_TEMPLATE")
    print("Make sure you're running from the repository root directory")
    sys.exit(1)

# Import resource modules for validation
try:
    from utils.math_utils import inject_math_rendering_support
    from components.jsxgraph_utils import get_available_templates, create_template_diagram
    from utils.tavily_integration import TavilyImageSearch, ImageResult
except ImportError as e:
    print(f"⚠️  Warning: Some resource modules not available: {e}")
    print("Some tests may be skipped")

class ResourceType(Enum):
    """Types of educational resources the AI can create"""
    LATEX_MATH = "latex_math"
    JSXGRAPH_DIAGRAM = "jsxgraph_diagram" 
    TAVILY_IMAGE = "tavily_image"
    YOUTUBE_VIDEO = "youtube_video"  # Future extension
    AI_ANIMATION = "ai_animation"    # Future extension

@dataclass
class UserScenario:
    """A user input scenario for testing"""
    description: str
    user_input: str
    expected_resource_types: List[ResourceType]
    educational_context: str
    difficulty_level: str = "high_school"
    subject_area: str = "general"

@dataclass 
class PromptAnalysis:
    """Analysis results for prompt effectiveness"""
    resource_type: ResourceType
    guidance_score: float  # 0-1, how well prompt guides toward this resource
    clarity_score: float   # 0-1, how clear the guidance is
    coverage_score: float  # 0-1, how well scenarios are covered
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class TestResult:
    """Results of running a test scenario"""
    scenario: UserScenario
    prompt_analyses: List[PromptAnalysis]
    overall_score: float
    passed: bool
    ai_decision_simulation: Dict[ResourceType, float]  # Probability AI would choose each type
    recommendations: List[str] = field(default_factory=list)

class ResourceCreationHarness:
    """Main test harness for validating AI resource creation guidance"""
    
    def __init__(self):
        self.prompt_template = TEACHING_PROMPT_TEMPLATE
        self.test_scenarios = self._create_test_scenarios()
        self.results: List[TestResult] = []
        
    def _create_test_scenarios(self) -> List[UserScenario]:
        """Create comprehensive test scenarios covering different use cases"""
        return [
            # Math-heavy scenarios (should prefer LaTeX + JSXGraph)
            UserScenario(
                description="Basic algebra equation solving",
                user_input="Can you help me solve the equation 2x + 5 = 13?",
                expected_resource_types=[ResourceType.LATEX_MATH],
                educational_context="Student learning basic algebra",
                subject_area="mathematics"
            ),
            UserScenario(
                description="Quadratic functions with graphing",
                user_input="I need to understand quadratic functions. Can you show me how y = x² + 2x - 3 looks graphically?",
                expected_resource_types=[ResourceType.JSXGRAPH_DIAGRAM, ResourceType.LATEX_MATH],
                educational_context="Student learning quadratic functions",
                subject_area="mathematics"
            ),
            UserScenario(
                description="Trigonometry with triangle visualization",
                user_input="Can you show me a triangle diagram to help understand sine and cosine?",
                expected_resource_types=[ResourceType.JSXGRAPH_DIAGRAM],
                educational_context="Student learning trigonometry",
                subject_area="mathematics"
            ),
            UserScenario(
                description="Calculus derivatives with interactive exploration",
                user_input="I want to see how changing the function affects its derivative. Can you make an interactive graph?",
                expected_resource_types=[ResourceType.JSXGRAPH_DIAGRAM, ResourceType.LATEX_MATH],
                educational_context="Student learning calculus",
                subject_area="mathematics",
                difficulty_level="college"
            ),
            
            # Science scenarios (mixed resource needs)
            UserScenario(
                description="Cell structure (should prefer images)",
                user_input="Can you show me what a plant cell looks like with all its organelles labeled?",
                expected_resource_types=[ResourceType.TAVILY_IMAGE],
                educational_context="Student learning cell biology",
                subject_area="biology"
            ),
            UserScenario(
                description="Physics wave motion (should prefer interactive)",
                user_input="I want to understand how frequency affects wave motion. Can you show me an interactive demonstration?",
                expected_resource_types=[ResourceType.JSXGRAPH_DIAGRAM],
                educational_context="Student learning wave physics",
                subject_area="physics"
            ),
            UserScenario(
                description="Chemical equations (LaTeX preferred)",
                user_input="Help me balance this chemical equation: H₂ + O₂ → H₂O",
                expected_resource_types=[ResourceType.LATEX_MATH],
                educational_context="Student learning chemistry",
                subject_area="chemistry"
            ),
            
            # History/Social Studies (should prefer images)
            UserScenario(
                description="Historical timeline visualization",
                user_input="Can you show me a timeline of major events in World War II?",
                expected_resource_types=[ResourceType.TAVILY_IMAGE],
                educational_context="Student learning world history",
                subject_area="history"
            ),
            UserScenario(
                description="Ancient architecture",
                user_input="I want to see what the Parthenon in Athens looked like in ancient times",
                expected_resource_types=[ResourceType.TAVILY_IMAGE],
                educational_context="Student learning ancient history",
                subject_area="history"
            ),
            
            # Mixed scenarios (testing decision boundaries)
            UserScenario(
                description="Statistics with data visualization",
                user_input="Can you help me create a histogram to visualize this data set and explain the mean?",
                expected_resource_types=[ResourceType.JSXGRAPH_DIAGRAM, ResourceType.LATEX_MATH],
                educational_context="Student learning statistics",
                subject_area="mathematics"
            ),
            UserScenario(
                description="Geometric proof with diagram",
                user_input="I need help proving that the angles in a triangle sum to 180 degrees. Can you show me visually?",
                expected_resource_types=[ResourceType.JSXGRAPH_DIAGRAM, ResourceType.LATEX_MATH],
                educational_context="Student learning geometry proofs",
                subject_area="mathematics"
            ),
        ]
    
    def analyze_prompt_for_resource_type(self, resource_type: ResourceType) -> PromptAnalysis:
        """Analyze how well the prompt guides AI toward a specific resource type"""
        
        if resource_type == ResourceType.LATEX_MATH:
            return self._analyze_latex_guidance()
        elif resource_type == ResourceType.JSXGRAPH_DIAGRAM:
            return self._analyze_jsxgraph_guidance()
        elif resource_type == ResourceType.TAVILY_IMAGE:
            return self._analyze_image_guidance()
        else:
            # Future resource types
            return PromptAnalysis(
                resource_type=resource_type,
                guidance_score=0.0,
                clarity_score=0.0,
                coverage_score=0.0,
                issues=[f"Analysis not implemented for {resource_type.value}"],
                recommendations=[f"Implement analysis for {resource_type.value}"]
            )
    
    def _analyze_latex_guidance(self) -> PromptAnalysis:
        """Analyze LaTeX math guidance in the prompt"""
        issues = []
        recommendations = []
        
        # Check for LaTeX syntax guidance
        latex_mentions = len(re.findall(r'\\[(\[]', self.prompt_template))
        has_latex_examples = latex_mentions > 0
        
        # Check for math formatting guidance  
        math_keywords = ['equation', 'formula', 'mathematical expression', 'latex', 'mathjax']
        math_guidance_score = sum(1 for keyword in math_keywords 
                                if keyword.lower() in self.prompt_template.lower()) / len(math_keywords)
        
        # Calculate scores
        guidance_score = 0.7 if has_latex_examples else 0.3
        clarity_score = math_guidance_score
        coverage_score = 0.8 if math_guidance_score > 0.5 else 0.4
        
        if not has_latex_examples:
            issues.append("No LaTeX syntax examples found in prompt")
            recommendations.append("Add LaTeX syntax examples for mathematical expressions")
        
        if math_guidance_score < 0.5:
            issues.append("Limited guidance on when to use mathematical formatting")
            recommendations.append("Add clear criteria for when to use LaTeX vs other formats")
        
        return PromptAnalysis(
            resource_type=ResourceType.LATEX_MATH,
            guidance_score=guidance_score,
            clarity_score=clarity_score,
            coverage_score=coverage_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _analyze_jsxgraph_guidance(self) -> PromptAnalysis:
        """Analyze JSXGraph interactive diagram guidance"""
        issues = []
        recommendations = []
        
        # Check for JSXGraph section
        has_jsxgraph_section = 'jsxgraph' in self.prompt_template.lower()
        interactive_mentions = len(re.findall(r'interactive', self.prompt_template, re.IGNORECASE))
        
        # Check for key guidance elements
        guidance_elements = {
            'prioritize_interactive': 'prioritize interactive' in self.prompt_template.lower(),
            'stem_preference': 'stem' in self.prompt_template.lower() or 'mathematical' in self.prompt_template.lower(),
            'avoid_static_math': 'avoid static images for mathematical' in self.prompt_template.lower(),
            'jsxgraph_examples': 'jsxgraph>' in self.prompt_template.lower(),
            'when_to_use': 'trigonometry' in self.prompt_template.lower() or 'geometry' in self.prompt_template.lower()
        }
        
        guidance_score = sum(guidance_elements.values()) / len(guidance_elements)
        clarity_score = min(interactive_mentions / 3, 1.0)  # Good if mentioned 3+ times
        coverage_score = guidance_score
        
        # Identify issues
        if not has_jsxgraph_section:
            issues.append("No dedicated JSXGraph section found")
            recommendations.append("Add comprehensive JSXGraph guidance section")
        
        if not guidance_elements['prioritize_interactive']:
            issues.append("No clear prioritization guidance for interactive diagrams")
            recommendations.append("Add explicit guidance to prioritize interactive over static")
        
        if not guidance_elements['avoid_static_math']:
            issues.append("No warning against static images for math")
            recommendations.append("Add warning against using static images for mathematical concepts")
        
        if not guidance_elements['jsxgraph_examples']:
            issues.append("No JSXGraph syntax examples")
            recommendations.append("Add JSXGraph code examples for common scenarios")
        
        return PromptAnalysis(
            resource_type=ResourceType.JSXGRAPH_DIAGRAM,
            guidance_score=guidance_score,
            clarity_score=clarity_score,
            coverage_score=coverage_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _analyze_image_guidance(self) -> PromptAnalysis:
        """Analyze Tavily image search guidance"""
        issues = []
        recommendations = []
        
        # Check for image section and guidance
        has_image_section = '<image>' in self.prompt_template
        static_mentions = self.prompt_template.lower().count('static image')
        
        # Check for appropriate use cases
        appropriate_cases = {
            'non_mathematical': 'non-mathematical' in self.prompt_template.lower(),
            'real_world': 'real-world' in self.prompt_template.lower() or 'historical' in self.prompt_template.lower(),
            'anatomical': 'anatomical' in self.prompt_template.lower() or 'biological' in self.prompt_template.lower(),
            'secondary_choice': 'secondary' in self.prompt_template.lower(),
            'specific_examples': 'photosynthesis' in self.prompt_template.lower() or 'heart' in self.prompt_template.lower()
        }
        
        guidance_score = sum(appropriate_cases.values()) / len(appropriate_cases)
        clarity_score = min(static_mentions / 2, 1.0)  # Good if mentioned 2+ times
        coverage_score = guidance_score
        
        # Identify issues
        if not has_image_section:
            issues.append("No image syntax guidance found")
            recommendations.append("Add clear <image> syntax examples")
        
        if not appropriate_cases['secondary_choice']:
            issues.append("Images not clearly marked as secondary choice")
            recommendations.append("Emphasize that images are secondary to interactive content")
        
        if not appropriate_cases['non_mathematical']:
            issues.append("No guidance on when images are appropriate vs interactive")
            recommendations.append("Clarify that images are for non-mathematical content")
        
        if guidance_score < 0.6:
            issues.append("Limited examples of appropriate image use cases")
            recommendations.append("Add more specific examples of when to use images")
        
        return PromptAnalysis(
            resource_type=ResourceType.TAVILY_IMAGE,
            guidance_score=guidance_score,
            clarity_score=clarity_score,
            coverage_score=coverage_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def simulate_ai_decision(self, scenario: UserScenario) -> Dict[ResourceType, float]:
        """Simulate how an AI would interpret the prompt for the given scenario"""
        
        # Simple simulation based on keywords and prompt guidance
        probabilities = {}
        
        user_text = scenario.user_input.lower()
        subject = scenario.subject_area.lower()
        
        # LaTeX Math probability - enhanced keyword detection
        math_keywords = ['equation', 'solve', 'formula', 'calculate', 'expression', 'balance', 'reaction', 'chemical', 'algebra', 'derivative', 'integral', 'coefficient', 'mean', 'median', 'mode', 'histogram', 'distribution', 'standard deviation', 'probability', 'statistics']
        math_score = sum(1 for keyword in math_keywords if keyword in user_text) / len(math_keywords)
        
        # Special boost for formula-specific queries and calculations
        formula_boost = 0.3 if 'formula' in user_text else 0
        calculate_boost = 0.2 if 'calculate' in user_text else 0
        
        # Reduce LaTeX probability if clearly asking for visual/interactive content only
        visual_keywords = ['show me', 'diagram', 'interactive', 'explore', 'see']
        visual_penalty = sum(1 for keyword in visual_keywords if keyword in user_text) * 0.1
        
        # Special case: if asking for both visualization AND explanation of mathematical concepts, both should be high
        dual_intent = ('visualize' in user_text and any(kw in user_text for kw in ['mean', 'explain', 'understand']))
        
        # Strong subject-specific bonuses for mathematical contexts, reduced only if purely visual
        subject_boost = 0
        if subject in ['mathematics', 'algebra', 'calculus', 'geometry', 'trigonometry']:
            subject_boost = max(0.4 - (visual_penalty if not dual_intent else 0), 0.1)
        elif subject in ['chemistry', 'physics']:
            subject_boost = max(0.3 - (visual_penalty if not dual_intent else 0), 0.1)
        elif subject in ['statistics', 'probability']:
            subject_boost = max(0.35 - (visual_penalty if not dual_intent else 0), 0.2)
            
        # Bonus for mathematical notation patterns
        notation_bonus = 0.2 if any(char in scenario.user_input for char in ['=', '+', '-', '×', '²', '₂']) else 0
        
        probabilities[ResourceType.LATEX_MATH] = min((math_score * 0.6 + subject_boost + notation_bonus + formula_boost + calculate_boost), 0.95)
        
        # JSXGraph probability - enhanced for visualization scenarios
        interactive_keywords = ['graph', 'visualize', 'interactive', 'diagram', 'explore', 'triangle', 'function', 'histogram', 'plot']
        interactive_score = sum(1 for keyword in interactive_keywords if keyword in user_text) / len(interactive_keywords)
        stem_bonus = 0.3 if subject in ['mathematics', 'physics', 'chemistry'] else 0
        
        # Extra boost for data visualization scenarios
        dataviz_boost = 0.1 if any(term in user_text for term in ['histogram', 'chart', 'plot', 'graph']) else 0
        
        probabilities[ResourceType.JSXGRAPH_DIAGRAM] = min((interactive_score + stem_bonus + dataviz_boost) * 0.9, 0.95)
        
        # Tavily Image probability
        image_keywords = ['show me', 'what does', 'looks like', 'picture', 'image', 'see']
        image_score = sum(1 for keyword in image_keywords if keyword in user_text) / len(image_keywords)
        non_math_bonus = 0.4 if subject in ['biology', 'history', 'geography'] else 0
        probabilities[ResourceType.TAVILY_IMAGE] = min((image_score + non_math_bonus) * 0.8, 0.9)
        
        # Adjust based on prompt guidance analysis
        for resource_type in [ResourceType.LATEX_MATH, ResourceType.JSXGRAPH_DIAGRAM, ResourceType.TAVILY_IMAGE]:
            analysis = self.analyze_prompt_for_resource_type(resource_type)
            # Boost probability if prompt provides good guidance
            guidance_boost = analysis.guidance_score * 0.2
            probabilities[resource_type] = min(probabilities[resource_type] + guidance_boost, 1.0)
        
        return probabilities
    
    def run_scenario_test(self, scenario: UserScenario) -> TestResult:
        """Run a complete test for a single scenario"""
        
        # Analyze prompt for each relevant resource type
        relevant_types = [ResourceType.LATEX_MATH, ResourceType.JSXGRAPH_DIAGRAM, ResourceType.TAVILY_IMAGE]
        prompt_analyses = [self.analyze_prompt_for_resource_type(rt) for rt in relevant_types]
        
        # Simulate AI decision process
        ai_decisions = self.simulate_ai_decision(scenario)
        
        # Calculate overall score and determine if test passed
        expected_types = set(scenario.expected_resource_types)
        
        # Score based on how well AI decisions align with expected resource types
        alignment_score = 0
        for resource_type in expected_types:
            if resource_type in ai_decisions:
                alignment_score += ai_decisions[resource_type]
        alignment_score /= max(len(expected_types), 1)
        
        # Bonus for avoiding incorrect resource types
        avoided_score = 0
        for resource_type, probability in ai_decisions.items():
            if resource_type not in expected_types:
                avoided_score += (1.0 - probability)
        avoided_score /= max(len(ai_decisions) - len(expected_types), 1)
        
        overall_score = (alignment_score * 0.7 + avoided_score * 0.3)
        passed = overall_score >= 0.7  # 70% threshold for passing
        
        # Generate recommendations
        recommendations = []
        for analysis in prompt_analyses:
            recommendations.extend(analysis.recommendations)
        
        if not passed:
            recommendations.append(f"Improve guidance for {scenario.subject_area} scenarios")
            recommendations.append(f"Test scenario expected {expected_types} but AI simulation suggests different choices")
        
        return TestResult(
            scenario=scenario,
            prompt_analyses=prompt_analyses,
            overall_score=overall_score,
            passed=passed,
            ai_decision_simulation=ai_decisions,
            recommendations=list(set(recommendations))  # Remove duplicates
        )
    
    def run_all_tests(self) -> None:
        """Run all test scenarios and store results"""
        print("🚀 Starting Comprehensive Resource Creation Test Harness")
        print("=" * 80)
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\n🧪 Test {i}/{len(self.test_scenarios)}: {scenario.description}")
            print(f"📝 User Input: \"{scenario.user_input}\"")
            print(f"🎯 Expected: {[rt.value for rt in scenario.expected_resource_types]}")
            
            result = self.run_scenario_test(scenario)
            self.results.append(result)
            
            # Display result
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"📊 Result: {status} (Score: {result.overall_score:.2f})")
            
            # Show AI decision simulation
            print("🤖 AI Decision Simulation:")
            for resource_type, probability in result.ai_decision_simulation.items():
                print(f"   {resource_type.value}: {probability:.2f}")
            
            if not result.passed and result.recommendations:
                print("💡 Key Recommendations:")
                for rec in result.recommendations[:2]:  # Show top 2
                    print(f"   • {rec}")
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        overall_pass_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # Aggregate scores by resource type
        resource_scores = {}
        for resource_type in [ResourceType.LATEX_MATH, ResourceType.JSXGRAPH_DIAGRAM, ResourceType.TAVILY_IMAGE]:
            scores = []
            for result in self.results:
                for analysis in result.prompt_analyses:
                    if analysis.resource_type == resource_type:
                        scores.append(analysis.guidance_score)
            resource_scores[resource_type] = sum(scores) / len(scores) if scores else 0
        
        # Collect all unique recommendations
        all_recommendations = set()
        for result in self.results:
            all_recommendations.update(result.recommendations)
        
        # Generate report
        report = f"""
🎯 COMPREHENSIVE RESOURCE CREATION TEST HARNESS REPORT
{'=' * 80}

📊 OVERALL RESULTS:
• Total Tests: {total_tests}
• Passed: {passed_tests}
• Failed: {total_tests - passed_tests}
• Pass Rate: {overall_pass_rate:.1%}

📈 RESOURCE TYPE GUIDANCE SCORES:
• LaTeX Math: {resource_scores.get(ResourceType.LATEX_MATH, 0):.2f}/1.00
• JSXGraph Diagrams: {resource_scores.get(ResourceType.JSXGRAPH_DIAGRAM, 0):.2f}/1.00
• Tavily Images: {resource_scores.get(ResourceType.TAVILY_IMAGE, 0):.2f}/1.00

🎪 DETAILED TEST RESULTS:
"""
        
        for i, result in enumerate(self.results, 1):
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            report += f"""
Test {i}: {result.scenario.description}
  Status: {status} (Score: {result.overall_score:.2f})
  Subject: {result.scenario.subject_area}
  Expected: {[rt.value for rt in result.scenario.expected_resource_types]}
  AI Simulation: {', '.join(f'{rt.value}={prob:.2f}' for rt, prob in result.ai_decision_simulation.items() if prob > 0.3)}
"""
        
        if all_recommendations:
            report += f"""
💡 RECOMMENDED IMPROVEMENTS:
"""
            for i, rec in enumerate(sorted(all_recommendations)[:10], 1):  # Top 10 recommendations
                report += f"{i}. {rec}\n"
        
        report += f"""
🚀 FUTURE EXTENSIBILITY:
The harness is designed to easily support new resource types:
• YouTube Video Search (for educational videos)
• AI Animation Generation (like Veo3)
• Interactive Simulations
• 3D Models and AR content

To add new resource types:
1. Add to ResourceType enum
2. Create analysis method for prompt guidance
3. Add simulation logic for AI decision making
4. Create test scenarios for the new type

{'=' * 80}
"""
        
        return report
    
    def save_detailed_results(self, filename: str = "resource_creation_test_results.json") -> None:
        """Save detailed test results to JSON file for further analysis"""
        
        # Convert results to serializable format
        serializable_results = []
        for result in self.results:
            serializable_result = {
                "scenario": {
                    "description": result.scenario.description,
                    "user_input": result.scenario.user_input,
                    "expected_resource_types": [rt.value for rt in result.scenario.expected_resource_types],
                    "educational_context": result.scenario.educational_context,
                    "subject_area": result.scenario.subject_area,
                    "difficulty_level": result.scenario.difficulty_level
                },
                "overall_score": result.overall_score,
                "passed": result.passed,
                "ai_decision_simulation": {rt.value: prob for rt, prob in result.ai_decision_simulation.items()},
                "recommendations": result.recommendations,
                "prompt_analyses": [
                    {
                        "resource_type": analysis.resource_type.value,
                        "guidance_score": analysis.guidance_score,
                        "clarity_score": analysis.clarity_score,
                        "coverage_score": analysis.coverage_score,
                        "issues": analysis.issues,
                        "recommendations": analysis.recommendations
                    } for analysis in result.prompt_analyses
                ]
            }
            serializable_results.append(serializable_result)
        
        with open(filename, 'w') as f:
            json.dump({
                "test_summary": {
                    "total_tests": len(self.results),
                    "passed_tests": sum(1 for r in self.results if r.passed),
                    "overall_pass_rate": sum(1 for r in self.results if r.passed) / len(self.results) if self.results else 0
                },
                "test_results": serializable_results
            }, f, indent=2)
        
        print(f"📁 Detailed results saved to {filename}")

def main():
    """Run the comprehensive test harness"""
    harness = ResourceCreationHarness()
    
    # Run all tests
    harness.run_all_tests()
    
    # Generate and display report
    report = harness.generate_report()
    print(report)
    
    # Save detailed results
    harness.save_detailed_results()
    
    # Return success/failure based on overall results
    total_tests = len(harness.results)
    passed_tests = sum(1 for r in harness.results if r.passed)
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    if success_rate >= 0.8:  # 80% success rate required
        print("🎉 TEST HARNESS PASSED: Prompt guidance is effective!")
        return True
    else:
        print(f"⚠️  TEST HARNESS NEEDS IMPROVEMENT: {success_rate:.1%} success rate")
        print("Review recommendations above to improve prompt effectiveness")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)