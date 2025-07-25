#!/usr/bin/env python3
"""
Wrapper script to run the Autodidact app with debug support.

This script handles the --debug flag that Streamlit CLI doesn't natively support.
"""
import sys
import os
import subprocess
import argparse

def main():
    """Main entry point for the wrapper script."""
    parser = argparse.ArgumentParser(
        description="Run Autodidact with Streamlit", 
        add_help=False  # We'll pass through --help to streamlit
    )
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Parse known args to extract --debug, leaving the rest for streamlit
    args, remaining_args = parser.parse_known_args()
    
    # Set debug environment variable if --debug was specified
    env = os.environ.copy()
    if args.debug:
        env['AUTODIDACT_DEBUG'] = 'true'
        print("🐛 Debug mode enabled")
    
    # Build streamlit command with remaining arguments
    streamlit_cmd = ['streamlit', 'run', 'app.py'] + remaining_args
    
    # Execute streamlit with the modified environment
    try:
        subprocess.run(streamlit_cmd, env=env)
    except KeyboardInterrupt:
        print("\n👋 Stopping Autodidact...")
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()