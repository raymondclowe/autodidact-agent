# Enhanced Logging and Debugging Tools

This document describes the enhanced logging and debugging tools implemented to address issue #42. These tools help diagnose and troubleshoot issues, especially when processes like "Deep Research" fail.

## Features

### 1. Debug Mode Activation

Debug mode can be enabled in two ways:

#### Command Line Flag
```bash
# Direct Python execution
python app.py --debug

# With Streamlit (using environment variable)
AUTODIDACT_DEBUG=true streamlit run app.py
```

#### Environment Variable
```bash
# Set environment variable
export AUTODIDACT_DEBUG=true
python app.py

# Or inline
AUTODIDACT_DEBUG=true python app.py
```

### 2. Persistent Debug Logging

When debug mode is enabled:

- **Debug Level Logging**: All log levels (DEBUG, INFO, WARNING, ERROR) are captured
- **Timestamped Files**: Debug logs are saved to `~/.autodidact/debug-YYYYMMDD-HHMMSS.log`
- **Dual Output**: Logs appear both in console and persistent file
- **Enhanced Formatting**: Detailed format includes timestamps, log levels, module names, and line numbers

Example debug log format:
```
2025-07-24 23:28:32,877 DEBUG [backend.db:70] get_db_connection called, DB_PATH=/home/runner/.autodidact/autodidact.db
2025-07-24 23:28:32,877 INFO [utils.config:59] Debug mode enabled - logging to /home/runner/.autodidact/debug-20250724-232832.log
```

### 3. Incident File Generation

For major errors (Deep Research failures, API errors, etc.), the system automatically creates comprehensive incident reports:

#### File Naming
- Format: `incident-YYYYMMDD-HHMMSS.log`
- Location: `~/.autodidact/incident-YYYYMMDD-HHMMSS.log`
- Unique timestamp ensures no overwrites

#### Content Structure
Each incident file contains:

1. **Header**: Incident report title and timestamp
2. **Error Details**: Message, type, status code, request ID
3. **Additional Information**: Context-specific debugging data
4. **System Information**: Python version, platform, working directory
5. **Environment Variables**: Autodidact-related environment settings (API keys excluded)
6. **Full JSON Data**: Complete structured data for programmatic analysis

Example incident file structure:
```
================================================================================
AUTODIDACT INCIDENT REPORT - 20250724-232404
================================================================================

INCIDENT TIME: 2025-07-24T23:24:04.820424
CONTEXT: Deep Research

ERROR DETAILS:
----------------------------------------
MESSAGE: Token limit exceeded for deep research model
TYPE: requested_too_many_tokens
CODE: None
STATUS_CODE: 400
REQUEST_ID: None
BODY: None

ADDITIONAL INFORMATION:
----------------------------------------
MODEL: o4-mini-deep-research-2025-06-26
TOPIC: Advanced Machine Learning Concepts
STUDY_HOURS: 5
ESTIMATED_TOKENS: 150000

SYSTEM INFORMATION:
----------------------------------------
PYTHON_VERSION: 3.12.3 (main, Jun 18 2025, 17:59:45) [GCC 13.3.0]
PLATFORM: posix
WORKING_DIRECTORY: /home/runner/work/autodidact-agent/autodidact-agent
ENVIRONMENT_VARS:

FULL JSON DATA:
----------------------------------------
{
  "timestamp": "2025-07-24T23:24:04.820424",
  "context": "Deep Research",
  "error_details": { ... },
  "additional_info": { ... },
  "system_info": { ... }
}
```

## Implementation Details

### Code Changes

#### `app.py` 
- Added `parse_debug_args()` function to detect debug flags before Streamlit initialization
- Supports both `--debug` command line argument and `AUTODIDACT_DEBUG` environment variable
- Removes `--debug` from `sys.argv` to prevent Streamlit conflicts

#### `utils/config.py`
- Added `configure_debug_logging()` function
- Creates timestamped debug log files in `~/.autodidact/` directory
- Configures Python logging with DEBUG level and enhanced formatting
- Supports both console and file output handlers

#### `utils/error_handling.py`
- Added `create_incident_file()` for comprehensive incident reporting
- Added `log_major_error()` for automated incident file generation
- Enhanced `handle_api_error()` to create incident files for major API errors
- Maintains existing error handling while adding incident reporting

### File Locations

All log files are stored in the user's home directory:
```
~/.autodidact/
├── debug-YYYYMMDD-HHMMSS.log     # Debug session logs
├── incident-YYYYMMDD-HHMMSS.log  # Error incident reports
└── autodidact.db                 # Application database
```

### Security Considerations

- **API Key Protection**: Environment variables containing API keys are not logged
- **File Permissions**: Log files use appropriate permissions (readable by user only)
- **Directory Creation**: Automatically creates `~/.autodidact/` directory with secure permissions

## Usage Examples

### Basic Debug Session
```bash
# Enable debug mode
python app.py --debug

# Check log file
ls ~/.autodidact/debug-*.log
tail -f ~/.autodidact/debug-20250724-232832.log
```

### Environment Variable Usage
```bash
# For Streamlit compatibility
export AUTODIDACT_DEBUG=true
streamlit run app.py

# Or inline
AUTODIDACT_DEBUG=true python app.py
```

### Incident Investigation
When an error occurs, check for incident files:
```bash
# List recent incidents
ls -la ~/.autodidact/incident-*.log

# View latest incident
cat ~/.autodidact/incident-$(ls ~/.autodidact/incident-*.log | sort | tail -1 | sed 's/.*incident-//' | sed 's/.log//')
```

## Testing

The implementation includes comprehensive tests in `test_enhanced_logging.py`:

- **Debug Logging Tests**: Verify log file creation and content
- **Incident Reporting Tests**: Validate incident file generation and format
- **Command Line Parsing Tests**: Test both flag and environment variable methods
- **Error Handling Tests**: Ensure proper error detail extraction

Run tests:
```bash
python -m pytest test_enhanced_logging.py -v
```

## Troubleshooting

### Debug Mode Not Working
1. Verify flag syntax: `--debug` (not `-debug` or `--debug=true`)
2. Check environment variable: `echo $AUTODIDACT_DEBUG`
3. Ensure permissions on `~/.autodidact/` directory

### Log Files Not Created
1. Check disk space and permissions
2. Verify `~/.autodidact/` directory exists and is writable
3. Look for error messages in console output

### Missing Incident Files
1. Verify error actually triggers incident creation (major errors only)
2. Check `~/.autodidact/` directory for recent files
3. Review console logs for incident file creation messages

## Benefits

1. **Improved Debugging**: Persistent logs survive application restarts
2. **Comprehensive Error Information**: Incident files provide complete context
3. **User-Friendly**: Simple activation via command line or environment variable
4. **Streamlit Compatible**: Works with both direct Python execution and Streamlit
5. **Non-Intrusive**: Minimal impact on normal operation when debug mode is disabled
6. **Automated**: Incident files are created automatically for major errors