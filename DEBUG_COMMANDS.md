# Debug Mode for Skipping Lessons

This feature adds debug commands to the Autodidact learning sessions to help developers and testers quickly progress through lessons without completing the full learning process.

## Available Commands

### `/completed`
Force completes the current learning session with a high score (85%).

**What it does:**
- Marks the current session as completed
- Sets all learning objectives for the current node to high mastery (0.85/1.0)
- Updates the node's overall mastery score
- Allows progression to the next topic in the knowledge graph

**Usage:**
Type `/completed` in the chat input during any active learning session.

### `/help` or `/debug`
Shows a help message with available debug commands.

**Usage:**
Type `/help` or `/debug` in the chat input to see the available commands.

## How It Works

1. **Command Detection**: The system detects any message starting with `/` as a potential debug command
2. **Command Processing**: Valid debug commands are processed before normal tutoring responses  
3. **Session State**: Commands modify the session state and database directly
4. **User Feedback**: Users receive immediate feedback about the command execution

## Implementation Details

### Files Modified/Added:
- `backend/debug_commands.py` - New module containing debug command logic
- `pages/session_detail.py` - Modified to handle debug commands in chat input
- `test_debug_commands.py` - Test script to verify functionality

### Key Functions:
- `is_debug_command(message)` - Detects if a message is a debug command
- `handle_debug_command(message, session_info)` - Processes debug commands
- `force_complete_session(session_id, node_id)` - Completes a session with high scores

## Usage Scenarios

This feature is designed for:

1. **Development Testing**: Quickly progress through lessons to test other features
2. **Debugging**: Skip to specific parts of the learning flow
3. **Demo Preparation**: Set up demo scenarios with completed lessons
4. **QA Testing**: Test progression logic without manual lesson completion

## Safety Considerations

- Debug commands only work during active learning sessions
- Commands are case-insensitive for user convenience
- Invalid commands show helpful error messages
- The feature doesn't interfere with normal learning flow
- Help is easily accessible via `/help` command

## Testing

Run the test script to verify functionality:

```bash
python test_debug_commands.py
```

This will test command detection, handling, and error cases to ensure the feature works correctly.