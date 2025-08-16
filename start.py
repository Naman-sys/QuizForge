#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    # Get port from environment or use default
    port = os.environ.get('PORT', '8501')
    
    # Build streamlit command
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'app.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false'
    ]
    
    print(f"Starting Streamlit on port {port}")
    print(f"Command: {' '.join(cmd)}")
    
    # Run streamlit
    subprocess.run(cmd)

if __name__ == "__main__":
    main()