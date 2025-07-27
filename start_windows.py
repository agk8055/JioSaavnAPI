#!/usr/bin/env python3
"""
Windows-specific startup script for JioSaavn API
Uses Flask development server since Gunicorn is not available on Windows
"""
import os
import sys

def main():
    # Get port from environment or use default
    port = int(os.environ.get('PORT', '5100'))
    
    print(f"Starting JioSaavn API with Flask development server on port {port}")
    print("Note: Using Flask dev server (Gunicorn not available on Windows)")
    print("For production deployment, use a Unix-based system or cloud platform")
    print("Press Ctrl+C to stop")
    
    try:
        from app import app
        app.run(host='0.0.0.0', port=port, debug=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 