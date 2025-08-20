# Resource Creation Test Harness

A comprehensive test harness for validating that prompts effectively guide AI to create the correct types of educational resources (LaTeX math, JSXGraph diagrams, Tavily images).

## Purpose

This test harness addresses the need identified in Issue #98 to validate and fine-tune lesson prompts to ensure AI creates appropriate educational resources. It helps ensure that when users ask for mathematical concepts, the AI chooses interactive diagrams over static images, and when users ask for biological structures, the AI chooses appropriate visual resources.

## Features

- ✅ **Validates prompt effectiveness** for all resource types
- ✅ **Tests realistic user scenarios** across multiple subjects
- ✅ **Simulates AI decision-making** process
- ✅ **Provides actionable recommendations** for prompt improvement
- ✅ **Extensible design** for future resource types (YouTube videos, AI animations)
- ✅ **Generates detailed reports** and metrics
- ✅ **JSON output** for further analysis

## Resource Types Supported

### Current Implementation
1. **LaTeX Math** (`latex_math`) - Mathematical equations and formulas
2. **JSXGraph Diagrams** (`jsxgraph_diagram`) - Interactive mathematical visualizations
3. **Tavily Images** (`tavily_image`) - Static images for non-mathematical content

### Future Extensions (Ready for Implementation)
4. **YouTube Videos** (`youtube_video`) - Educational video search
5. **AI Animations** (`ai_animation`) - AI-generated animations (e.g., Veo3)

## Usage

### Quick Start

```bash
# Run the full test harness
python test_resource_creation_harness.py

# Run integration tests
python test_resource_validation_integration.py

# See demonstration of features
python demo_resource_creation_testing.py
```

### Basic Usage

```python
from test_resource_creation_harness import ResourceCreationHarness, UserScenario, ResourceType

# Create and run the harness
harness = ResourceCreationHarness()
harness.run_all_tests()

# Generate report
report = harness.generate_report()
print(report)

# Save detailed results
harness.save_detailed_results("my_test_results.json")
```

### Adding Custom Test Scenarios

```python
# Create a custom scenario
custom_scenario = UserScenario(
    description="Custom physics scenario",
    user_input="Can you show me how waves interfere with each other?",
    expected_resource_types=[ResourceType.JSXGRAPH_DIAGRAM],
    educational_context="Student learning wave physics",
    subject_area="physics"
)

# Test the scenario
harness = ResourceCreationHarness()
result = harness.run_scenario_test(custom_scenario)
print(f"Result: {'PASSED' if result.passed else 'FAILED'} (Score: {result.overall_score:.2f})")
```

## Test Scenarios

The harness includes comprehensive test scenarios covering:

### Mathematics
- Basic algebra (should prefer LaTeX)
- Quadratic functions with graphing (should prefer JSXGraph + LaTeX)
- Trigonometry with triangles (should prefer JSXGraph)
- Calculus derivatives (should prefer JSXGraph + LaTeX)
- Statistics with data visualization (should prefer JSXGraph + LaTeX)
- Geometric proofs (should prefer JSXGraph + LaTeX)

### Sciences
- Cell biology (should prefer images)
- Physics wave motion (should prefer JSXGraph)
- Chemical equations (should prefer LaTeX)

### History/Social Studies
- Historical timelines (should prefer images)
- Ancient architecture (should prefer images)

## Output and Reports

### Console Output
- Real-time test progress
- Pass/fail status for each scenario
- AI decision simulation results
- Key recommendations

### Comprehensive Report
- Overall pass rate and statistics
- Resource type guidance scores
- Detailed test results
- Prioritized recommendations for improvement

### JSON Output
- Machine-readable test results
- Detailed analysis data
- Perfect for integration with CI/CD pipelines

## Understanding the Analysis

### Scoring System
- **Guidance Score** (0-1.0): How well the prompt guides toward the resource type
- **Clarity Score** (0-1.0): How clear the guidance is
- **Coverage Score** (0-1.0): How well scenarios are covered
- **Overall Score** (0-1.0): Combined effectiveness for each test scenario

### AI Decision Simulation
The harness simulates how an AI model would interpret prompts by:
1. Analyzing keywords in user input
2. Considering subject area context
3. Applying prompt guidance weighting
4. Generating probability scores for each resource type

### Pass/Fail Criteria
- Tests pass with an overall score ≥ 0.70 (70%)
- AI simulation must favor expected resource types
- Unexpected resource types should have low probability

## Extending for New Resource Types

To add support for new resource types (e.g., YouTube videos):

1. **Add to enum:**
```python
class ResourceType(Enum):
    YOUTUBE_VIDEO = "youtube_video"
```

2. **Create analysis method:**
```python
def _analyze_youtube_guidance(self) -> PromptAnalysis:
    # Analyze prompt for YouTube guidance
    pass
```

3. **Add simulation logic:**
```python
# Add YouTube probability calculation
youtube_score = calculate_youtube_probability(user_input, subject_area)
probabilities[ResourceType.YOUTUBE_VIDEO] = youtube_score
```

4. **Create test scenarios:**
```python
UserScenario(
    description="Historical documentary request",
    user_input="Can you find a documentary about the Industrial Revolution?",
    expected_resource_types=[ResourceType.YOUTUBE_VIDEO],
    subject_area="history"
)
```

## Integration with CI/CD

The test harness is designed for integration with continuous integration:

```bash
# Exit code 0 for success, 1 for failure
python test_resource_creation_harness.py
if [ $? -eq 0 ]; then
    echo "Prompt validation passed"
else
    echo "Prompt validation failed - check recommendations"
fi
```

## Current Results

Based on initial testing with existing prompts:

- **Overall Pass Rate:** 36.4% (needs improvement)
- **LaTeX Math Guidance:** 70% effective
- **JSXGraph Diagrams:** 100% effective  
- **Tavily Images:** 100% effective

### Key Issues Identified
1. LaTeX math scenarios need better guidance keywords
2. Chemistry and physics scenarios need subject-specific guidance
3. Mixed resource scenarios (LaTeX + JSXGraph) need clearer criteria

### Recommended Improvements
1. Add more LaTeX syntax examples in prompts
2. Include subject-specific decision criteria
3. Clarify when to use multiple resource types
4. Add warning against inappropriate resource choices

## Files

- `test_resource_creation_harness.py` - Main test harness implementation
- `test_resource_validation_integration.py` - Integration tests
- `demo_resource_creation_testing.py` - Feature demonstration
- `resource_creation_test_results.json` - Sample output (generated)

## Dependencies

- Python 3.7+
- Existing autodidact-agent components:
  - `backend.tutor_prompts`
  - `utils.math_utils` (optional)
  - `components.jsxgraph_utils` (optional)
  - `utils.tavily_integration` (optional)

## Contributing

To contribute new test scenarios or improvements:

1. Add test scenarios to `_create_test_scenarios()`
2. Enhance analysis methods for better prompt evaluation
3. Improve AI decision simulation accuracy
4. Add support for new resource types

## License

Part of the autodidact-agent project. See main project license.