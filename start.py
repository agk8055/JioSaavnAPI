#!/usr/bin/env python3
"""
Startup script for local development
Uses Gunicorn on Unix/Linux/Mac, Flask dev server on Windows
"""
import os
import subprocess
import sys
import platform

def main():
    # Get port from environment or use default
    port = os.environ.get('PORT', '5100')
    
    # Check if running on Windows
    if platform.system() == 'Windows':
        print(f"Starting JioSaavn API with Flask development server on port {port}")
        print("Note: Using Flask dev server (Gunicorn not available on Windows)")
        print("For production deployment, use a Unix-based system or cloud platform")
        print("Press Ctrl+C to stop")
        
        # Import and run Flask app directly
        try:
            from app import app
            app.run(host='0.0.0.0', port=int(port), debug=True)
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)
    else:
        # Gunicorn command for Unix/Linux/Mac
        cmd = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '2',  # Fewer workers for local development
            '--timeout', '120',
            '--keep-alive', '2',
            '--reload',  # Auto-reload on code changes
            'app:app'
        ]
        
        print(f"Starting JioSaavn API with Gunicorn on port {port}")
        print(f"Command: {' '.join(cmd)}")
        print("Press Ctrl+C to stop")
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)

if __name__ == '__main__':
    main() 