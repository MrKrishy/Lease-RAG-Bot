#!/usr/bin/env python3
"""
Simple launcher script for the Lease Document Q&A Web Application
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Lease Document Q&A Web Application...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found. Please run this script from the final/ directory.")
        sys.exit(1)
    
    # Check if openai.txt exists
    if not os.path.exists("openai.txt"):
        print("⚠️  Warning: openai.txt not found. Make sure your OpenAI API key is set.")
    
    # Check if Lease Contracts folder exists
    if not os.path.exists("Lease Contracts"):
        print("⚠️  Warning: 'Lease Contracts' folder not found.")
    
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please check requirements.txt")
        sys.exit(1)
    
    print("\n🌐 Starting web server...")
    print("📱 Once started, open your browser and go to: http://localhost:5000")
    print("🔍 You can then ask questions about your lease documents!")
    print("\nPress Ctrl+C to stop the server.")
    print("=" * 60)
    
    # Start the Flask app
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

