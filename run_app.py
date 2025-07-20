#!/usr/bin/env python3
"""
Simple script to run the Oppenheimer Time Machine application.
This handles the streamlit command and provides helpful error messages.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import google.generativeai
        import chromadb
        print("✓ All required dependencies found")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are set."""
    env_file = Path(".env")
    if not env_file.exists():
        print("✗ .env file not found")
        print("Create .env file with GEMINI_API_KEY and GOOGLE_CLOUD_PROJECT")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('GEMINI_API_KEY'):
        print("✗ GEMINI_API_KEY not set in .env")
        return False
    
    print("✓ Environment variables configured")
    return True

def main():
    """Main function to run the application."""
    print("🚀 Oppenheimer Time Machine Setup Check")
    print("=" * 50)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    print("\n✓ All checks passed!")
    print("🎭 Starting the Conversational Time Machine...")
    print("=" * 50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Goodbye from Dr. Oppenheimer!")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()