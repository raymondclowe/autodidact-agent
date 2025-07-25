# Debug Mode for Autodidact

This document explains how to activate and use debug mode in Autodidact for enhanced logging and troubleshooting.

## What is Debug Mode?

Debug mode provides enhanced logging, verbose output, and additional debugging information in both the console and UI. When enabled, it:

- Creates timestamped debug log files
- Shows a prominent debug banner in the UI
- Displays debug information in the sidebar
- Enables verbose logging for troubleshooting
- Provides detailed environment and system information

## How to Enable Debug Mode

### Method 1: Command Line Flag

```bash
# For direct streamlit execution
streamlit run app.py -- --debug

# For development/testing
python app.py --debug
```

### Method 2: Environment Variable

```bash
# Set environment variable
export AUTODIDACT_DEBUG=true

# Then run normally
streamlit run app.py
```

### Method 3: Docker Environment Variable

```bash
# Using docker run
docker run -e AUTODIDACT_DEBUG=true -p 8501:8501 autodidact

# Using docker-compose with debug configuration
docker-compose -f docker-compose.debug.yml up
```

## Debug Mode Features

### Visual Indicators

When debug mode is active, you'll see:

1. **Red Debug Banner**: A prominent red banner at the top of every page stating "🐛 DEBUG MODE ACTIVE - Enhanced logging enabled"

2. **Sidebar Debug Info**: A "🐛 Debug Info" section in the sidebar showing:
   - Debug Mode: Active
   - Log File: Current debug log filename

### Debug Log Files

Debug log files are created in the configuration directory:
- **Location**: `~/.autodidact/debug-YYYYMMDD-HHMMSS.log`
- **Format**: Timestamped entries with detailed information
- **Permissions**: Secure (600) - readable only by owner
- **Content**: System info, environment variables, application events

### Enhanced Logging

Debug mode enables:
- **Verbose output**: Detailed system and environment information
- **File logging**: Persistent logs for later analysis
- **Console logging**: Real-time debug information
- **Structured format**: Easy to parse and analyze

## Docker Debug Configuration

### Using docker-compose.debug.yml

A special debug configuration is provided:

```yaml
services:
  autodidact:
    environment:
      - AUTODIDACT_DEBUG=true
      - STREAMLIT_LOGGER_LEVEL=debug
      - STREAMLIT_GLOBAL_DEVELOPMENT_MODE=true
    volumes:
      - ./debug-logs:/app/data/.autodidact
    entrypoint: ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--", "--debug"]
```

**Features**:
- Debug logs mounted to host `./debug-logs` directory
- Enhanced Streamlit logging
- Development mode enabled
- Debug flag passed to application

**Usage**:
```bash
# Start in debug mode
docker-compose -f docker-compose.debug.yml up

# Debug logs will be available in ./debug-logs/ directory
```

### Building with Debug Support

The Dockerfile supports debug mode via build arguments:

```bash
# Build with debug support
docker build --build-arg DEBUG_MODE=true -t autodidact-debug .

# Run with debug enabled
docker run -p 8501:8501 autodidact-debug
```

## Troubleshooting

### Debug Mode Not Activating

1. **Check argument parsing**: Ensure `--debug` comes after `--` when using streamlit
   ```bash
   # Correct
   streamlit run app.py -- --debug
   
   # Incorrect
   streamlit run app.py --debug
   ```

2. **Verify environment variable**: Check if `AUTODIDACT_DEBUG` is set correctly
   ```bash
   echo $AUTODIDACT_DEBUG
   ```

3. **Check permissions**: Ensure the config directory is writable
   ```bash
   ls -la ~/.autodidact/
   ```

### Log Files Empty

If debug log files are created but empty:
- Check file permissions
- Verify the application has write access to the config directory
- Look for error messages in console output

### Docker Debug Issues

For Docker-related debug problems:
- Ensure volume mounts are correct
- Check container environment variables: `docker exec -it <container> env | grep DEBUG`
- Verify the debug log directory is mounted properly

## Security Considerations

- Debug log files contain system information - review before sharing
- Log files are created with secure permissions (600)
- Debug mode may expose additional information in the UI
- Disable debug mode in production environments

## Example Debug Session

```bash
# Start debug mode
streamlit run app.py -- --debug

# Check debug log
tail -f ~/.autodidact/debug-$(date +%Y%m%d)*.log

# Debug information will show:
# - Python version and environment
# - Working directory
# - Environment variables
# - Application events and errors
```

## Integration with Development

Debug mode is designed to integrate seamlessly with development workflows:

- **Testing**: Use debug mode during testing to capture detailed logs
- **Development**: Enable debug mode during development for verbose output
- **CI/CD**: Debug logs can be captured and archived for analysis
- **Troubleshooting**: User issues can be diagnosed with debug logs

The debug functionality is designed to be minimal, secure, and helpful for both developers and users troubleshooting issues.